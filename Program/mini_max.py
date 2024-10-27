import globals as glob
import time
import ai
from trans_table import TransTable



class MiniMax():
    ##Inicializa a classe MiniMax
    def __init__(self, color, utility, filter_move):
        self.table = TransTable()
        self.color = color
        self.utility = utility
        self.filter_move = filter_move

    #retorna a melhor jogada do algoritmo Mini Max. Também retorna todas as jogadas possíveis em caso do utilizador quiser pistas sobre qual jogada jogar.
    #Tem duas versões: Uma que faz iterative deepening e outra que não a faz
    def search(self, state, player, players, depth, finish_time, move_history, show_possible_moves = False):
        self.second_best = (None, None)

        self.possible_moves = []
        self.show_possible_moves = show_possible_moves
        
        self.finish_time = finish_time
        players.appendleft(player)

        self.start_time = time.time()

        best_move = None

        curr_time = 0.0
        self.prev_time = 0.0

        curr_depth = depth

        if(finish_time):
            curr_depth = len(players)
            while(curr_time+self.prev_time*2 < finish_time):
                self.max_depth = curr_depth
                (value, move) = self.max_value(state, glob.MIN_VALUE, glob.MAX_VALUE, players.copy(), curr_depth)
                
                if(move):
                    best_move = move
                    if(value == glob.MAX_VALUE or value == glob.MIN_VALUE):
                        return best_move
                else:
                    break

                curr_depth += len(players)
                curr_time = time.time()-self.start_time
                self.prev_time = time.time()-self.start_time-self.prev_time

            curr_depth -= len(players)
            if(curr_depth >= 9):
                curr_depth = len(players)*2

        self.finish_time = None  

        self.max_depth = curr_depth
        (_, best_move) = self.max_value(state, glob.MIN_VALUE, glob.MAX_VALUE, players.copy(), curr_depth)

        if(show_possible_moves):
            self.possible_moves = sorted(self.possible_moves, key=lambda x: x[1], reverse=True)

        move_history.appendleft(best_move)

        if(state.is_draw(move_history, len(players))):
            if(self.second_best != (None, None) and self.second_best[1] >= 0):

                best_move = self.second_best[0]
                
                if(show_possible_moves):
                    self.possible_moves[0][1] = -1
                    self.possible_moves = sorted(self.possible_moves, key=lambda x: x[1], reverse=True) 
                
        move_history.popleft()

        return best_move
    
    #retorna a jogada com melhor valor de um determinado estado de jogo
    def max_value(self, state, alpha, beta, players, depth):
        table_entry = self.table.get(state, players.copy())
        if(table_entry and ((self.max_depth != depth and self.show_possible_moves) or self.finish_time or (not self.show_possible_moves and self.max_depth != depth))):
            return (table_entry['value'], table_entry['move'])
        
        if(depth == 0):
            return (self.utility(state), None)

        player = players.popleft()
        
        (maxValue, action) = (glob.MIN_VALUE, None)

        for (_, move) in ai.gen_moves(state, player.color, self.filter_move):           
                
                new_state = ai.make_move(state, move, player.color)

                if(new_state.has_won(players.copy())):
                    if(self.show_possible_moves and not self.finish_time and self.max_depth == depth):
                        self.possible_moves.append((move, glob.BEST_MOVE))
                    return (glob.BEST_MOVE, move)
                
                new_players = players.copy()
                new_players.append(player)
                
                (value, _) = self.min_value(new_state, alpha, beta, new_players, depth-1)

                if(self.finish_time and (time.time() - self.start_time) + self.prev_time*2 >= self.finish_time):
                    return (None, None)
                
                if(not self.finish_time and self.max_depth == depth):
                    if(self.second_best == (None, None)):
                        self.second_best = (move, value)
                    elif(value <= maxValue and value > self.second_best[1]):
                        self.second_best = (move, value)

                if(self.show_possible_moves and not self.finish_time and self.max_depth == depth):
                    self.possible_moves.append((move, value))
  
                if(value > maxValue):
                    (maxValue, action) = (value, move)
            
                if(maxValue >= beta):
                    return (maxValue, action)
                
                alpha = max(alpha, maxValue)

        if(action):
            if(abs(maxValue) >= 100 or (self.max_depth == depth and not self.finish_time)):
                self.table.store(state, maxValue, action)
            return (maxValue, action)
        
        return (-glob.BEST_MOVE+1, glob.PASS_MOVE)

    #retorna a jogada com maior valor para o inimigo do bot
    def min_value(self, state, alpha, beta, players, depth):
        table_entry = self.table.get(state, players.copy())
        if(table_entry):
            return (table_entry['value'], table_entry['move'])
        if(depth == 0):
           return (self.utility(state), None)

        player = players.popleft()

        (minValue, action) = (glob.MAX_VALUE, None)
        
        for (_, move) in ai.gen_moves(state, player.color, self.filter_move):

                new_state = ai.make_move(state, move, player.color)
                
                new_players = players.copy()
                new_players.append(player)

                if(new_state.has_lost(self.color, new_state.board.pieces[self.color]['reserves'])):
                    return(-glob.BEST_MOVE, move)

                if(players[0].color == self.color):
                    (value, _) = self.max_value(new_state, alpha, beta, new_players, depth-1)
                else:
                    (value, _) = self.min_value(new_state, alpha, beta, new_players, depth-1)

                if(self.finish_time and (time.time() - self.start_time) + self.prev_time*2 >= self.finish_time):
                    return (None, None)

                if(value < minValue):
                    (minValue, action) = (value, move)     

                if(minValue <= alpha):
                    return (minValue, action)
                
                beta = min(minValue, beta)

        if(action):
             if(abs(minValue) >= 100):
                self.table.store(state, minValue, action)
             return (minValue, action)
        return (0, glob.PASS_MOVE)
