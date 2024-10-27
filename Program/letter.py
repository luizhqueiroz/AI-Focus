import pygame as pg
import globals as glob

#Desenha um texto na tela
def draw(screen, text, pos, size, color=glob.WHITE):
    font = pg.font.SysFont('constantia', size[1])
    text_img = font.render(text, True, color)
    screen.blit(text_img, (pos[0]+int(size[0]/2) - int(text_img.get_width()/2), pos[1] + 5))

#Desenha um texto grande na tela respeitando as delimitações de largura máxima
def draw_text(screen, text, pos, size,  max_width, color=glob.WHITE):
    font = pg.font.SysFont('constantia', size)
    max_width = max_width
    words_in_lines = [line.split(' ') for line in text.splitlines()]
    line = []
    
    for words_in_line in words_in_lines:
        for word in words_in_line:
            newline = ' '.join(line + [word])
            if font.size(newline)[0] < max_width:
                line.append(word)
            else:
                text_img = font.render(' '.join(line), True, color)
                text_rect = text_img.get_rect()
                text_rect.topleft = pos
                screen.blit(text_img, text_rect)
                pos[1] += text_rect.height + 10
                line = [word]

        text_img = font.render(' '.join(line), True, color)
        text_rect = text_img.get_rect()
        text_rect.topleft = pos
        screen.blit(text_img, text_rect)
        pos[1] += text_rect.height + 10
        line = []
