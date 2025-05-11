import math
import random
import copy
import time

PLAYER_X = 'X'  # Human
PLAYER_O = 'O'  # AI
EMPTY = '.'

class SuperTicTacToe:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = random.choice([PLAYER_X, PLAYER_O])  # Random start
        self.last_move = None
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner = None
        self.valid_moves = self.get_valid_moves(self.board, self.last_move)

    def create_board(self):
        return [[EMPTY for _ in range(9)] for _ in range(9)]

    def get_subboard(self, board, index):
        row_offset = (index // 3) * 3
        col_offset = (index % 3) * 3
        return [row[col_offset:col_offset+3] for row in board[row_offset:row_offset+3]]

    def subboard_winner(self, sub):
        # Check rows
        for row in sub:
            if row[0] != EMPTY and row[0] == row[1] == row[2]:
                return row[0]
        
        # Check columns
        for col in range(3):
            if sub[0][col] != EMPTY and sub[0][col] == sub[1][col] == sub[2][col]:
                return sub[0][col]
        
        # Check diagonals
        if sub[0][0] != EMPTY and sub[0][0] == sub[1][1] == sub[2][2]:
            return sub[0][0]
        if sub[0][2] != EMPTY and sub[0][2] == sub[1][1] == sub[2][0]:
            return sub[0][2]
        
        return None

    def get_valid_moves(self, board, last_move):
        if last_move is None:
            return [(i, j) for i in range(9) for j in range(9) if board[i][j] == EMPTY]
        
        sub_index = (last_move[0] % 3) * 3 + (last_move[1] % 3)
        row_start = (sub_index // 3) * 3
        col_start = (sub_index % 3) * 3
        
        moves = [(i, j) for i in range(row_start, row_start+3)
                        for j in range(col_start, col_start+3)
                        if board[i][j] == EMPTY]
        
        if not moves:
            return [(i, j) for i in range(9) for j in range(9) if board[i][j] == EMPTY]
        
        return moves

    def is_full(self, board):
        return all(cell != EMPTY for row in board for cell in row)

    def get_meta_board(self, board):
        meta = [[EMPTY]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                sub = [row[j*3:j*3+3] for row in board[i*3:i*3+3]]
                winner = self.subboard_winner(sub)
                if winner:
                    meta[i][j] = winner
                elif all(cell != EMPTY for row in sub for cell in row):
                    meta[i][j] = 'D'  # Draw
        return meta

    def check_winner(self, meta):
        # Check rows
        for row in meta:
            if row[0] in (PLAYER_X, PLAYER_O) and row[0] == row[1] == row[2]:
                return row[0]
        
        # Check columns
        for col in range(3):
            if meta[0][col] in (PLAYER_X, PLAYER_O) and meta[0][col] == meta[1][col] == meta[2][col]:
                return meta[0][col]
        
        # Check diagonals
        if meta[0][0] in (PLAYER_X, PLAYER_O) and meta[0][0] == meta[1][1] == meta[2][2]:
            return meta[0][0]
        if meta[0][2] in (PLAYER_X, PLAYER_O) and meta[0][2] == meta[1][1] == meta[2][0]:
            return meta[0][2]
        
        return None

    def opponent(self, player):
        return PLAYER_O if player == PLAYER_X else PLAYER_X

    def evaluate(self, board, player):
        meta = self.get_meta_board(board)
        winner = self.check_winner(meta)
        
        if winner == player:
            return 1000
        elif winner == self.opponent(player):
            return -1000

        score = 0
        for i in range(3):
            for j in range(3):
                if meta[i][j] == player:
                    score += 50
                    if i == 1 and j == 1:  # Center sub-board is more valuable
                        score += 20
                elif meta[i][j] == self.opponent(player):
                    score -= 50
                    if i == 1 and j == 1:
                        score -= 20

        # Count pieces on the board
        score += sum(row.count(player) for row in board)
        score -= sum(row.count(self.opponent(player)) for row in board)
        
        return score

    def minimax(self, board, depth, alpha, beta, maximizing, player, last_move):
        meta = self.get_meta_board(board)
        winner = self.check_winner(meta)

        if winner == player:
            return 1000, None
        elif winner == self.opponent(player):
            return -1000, None
        elif depth == 0 or self.is_full(board):
            return self.evaluate(board, player), None

        # Use the correct get_valid_moves method with the board parameter
        moves = self.get_valid_moves(board, last_move)
        random.shuffle(moves)  # Adds randomness

        if maximizing:
            max_eval = -math.inf
            best_move = None
            for move in moves:
                board_copy = [row[:] for row in board]  # Create a copy of the board
                board_copy[move[0]][move[1]] = player
                eval_score, _ = self.minimax(board_copy, depth - 1, alpha, beta, False, player, move)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move

        else:
            min_eval = math.inf
            best_move = None
            for move in moves:
                board_copy = [row[:] for row in board]  # Create a copy of the board
                board_copy[move[0]][move[1]] = self.opponent(player)
                eval_score, _ = self.minimax(board_copy, depth - 1, alpha, beta, True, player, move)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move


    def update_score(self, player, actual_move, optimal_move):
        if actual_move == optimal_move:
            score = 20  # Optimal move
        else:
            score = 10  # Suboptimal move
            
        if player == PLAYER_X:
            self.player_score += score
        else:
            self.ai_score += score

    def make_move(self, row, col):
        if self.game_over:
            return {"error": "Game is already over"}
        
        if self.current_player != PLAYER_X:
            return {"error": "Not your turn"}
        
        move = (row, col)
        if move not in self.valid_moves:
            return {"error": "Invalid move"}

        # Calculate optimal move for scoring
        board_copy = [row[:] for row in self.board]  # Create a copy of the board
        _, optimal_move = self.minimax(board_copy, 3, -math.inf, math.inf, True, self.current_player, self.last_move)
        
        # Update score
        self.update_score(self.current_player, move, optimal_move)
        
        # Make the move
        self.board[row][col] = self.current_player
        self.last_move = move
        
        # Check for game over
        meta = self.get_meta_board(self.board)
        winner = self.check_winner(meta)
        
        if winner:
            self.game_over = True
            self.winner = winner
            return self.get_game_state()
        
        if self.is_full(self.board):
            self.game_over = True
            return self.get_game_state()
        
        # Switch player
        self.current_player = self.opponent(self.current_player)
        self.valid_moves = self.get_valid_moves(self.board, self.last_move)
        
        return self.get_game_state()

    def ai_move(self):
        if self.game_over or self.current_player != PLAYER_O:
            return self.get_game_state()
        
        # AI uses minimax to find the best move
        board_copy = [row[:] for row in self.board]  # Create a copy of the board
        _, move = self.minimax(board_copy, 3, -math.inf, math.inf, True, PLAYER_O, self.last_move)
        
        if move:
            # Update score using the selected move itself as the "optimal" move
            self.update_score(self.current_player, move, move)
            
            # Make the move
            self.board[move[0]][move[1]] = self.current_player
            self.last_move = move
            
            # Check for game over
            meta = self.get_meta_board(self.board)
            winner = self.check_winner(meta)
            
            if winner:
                self.game_over = True
                self.winner = winner
            elif self.is_full(self.board):
                self.game_over = True
            
            # Switch player
            self.current_player = self.opponent(self.current_player)
            self.valid_moves = self.get_valid_moves(self.board, self.last_move)
        
        return self.get_game_state()


    def get_game_state(self):
        meta_board = self.get_meta_board(self.board)
        active_subboard = None
        
        if self.last_move:
            sub_index = (self.last_move[0] % 3) * 3 + (self.last_move[1] % 3)
            row_start = (sub_index // 3) * 3
            col_start = (sub_index % 3) * 3
            
            # Check if the subboard is already won or full
            sub = [row[col_start:col_start+3] for row in self.board[row_start:row_start+3]]
            if self.subboard_winner(sub) or all(cell != EMPTY for row in sub for cell in row):
                active_subboard = -1  # Any subboard
            else:
                active_subboard = sub_index
        
        return {
            "board": self.board,
            "meta_board": meta_board,
            "current_player": self.current_player,
            "player_score": self.player_score,
            "ai_score": self.ai_score,
            "game_over": self.game_over,
            "winner": self.winner,
            "valid_moves": self.valid_moves,
            "active_subboard": active_subboard,
            "last_move": self.last_move  # Add this line to include the last move
        }

    def reset_game(self):
        self.board = self.create_board()
        self.current_player = random.choice([PLAYER_X, PLAYER_O])
        self.last_move = None
        self.game_over = False
        self.winner = None
        self.valid_moves = self.get_valid_moves(self.board, self.last_move)
        # Don't reset scores to keep track across games
        
        return self.get_game_state()
