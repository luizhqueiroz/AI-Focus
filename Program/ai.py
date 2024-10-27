import globals as glob
from copy import deepcopy
from state import State




#gera um array de jogadas possíveis a partir de um estado de jogo e da vez de um jogador dado como argumento. Filtra algumas jogadas com base numa função dada como argumento.
#Ordena as jogadas de forma decrescente com base em valores atribuídos a eles pela funcao de filter_move
def gen_moves(state, player_color, filter_move):
        new_moves = []
        for pos in state.board.pieces[player_color]['pos'].values():
            if(state.board.isSym and pos[0] >= (state.board.size//2)):
                continue

            new_moves.extend(filter_move(state, pos[0], pos[1], player_color))

        if(state.board.pieces[player_color]['reserves'] > 0):
            for color in state.board.pieces.keys():
                if(color != player_color):
                    for pos in state.board.pieces[color]['pos'].values():
                        if(state.board.isSym and pos[0] >= (state.board.size//2)):
                            continue

                        (_, height) = state.board.get_top_piece(pos[0], pos[1])
                        new_moves.append((height*5, (glob.RESERVE_MOVE, pos)))

        return sorted(new_moves, key=lambda x: x[0], reverse=True)

#Fax o mesmo que o gen_moves, mas só que não ordena as jogadas com base em valores, pois alguns algoritmos não necessitam disso.
def gen_moves_unsorted(state, player_color, filter_move):
        new_moves = []
        for pos in state.board.pieces[player_color]['pos'].values():
            if(state.board.isSym and pos[0] >= (state.board.size//2)):
                continue

            new_moves.extend(filter_move(state, pos[0], pos[1], player_color)) 

        if(state.board.pieces[player_color]['reserves'] > 0):
            for color in state.board.pieces.keys():
                if(color != player_color):
                    for pos in state.board.pieces[color]['pos'].values():
                        if(state.board.isSym and pos[0] >= (state.board.size//2)):
                            continue
                        new_moves.append((glob.RESERVE_MOVE, pos)) 

        return new_moves
                
#Leva um estado de jogo, uma jogada e a cor das peças do jogador atual. Efetua a jogada nesse estado de jogo e verifica se esse novo estado de jogo é simétrico. No final devolve o estado de jogo novo.
def make_move(state, move, color):
        new_state = State(state.board.board, state.board.size, deepcopy(state.board.pieces))
        
        new_state.move_piece(move, color)

        new_state.board.verify_symmetry()


        return new_state
