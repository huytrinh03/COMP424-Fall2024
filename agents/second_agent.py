# Second agent
from agents.agent import Agent
from store import register_agent
import sys
import numpy as np
from copy import deepcopy
import time
from helpers import random_move, count_capture, execute_move, check_endgame, get_valid_moves

def heuristics(board, player):
  def corner(board, player):
    board_size = len(board)
    corners = [(0, 0), (0, board_size - 1), (board_size - 1, 0), (board_size - 1, board_size - 1)]
    this_player_corner = sum(1 for row, col in corners if board[row][col] == player)
    opponent_corner = sum(1 for row, col in corners if board[row][col] == 3-player)

    if this_player_corner + opponent_corner != 0:
      return 100*(this_player_corner - opponent_corner)/(this_player_corner+opponent_corner)
    else:
      return 0

  def mobility(board, player):
    this_player_valid_moves = len(get_valid_moves(board, player))
    opponent_valid_moves = len(get_valid_moves(board, 3-player))
    if this_player_valid_moves + opponent_valid_moves != 0:
      return 100*(this_player_valid_moves - opponent_valid_moves)/(this_player_valid_moves + opponent_valid_moves)
    else:
      return 0

# Edited and generated by chatGPT using the following prompt:
# "Write code to calculate the stability component of heuristics in Reversi. Stable stones are given 1
# point, semi-stable stones are given 0, and unstable stones are given -1. Given that the Reversi board
# is coded using Python's numpy array. In this array, 0 denotes empty square, 1 denotes player 1's stone,
# and 2 denotes player 2's stone"
  def stability_score(board, player):
    """
        Calculate the (approximate) stability component of heuristics for a given player in Reversi.

        Parameters:
        - board (numpy array): The Reversi board (2D numpy array).
        - player (int): The player's ID (1 or 2).

        Returns:
        - int: The stability score for the player.
        """

    def is_stable(x, y):
      """
      Check if a stone is stable (cannot be flipped for the rest of the game).
      """
      if (x, y) in [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]:
        return True  # Corners are always stable
      # Check if stone is along a completely filled edge
      if x == 0 or x == rows - 1:  # Top or bottom edge
        return all(board[x, :] != 0) or all(board[x, 0:y] == player) or all(board[x, y+1:cols] == player)
      if y == 0 or y == cols - 1:  # Left or right edge
        return all(board[:, y] != 0) or all(board[0:x, y] == player) or all(board[x+1:rows, y] == player)

    def is_unstable(x, y):
      """
      Check if a stone is unstable (can currently be flipped).
      """
      directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
      for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if dx == 0:
          mx, my = x, y - dy
        elif dy == 0:
          mx, my = x - dx, y
        else:
          mx, my = x - dx, y - dy
        if 0 <= nx < rows and 0 <= ny < cols and board[nx, ny] == opponent and 0 <= mx < rows and 0 <= my < cols and board[mx, my] == 0:
          return True
      return False

    opponent = 3-player
    rows, cols = board.shape

    stability_score = 0

    for x in range(rows):
      for y in range(cols):
        if board[x, y] == player:
          if is_stable(x, y):
            stability_score += 1  # Stable stone
          elif is_unstable(x, y):
            stability_score -= 1  # Unstable stone
          # Semi-stable stones are neutral (0), so we don't adjust the score
    return stability_score
  def stability(board, player):
    this_player_stability = stability_score(board, player)
    opponent_stability = stability_score(board, 3-player)

    if this_player_stability + opponent_stability != 0:
      return 100*(this_player_stability - opponent_stability)/abs(this_player_stability + opponent_stability)
    else:
      return 0

  def stone_parity(board, player):
    player1_stone = check_endgame(board, player, opponent=3 - player)[1]
    player2_stone = check_endgame(board, player, opponent=3 - player)[2]
    heuristics = 100 * (player1_stone - player2_stone) / (player1_stone + player2_stone)
    return heuristics if player==1 else -heuristics

  return 0.35 * corner(board, player) + 0.25 * mobility(board, player) + 0.25 * stability(board, player) + 0.15 * stone_parity(board, player)

# Generated by chatGPT using the following prompt:
# "Write Python code to implement a search tree with depth-first search in python."
# "The nodes represent the state of the Reversi game."
class ReversiNode:
  """
  A class to represent a node in the Reversi game tree.
  """

  def __init__(self, board, player, move=None):
    self.board = board  # The state of the game board
    self.player = player  # The current player (1 or 2)
    self.move = move  # The move that led to this state
    self.children = []  # List of child nodes

  def __str__(self):
    return f"Player: {self.player}, Move: {self.move}, Board:\n{np.array2string(self.board)}"

  def print_tree(self, depth=0):
    """
    Recursively print the tree for visualization.
    """
    indent = "  " * depth
    print(f"{indent}{self}")
    for child in self.children:
      child.print_tree(depth + 1)
  def dfs(self, max_depth, start_time, depth=1):
    """
    Perform DFS to explore the game tree.
    """
    if time.time() - start_time > 0.4:
      return

    if depth > max_depth:
      return # Stop expanding at maximum depth

    moves = get_valid_moves(self.board, self.player)
    for move in moves:
      next_player = 3 - self.player  # Switch player
      simulated_board = deepcopy(self.board)
      execute_move(simulated_board, move, self.player)
      child_node = ReversiNode(simulated_board, next_player, move)
      self.children.append(child_node)
      child_node.dfs(max_depth, start_time, depth + 1)

  # Generated by chatGPT accoding to the following prompt:
  # "Write a program that does alpha-beta pruning in Python"
  def alpha_beta_pruning(self, alpha, beta, maximizing_player, start_time):
    """
    Perform alpha-beta pruning.

    Args:
    - node (list or int): The current node value (int) or a list of child nodes.
    - depth (int): The current depth in the tree.
    - alpha (float): The alpha value (best score for maximizing player so far).
    - beta (float): The beta value (best score for minimizing player so far).
    - maximizing_player (bool): True if the current layer is maximizing; False otherwise.

    Returns:
    - int: The best score for the current player.
    """

    # If leaf node, evaluate the node
    if len(self.children) == 0 or time.time() - start_time > 1.57:
      return heuristics(self.board, self.player) if maximizing_player else -heuristics(self.board, self.player)

    if maximizing_player:
      for child in self.children:
        eval = child.alpha_beta_pruning(alpha, beta, False, start_time)
        if eval > alpha:
          alpha = eval
        if alpha >= beta:
          return beta
      return alpha

    else:
      for child in self.children:
        eval = child.alpha_beta_pruning(alpha, beta, True, start_time)
        if eval < beta:
          beta = eval
        if alpha >= beta:
          return alpha
      return beta

  # Generated by chatGPT using the following prompt: "Implement alpha-beta pruning with choosing the best move with a tree in python"
  def find_best_move(self, start_time, maximizing_player=True):
    """
    Find the best move for the player using alpha-beta pruning.
    :param root: The root of the game tree (TreeNode).
    :param maximizing_player: True if it's the maximizer's turn, False for minimizer.
    :return: The best child node corresponding to the best move.
    """

    best_value = float('-inf') if maximizing_player else float('inf')
    best_move = None

    for child in self.children:
      if time.time() - start_time > 1.57:
        return best_move
      # Perform alpha-beta pruning for each child
      eval = child.alpha_beta_pruning(float('-inf'), float('inf'), not maximizing_player, start_time)
      if maximizing_player:
        if eval > best_value:
          best_value = eval
          best_move = child.move
      else:
        if eval < best_value:
          best_value = eval
          best_move = child.move
    return best_move

@register_agent("second_agent")
class SecondAgent(Agent):
  """
  A class for your implementation. Feel free to use this class to
  add any helper functionalities needed for your agent.
  """

  def __init__(self):
    super(SecondAgent, self).__init__()
    self.name = "SecondAgent"

  def step(self, chess_board, player, opponent):
    """
    Implement the step function of your agent here.
    You can use the following variables to access the chess board:
    - chess_board: a numpy array of shape (board_size, board_size)
      where 0 represents an empty spot, 1 represents Player 1's discs (Blue),
      and 2 represents Player 2's discs (Brown).
    - player: 1 if this agent is playing as Player 1 (Blue), or 2 if playing as Player 2 (Brown).
    - opponent: 1 if the opponent is Player 1 (Blue), or 2 if the opponent is Player 2 (Brown).

    You should return a tuple (r,c), where (r,c) is the position where your agent
    wants to place the next disc. Use functions in helpers to determine valid moves
    and more helpful tools.

    Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.

    Source:
    https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/miniproject1_vaishu_muthu/Paper/Final_Paper.pdf
    https://barberalec.github.io/pdf/An_Analysis_of_Othello_AI_Strategies.pdf
    https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=ab55658867e68b09597a982681a983640af88afe

    Chosen strategy: alpha-beta pruning + IDS, component-wise heuristics

    Heuristics's weights:
    - corner: 35
    - mobility: 25
    - stability: 25
    - stone parity: 15
    """

    root = ReversiNode(chess_board, player, None)
    root.dfs(3, time.time())
    best_move = root.find_best_move(time.time(), maximizing_player=True)
    if best_move == None:
      best_move = random_move(chess_board, player)
    return best_move
