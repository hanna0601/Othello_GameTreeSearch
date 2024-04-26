"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

# v3

# create a global dictionary variable to store the visited state of the board
# for minmax
# cached_states stores (board, color) as the key and the value is (action, utility)
# given the board, and player color (max node or min node)
# action is the move of the player color, could be the action of max node or the min node
# utility is always the utility of the max node 

# for alpha-beta pruning
# cached_states stores (board, color, alpha, beta) as the key and the value is (action, utility)
# given the board, player color, alpha and beta
# action is the move of the player color, could be the action of max node or the min node
# utility is always the utility of the max node

cached_states = {} 


def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT

    ## color = 1 indicates first player, color = 2 indicates second player
    score = get_score(board) # a tuple containing the score of player 1 and player 2

    utility = score[0] - score[1]

    if color == 1:
        return utility
    elif color == 2:
        return -utility
    else:
        return 0


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT

    # consider the following factors to compute the heuristic value
    # - the number of sub plots that can not be claimed anymore
    #    - on the corners
    #    - on the edges
    #    - on the sub plots that are adjacent to the corners
    # - the number of sub plots that can be claimed by the player

    # for the four edges
    n = len(board)
    
    # check the four edges and the four corners
    horizontal = 0
    for a in [0, n - 1]:

        i = 0
        while i < n and board[a][i] == color:
            i += 1
        
        j = 0
        while j < n and board[a][n-1-j] == color and i + j < n:
            j += 1
        
        if i + j == n:
            horizontal += n
        else:
            horizontal += i + j

    vertical = 0
    for b in [0, n - 1]:

        i = 0
        while i < n and board[i][b] == color:
            i += 1
        
        j = 0
        while j < n and board[n-1-j][b] == color and i + j < n:
            j += 1
        
        if i + j == n:
            vertical += n
        else:
            vertical += i + j
    
    # mobile reflects the number of possible moves 
    mobile = len(get_possible_moves(board, color)) - len(get_possible_moves(board, 3 - color))

    # score reflects the difference between the player's score and the competitor's score
    score = compute_utility(board, color)

    return mobile +  2* score + 3 * (horizontal + vertical)


############ MINIMAX ###############################

# return the color of the competitor
def get_competitor_color(color):
    # if the color is 1, return 2
    # if the color is 2, return 1
    return 3 - color  
    

def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)

    # Note here, the color is the max player color
    # its competitor is the min node, which tries to minimize the max node's utility
    # !!!! Assume the returned value is the action of the min node and the corresponding utility for the max node

    # if the current board state has been visited before, return the value from the cache
    if caching != 0 and (board, 3 - color) in cached_states.keys():

        return cached_states[(board, 3 - color)] # return the action of the min node and the corresponding utility for max node
    
    if limit == 0:
        return None, compute_utility(board, color)
    

    # get the possible moves for the min node
    possible_moves = get_possible_moves(board, 3 - color)  # get the possible moves for the min player

    # if the possible moves are empty, or the limit is reduced to 0, return (NULL, utility)
    if possible_moves == []:
        return None, compute_utility(board, color)  # this is the utility for the max player

    # initialize the minimum utility and the minimum action
    min_utility = float('inf')
    min_action = None

    # iterate through the possible moves, and get the minimum utility and the minimum action
    for i, j in possible_moves:
        new_board = play_move(board, 3 - color, i, j)

        new_action, new_utility = minimax_max_node(new_board, color, limit - 1, caching)

        # the competitor tries to minimize the utility
        if new_utility < min_utility:
            min_utility = new_utility
            min_action = (i, j)
    
    if caching != 0:
        cached_states[(board, 3 - color)] = (min_action, min_utility)
    
    return min_action, min_utility # return the action and utility of the max node based on the min node's move


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)


    # if the current board state has been visited before, return the value from the cache

    if caching != 0 and (board, color) in cached_states.keys():

        return cached_states[(board, color)]
    
    if limit == 0:
        return None, compute_utility(board, color)
    
    # get the possible moves for the current max player
    possible_moves = get_possible_moves(board, color)  # returns a list of (column, row) tuples.


    # if the possible moves are empty, or the limit is reduced to 0, return (NULL, utility)
    if possible_moves == []:
        return None, compute_utility(board, color)
    
    # initialize the maximum utility and the maximum action
    max_utility = float('-inf')
    max_action = None

    # iterate through the possible moves, and get the maximum utility and the maximum action
    for i, j in possible_moves:

        # get the new board after playing the move for the current max player
        new_board = play_move(board, color, i, j)

        new_action, new_utility = minimax_min_node(new_board, color, limit - 1, caching) # _ means the returned action is ignored

       
        if new_utility > max_utility:
            max_utility = new_utility
            max_action = (i, j)

    if caching != 0:
        cached_states[(board, color)] = (max_action, max_utility)
    
    return max_action, max_utility # return the action and utility of the max node based on the min node's move



def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    #IMPLEMENT (and replace the line below)

    # # clear the cached_states 
    cached_states.clear()
    
    # covert board to tuple
    if not isinstance(board, tuple):
        board = tuple(tuple(row) for row in board)

    next_move, _ = minimax_max_node(board, color, limit, caching)

    return next_move

############ ALPHA-BETA PRUNING #####################

def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)

    # Note here, the color is the max player color
    # its competitor is the min node, which tries to minimize the utility
    # this function return the action and utility by the min player

    # if the current board state has been visited before, return the value from the cache
    if caching != 0 and (board, 3 - color, alpha, beta) in cached_states:

        return cached_states[(board, 3 - color, alpha, beta)]
    
    if limit == 0:
        return None, compute_utility(board, color)

    # get the possible moves for the min node
    possible_moves = get_possible_moves(board, 3 - color) # returns a list of (column, row) tuples.

    # if the possible moves are empty, or the limit is reduced to 0, return (NULL, utility)
    if possible_moves == []:
        return None, compute_utility(board, color)
    
    # initialize the minimum utility and the minimum action
    min_utility = float('inf')
    min_action = None

    if ordering != 0:
        # child yielding the lowest value is explored first
        # sort the possible_moves based on the increasing order of the utility

        competitor = 3 - color

        possible_moves = sorted(possible_moves, key = lambda x: compute_utility(play_move(board, competitor, x[0], x[1]), color), reverse = False)


    # iterate through the possible moves, and get the minimum utility and the minimum action
    for i, j in possible_moves:
        new_board = play_move(board, 3 - color, i, j)

        new_action, new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)

        if new_utility < min_utility:
            min_utility = new_utility
            min_action = (i, j)

        beta = min(beta, new_utility)

        if alpha >= beta:
            break
    
    if caching != 0:
        cached_states[(board, 3 - color, alpha, beta)] = (min_action, min_utility)

    return min_action, min_utility


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)

    # if the current board state has been visited before, return the value from the cache
    if caching != 0 and (board, color, alpha, beta) in cached_states:

        return cached_states[(board, color, alpha, beta)]
    
    if limit == 0:
        return None, compute_utility(board, color)
    
    # get the possible moves for the player color
    possible_moves = get_possible_moves(board, color) # returns a list of (column, row) tuples.

    # if the possible moves are empty, or the limit is reduced to 0, return (NULL, utility)
    if possible_moves == []:
        return None, compute_utility(board, color)
    
    if ordering != 0:
        # child yielding the highest value is explored first
        # sort the possible_moves based on the decreasing order of the utility

        possible_moves = sorted(possible_moves, key = lambda x: compute_utility(play_move(board, color, x[0], x[1]), color), reverse = True)

    # initialize the maximum utility and the maximum action
    max_utility = float('-inf')
    max_action = None

 
    # iterate through the possible moves, and get the maximum utility and the maximum action
    for i, j in possible_moves:

        # get the new board after playing the move for the current max player
        new_board = play_move(board, color, i, j)

        new_action, new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering) # _ means the returned action is ignored

        if new_utility > max_utility:
            max_utility = new_utility
            max_action = (i, j)

        alpha = max(alpha, max_utility)  #################
  

        if alpha >= beta:
            break

    if caching != 0:
        cached_states[(board, color, alpha, beta)] = (max_action, max_utility)

    return max_action, max_utility


def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    #IMPLEMENT (and replace the line below)

    # # clear the cached_states
    cached_states.clear()

    # covert board to tuple
    if not isinstance(board, tuple):
        board = tuple(tuple(row) for row in board)

    next_move, _ = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)

    return next_move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
