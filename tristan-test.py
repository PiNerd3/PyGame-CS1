import pygame
import sys

from pygame.locals import *

pygame.init()

windowSurface = pygame.display.set_mode((500 , 500) , 0 , 32)

pygame.display.set_caption("Play")

RED = (255 , 0 , 0)
BLACK = (222,222,0)
print(RED, BLACK)

windowSurface.fill(BLACK)
#FIGURED IT OUT: NEED v
pygame.display.update()
print("filled")

while True:
    windowSurface.fill(BLACK)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
