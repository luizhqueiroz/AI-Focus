import globals as glob
import pygame as pg  
from game import Game


pg.init()
game = Game(glob.SCREEN_WIDTH, glob.SCREEN_HEIGHT, glob.FPS)
game.run_game()  
pg.quit()
