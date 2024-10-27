import sqlite3
import globals as glob



class DBTable():
    #Inicializa a classe DataBase Table
    def __init__(self, db_name, color, num_players, board_size):
        self.color = color
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        match(color):
            case glob.CODED_BLUE:
                self.table_name = "blue_"
            case glob.CODED_ORANGE:
                self.table_name = "orange_"
            case glob.CODED_GREEN:
                self.table_name = "green_"
            case glob.CODED_YELLOW:
                self.table_name = "yellow_"

        self.table_name += str(num_players) + "_" + str(board_size)

        self.cursor.execute("CREATE TABLE IF NOT EXISTS states_"+self.table_name+"""(board TEXT, init_row INTEGER, init_col INTEGER,
                                     fin_row INTEGER, fin_col INTEGER, value INTEGER, next_board TEXT, depth INTEGER, PRIMARY KEY (board, next_board))
                            """)
        
        self.cursor.execute("CREATE INDEX  IF NOT EXISTS board_index ON states_"+self.table_name+" (board);")


        
    #insere uma jogada na base de dados
    def insert_move(self, state, move, value, next_state):
        self.cursor.execute("INSERT INTO states_"+self.table_name+" VALUES(?, ?, ?, ?, ?, ?, ?, 0)", (str(state.board.board), move[0][0], move[0][1], move[1][0], move[1][1], value, str(next_state.board.board)))

        self.connection.commit()

    #retorna o valor da melhor jogada atual de um determinado estado de jogo
    def get_value(self, board, color):

        if(color == self.color):
            self.cursor.execute("SELECT value FROM states_"+self.table_name+" WHERE board = ? ORDER BY value DESC LIMIT 1", (str(board),))
        else:
            self.cursor.execute("SELECT value FROM states_"+self.table_name+" WHERE board = ? ORDER BY value ASC LIMIT 1", (str(board),))

        res = self.cursor.fetchone()

        return res
    
    #devolve o número de jogadas que um estado de jogo tem
    def get_count(self, board):
        self.cursor.execute("SELECT COUNT(*) FROM states_"+self.table_name+" WHERE board = ?", (str(board),))
        count = self.cursor.fetchone()
        return count[0]
    
    #retorna a melhor jogada e o seu valor do estado de jogo atual
    def get_move_and_value(self, board, color, num_move = 0):

        if(color == self.color):
            self.cursor.execute("SELECT init_row, init_col, fin_row, fin_col, value FROM states_"+self.table_name+" WHERE board = ? ORDER BY value DESC LIMIT 1 OFFSET ?", (str(board), num_move))
        else:
            self.cursor.execute("SELECT init_row, init_col, fin_row, fin_col, value FROM states_"+self.table_name+" WHERE board = ? ORDER BY value ASC LIMIT 1 OFFSET ?", (str(board), num_move))

        res = self.cursor.fetchone()
        
        return res
    
    #retorna a melhor jogada e o seu valor e o estado de jogo a que ela produz para um determinado estado de jogo
    def get_move_and_value_and_next_board(self, board, color, num_move = 0):

        if(color == self.color):
            self.cursor.execute("SELECT init_row, init_col, fin_row, fin_col, value, next_board, depth FROM states_"+self.table_name+" WHERE board = ? ORDER BY value DESC LIMIT 1 OFFSET ?", (str(board), num_move))
        else:
            self.cursor.execute("SELECT init_row, init_col, fin_row, fin_col, value, next_board, depth FROM states_"+self.table_name+" WHERE board = ? ORDER BY value ASC LIMIT 1 OFFSET ?", (str(board), num_move))

        res = self.cursor.fetchone()

        return res
    
    #retorna os estados de jogo e os valores das jogadas que originam o estado de jogo passado como argumento
    def get_next_board_moves(self, board):

        self.cursor.execute("SELECT board, value FROM states_"+self.table_name+" WHERE next_board = ?", (str(board),))

        return self.cursor.fetchall()

    #atualiza os valores das jogadas que originam os estados de jogo que foram introduzidos ou alterados na base de dados. Se a jogada com melhor valor desse estado de jogo mudar então atualiza os que a originam.
    def back_propagate(self, board, players, value):
        player = players.pop()

        for (prev_board, prev_value) in self.get_next_board_moves(board):

            if(prev_value != value):
                curr_best_value = self.get_value(prev_board, player.color)[0]

                self.cursor.execute("UPDATE states_"+self.table_name+" SET value = ? WHERE board = ? AND next_board = ?", (value, str(prev_board), str(board)))

                self.connection.commit()
                
                if((player.color == self.color and curr_best_value < value) or (player.color != self.color and curr_best_value > value)):
                    new_players = players.copy()
                    new_players.appendleft(player)
                    
                    self.back_propagate(prev_board, new_players, value)

    #a partir de um estado de jogo, simula as melhores jogadas de cada estado de jogo e depois corre o bot hard num estado de jogo que ainda não existe na base de dados. 
    #Ou entãp em vez de escolher jogadas de melhor valor, escolher jogadas com melhor valor menos quantas vezes é que elas foram escolhidas
    def train_bot(self, state, players, search, move_history):

        res = True
        move_value = 0


        visited = {}

        while(res and abs(move_value) != glob.BEST_MOVE):

            player = players.popleft()

            entry = visited.get(state.board.board)
            if(not entry):
                visited[state.board.board] = {"visit_num": 0}
                entry = 0 

            visited[state.board.board]["visit_num"] = entry + 1
            res = self.get_move_and_value_and_next_board(state.board.board, player.color, entry)

            if(res):
                move_value = res[4]
                visited[state.board.board]["next_board"] = res[5]

            if(res and abs(move_value) != glob.BEST_MOVE):
                state.move_piece(((res[0], res[1]), (res[2], res[3])), player.color)
                players.append(player)

                state.add_info_to_board(players.copy())
                
        if(not res):
            if(self.get_count(state.board.board) == 0):
                state.board.verify_symmetry()
                search(state, player, players.copy(), move_history, False)
                
    #reotorna um número de melhores jogadas passado como argumento de um determinado estado de jogo. Ou então devolve a segunda melhor jogada para eventualidade de a melhor não ser sempre a melhor.
    def get_best_moves(self, state, players, num_moves, offset=0):
        state.add_info_to_board(players)

        self.cursor.execute("SELECT init_row, init_col, fin_row, fin_col, value FROM states_"+self.table_name+" WHERE board = ? ORDER BY value DESC LIMIT ? OFFSET ?", (str(state.board.board), num_moves, offset))
    
        return self.cursor.fetchall()
