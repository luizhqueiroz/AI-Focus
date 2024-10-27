import pygame as pg
import globals as glob
from button import Button
import letter as let

class GameOver():
    #Inicializa a classe Game Over
    def __init__(self):
        self.winner_color = glob.WHITE
        self.result = ""
        self.buttons = [
            Button('Play Again', glob.GameState.BOARD_SETUP),
            Button('Back to Menu', glob.GameState.MENU)
        ]
    
    #Gerencia o estado de game over 
    def state_handler(self, screen):
        self.draw_screen(screen)
        return self.user_action()

    #Obtém a partir do botão selecionado, a ação que necessita ser realizada e muda o estado do game over
    def user_action(self):
        for button in self.buttons:
            action = button.was_clicked()
            if(action is not None):
                return self.change_state(action)
        return None

    #Altera o estado do game over com base na ação designada pelo botão selecionado
    def change_state(self, action):
        match(action):
            case glob.GameState.BOARD_SETUP:
                return glob.GameState.BOARD_SETUP
            case glob.GameState.MENU:
                return glob.GameState.MENU

    #Desenha a tela de game over
    def draw_screen(self, screen):
        x = 1.2*glob.SCREEN_WIDTH//4
        y = glob.SCREEN_HEIGHT//8
        width = glob.SCREEN_WIDTH//2
        height = glob.SCREEN_HEIGHT//4

        rect_surface = pg.Surface((glob.SCREEN_WIDTH, glob.SCREEN_HEIGHT), pg.SRCALPHA)
        rect_surface.fill((255, 255, 255, 150))
        screen.blit(rect_surface, (0, 0))

        if (self.result == "win"):
            pg.draw.circle(screen, self.winner_color, (x+width//2 + height//3, y+height//2), height//3-10)
            pg.draw.circle(screen, glob.BLACK, (x+width//2 + height//3, y+height//2), height//3-10, 2)
            pg.draw.circle(screen, glob.BLACK, (x+width//2 + height//3, y+height//2-(height//3-10)//5), height//3-10-((height//3-10)//20), 2, False, False, True, True)
            let.draw(screen, "Player: ", (x+width//2 - int(height//2) - width//20, y+height//4), (0, int(height//2)), self.winner_color)

            let.draw(screen, "WINS!!!", (glob.SCREEN_WIDTH/2, 0.9*(y + height)), (0, int(0.8*height)), glob.GOLD)
        else: 
             let.draw(screen, "DRAW!!!", (glob.SCREEN_WIDTH/2, 0.9*(y + height)), (0, int(0.8*height)), glob.ORANGE)

        button_height = 1.1*glob.SCREEN_HEIGHT//2
        for button in self.buttons:
            button.draw_button(screen, glob.SCREEN_WIDTH//2-(len(button.text)/2)*20, button_height)
            button_height += 60
