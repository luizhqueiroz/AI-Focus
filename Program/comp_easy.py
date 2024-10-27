from monte_carlo import MonteCarlo
import pygame as pg
import globals as glob


class CompEasy():
    #Inicializa a classe Computer Easy
    def __init__(self, color):
        self.color = color
        self.ai = MonteCarlo(color, self.filter_move)
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
    
    #retorna uma jogada depois de correr montecarlo e do utilizador ter pressionado no espaço
    def pick_move(self, screen, state, players, move_history, board_size): 
        if(self.press_space()):

            return self.ai.search(state, self, players, 100)
        return None
    
    #filtra a jogada se a acha inútil 
    def filter_move(self, state, row, col, color):
        new_moves = []
        (top_piece, height) = state.board.get_top_piece(row, col)                                               #gets the color and height of the piece on top of the pile

        if(state.board.pieces[color]['reserves'] > 0 and top_piece != color and height > 0):
            new_moves = [(glob.RESERVE_MOVE, (row, col))]                                              #filters non enemy pile reserve moves
                  
        if(top_piece == color):           
            while(height > 0):
                new_moves.extend([((row, col),move)               #gets valid moves of the piece in play
                                   for move in state.get_valid_moves(row, col, color, height)])
                                    
                height -= 1

        return new_moves
