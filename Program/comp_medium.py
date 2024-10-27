from mini_max import MiniMax
import globals as glob
import pygame as pg


class CompMedium():
    #Inicializa a classe Computer Medium
    def __init__(self, color):
        self.color = color
        self.ai = MiniMax(color, self.utility, self.filter_move)
        self.clicked = False

    #verifica se o utilizador pressionou no espaço
    def press_space(self):
        key_button = pg.key.get_pressed()

        if(key_button[pg.K_SPACE] and not self.clicked):
            self.clicked = True
            return True
        elif(not key_button[pg.K_SPACE] and self.clicked):
            self.clicked = False
        return False

    #retorna uma jogada depois de correr o Minimax e do utilizador ter pressionado no espaço
    def pick_move(self, screen, state, players, move_history, board_size): 
        
        if(self.press_space()):
            depth = len(players)+1
            if(board_size <= 6 and depth != 3):
                depth = 4
            return self.ai.search(state, self, players, depth, None, move_history)
        
        return None

    #filtra a jogada se a acha inútil, ou então retorna todas as posições para onde ela pode ir e atribuí valores a ela
    def filter_move(self, state, row, col, color):
        new_moves = []
        (top_piece, height) = state.board.get_top_piece(row, col)                                               
                                                                                                                                       
        if(top_piece == color):     
            original_height = height         
            while(height > 0):
                isPlayerPiece = True
                if(height != original_height):
                    pieces = state.board.get_pieces(row, col, original_height, height+1)
                    if(pieces & 0b111 != top_piece):
                        isPlayerPiece = False
                new_moves.extend([(self.get_value(state, move, color, isPlayerPiece), ((row, col),move))               
                                   for move in state.get_valid_moves(row, col, color, height)])       
                height -= 1

        return new_moves
    
    #retorna um valor para uma determinada jogada
    def get_value(self, state, final_pos, color, isPlayerPiece):
        (final_piece, final_height) = state.board.get_top_piece(final_pos[0], final_pos[1])                  
        value = 0
        if(isPlayerPiece):
            value += 1
        else:
            value -= 1
                                                                                      
        if(final_height == 0):
            value += 1
        elif(final_piece != color):
            value += 2
        else:
            value -= 1

        return value
    
    #retorna um valor para o estado de joga passado por argumento
    def utility(self, state):
        value = 0                                                
        isStable = True

        for color, entry in state.board.pieces.items():

            if(color == self.color):
                value += entry['reserves']
                value += entry['height']
            else:
                value -= entry['reserves']
                value -= entry['height']
                isStable = True                                                       
                if(isStable):
                    isStable = self.isStable(state, entry['pos'].values(), color)

        if(isStable):
            return (value+1) * 100                                                     
        
        return value

    #verifica se o estado de jogo é estável ou não
    def isStable(self, state, enemy_positions, enemy_color):
        for enemy_pos in enemy_positions:
            (_, height) = state.board.get_top_piece(enemy_pos[0], enemy_pos[1])
            while(height > 0):
                valid_moves = state.get_valid_moves(enemy_pos[0], enemy_pos[1], enemy_color, height)                        
                for valid_move in valid_moves:                                                                               
                    (top_piece, _) = state.board.get_top_piece(valid_move[0], valid_move[1])                                  
                    if(top_piece == self.color):
                        return False

                height-=1
        return True
 