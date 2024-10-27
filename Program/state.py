from board import Board
import globals as glob


class State():
    #Inicializa a classe State
    def __init__(self, board, size, pieces):
        self.board = Board(board, size, pieces)

    #Obtém os movimentos válidos para um jogador de uma determinada posição no tabuleiro
    def get_valid_moves(self, row, col, player, moves):
        (top_piece, _) = self.board.get_top_piece(row, col)
        if(not top_piece or top_piece != player):
            return []
    
        return list(filter(lambda x: x, [self.board.in_bounds(row-moves, col), self.board.in_bounds(row+moves, col),
                 self.board.in_bounds(row, col-moves), self.board.in_bounds(row, col+moves)]))

    #Realiza o movimento de uma peça do tabuleiro
    def move_piece(self, move, color):
        init_pos = move[0]
        final_pos = move[1]

        if(init_pos == glob.RESERVE_MOVE):
            (top_piece, height) = self.board.get_top_piece(final_pos[0], final_pos[1])
            self.board.remove_piece_entry(top_piece, height, final_pos[0], final_pos[1])
            if(height == 5):
                if(top_piece == color):
                    self.board.add_piece_entry(color, height, final_pos[0], final_pos[1], 0)
                else:
                    self.board.add_piece_entry(color, height, final_pos[0], final_pos[1], -1)
            else:
                self.board.add_piece_entry(color, height+1, final_pos[0], final_pos[1], -1)
            return self.board.set_pieces(final_pos[0], final_pos[1], color, 1, color) - 1

        num_moves = abs(final_pos[0] - init_pos[0]) + abs(final_pos[1]-init_pos[1])

        (top_piece, height) = self.board.get_top_piece(init_pos[0], init_pos[1])

        self.board.remove_piece_entry(top_piece, height, init_pos[0], init_pos[1])

        pieces = self.board.get_pieces(init_pos[0], init_pos[1], height, num_moves)

        self.board.clear_pieces(init_pos[0], init_pos[1], num_moves)

        (top_piece, height) = self.board.get_top_piece(init_pos[0], init_pos[1])

        self.board.add_piece_entry(top_piece, height, init_pos[0], init_pos[1])

        (top_piece, height) = self.board.get_top_piece(final_pos[0], final_pos[1])

        self.board.remove_piece_entry(top_piece, height, final_pos[0], final_pos[1])

        reserves = self.board.set_pieces(final_pos[0], final_pos[1], pieces, num_moves, color)

        if(height +num_moves > 5):
            self.board.add_piece_entry(color, 5, final_pos[0], final_pos[1], reserves)
        else:
            self.board.add_piece_entry(color, height+num_moves, final_pos[0], final_pos[1], reserves)
    
    #Verifica se um jogador venceu o jogo, verificando se os outros perderam
    def has_won(self, players):
        while(players):
            player = players.popleft()
            if(not self.has_lost(player.color, self.board.pieces[player.color]['reserves'])):
                return False
        
        return True

    #Verifica se um jogador perdeu o jogo
    def has_lost(self, color, reserves):
        if(reserves == 0 and self.board.pieces[color]['height'] == 0):
            return True
        return False
    
    #Adiciona informação dos jogadores ao tabuleiro
    def add_info_to_board(self, players):
        self.board.board &= ~(0b11111111111111111)
        self.board.board |= players[0].color

        for i in range(0, len(players)):
            self.board.board |= self.board.pieces[players[i].color]['reserves'] << (3+i*4)

    #Verifica se houve um empate por movimentos repetidos pelos jogadores
    def is_draw(self, move_history, num_players):
        if(len(move_history) >= 6*num_players):
            for i in range(0, num_players*6):
                if(i+num_players*2 >= 6*num_players):
                    return True
                if(move_history[i] != move_history[i+num_players*2]):
                    break
        return False
