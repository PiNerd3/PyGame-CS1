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

from collections import deque

from pygame.locals import *

import nathaniellib.main
from nathaniellib.npygame.colors import  *


###   init   ###

pygame.init()

displaySurface = pygame.display.set_mode( (700, 700) , 0, 32)
windowRect = displaySurface.get_rect()

_frameCount = 0


###   mode   ###   - for determining welcome text and window caption

mode_opts = ('weird', 'deez', 'ex', 'std')
mode_mode = 'ch'
mode_modes = {'ra': random.choice(mode_opts), 'ch': mode_opts}
if mode_mode == 'ra':
    mode = mode_modes['ra']
else:
    mode = 'std' ##choose here

###   some misc flags   ###

q_quit = 'yes'
changeTriCol = True
triAvoidOrange = False
backspaceAllowed = True
freezeAllowed = True
frozen = False
clearEveryTime = True

captions = {'weird': 'Ayyyy test thing!', 'deez': "Rip Vine! We're movin' on to U-toobe!", 'ex': "Example Window Caption!", 'std': "A PyGame Window! This *is* cool."}
pygame.display.set_caption(captions[mode])


###   Some font things and some message-init

courier = pygame.font.SysFont("Courier", 28, True, False)
times   = pygame.font.SysFont("Times New Roman", 23)

messages       = {'weird': r"Ayyy Pygame is<\n>wordy????! (YES)", 'deez': "Deez nuts vine compilation 2k17!!", 'ex': "Example text here! :)", 'std': "Hello, dear reader! Welcome to PyGame!"}
centerMessage = times.render(messages[mode], True, WHITE, RPURPLE)
centerMessageRect = centerMessage.get_rect()
centerMessageRect.center = windowRect.center

mvmt_prompt = times.render("Try pressing Alt, left arrow key, or right arrow key!", True, WHITE, BLACK)
mvmt_promptRect = mvmt_prompt.get_rect()
mvmt_promptRect.midtop = (windowRect.centerx, 0 + int(0.25 * mvmt_promptRect.height))
ctrl_pressed_ever, left_arrow_pressed_ever, right_arrow_pressed_ever = False, False, False

click_prompt = times.render("Try clicking the eye!", True, WHITE, BLACK)
click_promptRect = click_prompt.get_rect()
click_promptRect.center = (windowRect.centerx, windowRect.centery - windowRect.height/4)

text_prompt = times.render("Try typing something!", True, WHITE, BLACK)
text_promptRect = text_prompt.get_rect()
text_promptRect.center = (windowRect.centerx, windowRect.centery + windowRect.height/4)

freeze_prompt = times.render("Try clicking somewhere else!", True, WHITE, BLACK)
freeze_promptRect = freeze_prompt.get_rect()
freeze_promptRect.center = (windowRect.centerx, windowRect.height - int(0.25 * freeze_promptRect.height))



###   Efficient text   ###

def drawText(_text, _rect):
    displaySurface.blit(_text, _rect)

###   one misc thing   ###
def getNewTopLeft(_obj, _buf = 5):
    _temp_rect = _obj.get_rect()
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

###   Images   ###
imgs = {'sun': 'sun.png', 'eye': 'eye.jpg', 'treye': 'eye_transparent.png'}
img = pygame.image.load(imgs['treye'])
img = pygame.transform.smoothscale(img, (int(windowRect.width/8), int(windowRect.height/8)))
imgRect = img.get_rect()
imgRect.topleft = getNewTopLeft(img, 2)
img_clicked = False
img_clicked_ever = False

###   Circle constant things   ###
CIR_SIZE, CIR_BUF = 30, 3
cirBox = CIR_SIZE + CIR_BUF
x, y = cirBox, cirBox

_dx_orig, rot_orig = nathaniellib.main._round(2), 0.25

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

def cFromP(r, theta = None, dest = (0, 0)):
    """Take a tuple (radius, theta) or arguments radius, theta and return an (x, y) pair.
    """
    r, theta = r if theta is None else (r, theta)
    return r * math.cos(theta) + dest[0], r * math.sin(theta) + dest[1]

r90 = math.radians(-90)

def genPolyTuple(points, radius):
    return tuple( (radius, i * math.radians(360/points) + r90) for i in range(points) )

bigPent = genPolyTuple(5, 300)
smallPent = genPolyTuple(5, 150)


## triangles! ##
triL = genPolyTuple(3, 110)
triR = genPolyTuple(3, 110)

triDist = math.sqrt(((windowRect.centerx - windowRect.width/5) ** 2) * 2)
triCents = genPolyTuple(4, triDist)

triColsAvoid = (
    BLUE,
    RED,
    ORANGE if triAvoidOrange else None,
    #GREEN,
    )

triCols = (BLUE,)
while any(_col in triColsAvoid for _col in triCols):
    triCols = deque(random.choice(COLORS) for _ in range(4))
        
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
disallowed_typing = {27,  #escape  #not working????!?
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

#getNewTopLeft was defined here before I moved in above the img stuff

###   The loop   ###

while True:

    #  Fill red to start   #
    if clearEveryTime:
        displaySurface.fill(RED)

    # Polygons #
    pygame.draw.polygon(displaySurface, BLUE, cPolyFromP(bigPent))
    if (freezeAllowed and not frozen) or not freezeAllowed:
        bigPent = rotatePPolyBy(bigPent, math.radians(rot))

    pygame.draw.polygon(displaySurface, ORANGE, cPolyFromP(smallPent))
    if (freezeAllowed and not frozen) or not freezeAllowed:
        smallPent = rotatePPolyBy(smallPent, -math.radians(rot))


    # Image #
    if img_clicked:
        imgRect.topleft = getNewTopLeft(img, 2)
        img_clicked = False
    
    displaySurface.blit(img, imgRect.topleft)
    

    # Circle #
    pygame.draw.circle(displaySurface, GREEN, (x, y), CIR_SIZE - CIR_BUF, 0)
    x, y = increaseCoords(x, y, dx = _dx, mode = ('bk' if cirMode == 'bk' else 'fd'))


    #tris
    if changeTriCol:
        if _frameCount % 1000 == 0:
            triCols.rotate(-1)
    pygame.draw.polygon(displaySurface, triCols[0], cPolyFromP(triL, dest = cFromP(triCents[0], dest = windowRect.center)))
    pygame.draw.polygon(displaySurface, triCols[1], cPolyFromP(triR, dest = cFromP(triCents[1], dest = windowRect.center)))
    pygame.draw.polygon(displaySurface, triCols[2], cPolyFromP(triL, dest = cFromP(triCents[2], dest = windowRect.center)))
    pygame.draw.polygon(displaySurface, triCols[3], cPolyFromP(triR, dest = cFromP(triCents[3], dest = windowRect.center)))


    if (freezeAllowed and not frozen) or not freezeAllowed:
        triCents = rotatePPolyBy(triCents, math.radians(0.1))
        triL = rotatePPolyBy(triL, 1.5*math.radians(+rot))
        triR = rotatePPolyBy(triR, 1.5*math.radians(+rot))

    # The center text #
    
    pygame.draw.rect(displaySurface, BLACK, pygame.Rect(
        centerMessageRect.left  -  5, centerMessageRect.top    -  5,
        centerMessageRect.width + 10, centerMessageRect.height + 10
        ))
    drawText(centerMessage, centerMessageRect)
    


    # _strMessage #

    #if _str == '' and anythingTyped and lastBackspace:
    #    _str = '  '

    if not img_clicked_ever:
        drawText(click_prompt, click_promptRect)
    if False in {ctrl_pressed_ever, left_arrow_pressed_ever, right_arrow_pressed_ever}:
        drawText(mvmt_prompt , mvmt_promptRect )
    
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
    if not anythingTyped or _str == '':
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
    mods = pygame.key.get_mods()
    ctrl_pressed = mods & KMOD_CTRL
    alt_pressed = mods & KMOD_ALT


    #speed
    if keys[K_LEFT] and not keys[K_RIGHT]:
        _dx = nathaniellib.main._round(0.5 * _dx_orig)
        rot = 0.5 * rot_orig

        left_arrow_pressed_ever = True
    elif not keys[K_LEFT] and keys[K_RIGHT]:
        _dx = 2 * _dx_orig
        rot = 1.75 * rot_orig

        right_arrow_pressed_ever = True
    else:
        _dx = _dx_orig
        rot = rot_orig

    if keys[K_h] and ctrl_pressed:
        pass
        #this would be 'help': reset the _ever variables all to false so all "Try ..." messages show

    if keys[K_r] and ctrl_pressed:
        pass
        #this would be 'reset': randomly choose new colors for the tris, set _str to '', maybe show the prompts again as well

    #Go backwards
    if alt_pressed:
        cirMode = 'bk'
        rot *= -1
        ctrl_pressed_ever = True
    else:
        cirMode = 'fd'
    #Quitting on 'q'
    if q_quit.lower() in {'q', 'quit'}.union(nathaniellib.main.truthy_strings_lower):
        if keys[K_q] and ctrl_pressed:
            pygame.quit()
            sys.exit()

    for event in pygame.event.get():
        #quit
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            if imgRect.collidepoint(event.pos):
                     img_clicked = True
                     img_clicked_ever = True
            else:
                if freezeAllowed:
                    if windowRect.collidepoint(event.pos):
                        frozen = True
                    
        elif event.type == MOUSEBUTTONUP:
            if freezeAllowed:
                frozen = False
            
        
        elif event.type == KEYDOWN:
            
            #typing for _strMessage
            no_disalloweds = (event.key not in disallowed_typing)
            if True:#no_disalloweds and not pygame.key.get_mods() & KMOD_CTRL: #ctrl_pressed: 
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
                #debuggin!! --->>  #print("KEYCODE: {}: Meaning:  {}".format(event.key, pygame.key.name(event.key))) ---->>>   #print(pygame.key.get_mods() & KMOD_CTRL)
