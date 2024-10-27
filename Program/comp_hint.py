from mini_max import MiniMax
import globals as glob


class CompHint():
    #Inicializa a classe Computer Hint
    def __init__(self, color):
        self.color = color
        self.ai = MiniMax(color, self.utility, self.filter_move)

    #retorna as jogadas todas que o utilizador quer ver como pistas
    def get_hints(self, state, players, finish_time, move_history, num_hints, board_size):
        self.ai.hints = []
        depth = len(players)+1
        if(board_size <= 6 and depth != 3):
            depth = 4
        self.ai.search(state, self, players, depth, finish_time, move_history, True)
        hints = self.ai.possible_moves
        return hints[0:min(num_hints, len(hints))]

    #para cada pista ele chama uma função para a desenhar
    def show_hints(self, screen, state, color, hints):
        best_value = hints[0][1]

        for i in range (1, len(hints)):
            (move, value) = hints[i]
            if(value < best_value and value < 0):
                break
            if(state.board.draw_hint(screen, move, abs(value)+1, abs(best_value)+2, glob.GRAY, color)):
                return
                
        state.board.draw_hint(screen, hints[0][0], abs(best_value)+1, abs(best_value)+1, glob.GOLD, color)

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

    #filtra a jogada se a acha inútil, ou então retorna todas as posições para onde ela pode ir e atribuí valores a ela
    def filter_move(self, state, row, col, color):
        new_moves = []
        (top_piece, height) = state.board.get_top_piece(row, col)                                               #gets the color and height of the piece on top of the pile
                                                                                                             #filters non enemy pile reserve moves            
        if(top_piece == color):     
            original_height = height         
            while(height > 0):
                isPlayerPiece = True
                if(height != original_height):
                    pieces = state.board.get_pieces(row, col, original_height, height+1)
                    if(pieces & 0b111 != top_piece):
                        isPlayerPiece = False
                new_moves.extend([(self.get_value(state, move, color, isPlayerPiece), ((row, col),move))               #gets valid moves of the piece in play
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
                                                                                      #assigns values for the move
        if(final_height == 0):
            value += 1
        elif(final_piece != color):
            value += 2
        else:
            value -= 1

        return value
