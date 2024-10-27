import pygame as pg
import globals as glob
import letter as let
import hashlib
from math import ceil, sqrt


class Board():

    #Inicializa a classe Board
    def __init__(self, board, size, pieces, piece_size = 3):
        self.board = board
        self.size = size
        self.piece_size = piece_size
        self.piece_bits = 0b111
        self.space_size = 2 + piece_size*5
        self.pieces = pieces
        
    #É usado para dar hash da variável board para o tornar único
    def __hash__(self):
        hash_object = hashlib.sha256()
        hash_object.update(str(self.board).encode())
        return int(hash_object.hexdigest(), 16)
    
    #verifica se o estado do jogo é simétrico horizontalmente
    def verify_symmetry(self):
        info_bits = self.board & 0b11111111111111111
        self.board &= ~(0b11111111111111111)
        
        sym_bits = (pow(2, self.space_size*self.size)-1)
        
        sym_size = self.size//2
        self.isSym = True
        
        while(sym_size > 0):
            
            top_row = (self.board >> ((sym_size-1)*self.space_size*self.size)) & sym_bits
            bot_row = (self.board >> ((self.size-sym_size)*self.space_size*self.size)) & sym_bits
            if(top_row ^ bot_row != 0):
                self.isSym = False
                break
            sym_size -= 1
        self.board |= info_bits

    #Atualiza as coordenadas do tabuleiro e o seu tamanho
    def update_board_coords(self, x, y, size):
        self.board_x = x
        self.board_y = y
        self.board_size = size

    #Cria o tabuleiro inicial distribuindo as peças dos jogadores nas devidas posições
    def make_board(self, size, players):
        count = 1
        for i in range(0, len(players)):
            self.pieces[players[i].color] = {'height': 0, 'pos': {}, 'reserves': 0}
        player = players.popleft()

        self.size = size
        for row in range(0, size):
            for col in range(0, size):
                if(row == 0 or col == 0 or row == size-1 or col == size-1):
                    if(self.in_bounds(row, col)):
                        self.set_empty(row, col)
                        self.set_space(row, col, glob.CODED_WHITE)
                        
                else:
                    self.set_empty(row, col)
                    self.set_space(row, col, glob.CODED_WHITE)
                    self.set_pieces(row, col, player.color, 1)
                    self.add_piece_entry(player.color, 1, row, col)
                    
                    if(count % 2 == 0):
                        count = 0
                        players.append(player)
                        player = players.popleft()
                    count += 1

    #Desenha o tabuleiro na tela
    def draw(self, screen):
        for row in range(self.size):
            for col in range(self.size):
                if(self.in_bounds(row, col)):
                    space_color = self.get_color_space(self.get_space(row, col))
                
                    space_dimensions = self.board_size//self.size
                    pg.draw.rect(screen, space_color, (self.board_x+col*space_dimensions, self.board_y+row*space_dimensions, space_dimensions, space_dimensions))
                    pg.draw.rect(screen, glob.BLACK, (self.board_x+col*space_dimensions, self.board_y+row*space_dimensions, space_dimensions, space_dimensions), 2)
                    pieces = self.get_pieces(row, col)
                    
                    count = 0
                    while(pieces > 0 and (pieces & self.piece_bits) != glob.CODED_EMPTY and (pieces & self.piece_bits) != glob.CODED_INVIS):
                        piece_color = self.get_color_piece(pieces & self.piece_bits)
                        self.draw_piece(screen, piece_color, self.board_x+col*space_dimensions+space_dimensions/2, self.board_y+row*space_dimensions+space_dimensions/2-count*space_dimensions/10, space_dimensions/2-5)
                        
                        pieces = pieces >> self.piece_size
                        count += 1

    #Desenha as peças no tabuleiro
    def draw_piece(self, screen, color, x, y, radius):
        pg.draw.circle(screen, color, (x, y), radius)
        pg.draw.circle(screen, glob.BLACK, (x, y), radius, 2)
        pg.draw.circle(screen, glob.BLACK, (x, y-((self.board_size//self.size)/2-5)//5), (self.board_size//self.size)/2-5-((self.board_size//self.size)/2-5)//20, 2, False, False, True, True)

    #Desenha na tela o retângulo com as informações sobre as peças reservas dos jogadores
    def draw_reserves(self, screen, player_color, isFirst = False):
        (x, y, width, height, offset) = self.get_player_box(player_color)
        piece_color = self.get_color_piece(player_color)
            
        if(isFirst):
            pg.draw.rect(screen, glob.LIGHT_YELLOW, (x, y, width, height))
        else:
            pg.draw.rect(screen, glob.WHITE, (x, y, width, height))

        pg.draw.rect(screen, glob.BLACK, (x, y, width, height), 2)
        pg.draw.circle(screen, piece_color, (x+width//2-offset, y+height//2), height//2-10)
        pg.draw.circle(screen, glob.BLACK, (x+width//2-offset, y+height//2), height//2-10, 2)
        pg.draw.circle(screen, glob.BLACK, (x+width//2-offset, y+height//2-(height//2-10)//5), height//2-10-((height//2-10)//20), 2, False, False, True, True)
        let.draw(screen, "x"+str(self.pieces[player_color]['reserves']), (x+width//2+offset, y+height//4), (self.pieces[player_color]['reserves']//10 * 20, int(height//2)), piece_color)

    #Desenha as hints em formato de seta no tabuleiro
    def draw_hint(self, screen, move, value, best_value, color, player_color):
        if(move == glob.PASS_MOVE):
            return

        space_dimensions = self.board_size//self.size

        arrow_dimensions = (space_dimensions//6)*value/best_value

        color = (color[0], color[1], color[2], 200)

        if(arrow_dimensions == 0):
            return 0

        fin_pos = move[1]

        if(move[0] == glob.RESERVE_MOVE):
            (x, y, width, height, offset) = self.get_player_box(player_color)
            (x, y) = (x+width//2-offset, y+height)
            (edge_x, edge_y) = (self.board_x+fin_pos[1]*space_dimensions, self.board_y+fin_pos[0]*space_dimensions)
            if (player_color == glob.CODED_BLUE):
                (arrow_edge_x, arrow_edge_y) = (edge_x+arrow_dimensions*3/2,edge_y+arrow_dimensions*3/2)
                (vertice1_x, vertice1_y) = (edge_x+arrow_dimensions, edge_y)
                (vertice2_x, vertice2_y) = (edge_x, edge_y+arrow_dimensions)
                (arrow_vertice1_x, arrow_vertice1_y) = (edge_x+arrow_dimensions*3/2, edge_y-arrow_dimensions//2)
                (arrow_vertice2_x, arrow_vertice2_y) = (edge_x-arrow_dimensions//2, edge_y+arrow_dimensions*3/2)
            if(player_color == glob.CODED_ORANGE):
                y = y-height
                (edge_x, edge_y) = (edge_x+space_dimensions, edge_y+space_dimensions)
                (arrow_edge_x, arrow_edge_y) = (edge_x-arrow_dimensions*3/2,edge_y-arrow_dimensions*3/2)
                (vertice1_x, vertice1_y) = (edge_x-arrow_dimensions, edge_y)
                (vertice2_x, vertice2_y) = (edge_x, edge_y-arrow_dimensions)
                (arrow_vertice1_x, arrow_vertice1_y) = (edge_x-arrow_dimensions*3/2, edge_y+arrow_dimensions//2)
                (arrow_vertice2_x, arrow_vertice2_y) = (edge_x+arrow_dimensions//2, edge_y-arrow_dimensions*3/2)
            if (player_color == glob.CODED_GREEN):
                edge_x = edge_x+space_dimensions
                (arrow_edge_x, arrow_edge_y) = (edge_x-arrow_dimensions*3/2,edge_y+arrow_dimensions*3/2)
                (vertice1_x, vertice1_y) = (edge_x-arrow_dimensions, edge_y)
                (vertice2_x, vertice2_y) = (edge_x, edge_y+arrow_dimensions)
                (arrow_vertice1_x, arrow_vertice1_y) = (edge_x-arrow_dimensions*3/2, edge_y-arrow_dimensions//2)
                (arrow_vertice2_x, arrow_vertice2_y) = (edge_x+arrow_dimensions//2, edge_y+arrow_dimensions*3/2)
            if (player_color == glob.CODED_PURPLE):
                y = y-height
                edge_y =edge_y+space_dimensions
                (arrow_edge_x, arrow_edge_y) = (edge_x+arrow_dimensions*3/2,edge_y-arrow_dimensions*3/2)
                (vertice1_x, vertice1_y) = (edge_x+arrow_dimensions, edge_y)
                (vertice2_x, vertice2_y) = (edge_x, edge_y-arrow_dimensions)
                (arrow_vertice1_x, arrow_vertice1_y) = (edge_x+arrow_dimensions*3/2, edge_y+arrow_dimensions//2)
                (arrow_vertice2_x, arrow_vertice2_y) = (edge_x-arrow_dimensions//2, edge_y-arrow_dimensions*3/2)

            surface = pg.Surface(pg.display.get_surface().get_size(), pg.SRCALPHA)
            pg.draw.polygon(surface, color, [(x, y), (vertice1_x, vertice1_y), (vertice2_x, vertice2_y)])
            pg.draw.polygon(surface, color, [(arrow_edge_x, arrow_edge_y), (arrow_vertice1_x, arrow_vertice1_y), (arrow_vertice2_x, arrow_vertice2_y)])
            screen.blit(surface, (0, 0))
            return

        init_pos = move[0]
        space_distance = abs(init_pos[0] - fin_pos[0]) + abs(init_pos[1] - fin_pos[1])

        distance = space_distance*space_dimensions-space_dimensions//4

        if(abs(init_pos[1]-fin_pos[1]) > 0):
            if(init_pos[1]-fin_pos[1] > 0):     #Seta para a esquerda
                top_left = (self.board_x+init_pos[1]*space_dimensions+(space_dimensions//2)-distance, self.board_y+init_pos[0]*space_dimensions+(space_dimensions//2)-arrow_dimensions//2)
                surface = pg.Surface((distance, arrow_dimensions*3), pg.SRCALPHA)
                pg.draw.rect(surface, color, (arrow_dimensions, arrow_dimensions, distance, arrow_dimensions))
                pg.draw.polygon(surface, color, [(arrow_dimensions,0), (arrow_dimensions,arrow_dimensions*3), (0,arrow_dimensions*3/2)])
                screen.blit(surface, (top_left[0], top_left[1]-arrow_dimensions))

            else:                               #Seta para a direita
                top_left = (self.board_x+init_pos[1]*space_dimensions+(space_dimensions//2), self.board_y+init_pos[0]*space_dimensions+(space_dimensions//2)-arrow_dimensions//2)
                surface = pg.Surface((distance, arrow_dimensions*3), pg.SRCALPHA)
                pg.draw.rect(surface, color, (0, arrow_dimensions, distance-arrow_dimensions, arrow_dimensions))
                pg.draw.polygon(surface, color, [(distance-arrow_dimensions,0), (distance-arrow_dimensions,arrow_dimensions*3), (distance,arrow_dimensions*3/2)])
                screen.blit(surface, (top_left[0], top_left[1]-arrow_dimensions))
        else:
            if(init_pos[0]-fin_pos[0]>0):       #Seta para cima
                top_left = (self.board_x+init_pos[1]*space_dimensions+(space_dimensions//2)-arrow_dimensions//2, self.board_y+init_pos[0]*space_dimensions+(space_dimensions//2)-distance)
                surface = pg.Surface((arrow_dimensions*3, distance*2), pg.SRCALPHA)
                pg.draw.rect(surface, color, (arrow_dimensions, arrow_dimensions, arrow_dimensions, distance-arrow_dimensions))
                pg.draw.polygon(surface, color, [(0,arrow_dimensions), (arrow_dimensions*3,arrow_dimensions), (arrow_dimensions*3/2,0)])
                screen.blit(surface, (top_left[0]-arrow_dimensions, top_left[1]))
            else:                               #Seta para baixo
                top_left = (self.board_x+init_pos[1]*space_dimensions+(space_dimensions//2)-arrow_dimensions//2, self.board_y+init_pos[0]*space_dimensions+(space_dimensions//2))
                surface = pg.Surface((arrow_dimensions*3, distance*2), pg.SRCALPHA)
                pg.draw.rect(surface, color, (arrow_dimensions, 0, arrow_dimensions, distance-arrow_dimensions))
                pg.draw.polygon(surface, color, [(0,distance-arrow_dimensions), (arrow_dimensions*3,distance-arrow_dimensions), (arrow_dimensions*3/2,distance)])
                screen.blit(surface, (top_left[0]-arrow_dimensions, top_left[1]))
        return

    #Obtém as dimensões e coordenadas do retângulo com as informações das peças reservas para cada jogador
    def get_player_box(self, color):
        space_dimensions = self.board_size//self.size
        (x, y, width, height) = (self.board_x//2, self.board_y//2, space_dimensions*2, space_dimensions)
        offset = width//5
        match(color):
            case glob.CODED_ORANGE:
                (x, y) = (self.board_x+self.board_size+self.board_x//2-width, self.board_y+self.board_size+self.board_y//2-height)
                offset = -offset
            case glob.CODED_GREEN:
                (x, y) = (self.board_x+self.board_size+self.board_x//2-width, self.board_y//2)
            case glob.CODED_PURPLE:
                offset = -offset
                (x, y) =  (self.board_x//2, self.board_y+self.board_size+self.board_y//2-height)
        return (x, y, width, height, offset)

    #elimina todas as peças de um espaço do tabuleiro
    def set_empty(self, row, col):
        index = self.get_index(row, col)
        self.board |= (0b110110110110110 << (index+2))

    #coloca uma cor nova para um espaço do tabuleiro
    def set_space(self, row, col, space_color):
        index = self.get_index(row, col)
        self.board |= (space_color << (index))

    #elimina a cor do espaço do tabuleiro ou então elimina a cor de peças que se encontram nesse espaço
    def clear_color(self, row, col, height=None, num_moves=None):
        index = self.get_index(row, col)
        if(num_moves == None):
            self.board &= ~(0b11 << index) 
        elif(height == 5):
            self.board &= ~((((0b111111111111111 >> ((height-1)*3)) & (0b111111111111111 >> (5-num_moves)*3))) << (index+2+(height-1)*3))
        else:
            self.board &= ~((((0b111111111111111 >> ((height)*3)) & (0b111111111111111 >> (5-num_moves)*3))) << (index+2+(height)*3))

    #remove uma entrada no dicionário onde está guardado a informação do jogo atual
    def remove_piece_entry(self, color, height, row, col):
        if(color and color != glob.CODED_EMPTY):
            curr_entry = self.pieces[color]['pos'].get((row << 4) | col)
            if(curr_entry):
                del self.pieces[color]['pos'][(row << 4) | col]
                self.pieces[color]['height'] -= height
    
    #adiciona uma entrad no dicionário onde está guardado a informação do jogo atual
    def add_piece_entry(self, color, height, row, col, reserves=0):
        if(color and color != glob.CODED_EMPTY):
            self.pieces[color]['pos'][(row << 4) | col] = (row, col)
            self.pieces[color]['height'] += height
            self.pieces[color]['reserves'] += reserves

    #elimina uma serta quantidade de peças de um determinado espaço do tabuleiro
    def clear_pieces(self, row, col, num_moves):
        index = self.get_index(row, col)
        (_, height) = self.get_top_piece(row, col)

        
        self.clear_color(row, col, height-num_moves, num_moves)
        self.board |= ((0b110110110110110 >> (5-num_moves)*3)) << (index+2+(height-num_moves)*3)

    #coloca um determinado número de peças num espaço do tabuleiro
    def set_pieces(self, row, col, pieces, num_moves, color = None):
        index = self.get_index(row, col)
        (_, height) = self.get_top_piece(row, col)
        reserve_pieces = 0
        if(height + num_moves > 5):
            curr_pieces = self.get_pieces(row, col, height, 5-num_moves)
            captured_pieces = self.get_pieces(row, col, height-(5-num_moves), height-(5-num_moves))
            self.clear_pieces(row, col, height)
            self.set_pieces(row, col, curr_pieces, 5-num_moves)
            height = 5-num_moves
            while(captured_pieces > 0):
                if(captured_pieces & self.piece_bits == color):
                    reserve_pieces += 1
                captured_pieces = captured_pieces >> self.piece_size

        self.clear_color(row, col, height, num_moves)
        self.board |= pieces << (index+2+(height)*3)
        return reserve_pieces

    #Obtém a cor do espaço no tabuleiro para pintar a partir do código da cor definido
    def get_color_space(self, code):
        match(code):
            case glob.CODED_WHITE:
                return glob.WHITE
            case glob.CODED_GREEN_SPACE:
                return glob.GREEN
            case glob.CODED_YELLOW_SPACE:
                return glob.YELLOW
    
    #Obtém a cor da peça a partir do código da cor definido
    def get_color_piece(self, code):
        match(code):
            case glob.CODED_BLUE:
                return glob.BLUE
            case glob.CODED_ORANGE:
                return glob.ORANGE
            case glob.CODED_GREEN:
                return glob.GREEN
            case glob.CODED_PURPLE:
                return glob.PURPLE

    #retorna a cor do espaço correspondente às coordenadas passadas como argumento
    def get_space(self, row, col):
        index = self.get_index(row, col)
        return (self.board >> index) & 0b11
                    
    #retorna as cores de um número qualquer de peças passado por argumento que se encontram num determinado espaço do tabuleiro
    def get_pieces(self, row, col, height = 5, num_pieces=5):
        if(height == 0):
            return 0
        index = self.get_index(row, col)
        return (self.board >> (index+2+(height-num_pieces)*self.piece_size)) & (0b111111111111111 >> ((5-num_pieces)*3))

    #retorna a cor e altura da peça num determinado espaço do tabuleiro
    def get_top_piece(self, row, col):
        curr_piece = None
        top_piece = None
        height = 1
        while(curr_piece != glob.CODED_EMPTY):
            
            top_piece = curr_piece
            if(height == 6):
                return (top_piece, height-1)
            curr_piece = self.get_piece(row, col, height)
            height += 1
        

        return (top_piece, height-2)

    #retorn a cor de uma peça num determinado espaço do tabuleiro, quer que seja a peça do topo ou uma do meio
    def get_piece(self, row, col, height):
        num_bits = 0b111
        
        if(height == 0):
            offset = 0
            num_bits = 0b11
        else:
            offset = 2+(height-1)*3
            
        index = self.get_index(row, col)
        return (self.board >> (index+offset)) & num_bits

    #traduz coordenas reais do tabuleiro para coordenadas do bitmap
    def get_index(self, row, col):
        return row*self.size*self.space_size + col*self.space_size
    
    #coloca espaços verde com base numa array de espaços dado como argumento
    def draw_playable(self, valid_moves):  
        for (row, col) in valid_moves:
            self.clear_color(row, col, 0)
            self.set_space(row, col, glob.CODED_GREEN_SPACE)

    #coloca espaços branco com base numa array de espaços dado como argumento
    def remove_playable(self, valid_moves):
        for (row, col) in valid_moves:
            self.clear_color(row, col, 0)
            self.set_space(row, col, glob.CODED_WHITE)

    #verifica se as coordenadas reais corresponde a coordenadas válidas do tabuleiro
    def in_bounds(self, row, col):
        if(row < 0 or col < 0 or row > self.size-1 or col > self.size-1):
            return None
        if(((col == 0 or col == self.size-1) and (row <= 1 or row >= self.size-2)) or ((row == 0 or row == self.size-1) and (col <= 1 or col >= self.size-2))):
            return None
        
        return (row, col)
