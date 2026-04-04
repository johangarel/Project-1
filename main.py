import pygame
from scripts.game_engine import Game

game = Game()
while game.active :
    game.handle_events()
    game.update()
    game.render()

pygame.quit()