import globals as glob
from state import State
import ai
from DB_table import DBTable
from copy import deepcopy
import time


class LearningMiniMax():
    #Inicializa a classe Learning MiniMax
    def __init__(self, db_name, color, num_players, board_size, utility, filter_move):
        self.table = DBTable(db_name, color, num_players, board_size)
        self.color = color
        self.utility = utility
        self.filter_move = filter_move

    #coloca a veriável start time com o valor do tempo atual
    def set_time(self):
        self.start_time = time.time()

    #retorna a melhor jogada do algoritmo Learning Mini Max. Também retorna todas as jogadas possíveis em caso do utilizador quiser pistas sobre qual jogada jogar
    def search(self, state, player, players, move_history, show_possible_moves = False):
        players.appendleft(player)

        self.isTrained = False
        
        self.possible_moves = []

        self.max_depth = len(players)
        value = self.max_value(state, players.copy(), self.max_depth)

        if(value == glob.MAX_VALUE):
            return (-glob.BEST_MOVE, glob.PASS_MOVE)
 
        state.add_info_to_board(players.copy())

        move = self.table.get_move_and_value(state.board.board, self.color)


        if(show_possible_moves):
            moves = self.table.get_best_moves(state, players.copy(), 10)
            if(moves):
                for move in moves:
                    self.possible_moves.append((((move[0], move[1]), (move[2], move[3])), move[4]))

        self.table.back_propagate(state.board.board, players.copy(), value)
                
        return (move[4], ((move[0], move[1]),(move[2], move[3])))
    
    #retorna a jogada com melhor valor de um determinado estado de jogo
    def max_value(self, state, players, depth):
        state.add_info_to_board(players.copy())
        db_value = self.table.get_value(state.board.board, players[0].color)
        if(db_value):
                
            return db_value[0]
        
        if(depth == 0):
            return self.utility(state)           

        player = players.popleft()
     
        maxValue = glob.MIN_VALUE

        self.isTrained = True

        for move in ai.gen_moves_unsorted(state, player.color, self.filter_move):
                
                new_state = ai.make_move(state, move, player.color)

                new_players = players.copy()
                new_players.append(player)

                new_state.add_info_to_board(new_players.copy())
                
                if(new_state.has_won(players.copy())):         
                    self.table.insert_move(state, move, glob.BEST_MOVE, new_state)
                    maxValue = glob.BEST_MOVE
                    continue

                value = self.min_value(new_state, new_players.copy(), depth-1)

                self.table.insert_move(state, move, value, new_state)

                maxValue = max(maxValue, value)
        
        return maxValue
    
    #retorna a jogada com maior valor para o inimigo do bot
    def min_value(self, state, players, depth):
        state.add_info_to_board(players.copy())
        db_value = self.table.get_value(state.board.board, players[0].color)
        if(db_value):
            return db_value[0]
        if(depth == 0):
           return self.utility(state)
 
        player = players.popleft()

        minValue = glob.MAX_VALUE

        for move in ai.gen_moves_unsorted(state, player.color, self.filter_move):

                new_state = ai.make_move(state, move, player.color)

                new_players = players.copy()
                new_players.append(player)

                new_state.add_info_to_board(new_players.copy())

                if(new_state.has_lost(self.color, new_state.board.pieces[self.color]['reserves'])):
                    self.table.insert_move(state, move, -glob.BEST_MOVE, new_state)
                    minValue = -glob.BEST_MOVE
                    continue
                
                value = self.max_value(new_state, new_players.copy(), depth-1)

                self.table.insert_move(state, move, value, new_state)

                minValue = min(minValue, value)
                
        return minValue
