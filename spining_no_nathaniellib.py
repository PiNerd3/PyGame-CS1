#################################
##                             ##
##  PyGame Project 1           ##
##  Nathaniel Hamovitz         ##
##  CS1                        ##
##                             ##
#################################


###   Imports   ###

import pygame
import sys
import time
import math
import random

from pygame.locals import *

#import nathaniellib.main
#from nathaniellib.npygame.colors import *

BLACK   = (  0,   0,   0)
RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
RG      = (255, 255,   0)
AQUA    = (  0, 255, 255)
RB      = (255,   0, 255)
WHITE   = (255, 255, 255)
MAROON  = (128,   0,   0)
G2      = (  0, 128,   0)
B2      = (  0,   0, 128)
RG2     = (128, 128,   0)
GB2     = (  0, 128, 128)
RB2     = (128,   0, 128)
RGB2    = (128, 128, 128)
RPURPLE = (102,  51, 153)
ORANGE  = (255, 163,  26)

COLORS  = (BLACK,
           RED, GREEN, BLUE,
           RG, AQUA, RB,
           WHITE,

           MAROON, G2, B2,
           RG2, GB2, RB2,
           RGB2,

           RPURPLE, ORANGE,
           )

###   init   ###

pygame.init()

windowSurface = pygame.display.set_mode( (700, 700) , 0, 32)
windowRect = windowSurface.get_rect()

_frameCount = 0


###   mode   ###   - for determining welcome text and window caption

mode_opts = ('ex', 'std')
mode_mode = 'ch'
mode_modes = {'ra': random.choice(mode_opts), 'ch': mode_opts}
if mode_mode == 'ra':
    mode = mode_modes['ra']
else:
    mode = 'std' ##choose here

###   some misc flags   ###

q_quit = 'no'
changeTriCol = True
triAvoidOrange = True
backspaceAllowed = True

captions = {'ex': "Example Window Caption!", 'std': "A PyGame Window! This *is* cool."}
pygame.display.set_caption(captions[mode])


###   Some font things and some message-init

courier = pygame.font.SysFont("Courier", 28, True, False)
times   = pygame.font.SysFont("Times New Roman", 23)

message       = {'ex': "Example text here! :)", 'std': "Hello, dear reader! Welcome to PyGame!"}
centerMessage = times.render(message[mode], True, WHITE, RPURPLE)

centerMessageRect = centerMessage.get_rect()
centerMessageRect.center = windowRect.center

text_prompt = times.render("Try typing something!", True, WHITE, BLACK)
text_promptRect = text_prompt.get_rect()
text_promptRect.center = (centerMessageRect.centerx, centerMessageRect.centery + windowRect.height/4)

###   Efficient text   ###

#def drawText2(_text, _rect, 
def drawText(_text, _rect):
    windowSurface.blit(_text, _rect)


###   Circle constant things   ###
CIR_SIZE, CIR_BUF = 30, 3
cirBox = CIR_SIZE + CIR_BUF
x, y = cirBox, cirBox

_dx_orig, rot_orig = 2, 0.3

cirMode = 'fd'

def increaseCoords(x, y,
                   dx = 1, dy = 45,
                   minX = cirBox, minY = cirBox,
                   maxX = windowRect.width - cirBox, maxY = windowRect.height - cirBox,
                   mode = 'fd'):
    #something's still wrong here... 
    
    #yChanged = False
    if mode == 'fd':
        x += dx
        if x >= maxX:
            x = minX
            y += dy
            yChanged = True
        if y >= maxY:
            y = minY
        return x, y
    elif mode == 'bk':
        x -= dx
        if x < minX:
            x = maxX
            y -= dy
            yChanged = True
        if y <= minY:
            y = maxY
        return x, y


###  Pentagon  and polygon things   ###

def pFromC(x, y = None):
    """Take a tuple (x, y) or arguments x, y and return an (radius, theta) pair.
    """
    x, y = x if y is None else (x, y)
    return math.sqrt(x ** 2 + y ** 2), math.atan2(y, x)

def cFromP(r, theta = None):
    """Take a tuple (radius, theta) or arguments radius, theta and return an (x, y) pair.
    """
    r, theta = r if theta is None else (r, theta)
    return r * math.cos(theta), r * math.sin(theta)

r90 = math.radians(-90)

def genPoly(points, radius):
    return tuple( (radius, i * math.radians(360/points) + r90) for i in range(points) )

bigPent = genPoly(5, 300)
smallPent = genPoly(5, 150)


## triangles! ##
triL = genPoly(3, 110)
triR = genPoly(3, 110)

triColsAvoid = (
    BLUE,
    RED,
    ORANGE if triAvoidOrange else None,
    #GREEN,
    )

if not changeTriCol:
    triCols = (BLUE,)
    while any(_col in triCols for _col in triColsAvoid):
        triCols = tuple(random.choice(COLORS) for _ in range(4))
        
def cPolyFromP(_tuple, dest = windowRect.center):
    #return tuple( tuple(map(lambda num: num + windowRect.width/2, coord)) for coord in _tuple )
    return tuple( (x + dest[0], y + dest[1]) for x, y in map(cFromP, _tuple) )

def pPolyFromC(_tuple, loc = windowRect.center):
    _tuple = ( (x - loc[0], y - loc[1]) for x, y in _tuple)
    return tuple(map(pFromC, _tuple))

def rotatePPolyBy(poly_tuple, angle):
    #rip --- temp =
    #return tuple( (lambda _coord: (_coord[0], _coord[1] + angle))(coord) for coord in poly_tuple)
    return tuple( (r, t + angle) for r, t in poly_tuple )

###   keycodes   ### - help w/ typing

                          #pygame.key.name(code) / what I call it
disallowed_typing = {27,  #escape
                     9,   #tab
                     315, #help         / fn
                     311, #left super   / windows key
                     308, #left alt
                     307, #right alt
                     319, #menu         / weird lined one on right
                     273, #up           / up arrow
                     274, #down         / down arrow
                     275, #right        / right arrow
                     276, #left         / left arrow
                     278, #home
                     279, #end
                     280, #page up
                     281, #page down
                     127, #delete       / fd-delete
                     316, #print screen / PrtSc
                     13,  #return       / enter
                     #8,  #backspace
                     }.union(
                         {val for val in range(282, 293 + 1)} #f1 through t12 / function keys
                         ).union(
                             {8} if not backspaceAllowed else set()
                             ) #backspace

dont_moves        = {301,   #caps lock / caps lock on
                     303,   #right shift
                     304,   #left shift
                     }

###   _strMessage - related constants for the first-run through   ###

_str = ''
new_char = False
new_strMessageTopLeft = (random.randrange(0, windowRect.width), random.randrange(0, windowRect.height))
_strMessage = times.render(_str, True, BLACK, WHITE)
anythingTyped = False
lastBackspace = False
message_col1, message_col2 = BLACK, BLACK
#Also, relating to circle:
_dx, rot = _dx_orig, rot_orig

_strMessageLocked = False

def getNewTopLeft(_textBoxObj, _buf = 5):
    _temp_rect = _textBoxObj.get_rect()
    w = _temp_rect.width
    h = _temp_rect.height

    r = windowRect.width  - w - _buf
    d = windowRect.height - h - _buf

    if r <= 0 and d <= 0:
        _strMessageLocked = True
        return _temp_rect.topleft
    elif r <= 0:
        _strMessageLocked = True
        return (_temp_rect.left, random.randint(0, d))
    elif d <= 0:
        _strMessageLocked = True
        return (random.randint(0, r), _temp_rect.top)
    else:
        _strMessageLocked = False
        return (random.randint(0,r), random.randint(0, d))


###   The loop   ###

while True:

    #  Fill red to start   #
    windowSurface.fill(RED)

    # Polygons #
    pygame.draw.polygon(windowSurface, BLUE, cPolyFromP(bigPent))
    bigPent = rotatePPolyBy(bigPent, math.radians(rot))

    pygame.draw.polygon(windowSurface, ORANGE, cPolyFromP(smallPent))
    smallPent = rotatePPolyBy(smallPent, -math.radians(rot))

    # Circle #
    pygame.draw.circle(windowSurface, GREEN, (x, y), CIR_SIZE - CIR_BUF, 0)
    x, y = increaseCoords(x, y, dx = _dx, mode = ('bk' if cirMode == 'bk' else 'fd'))


    #tris
    if changeTriCol:
        if _frameCount % 1000 == 0:
            triCols = (BLUE,)
            while any(_col in triCols for _col in triColsAvoid):
                triCols = tuple(random.choice(COLORS) for _ in range(4))
    pygame.draw.polygon(windowSurface, triCols[0], cPolyFromP(triL, dest = (windowRect.width/5  , windowRect.height/5  )))
    pygame.draw.polygon(windowSurface, triCols[1], cPolyFromP(triR, dest = (windowRect.width/5*4, windowRect.height/5  )))
    pygame.draw.polygon(windowSurface, triCols[2], cPolyFromP(triL, dest = (windowRect.width/5  , windowRect.height/5*4)))
    pygame.draw.polygon(windowSurface, triCols[3], cPolyFromP(triR, dest = (windowRect.width/5*4, windowRect.height/5*4)))

    triL = rotatePPolyBy(triL, 1.5*math.radians(-rot))
    triR = rotatePPolyBy(triR, 1.5*math.radians(+rot))

    # The center text #
    drawText(centerMessage, centerMessageRect)
    


    # _strMessage #

    #if _str == '' and anythingTyped and lastBackspace:
    #    _str = '  '
    
    if new_char:
        message_col1 = random.choice(COLORS)
        choose_new = False
        while message_col2 == message_col1 or not choose_new:
            message_col2 = random.choice(COLORS)
            choose_new = True
        _strMessage = courier.render(_str, True, message_col1, message_col2)
        new_strMessageTopLeft = getNewTopLeft(_strMessage)
        new_char = False

    _strMessageRect = _strMessage.get_rect()
    _strMessageRect.topleft = new_strMessageTopLeft
    if not anythingTyped:
        drawText(text_prompt, text_promptRect)
    else:
        drawText(_strMessage, _strMessageRect)
    

    # update #
    pygame.display.update()
    _frameCount += 1


    ###   Sleep statements   ###

    #time.sleep(1)
    #time.sleep(0.5)
    #time.sleep(0.1)
    #time.sleep(0.05)
    #time.sleep(0.01)
    #time.sleep(0.005)
    #time.sleep(0.001)
    #time.sleep(0.0005)


    ###   Dealing w/ keypresses   ###

    keys = pygame.key.get_pressed()

    #speed
    if keys[K_LEFT] and not keys[K_RIGHT]:
        _dx = int(0.5 * _dx_orig)
        rot = 0.5 * rot_orig
    elif not keys[K_LEFT] and keys[K_RIGHT]:
        _dx = 2 * _dx_orig
        rot = 1.75 * rot_orig
    else:
        _dx = _dx_orig
        rot = rot_orig

    ctrl_pressed = pygame.key.get_mods() & KMOD_CTRL
    #print(ctrl_pressed, bool(ctrl_pressed))

    #Go backwards
    if keys[K_LCTRL] or keys[K_RCTRL]:#ctrl_pressed:
        cirMode = 'bk'
        rot *= -1
    else:
        cirMode = 'fd'
    #Quitting on 'q'
    if q_quit.lower() in {'q', 'quit',}.union({'t', 'true' , 'y', 'yes'}):#nathaniellib.main.truthy_strings_lower):
        if keys[K_q]:
            pygame.quit()
            sys.exit()

    for event in pygame.event.get():
        #quit
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        
        if event.type == KEYDOWN:
            
            #typing for _strMessage
            no_disalloweds = (event.key not in disallowed_typing)
            if no_disalloweds and not pygame.key.get_mods() & KMOD_CTRL: #ctrl_pressed: 
                anythingTyped = True
                if event.key == 8 and backspaceAllowed: #backspace
                    _str = _str[:-1]
                    lastBackspace = True
                else:
                    if not _strMessageLocked:
                        _str += event.unicode
                    lastBackspace = False


                if event.key not in dont_moves:
                    new_char = True
                #debuggin!! --->>  #print("KEYCODE: {}: Meaning:  {}".format(event.key, pygame.key.name(event.key)))
