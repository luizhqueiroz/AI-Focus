from learning_mini_max import LearningMiniMax
import globals as glob
import pygame as pg


class CompHard():
    #Inicializa a classe Computer Hard
    def __init__(self, color, num_players, board_size):
        self.color = color
        self.ai = LearningMiniMax("focus.db", color, num_players, board_size, self.utility, self.filter_move)
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

    #retorna uma jogada depois de correr o learning MiniMax e do utilizador ter pressionado no espaço
    def pick_move(self, screen, state, players, move_history, board_size):
        if(self.press_space()):
            self.ai.set_time()
            return self.ai.search(state, self, players, move_history, None)[1]
        return None

    #retorna um valor para o estado de joga passado por argumento
    def utility(self, state):
        value = 0                                                
        isStable = True
        top_capture = 0

        for color, entry in state.board.pieces.items():

            if(color != self.color):
                value -= entry['reserves']
                value -= entry['height']

                (capture_value, _, board_stability) = self.can_capture(state, entry['pos'].values(), False, isStable)

                if(isStable):
                    isStable = board_stability

                top_capture = max(top_capture, capture_value)

        if(isStable):
            value = 0
            for color, entry in state.board.pieces.items():
                if(self.color == color):
                    value += entry['reserves']*5
                    value += entry['height']
                else:
                    value -= entry['reserves']*5
                    value -= entry['height']

            return (value+1) * 100   
        
        else:
            value += state.board.pieces[self.color]['reserves']
            value += state.board.pieces[self.color]['height']
            value += top_capture*2

            if(top_capture == 0):
                (capture_value, pieces, _) = self.can_capture(state, state.board.pieces[self.color]['pos'].values(), True, isStable)
                value -= capture_value*pieces
                                                         
        return value
                                                                
    #verifica se para cada peça dada como argumento numa array se ela tem mais peças suas a ameaça-la do que peças inimigas a defendê-la e verifica se o estado de jogo é estável ou não
    def can_capture(self, state, enemy_positions, isPlayer, isStable):
        best_height = 0
        attacked_piece_count = 0
        for enemy_pos in enemy_positions:
            if((not isPlayer and attacked_piece_count > 1) or (best_height == 5 and not isStable)):
                return (best_height, attacked_piece_count, isStable)
            row = enemy_pos[0]
            col = enemy_pos[1]
            (_, enemy_height) = state.board.get_top_piece(row, col)
            if((not isPlayer and attacked_piece_count > 1) or (enemy_height <= best_height and not isStable)):
                continue

            (defending, isStable) = self.defend_count(state, enemy_pos[0], enemy_pos[1], isPlayer)
            if(defending > 0 and isPlayer):
                attacked_piece_count += 1
            if(defending > 0 and enemy_height > best_height):
                best_height = enemy_height

        return (best_height, attacked_piece_count, isStable)
                
    #verifica para uma dada peça se ela tem mais peças suas a ameaça-la do que peças inimigas a defendê-la e verifica se o estado de jogo é estável ou não
    def defend_count(self, state, row, col, isPlayer):
        defending = 0
        isStable = True
        for color, entry in state.board.pieces.items():
            if(not isPlayer):
                if(color == self.color):
                    defending += entry['reserves']
                else:
                    defending -= entry['reserves']
                    isStable = False
            else:
                if(color != self.color):
                    defending += entry['reserves']
                else:
                    defending -= entry['reserves']
        
        for i in range(state.board.size):                          #for each column in the enemy row
            if(i != col and state.board.in_bounds(row, i)):
                (top_piece, height) = state.board.get_top_piece(row, i)
                distance = abs(col - i)
                while(distance <= height):
                    height -= distance
                    pieces = state.board.get_pieces(row, i, height, 1)
                    if(pieces == 0 or (pieces == top_piece)):
                        if(not isPlayer):
                            if(top_piece == self.color):
                                defending += 1
                            else:
                                defending -= 1
                                isStable = False
                        else:
                            if(top_piece != self.color):
                                defending += 1
                            else:
                                defending -= 1
                    else:
                        break
        
        for i in range(state.board.size):
            if(i != row and state.board.in_bounds(i, col)):
                (top_piece, height) = state.board.get_top_piece(i, col)
                distance = abs(row - i)
                while(distance <= height):
                    height -= distance
                    pieces = state.board.get_pieces(i, col, height, 1)
                    if(pieces == 0 or (pieces == top_piece)):
                        if(not isPlayer):
                            if(top_piece == self.color):
                                defending += 1
                            else:
                                defending -= 1
                                isStable = False
                        else:
                            if(top_piece != self.color):
                                defending += 1
                            else:
                                defending -= 1
                    else:
                        break

        return (defending, isStable)

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

    
    

        





    

            
    