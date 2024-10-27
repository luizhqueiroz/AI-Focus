import pygame as pg
import globals as glob
from comp_medium import CompMedium

class Human():
    #Inicializa a classe Human
    def __init__(self, color, num_players, board_size):
        self.color = color
        self.leftClicked = True
        self.changeSize = False
        self.valid_moves = []
        self.row = 0
        self.col = 0
        self.moves = 1

    #atualiza as cores das peças que podem ser jogadas após clicar nelas
    def update_playable(self, state, moves): 
        (top_piece, height) = state.board.get_top_piece(self.row, self.col)
        if(moves == glob.RESERVE_MOVE[0]-1):
            valid_moves = self.get_all_spaces(state)
        else:
            valid_moves = state.get_valid_moves(self.row, self.col, self.color, moves)
            
        if(moves <= height and valid_moves != [] or not top_piece):
            self.moves = moves
            state.board.remove_playable(self.valid_moves)
            self.valid_moves = valid_moves
        elif((valid_moves == [] and moves <= height) or height == 0):
            state.board.remove_playable(self.valid_moves)
            if(top_piece == self.color):
                state.board.clear_color(self.row, self.col, 0)
                state.board.set_space(self.row, self.col, glob.CODED_YELLOW_SPACE)
            return

        if(top_piece == self.color):
                state.board.clear_color(self.row, self.col, 0)
                state.board.set_space(self.row, self.col, glob.CODED_YELLOW_SPACE)

        state.board.draw_playable(self.valid_moves)
    
    #gere os inputs que o jogador pode fazer no tabuleiro
    def handle_input(self, state, mouse, key):
        mouse_button = mouse.get_pressed()
        key_button = key.get_pressed()
        if(mouse_button[glob.LEFT_MOUSE_CLICK] and not self.leftClicked):
            self.leftClicked = True
            return self.left_click_action(state, mouse.get_pos())
        elif(key_button[pg.K_1] and not self.changeSize):
            self.changeSize = True
            self.update_playable(state, 1)
        elif(key_button[pg.K_2] and not self.changeSize):
            self.changeSize = True
            self.update_playable(state, 2)
        elif(key_button[pg.K_3] and not self.changeSize):
            self.changeSize = True
            self.update_playable(state, 3)
        elif(key_button[pg.K_4] and not self.changeSize):
            self.changeSize = True
            self.update_playable(state, 4)
        elif(key_button[pg.K_5] and not self.changeSize):
            self.changeSize = True
            self.update_playable(state, 5)

        return None

    #ações que o utilizador pode fazer quando clica com a tecla esquerda do rato na parte do tabuleiro
    def left_click_action(self, state, mouse_pos): 
        if((self.row, self.col) != (0, 0)):
            state.board.clear_color(self.row, self.col) 
            state.board.set_space(self.row, self.col, glob.CODED_WHITE)
        (x, y, width, height ,_) = state.board.get_player_box(self.color)
        player_box = pg.Rect(x, y, width, height)
        if(player_box.collidepoint(mouse_pos)):
            if(self.moves == glob.RESERVE_MOVE[0]-1):
                self.moves = 1
                state.board.remove_playable(self.valid_moves)
            elif(state.board.pieces[self.color]['reserves']>0):
                (self.row, self.col) = glob.RESERVE_MOVE
                self.update_playable(state, glob.RESERVE_MOVE[0]-1)
            else:
                (self.row, self.col) = (0, 0)
                state.board.remove_playable(self.valid_moves)
                
        elif(self.in_bounds(state, mouse_pos[0], mouse_pos[1])):
            (row, col) = self.get_board_pos(state, mouse_pos[0], mouse_pos[1])               

            if(state.board.in_bounds(row, col)):

                if(state.board.get_space(row, col) == glob.CODED_GREEN_SPACE):
                    state.board.remove_playable(self.valid_moves)
                    self.moves = 1
                    return ((self.row, self.col),(row, col))  
                
                if((row, col) == (self.row, self.col)):
                    (self.row, self.col) = (0, 0)
                    state.board.remove_playable(self.valid_moves)
                else:
                    self.row = row
                    self.col = col       
                    (_, height) = state.board.get_top_piece(row, col)
                    self.moves = height
                    
                    self.update_playable(state, self.moves)

            else:
                state.board.remove_playable(self.valid_moves)
                (self.row, self.col, self.moves) = (0, 0, 0)

        else:
            state.board.remove_playable(self.valid_moves)
            (self.row, self.col, self.moves) = (0, 0, 0)

        return None

    #verifica se o utilizador deixou de carregar uma tecla do comoutador
    def discard_input(self, mouse, key):
        mouse_button = mouse.get_pressed()
        key_button = key.get_pressed()
        if (not mouse_button[glob.LEFT_MOUSE_CLICK]):
            self.leftClicked = False
        if (not key_button[pg.K_1] and  not key_button[pg.K_2] and not key_button[pg.K_3]
              and not key_button[pg.K_4] and not key_button[pg.K_5]):

            self.changeSize = False
        
    #retorna uma jogada feita pelo jogador
    def pick_move(self, screen, state, players, move_history, board_size):
        mouse = pg.mouse
        key = pg.key
        action = self.handle_input(state, mouse, key)
        self.discard_input(mouse, key)

        return action
    
    #verifica se o clique do rato está entre as coordenadas do retângulo do tabuleiro
    def in_bounds(self, state, x, y):
        return (x >= state.board.board_x and x <= state.board.board_x+state.board.board_size
                and y >= state.board.board_y
                and y <= state.board.board_y+state.board.board_size)
    
    #retorna as coordenadas do retângulo do tabuleiro
    def get_board_pos(self, state, x, y):
        return (int((y-state.board.board_y) // (state.board.board_size//state.board.size)),
                int((x-state.board.board_x) // (state.board.board_size//state.board.size)))
    
    #retorna todos os espaços do tabuleiro
    def get_all_spaces(self, state):
        res = []
        for row in range(0, state.board.size):
            for col in range(0, state.board.size):
                if(state.board.in_bounds(row, col)):
                    res.append((row, col))
                    
        return res
