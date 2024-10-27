import pygame as pg
import globals as glob
import os
from menu import Menu
from game_over import GameOver
from human import Human
from comp_easy import CompEasy
from comp_medium import CompMedium
from comp_hard import CompHard
from comp_hint import CompHint
from side_panel import SidePanel
from collections import deque
from state import State


class Game():
    #initializa a classe Game
    def __init__(self, screen_width, screen_height, fps):

        self.info_display = pg.display.Info()
        self.screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.fps = fps
        self.game_state = glob.GameState.MENU
        self.menu = Menu()
        self.gameover = GameOver()
        pg.display.set_caption("Focus")
        self.mouse_click_sound = pg.mixer.Sound(os.path.join('sounds', 'mouseclick.mp3'))
        self.keyboard_click_sound = pg.mixer.Sound(os.path.join('sounds', 'keyboardclick.mp3'))
        self.background = pg.image.load(os.path.join('images', 'background.jpg')).convert()
        self.background2 = pg.image.load(os.path.join('images', 'background2.jpg')).convert()
        
    #Inicia o loop principal do jogo
    def run_game(self):

        while(True):
            self.clock.tick(self.fps)

            if (self.game_state == glob.GameState.GAME or self.game_state == glob.GameState.BOARD_SETUP or self.game_state == glob.GameState.GAME_OVER): 
                background = pg.transform.scale(self.background, (glob.SCREEN_WIDTH, glob.SCREEN_HEIGHT))
                self.screen.blit(background, (0, 0))
            else:
                background2 = pg.transform.scale(self.background2, (glob.SCREEN_WIDTH, glob.SCREEN_HEIGHT))
                self.screen.blit(background2, (0, 0))
 
            if(self.state_handler() == glob.GameState.EXIT):
                return

            for event in pg.event.get():
                match(event.type):
                    case pg.QUIT:
                        return
                    case pg.VIDEORESIZE:
                     self.set_screen_variables()
                    case pg.KEYDOWN:
                        self.keyboard_click_sound.play()
                        match(event.key):
                            case pg.K_ESCAPE:
                                if(self.game_state == glob.GameState.GAME):
                                    self.game_state = glob.GameState.MENU
                                elif(self.menu.menu_state == glob.MenuState.BOARD_SETUP or self.menu.menu_state == glob.MenuState.PLAYER_SETUP):
                                    self.menu.change_state(glob.MenuState.GAME_SETUP)
                                elif(self.menu.menu_state == glob.MenuState.GAME_SETUP):
                                    self.menu.change_state(glob.MenuState.MAIN_MENU)
                                elif(self.game_state == glob.GameState.MENU and self.menu.menu_state == glob.MenuState.MAIN_MENU):
                                    return
                                elif(self.game_state == glob.GameState.GAME_OVER):
                                    self.game_state = glob.GameState.MENU
                    case pg.MOUSEBUTTONDOWN:
                        if(event.button == 1):
                            self.mouse_click_sound.play()
                               
            pg.display.flip()

    #Gerencia os diferentes estados do jogo e suas transições
    def state_handler(self):
        match(self.game_state):
            case glob.GameState.MENU:
                
                menu_handler = self.menu.state_handler(self.screen)
                if(menu_handler is not None):
                    self.game_state = menu_handler
                    
            case glob.GameState.BOARD_SETUP:
                
                self.game_state = glob.GameState.GAME
                
                match(self.menu.num_players):
                    case 2:
                        self.players = deque([self.get_player_type(self.menu.players[0], glob.CODED_BLUE), self.get_player_type(self.menu.players[1], glob.CODED_ORANGE)])
                    case 3:
                        self.players = deque([self.get_player_type(self.menu.players[0], glob.CODED_BLUE), self.get_player_type(self.menu.players[1], glob.CODED_GREEN), self.get_player_type(self.menu.players[2], glob.CODED_ORANGE)])
                    case 4:
                        self.players = deque([self.get_player_type(self.menu.players[0], glob.CODED_BLUE), self.get_player_type(self.menu.players[1], glob.CODED_GREEN), self.get_player_type(self.menu.players[2], glob.CODED_ORANGE), self.get_player_type(self.menu.players[3], glob.CODED_PURPLE)])
                
                self.state = State(0, self.menu.board_size, {})

                self.turnEnd = False

                self.move_history = deque([])
                self.hints = []

                self.state.board.make_board(self.menu.board_size, self.players.copy())
                self.state.board.verify_symmetry()
                self.panel = SidePanel(glob.SIDE_PANEL_SIZE)
                    
                self.curr_player = self.players.popleft()
                self.manage_board_coords()       
                self.state.board.draw(self.screen)
                self.draw_reserves(self.curr_player, self.players.copy())

            case glob.GameState.GAME:
                            
                self.game_state = self.play_turn(self.curr_player, self.state.board.pieces[self.curr_player.color]['reserves'] == 0 and
                                                                 self.state.board.pieces[self.curr_player.color]['height'] == 0)
                self.state.board.draw(self.screen)
                self.draw_reserves(self.curr_player, self.players.copy())
                self.manage_panel()
                
            case glob.GameState.GAME_OVER:
                self.state.board.draw(self.screen)
                self.draw_reserves(self.curr_player, self.players.copy())
                self.gameover.winner_color = self.state.board.get_color_piece(self.curr_player.color)
                self.gameover.result = self.result
                gameover_handler = self.gameover.state_handler(self.screen)
                if(gameover_handler):
                    self.game_state = gameover_handler
            case other:
                print("error in game state handler")
        return self.game_state

    #Executa uma rodada do jogo
    def play_turn(self, player, isPassMove):
        if(isPassMove):
            move = glob.PASS_MOVE
        else:
            move = player.pick_move(self.screen, self.state, self.players.copy(), self.move_history, self.menu.board_size)
        if(move):
            
            self.move_history.appendleft(move)
            if(move != glob.PASS_MOVE):
                self.state.move_piece(move, player.color) 
                self.state.board.verify_symmetry()  
                if(self.state.has_won(self.players.copy())):
                    self.result = "win"
                    return glob.GameState.GAME_OVER
                elif (self.state.is_draw(self.move_history, len(self.players)+1)):
                    self.result = "draw"
                    return glob.GameState.GAME_OVER
            self.players.append(self.curr_player) 
            self.curr_player = self.players.popleft() 
            self.hints = []
            if(self.panel.panel_state == glob.SidePanelState.HINT and self.panel.buttons[0].isHeld):
                self.hint_bot = CompHint(self.curr_player.color)
                finish_time = self.panel.finish_time
                if(finish_time == 0.0):
                    finish_time = None
                self.hints = self.hint_bot.get_hints(self.state, self.players.copy(), finish_time, self.move_history, self.panel.hint_num, self.menu.board_size)

        return self.game_state

    #Desenha o retangulo com a quantidade de peça reserva do jogador
    def draw_reserves(self, curr_player, players):
        while(players):
            player = players.popleft()
            self.state.board.draw_reserves(self.screen, player.color)
            
        self.state.board.draw_reserves(self.screen, curr_player.color, True)
        
    #Gerencia os diferentes estados do painel lateral do jogo
    def manage_panel(self):
        panel_state = self.panel.state_handler(self.screen)
        match(panel_state):
            case glob.SidePanelState.GAME:
                self.set_screen_variables()
            case glob.SidePanelState.GAME_INFO:
                self.set_screen_variables()
                self.hints = []
            case glob.SidePanelState.HINT:
                if(self.panel.buttons[0].isHeld):
                    self.hint_bot = CompHint(self.curr_player.color)
                    finish_time = self.panel.finish_time
                    if(finish_time == 0.0):
                        finish_time = None
                    self.hints = self.hint_bot.get_hints(self.state, self.players.copy(), finish_time, self.move_history, self.panel.hint_num, self.menu.board_size)
                else:
                    self.hints = []

            case glob.SidePanelState.QUIT:
                self.game_state = glob.GameState.MENU
        if(self.hints != []):
            self.hint_bot.show_hints(self.screen, self.state, self.curr_player.color, self.hints)
        
    #Devolve uma instância do jogador referente ao tipo de jogador fornecido
    def get_player_type(self, type, color):
        match(type):
            case glob.PLAYER:
                return Human(color, self.menu.num_players, self.menu.board_size)
            case glob.COMP_EASY:
                return CompEasy(color)
            case glob.COMP_MEDIUM:
                return CompMedium(color)
            case glob.COMP_HARD:
                return CompHard(color, self.menu.num_players, self.menu.board_size)
            case other:
                print("entered other")

    #Gerencia as coordenadas do tabuleiro para se ajustar dentro do formato desejado
    def manage_board_coords(self):
        if(self.panel.panel_state is not glob.SidePanelState.GAME):
            if(glob.SCREEN_WIDTH-self.panel.size > glob.SCREEN_HEIGHT):
                (board_x, board_y, board_size) = ((glob.SCREEN_WIDTH-self.panel.size)/2, glob.SCREEN_HEIGHT/10, glob.SCREEN_HEIGHT-2*glob.SCREEN_HEIGHT/10)
                board_x -= board_size/2
            else:
                (board_x, board_y, board_size) = ((glob.SCREEN_WIDTH-self.panel.size)/10, glob.SCREEN_HEIGHT/2, (glob.SCREEN_WIDTH-self.panel.size)-2*(glob.SCREEN_WIDTH-self.panel.size)/10)
                board_y -= board_size/2
        else:
            if(glob.SCREEN_WIDTH > glob.SCREEN_HEIGHT):
                (board_x, board_y, board_size) = (glob.SCREEN_WIDTH/2, glob.SCREEN_HEIGHT/10, glob.SCREEN_HEIGHT-2*glob.SCREEN_HEIGHT/10)
                board_x -= board_size/2
            else:
                (board_x, board_y, board_size) = (glob.SCREEN_WIDTH/10, glob.SCREEN_HEIGHT/2, glob.SCREEN_WIDTH-2*glob.SCREEN_WIDTH/10)
                board_y -= board_size/2

        self.state.board.update_board_coords(board_x, board_y, board_size)

    #Gerencia os redimensionamentos feitos na janela da aplicação
    def set_screen_variables(self):
        glob.SCREEN_WIDTH = self.screen.get_width()
        glob.SCREEN_HEIGHT = self.screen.get_height()
        max_width = self.info_display.current_w
        max_height = self.info_display.current_h

        if(glob.SCREEN_WIDTH < 750): 
            glob.SCREEN_WIDTH = 750
                            
        if(glob.SCREEN_HEIGHT < 500):
            glob.SCREEN_HEIGHT = 500

        if(glob.SCREEN_WIDTH > max_width):
            glob.SCREEN_WIDTH = max_width

        if(glob.SCREEN_HEIGHT > max_height):
            glob.SCREEN_HEIGHT = max_height

        if (self.game_state == glob.GameState.GAME or self.game_state == glob.GameState.GAME_OVER):
            self.manage_board_coords()
        
        if (self.game_state == glob.GameState.MENU):
            self.menu.change_state(self.menu.menu_state)
        
        pg.display.set_mode((glob.SCREEN_WIDTH, glob.SCREEN_HEIGHT), pg.RESIZABLE)
