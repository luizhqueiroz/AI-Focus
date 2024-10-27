import globals as glob
from button import Button
import letter as let


class Menu():
    #Inicializa a classe Menu
    def __init__(self):
            self.board_size = 6
            self.num_players = 2
            self.players_type = {glob.PLAYER: "Human", glob.COMP_EASY: "Computer Easy", glob.COMP_MEDIUM: "Computer Medium", glob.COMP_HARD: "Computer Hard"}
            self.players = [glob.PLAYER, glob.PLAYER, glob.PLAYER, glob.PLAYER]
            self.change_state(glob.MenuState.MAIN_MENU)

    #Gerencia os diferentes estados do menu
    def state_handler(self, screen):
        match(self.menu_state):
            case glob.MenuState.MAIN_MENU:
                self.draw_screen(screen)
                return self.user_action()
            case glob.MenuState.GAME_SETUP:
                self.draw_screen(screen)
                return self.user_action()
            case glob.MenuState.PLAYER_NUMBER_SETUP:
                self.draw_setup_screen(screen)
                return self.user_action()
            case glob.MenuState.PLAYER_SETUP:
                self.draw_setup_screen(screen)
                return self.user_action()
            case glob.MenuState.BOARD_SETUP:
                self.draw_setup_screen(screen)
                return self.user_action()
            case glob.MenuState.EXIT:
                return glob.GameState.EXIT
            case glob.MenuState.PLAY_GAME:
                return glob.GameState.GAME                

    #Altera o estado do menu com base na ação designada pelo botão selecionado
    def change_state(self, action, button=None):
        match(action):
            case glob.MenuState.MAIN_MENU:
                self.buttons = [
                    Button('Start', glob.MenuState.PLAY_GAME, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//10),
                    Button('Settings', glob.MenuState.GAME_SETUP, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//10),
                    Button('Exit', glob.MenuState.EXIT, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//10)
                ]
                self.menu_state = glob.MenuState.MAIN_MENU
            case glob.MenuState.GAME_SETUP:
                self.buttons = [
                    Button('Choose Players', glob.MenuState.PLAYER_NUMBER_SETUP, None,(glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//4),
                    Button('Choose Board Size', glob.MenuState.BOARD_SETUP, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//4),
                    Button('Back', glob.MenuState.EXIT, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//4)
                ]
                self.menu_state = glob.MenuState.GAME_SETUP
            case glob.MenuState.PLAYER_NUMBER_SETUP:
                    self.buttons = [
                    Button('-', glob.MenuState.SWITCH_TYPE, 4, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//35),
                    Button('+', glob.MenuState.SWITCH_TYPE, 5, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//35),
                    Button('Next', glob.MenuState.PLAYER_SETUP, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15)
                ]
                    self.menu_state = glob.MenuState.PLAYER_NUMBER_SETUP
            case glob.MenuState.PLAYER_SETUP:
                self.buttons.clear()
                for i in range(self.num_players):
                    self.buttons.append(Button('->', glob.MenuState.SWITCH_TYPE, i, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//35))

                self.buttons.append(Button('Save', glob.MenuState.EXIT, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15))
                self.menu_state = glob.MenuState.PLAYER_SETUP
            case glob.MenuState.BOARD_SETUP:
                if (self.num_players == 3):
                        self.buttons = [
                        Button('8x8', glob.MenuState.BOARD_SIZE, 8, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 8),
                        Button('Save', glob.MenuState.EXIT, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15)
                    ]

                elif (self.num_players == 4):
                        self.buttons = [
                        Button('6x6', glob.MenuState.BOARD_SIZE, 6, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 6),
                        Button('10x10', glob.MenuState.BOARD_SIZE, 10, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 10),
                        Button('Save', glob.MenuState.EXIT, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15)
                    ]
                else: 
                    self.buttons = [
                        Button('6x6', glob.MenuState.BOARD_SIZE, 6, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 6),
                        Button('8x8', glob.MenuState.BOARD_SIZE, 8, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 8),
                        Button('10x10', glob.MenuState.BOARD_SIZE, 10, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 10),
                        Button('12x12', glob.MenuState.BOARD_SIZE, 12, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15, 30, self.board_size == 12),
                        Button('Save', glob.MenuState.EXIT, None, (glob.SCREEN_WIDTH+glob.SCREEN_HEIGHT)//15)
                    ]

                self.menu_state = glob.MenuState.BOARD_SETUP
            case glob.MenuState.BOARD_SIZE:
                self.board_size = button.value
                for but in self.buttons:
                    if(but.isHeld and but.value is not button.value):
                        but.isHeld = False
            case glob.MenuState.SWITCH_TYPE:                    
                    match(button.value): 
                        case 4:
                            self.num_players = (self.num_players - 1) % 5
                            if (self.num_players == 1):
                                self.num_players = 4
                        case 5:
                            self.num_players = (self.num_players + 1) % 5 
                            if (self.num_players == 0):
                                self.num_players = 2
                        case other:
                            if(self.num_players > 2):
                                self.players[button.value] = (self.players[button.value] + 2) % len(self.players_type)        
                            else:
                                self.players[button.value] = (self.players[button.value] + 1) % len(self.players_type)

                    if (self.num_players == 3):
                        self.board_size = 8
                    elif (self.num_players == 4 and self.board_size != 10):
                        self.board_size = 6
                        
            case glob.MenuState.EXIT:
                match(self.menu_state):
                    case glob.MenuState.MAIN_MENU:
                        return glob.GameState.EXIT
                    case glob.MenuState.GAME_SETUP:
                        self.change_state(glob.MenuState.MAIN_MENU)
                    case glob.MenuState.PLAYER_SETUP:
                        self.change_state(glob.MenuState.GAME_SETUP)
                    case glob.MenuState.BOARD_SETUP:
                        self.change_state(glob.MenuState.GAME_SETUP)
            case glob.MenuState.PLAY_GAME:
                return glob.GameState.BOARD_SETUP
            
        return glob.GameState.MENU
                
    #Obtém a partir do botão selecionado, a ação que necessita ser realizada e muda o estado do menu            
    def user_action(self):
        for button in self.buttons:
            action = button.was_clicked()
            if(action is not None):
                return self.change_state(action, button)
        return None

    #Desenha as telas do Menu principal e do menu de configuração        
    def draw_screen(self, screen):
        if (self.menu_state == glob.MenuState.MAIN_MENU):
            let.draw(screen, "Focus", (glob.SCREEN_WIDTH//2, glob.SCREEN_HEIGHT//7), (0, glob.SCREEN_HEIGHT//3))
        
        match(self.menu_state):
            case  glob.MenuState.MAIN_MENU:
                height = glob.SCREEN_HEIGHT//2
                for button in self.buttons:
                    button.draw_button(screen, glob.SCREEN_WIDTH//2 - button.width//2, height)
                    height += 3.2*button.height//2
            case glob.MenuState.GAME_SETUP:
                height = glob.SCREEN_HEIGHT//3
                for button in self.buttons:
                    button.draw_button(screen, glob.SCREEN_WIDTH//2 - button.width//2, height)
                    height += 3.2*button.height//2

    #Desenha as telas do menu para escolha de jogador e tabuleiro  
    def draw_setup_screen(self, screen):
        bsize_accX = 0
        for button in self.buttons:
            if(button.action == glob.MenuState.BOARD_SIZE):
                button.draw_button(screen, glob.SCREEN_WIDTH//5 + bsize_accX,  1.1*glob.SCREEN_HEIGHT//3)
                bsize_accX += glob.SCREEN_WIDTH//6
            elif(button.action == glob.MenuState.SWITCH_TYPE):
                bsize_accX = 3*glob.SCREEN_WIDTH//5

                if (self.num_players == 2):
                    match(button.value):
                        case 0:
                            let.draw(screen, self.players_type[self.players[0]], (1.1*glob.SCREEN_WIDTH//4 -12, glob.SCREEN_HEIGHT//4), (len(self.players_type[self.players[0]])//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//35))
                            button.draw_button(screen, 1.1*glob.SCREEN_WIDTH//4 -10, 1.1*glob.SCREEN_HEIGHT//3)
                        case 1:
                            let.draw(screen, self.players_type[self.players[1]], (2*glob.SCREEN_WIDTH//3 + 10, glob.SCREEN_HEIGHT//4), (len(self.players_type[self.players[1]])//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//35))
                            button.draw_button(screen, 2.05*glob.SCREEN_WIDTH//3, 1.1*glob.SCREEN_HEIGHT//3)
                        case 4:
                            let.draw(screen, str(self.num_players), (glob.SCREEN_WIDTH//2, 1.1*glob.SCREEN_HEIGHT//3 -10), (len(str(self.num_players))//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//30))
                            button.draw_button(screen, 1.1*glob.SCREEN_WIDTH//4, 1.1*glob.SCREEN_HEIGHT//3)
                        case 5:
                            button.draw_button(screen, 2.05*glob.SCREEN_WIDTH//3 +10, 1.1*glob.SCREEN_HEIGHT//3)
                else: 
                    match(button.value):
                        case 0:
                            let.draw(screen, self.players_type[self.players[0]], (1.1*glob.SCREEN_WIDTH//4 -12, glob.SCREEN_HEIGHT//6), (len(self.players_type[self.players[0]])//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//35))
                            button.draw_button(screen, 1.1*glob.SCREEN_WIDTH//4, 1.1*glob.SCREEN_HEIGHT//4)
                        case 1:
                            let.draw(screen, self.players_type[self.players[1]], (2*glob.SCREEN_WIDTH//3 + 10, glob.SCREEN_HEIGHT//6), (len(self.players_type[self.players[1]])//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//35))
                            button.draw_button(screen, 2.05*glob.SCREEN_WIDTH//3, 1.1*glob.SCREEN_HEIGHT//4)
                        case 2:
                            let.draw(screen, self.players_type[self.players[2]], (1.1*glob.SCREEN_WIDTH//4 -12, glob.SCREEN_HEIGHT//2), (len(self.players_type[self.players[2]])//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//35))
                            button.draw_button(screen, 1.1*glob.SCREEN_WIDTH//4, 1.22*glob.SCREEN_HEIGHT//2)
                        case 3:
                            let.draw(screen, self.players_type[self.players[3]], (2*glob.SCREEN_WIDTH//3 + 10, glob.SCREEN_HEIGHT//2), (len(self.players_type[self.players[3]])//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//35))
                            button.draw_button(screen, 2.05*glob.SCREEN_WIDTH//3, 1.22*glob.SCREEN_HEIGHT//2)
                        case 4:
                            let.draw(screen, str(self.num_players), (glob.SCREEN_WIDTH//2, 1.1*glob.SCREEN_HEIGHT//3 -10), (len(str(self.num_players))//2*20, (glob.SCREEN_WIDTH + glob.SCREEN_HEIGHT)//30))
                            button.draw_button(screen, 1.1*glob.SCREEN_WIDTH//4, 1.1*glob.SCREEN_HEIGHT//3)
                        case 5:
                            button.draw_button(screen, 2.05*glob.SCREEN_WIDTH//3, 1.1*glob.SCREEN_HEIGHT//3)
            elif(button.action == glob.MenuState.EXIT or button.action == glob.MenuState.PLAYER_SETUP):
                if (self.num_players != 2 and self.menu_state == glob.MenuState.PLAYER_SETUP):
                    button.draw_button(screen, glob.SCREEN_WIDTH//2 - glob.SCREEN_WIDTH//20  , 3.3*glob.SCREEN_HEIGHT//5 + 70)
                else:
                    button.draw_button(screen, glob.SCREEN_WIDTH//2 - glob.SCREEN_WIDTH//20  , 2*glob.SCREEN_HEIGHT//5 + 70)
