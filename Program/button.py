import pygame as pg
import globals as glob
import letter as let


class Button():
    button_color = glob.BLUE
    button_hover_color = glob.LIGHT_BLUE
    button_click_color = glob.DARK_BLUE
    button_text_color = glob.WHITE
    clicked = False
    #param -> text of button, action it will perform after being clicked, value that it has when it's clicked, fixedWidth to set its width manually, if it is held or not
    #Inicializa a classe Button
    def __init__(self, text, action, value=None, fixedWidth=None, fixedHeight=30, isHeld=False):
        self.width = len(text) * 20
        if(fixedWidth):
            self.width = fixedWidth
        self.height =fixedHeight+10
        self.fixedHeight = fixedHeight
        self.text = text
        self.action = action
        self.value = value
        self.isHeld = isHeld

    #Verifica se o botão foi clicado com o rato
    def was_clicked(self):
        mouse_pos = pg.mouse.get_pos()

        if(self.button_rect.collidepoint(mouse_pos)):
            if(not pg.mouse.get_pressed()[glob.LEFT_MOUSE_CLICK] and self.clicked and (self.isHeld == False or self.action == glob.SidePanelState.ANALYSE)):
                self.clicked = False
                
                if(self.action == glob.MenuState.BOARD_SIZE):
                    
                    self.isHeld = True
                return self.action

        return None

    #Desenha o botão na tela
    def draw_button(self, screen, x, y):
        mouse_pos = pg.mouse.get_pos()

        self.button_rect = pg.Rect(x, y, self.width, self.height)

        if(self.isHeld):
            pg.draw.rect(screen, self.button_click_color, self.button_rect)
        if((not self.isHeld or self.action == glob.SidePanelState.ANALYSE) and self.button_rect.collidepoint(mouse_pos)):
            if(pg.mouse.get_pressed()[glob.LEFT_MOUSE_CLICK]):
                self.clicked = True
                pg.draw.rect(screen, self.button_click_color, self.button_rect)
            else:
                pg.draw.rect(screen, self.button_hover_color, self.button_rect)
        elif(not self.isHeld):
            pg.draw.rect(screen, self.button_color, self.button_rect)

        pg.draw.line(screen, glob.WHITE, (x, y), (x + self.width, y), 2)
        pg.draw.line(screen, glob.WHITE, (x, y), (x, y + self.height), 2)
        pg.draw.line(screen, glob.BLACK, (x, y+self.height), (x + self.width, y + self.height), 2)
        pg.draw.line(screen, glob.BLACK, (x + self.width, y), (x + self.width, y + self.height), 2)
        let.draw(screen, self.text, (x, y), (self.width, ( int(1.2*self.fixedHeight))))
