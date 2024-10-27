import pygame as pg
import globals as glob
import letter as let
import os
from button import Button


class SidePanel():
    #Inicializa a classe do Painel Lateral
    def __init__(self, size, toggle = False):
        self.size = size
        self.toggle = toggle

        self.change_state(glob.SidePanelState.TOGGLE)
        self.background = pg.image.load(os.path.join('images', 'background3.jpg')).convert()
        self.instructions = [
            """The objective of Focus is to capture all of your opponent's pieces.""",
            """1 - A player needs to move a stack of their pieces up, down, right, or left.""",
            """2 - The topmost piece of the stack determines which player controls the stack.""",
            """3 - The height of the stack determines how far the player can move the stack.""",
            """4 - A stack can have 1 to 5 pieces.""",
            """5 - The player can split the stack and move just a part of it, following rule 3.""",
            """6 - The player can take control of the opponent's stack by moving their stack to where the opponent's stack is.""",
            """7 - If a stack reaches more than 5 pieces, its owner has to take out the pieces from the bottom until the stack is reduced back to 5 pieces.""",
            """8 - If the pieces that the player is taking out (as per rule 7) belong to this player, the player keeps the pieces as reserved.""",
            """9 - If the pieces that the player is taking out (as per rule 7) belong to the opponent, the player captures the opponent's pieces.""",
            """10 - Reserved pieces can be placed again in any position on the board during its owner's turn.""",
            """11 - Captured pieces cannot be placed again on the board."""]
        self.instruction = 0
        self.finish_time = 0.0
        self.hint_num = 1

    #Gerencia os diferentes estados do painel lateral
    def state_handler(self, screen):
            match(self.panel_state):
                case glob.SidePanelState.GAME:
                    accX = 0
                    for button in self.buttons:
                        button.draw_button(screen, glob.SCREEN_WIDTH-40 + accX, 0)
                        accX += 40
                    return self.user_action()
                case glob.SidePanelState.GAME_INFO:
                    self.draw_bg_panel(screen)
                    self.buttons[0].draw_button(screen, glob.SCREEN_WIDTH-40, 0)
                    accY = 0
                    for button in self.buttons[1:]:
                        button.draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//5, glob.SCREEN_HEIGHT//3 + accY)
                        accY += 70
                    return self.user_action()
                case glob.SidePanelState.HINT:
                    self.draw_bg_panel(screen)

                    self.draw_hints(screen)

                    return self.user_action()
                case glob.SidePanelState.INSTRUCTIONS:
                    self.draw_bg_panel(screen)
                    self.draw_instructions(screen)
                    return self.user_action()
                case glob.SidePanelState.QUIT:
                    pass
                    return self.user_action()
                
    #Obtém a partir do botão selecionado, a ação que necessita ser realizada e muda o estado do painel lateral   
    def user_action(self):
        for button in self.buttons:
            action = button.was_clicked()
            if(action):
                return self.change_state(action, button)
        return None
    
    #Altera o estado do painel lateral com base na ação designada pelo botão selecionado
    def change_state(self, action, button=None):
        match(action):
            case glob.SidePanelState.TOGGLE:
                if (self.toggle):
                    self.buttons = [
                    Button("x", glob.SidePanelState.TOGGLE, None, 40),
                    Button("Instructions", glob.SidePanelState.INSTRUCTIONS, None, 200),
                    Button("Analyse", glob.SidePanelState.HINT, None, 200),
                    Button("Quit Game", glob.SidePanelState.QUIT, None, 200)
                    ]                    
                    self.panel_state = glob.SidePanelState.GAME_INFO
                else:
                    self.buttons = [
                        Button("+", glob.SidePanelState.TOGGLE, None, 40)
                    ]                    
                    self.panel_state = glob.SidePanelState.GAME
                self.toggle = not self.toggle
            case glob.SidePanelState.HINT:
                self.buttons = [
                    Button("Show Hints", glob.SidePanelState.ANALYSE, None, None, 30, False),
                    Button("<-", glob.SidePanelState.SWITCH_TYPE, 3),
                    Button("->", glob.SidePanelState.SWITCH_TYPE, 4),
                    Button("<-", glob.SidePanelState.SWITCH_TYPE, 5),
                    Button("->", glob.SidePanelState.SWITCH_TYPE, 6),
                    Button("Back", glob.SidePanelState.EXIT, None, 100)
                    ]                    
                self.panel_state = glob.SidePanelState.HINT
            case glob.SidePanelState.INSTRUCTIONS:
                self.buttons = [
                    Button("<-", glob.SidePanelState.SWITCH_TYPE, 1),
                    Button("->", glob.SidePanelState.SWITCH_TYPE, 2),
                    Button("Back", glob.SidePanelState.EXIT, None, 100)
                    ] 
                             
                self.panel_state = glob.SidePanelState.INSTRUCTIONS
            case glob.SidePanelState.SWITCH_TYPE:
                match(button.value):
                    case 1:
                        self.instruction = (self.instruction - 1)%len(self.instructions)
                    case 2:
                        self.instruction = (self.instruction + 1)%len(self.instructions)
                    case 3:
                        self.finish_time -= 0.5
                        if(self.finish_time <= 0.0):
                            self.finish_time = 0.0
                    case 4:
                        self.finish_time += 0.5
                        if(self.finish_time >= 10.0):
                            self.finish_time = 10.0
                    case 5:
                        self.hint_num -= 1
                        if(self.hint_num <= 1):
                            self.hint_num = 1
                    case 6:
                        self.hint_num += 1
                        if(self.hint_num >= 99):
                            self.hint_num = 99

            case glob.SidePanelState.ANALYSE:
                button.isHeld = not button.isHeld
                self.panel_state = glob.SidePanelState.HINT

            case glob.SidePanelState.QUIT:                 
                self.panel_state = glob.SidePanelState.QUIT
            case glob.SidePanelState.EXIT:
                if (self.panel_state == glob.SidePanelState.HINT or self.panel_state == glob.SidePanelState.INSTRUCTIONS):
                    self.toggle = not self.toggle
                    self.change_state(glob.SidePanelState.TOGGLE)

        return self.panel_state

    #Desenha o background do painel lateral
    def draw_bg_panel(self, screen):
        background = pg.transform.scale(self.background, (self.size, glob.SCREEN_HEIGHT))
        screen.blit(background, (glob.SCREEN_WIDTH-self.size+3.5, 0))
        pg.draw.line(screen, glob.BLACK, (glob.SCREEN_WIDTH-self.size,0), (glob.SCREEN_WIDTH-self.size, glob.SCREEN_HEIGHT), 5)

    #Desenha a tela de instruções do jogo no painel lateral
    def draw_instructions(self, screen):
        accX = -glob.SIDE_PANEL_SIZE//15
        for button in self.buttons[:2]:
            button.draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(button.text)//2)*20 + accX, 1.8*glob.SCREEN_HEIGHT//3)
            accX += 2*glob.SIDE_PANEL_SIZE//10
        accY = 70
        for button in self.buttons[2:]:
            button.draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(button.text)//2)*20, 1.8*glob.SCREEN_HEIGHT//3 + accY)
            accY += 70
        
        if (self.instruction == 0):
            let.draw(screen, "Objective:", (glob.SCREEN_WIDTH-glob.SIDE_PANEL_SIZE + glob.SIDE_PANEL_SIZE//2,glob.SCREEN_HEIGHT//5), (0, 30), glob.BLACK)
        else:
            let.draw(screen, "Rule:", (glob.SCREEN_WIDTH-glob.SIDE_PANEL_SIZE + glob.SIDE_PANEL_SIZE//2,glob.SCREEN_HEIGHT//5), (0, 30), glob.BLACK)
        let.draw_text(screen, self.instructions[self.instruction], [glob.SCREEN_WIDTH-glob.SIDE_PANEL_SIZE + 0.09*glob.SIDE_PANEL_SIZE, glob.SCREEN_HEIGHT//3], 20, 0.9*glob.SIDE_PANEL_SIZE, glob.BLACK)

    #Desenha a tela de hints do painel lateral        
    def draw_hints(self, screen):
        self.buttons[0].draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(self.buttons[0].text)//2)*20, glob.SCREEN_HEIGHT//2 - 200)

        accX = -glob.SIDE_PANEL_SIZE//10-25
            
        for button in self.buttons[1:3]:
            button.draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(button.text)//2)*20 +accX, 1.8*glob.SCREEN_HEIGHT//3)
            accX += 2*glob.SIDE_PANEL_SIZE//10+50

        let.draw(screen, str(self.finish_time)+"s", ((glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(self.buttons[1].text)//2)*20-glob.SIDE_PANEL_SIZE//10+self.buttons[1].width*2-30, 1.8*glob.SCREEN_HEIGHT//3), (0, 30), glob.BLACK)
        let.draw(screen, "Total Depth Time", ((glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(self.buttons[1].text)//2)*20-glob.SIDE_PANEL_SIZE//10+self.buttons[1].width*2-25, 1.8*glob.SCREEN_HEIGHT//3-self.buttons[1].height), (0, 30), glob.BLACK)


        accX = -glob.SIDE_PANEL_SIZE//10-25
        for button in self.buttons[3:5]:
            button.draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(button.text)//2)*20 +accX, 1.8*glob.SCREEN_HEIGHT//3-button.height*2-button.height)
            accX += 2*glob.SIDE_PANEL_SIZE//10+50

        let.draw(screen, str(self.hint_num), ((glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(self.buttons[1].text)//2)*20-glob.SIDE_PANEL_SIZE//10+self.buttons[1].width*2-30, 1.8*glob.SCREEN_HEIGHT//3-button.height*2-button.height), (0, 30), glob.BLACK)
        let.draw(screen, "Number of Hints", ((glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(self.buttons[1].text)//2)*20-glob.SIDE_PANEL_SIZE//10+self.buttons[1].width*2-25, 1.8*glob.SCREEN_HEIGHT//3-button.height*4), (0, 30), glob.BLACK)
            
        self.buttons[-1].draw_button(screen, (glob.SCREEN_WIDTH - glob.SIDE_PANEL_SIZE)  + glob.SIDE_PANEL_SIZE//2-(len(self.buttons[-1].text)//2)*20, 1.8*glob.SCREEN_HEIGHT//3 + glob.SCREEN_HEIGHT//6)
