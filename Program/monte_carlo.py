import globals as glob
from copy import deepcopy
from state import State
import random
import math
import ai
from trans_table import TransTable
import time

class TreeNode():
    #Inicializa a classe Tree Node
    def __init__(self, state, move = None, parent=None, n = 0, t = 0):
        self.state = state
        self.move = move
        self.parent = parent
        self.n = n
        self.t = t
        self.children = []

    #
    def add_child(self, child):
        self.children.append(child)

    #
    def get_children(self, depth):
        if(depth == 0):
            return self.children
        children = []
        for child_node in self.children:
            children.extend(child_node.get_children(depth-1))
        return children

    #
    def make_root(self):
        self.parent = None
        self.n = 0
        self.t = 0
        for child_node in self.children:
            child_node.parent = self


class MonteCarlo():
    #Inicializa a classe Monte Carlo
    def __init__(self, color, filter_move):
        self.table = TransTable()
        self.root = None
        self.filter_move = filter_move
        self.color = color

    #retorna a melhor jogada do algoritmo MonteCarlo.
    def search(self, state, player, players, depth):
        self.max_depth = depth
        
        self.root = TreeNode(state)
        players.appendleft(player)

        while(depth > 0):
            self.select(self.root, players.copy())
            depth -= 1
        res = sorted(self.root.children, key=lambda x: x.t, reverse=True)

        return res[0].move

    #seleciona o node que ele deseja atualizar
    def select(self, node, players):
        player = players.popleft()
   
        if(node.children == []):
            for move in ai.gen_moves_unsorted(node.state, player.color, self.filter_move):
                new_state = ai.make_move(node.state, move, player.color)

                node.add_child(TreeNode(new_state, move, node))

        if(node.children == []):
            if(player.color == self.color):
                self.back_propogate(node, -1)
            else:
                self.back_propogate(node, 1)
            return

        new_players = players.copy()
        new_players.append(player)
        
        best_child = sorted(node.children, key=lambda x: self.ucbi(x), reverse=True)[0]
        
        if(best_child.n == 0):

            value = self.rollout(best_child.state, new_players)

            self.back_propogate(best_child, value)
            return

        self.select(best_child, new_players)

    #atualiza os valores dos pais do node
    def back_propogate(self, node, value):
        if(node):
            node.t += value
            node.n += 1
            self.back_propogate(node.parent, value)

    #simula jogadas até chegar ao fim do jogo e devolve o valor deste
    def rollout(self, state, players):
        new_state = State(state.board.board, state.board.size, deepcopy(state.board.pieces))

        if(new_state.has_lost(players[0].color, new_state.board.pieces[players[0].color]['reserves'])):
            if(players[-1].color == self.color):
                return -1
            return 1
        
        while(True):
            player = players.popleft()
            
            move = self.get_random_move(new_state, player)

            new_state.move_piece(move, player.color)    

            if(new_state.has_won(players.copy())):
                if(player.color == self.color):
                    return 1
                return -1
            
            players.append(player)

    #retorna uma jogada à sorte de um determinado estado de jogo passado como argumento
    def get_random_move(self, state, player):
        start_random = 1
        if(state.board.pieces[player.color]['reserves'] > 0):
            start_random = 0

        rand = random.randint(start_random, len(state.board.pieces[player.color]['pos']))
        if(rand == 0):
            player_index = random.randint(0, len(state.board.pieces)-2)
            for color in state.board.pieces.keys():
                if(color != player.color):
                    if(player_index == 0 and len(state.board.pieces[color]['pos']) != 0):
                        
                        return (glob.RESERVE_MOVE, random.choice(list(state.board.pieces[color]['pos'].values())))
                    player_index -= 1
            rand = random.randint(1, len(state.board.pieces[player.color]['pos']))
        else:
            init_pos =list(state.board.pieces[player.color]['pos'].values())[rand-1]

        (_, height) = state.board.get_top_piece(init_pos[0], init_pos[1])

        valid_moves = self.filter_move(state, init_pos[0], init_pos[1], player.color)

        return random.choice(valid_moves)

    #
    def ucbi(self, node):
        if(node.n == 0):
            return glob.MAX_VALUE

        return node.t + 2* math.sqrt(math.log(node.parent.n)/node.n)
