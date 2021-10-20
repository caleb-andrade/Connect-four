from util import memoize, run_search_function
from connectfour import *
import time

def basic_evaluate(board):
    """
    The original focused-evaluate function from the lab.
    The original is kept because the lab expects the code in the lab to be modified. 
    """
    if board.is_game_over():
        # If the game has been won, we know that it must have been
        # won or ended by the previous move.
        # The previous move was made by our opponent.
        # Therefore, we can't have won, so return -1000.
        # (note that this causes a tie to be treated like a loss)
        score = -1000
    else:
        score = board.longest_chain(board.get_current_player_id()) * 10
        # Prefer having your pieces in the center of the board.
        for row in range(6):
            for col in range(7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    score -= abs(3-col)
                elif board.get_cell(row, col) == board.get_other_player_id():
                    score += abs(3-col)

    return score


def get_all_next_moves(board):
    """ Return a generator of all moves that the current player could take from this position """
    from connectfour import InvalidMoveException

    for i in xrange(board.board_width):
        try:
            yield (i, board.do_move(i))
        except InvalidMoveException:
            pass

def is_terminal(depth, board):
    """
    Generic terminal state check, true when maximum depth is reached or
    the game has ended.
    """
    return depth <= 0 or board.is_game_over()

# Global variables to store minimax players stats
total_nodesN = 0
total_timeN = 0
total_nodesB = 0
total_timeB = 0

def minimax(board, depth, eval_fn = basic_evaluate,
            get_next_moves_fn = get_all_next_moves,
            is_terminal_fn = is_terminal,
            verbose = True):
    """
    Do a minimax search to the specified depth on the specified board.

    board -- the ConnectFourBoard instance to evaluate
    depth -- the depth of the search tree (measured in maximum distance from a leaf to the root)
    eval_fn -- (optional) the evaluation function to use to give a value to a leaf of the tree; see "focused_evaluate" in the lab for an example

    Returns an integer, the column number of the column that the search determines you should add a token to
    """
    global nodes_expanded, total_nodesN, total_timeN, total_nodesB, total_timeB

    # counter variable to keep track of nodes expanded in the search
    nodes_expanded = 0
      
    def minimaxDLS(board, depth):
        """
        Implements Depth Limited Search to return best column move given a board.
        Arguments: 'board' and 'depth' 
        Returns:   'best_score', 'modified_column'
        """
        global nodes_expanded, total_nodesN, total_timeN, total_nodesB, total_timeB
        # check if board is final: depth reached or game is over    
        if is_terminal_fn(depth, board):
            return eval_fn(board), None
        # initializing best score 
        best_score = -float('inf')
        # expanding node to explore its children
        nodes_expanded += 1
        for next_board in get_next_moves_fn(board):
            score_column_board = minimaxDLS(next_board[1], depth - 1)
            next_board_score = -score_column_board[0]
            if next_board_score > best_score:
                best_score =  next_board_score
                modified_column = next_board[0]

        return best_score, modified_column
        
    # running time
    tic = time.clock()
    solution = minimaxDLS(board, depth)
    toc = time.clock()
    
    if eval_fn == basic_evaluate:
        total_nodesB += nodes_expanded
        total_timeB += toc - tic
        print "Minimax basic_player "
        print "Expanded nodes: ", total_nodesB
        print "Running time: ", total_timeB, "\n\n"
    else:
        total_nodesN += nodes_expanded
        total_timeN += toc - tic
        print "Minimax new_player "
        print "Expanded nodes: ", total_nodesN
        print "Running time: ", total_timeN, "\n\n"
    
    return solution[1]


def rand_select(board):
    """
    Pick a column by random
    """
    import random
    moves = [move for move, new_board in get_all_next_moves(board)]
    return moves[random.randint(0, len(moves) - 1)]


def new_evaluate(board):
    """
    A modified version of basic_evaluate.
    """
    if board.is_game_over():
        # If the game has been won, we know that it must have been
        # won or ended by the previous move.
        # The previous move was made by our opponent.
        # Therefore, we can't have won, so return -1000.
        # (note that this causes a tie to be treated like a loss)
        score = -1000000
    else:
        chain_length = board.longest_chain(board.get_current_player_id())
        # We give an exponential increasing weigth to longer chains
        score = 10**chain_length 
        # Prefer having your pieces in the center of the board.
        for row in range(6):
            for col in range(7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    score -= abs(3-col)
                elif board.get_cell(row, col) == board.get_other_player_id():
                    score += abs(3-col)
                # we favor the first game's move to be in the middle
                if col == 3 and row == 5:
                    if board.get_cell(row, col) == board.get_current_player_id():
                        score += 10
                        
    # it's preferably to win with less tokens on the board, so we divide by the
    # the number of tokens on the board. This is also a criteria to break ties.
    return float(score) / board.num_tokens_on_board()


random_player = lambda board: rand_select(board)
basic_player = lambda board: minimax(board, depth=4, eval_fn=basic_evaluate)
new_player = lambda board: minimax(board, depth=4, eval_fn=new_evaluate)
progressive_deepening_player = lambda board: run_search_function(board, search_fn=minimax, eval_fn=basic_evaluate)
