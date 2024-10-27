import globals as glob

class TransTable():
    #Inicializa a classe Transposition Table
    def __init__(self):
        self.table = {}

    #guarda a melhor jogada e o seu valor na tabela de transposição
    def store(self, state, value, move):
        self.table[state.board.board] = {'value': value, 'move': move}

    #retorna uma entrada existente na tabela de transposição para um dado estado de jogo passado como argumento
    def get(self, state, players):
        state.board.board &= ~(0b11111111111111111)
        state.board.board |= players[0].color

        for i in range(0, len(players)):
            state.board.board |= state.board.pieces[players[i].color]['reserves'] << (3+i*4)

        res = self.table.get(state.board.board)

        if(res):
            return res

        return None
