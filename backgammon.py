import sys,os,pygame,time,random
import numpy as np
from pygame.locals import *

WINDOWWIDTH = 1035
WINDOWHEIGHT = 720
COL_MID_PTS = []
COL_HEIGHT = 1./2.3*WINDOWHEIGHT
NUM_COLS = 14
COL_WIDTH = 1./float(NUM_COLS)*WINDOWWIDTH
SECTOR_START = []
PIECE_RAD = int(COL_WIDTH/2.)
BOARD_STATUS = {}
MAX_PER_COLUMN = 5
PIECE_CLICK_THRESH = PIECE_RAD * 4.5/5.
SELECTED_PIECE = {'sect':-1,'col':-1,'num':-1,'color':-1}
DARK_COLOR = (120,50,50)
LIGHT_COLOR = (120,120,180)
SELECTED_COLOR = (0,255,0)
DICE_NUMS = [0,0]
JAIL = {DARK_COLOR:{'sect':1, 'col': 6, 'num':-1}, LIGHT_COLOR:{'sect':1, 'col': 6, 'num':1}}
POSSIBLE_PIECES = []


#ordered board to to solve difference between gameplay flow and geometric flow of board
#Still notated the same way. Starts from sector 0
#USED IN:
ORDERED_BOARD = [(0,5),(0,4),(0,3),(0,2),(0,1),(0,0),
(1,5),(1,4),(1,3),(1,2),(1,1),(1,0),
(2,0),(2,1),(2,2),(2,3),(2,4),(2,5),
(3,0),(3,1),(3,2),(3,3),(3,4),(3,5)]

#TODO: implement doubles and combining dice numbers
#TODO: implement undo

def scn2xy(sect,col,num,integer = True):
    """
    sect: sector number
    col: column number in sector
    num: number piece offset in column
    Returns: base x,y coordinates of that column to place piece at
    """
    num = num % MAX_PER_COLUMN #account for overflow in column. 5 is maximum
    x = SECTOR_START[sect] + COL_WIDTH*col
    if sect == 0:
        y = PIECE_RAD + num*PIECE_RAD*2
    elif sect == 1:
        y = PIECE_RAD + num*PIECE_RAD*2
    elif sect == 2:
        y = WINDOWHEIGHT - (PIECE_RAD + num*PIECE_RAD*2)
    elif sect == 3:
        y = WINDOWHEIGHT - (PIECE_RAD +num*PIECE_RAD*2)
    elif BOARD_STATUS[BOARD_STATUS[sect][col]['color']]['home'] == 1:
        print "ERROR"
        exit()

    if integer:
        return (int(x),int(y))
    else:
        return (x,y)

def draw_piece(sect,col,num,color):
    if sect != -1:
        pygame.draw.circle(DISPLAYWINDOW,color,(scn2xy(sect,col,num)), PIECE_RAD)
        pygame.draw.circle(DISPLAYWINDOW,(0,0,0),(scn2xy(sect,col,num)), PIECE_RAD,2)

def draw_selected_piece(sect,col):
    if sect != -1:
        draw_piece(sect,col,BOARD_STATUS[sect][col]['num']-1,SELECTED_COLOR)

def draw_possible_piece(sect,col,num):

    if col == 6:
        draw_trench(SELECTED_COLOR) #assuming this information will be here
    elif sect == -1:
        return
    else:
        pygame.draw.circle(DISPLAYWINDOW,SELECTED_COLOR,(scn2xy(sect,col,num)), PIECE_RAD,4)

def draw_jail(color):
    global JAIL_COL
    x = SECTOR_START[JAIL[color]['sect']] + COL_WIDTH*JAIL[color]['col']
    y = WINDOWHEIGHT/2 + JAIL[color]['num']*PIECE_RAD
    ix = int(x)
    iy = int(y)

    pygame.draw.circle(DISPLAYWINDOW,color,(ix,iy), PIECE_RAD)
    pygame.draw.circle(DISPLAYWINDOW,(0,0,0),(ix,iy), PIECE_RAD,2)

    jailtext,jailtext_rect = make_text_objs(str(BOARD_STATUS[color]['jailed']),num_font,(0,0,0))
    jailtext_rect.center = (x,y)
    DISPLAYWINDOW.blit(jailtext,jailtext_rect)

def draw_trench(color):
    global BOARD_STATUS,SELECTED_PIECE,SELECTED_COLOR,LIGHT_COLOR,DARK_COLOR

    print SELECTED_COLOR, SELECTED_PIECE,color

    #check drawing possible piece
    if color == SELECTED_COLOR and SELECTED_PIECE['color'] != -1:
        color_selected = SELECTED_PIECE['color']
        if color_selected == LIGHT_COLOR:
            pygame.draw.polygon(DISPLAYWINDOW,SELECTED_COLOR,[(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,BOARD_STATUS[color_selected]['off']*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,(BOARD_STATUS[color_selected]['off'])*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,0+(BOARD_STATUS[color_selected]['off']+1)*20),(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,0+(BOARD_STATUS[color_selected]['off']+1)*20)],2)
        elif color_selected == DARK_COLOR:
            pygame.draw.polygon(DISPLAYWINDOW,SELECTED_COLOR,[(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,WINDOWHEIGHT - BOARD_STATUS[color_selected]['off']*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,WINDOWHEIGHT - BOARD_STATUS[color_selected]['off']*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,WINDOWHEIGHT-(BOARD_STATUS[color_selected]['off']+1)*20),(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,WINDOWHEIGHT-(BOARD_STATUS[color_selected]['off']+1)*20)],2)

    elif BOARD_STATUS[color]['off'] > 0:
        if color == LIGHT_COLOR:
            for i in range(BOARD_STATUS[color]['off']):
                pygame.draw.polygon(DISPLAYWINDOW,color,[(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,WINDOWHEIGHT - i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,WINDOWHEIGHT - i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,WINDOWHEIGHT-(i+1)*20),(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,WINDOWHEIGHT-(i+1)*20)])
                pygame.draw.polygon(DISPLAYWINDOW,(0,0,0),[(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,WINDOWHEIGHT - i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,WINDOWHEIGHT - i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,WINDOWHEIGHT-(i+1)*20),(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,WINDOWHEIGHT-(i+1)*20)],2)

        elif color == DARK_COLOR:
            for i in range(BOARD_STATUS[color]['off']):
                pygame.draw.polygon(DISPLAYWINDOW,color,[(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,0+(i+1)*20),(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,0+(i+1)*20)])
                pygame.draw.polygon(DISPLAYWINDOW,(0,0,0),[(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,i*20),(COL_MID_PTS[NUM_COLS-1]+COL_WIDTH/2,0+(i+1)*20),(COL_MID_PTS[NUM_COLS-1]-COL_WIDTH/2,0+(i+1)*20)],2)

def toggle_piece(sect,col):
    global SELECTED_PIECE,POSSIBLE_PIECES
    #if no selected piece, select this piece
    if SELECTED_PIECE['sect'] == -1:
        print BOARD_STATUS[sect][col]['num']
        SELECTED_PIECE = {'sect':sect,'col':col,'num':BOARD_STATUS[sect][col]['num'],'color':BOARD_STATUS[sect][col]['color']}

        #show possible moves, if there are any
        find_moves()
        draw_board()

    #this piece is already selected, so deselect it
    elif SELECTED_PIECE['sect'] == sect and SELECTED_PIECE['col'] == col and SELECTED_PIECE['num'] == BOARD_STATUS[sect][col]['num']:
        SELECTED_PIECE = {'sect':-1,'col':-1,'num':-1,'color': -1}
        POSSIBLE_PIECES = []
        draw_board()
    #there is already another piece selected, so do nothing
    else:
        pass

    pygame.display.flip()

def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def move_selected(sect,col): #ASSUME SELECTED PIECE IS BEING MOVED
    global SELECTED_PIECE, POSSIBLE_PIECES,BOARD_STATUS
    old_sect = SELECTED_PIECE['sect']
    old_col = SELECTED_PIECE['col']
    old_color = SELECTED_PIECE['color']

    #whether we're kicking out opponent piece or not, we remove the selected piece
    BOARD_STATUS[old_sect][old_col]['num'] -= 1

    #if moving to self-occupied or empty space
    if BOARD_STATUS[sect][col]['color'] == -1 or BOARD_STATUS[sect][col]['color'] == old_color:
        BOARD_STATUS[sect][col]['num'] += 1
        BOARD_STATUS[sect][col]['color'] = old_color

    elif BOARD_STATUS[sect][col]['color'] != -1 and BOARD_STATUS[sect][col]['color'] != old_color:
        BOARD_STATUS[BOARD_STATUS[sect][col]['color']]['jailed'] += 1
        BOARD_STATUS[sect][col]['color'] = old_color

    #update globals
    SELECTED_PIECE = {'sect':-1,'col':-1,'num':-1,'color':-1}
    POSSIBLE_PIECES = []
    draw_board()

def find_moves():
    global SELECTED_PIECE,POSSIBLE_PIECES
    print "FINDING MOVES\n"
    sect = SELECTED_PIECE['sect']
    col = SELECTED_PIECE['col']
    curr_color = BOARD_STATUS[sect][col]['color']
    new_sect0, new_col0 = shift_by(sect,col,DICE_NUMS[0],curr_color)
    new_sect1, new_col1 = shift_by(sect,col,DICE_NUMS[1],curr_color)
    new_num0 = BOARD_STATUS[new_sect0][new_col0]['num']
    new_num1 = BOARD_STATUS[new_sect1][new_col1]['num']
    POSSIBLE_PIECES = []
    #check first dice roll
    if BOARD_STATUS[new_sect0][new_col0]['color'] == -1 or BOARD_STATUS[new_sect0][new_col0]['color'] == curr_color or new_num0 == 1:
        if new_num0 == 1 and BOARD_STATUS[new_sect0][new_col0]['color'] != curr_color: #if we're bouncing a piece
            POSSIBLE_PIECES += [{'sect':new_sect0,'col':new_col0,'num':0}]
        else:
            POSSIBLE_PIECES += [{'sect':new_sect0,'col':new_col0,'num':new_num0}]

    #check second dice roll
    if BOARD_STATUS[new_sect1][new_col1]['color'] == -1 or BOARD_STATUS[new_sect1][new_col1]['color'] == curr_color or new_num1 == 1:
        if new_num1 == 1 and BOARD_STATUS[new_sect1][new_col1]['color'] != curr_color: #if we're bouncing a piece
            POSSIBLE_PIECES += [{'sect':new_sect1,'col':new_col1,'num':0}]
        else:
            POSSIBLE_PIECES += [{'sect':new_sect1,'col':new_col1,'num':new_num1}]

    if BOARD_STATUS[curr_color]['home'] == 1 or BOARD_STATUS[curr_color]['off'] > 0: #then we're maybe drawing a trench possible
        dice_roll = max(DICE_NUMS)
        print SELECTED_PIECE,col, dice_roll
        if (5-col) < dice_roll: #translate index space
            print "FOUND ONE"
            POSSIBLE_PIECES += [{'sect':-1,'col':6,'num': -1, 'color': curr_color}]

def shift_by(sect,col,shift,color): #DOESNT WORK WITH TAKING OFF!!!! OR DOUBLES!

    if color == LIGHT_COLOR:
        order = []
        for i in range(len(ORDERED_BOARD)):
            order += [ORDERED_BOARD[len(ORDERED_BOARD)-1-i]]
    else:
        order = ORDERED_BOARD

    curr_idx = order.index((sect,col))
    if curr_idx + shift >= len(order):
        return order[len(order)-1]
    else:
        return order[curr_idx+shift]

def check_click(pos): #better way to do this would be to translate click to board position and check if there's a piece
    print "CHECKING CLICK"
    #Check click on existing piece
    for sect in range(4):
        for col in range(6):
            for num in range(BOARD_STATUS[sect][col]['num']):
                true_pos = scn2xy(sect,col,num)
                if pos[0] > true_pos[0] - PIECE_CLICK_THRESH and pos[0] < true_pos[0] + PIECE_CLICK_THRESH:
                    if pos[1] > true_pos[1] - PIECE_CLICK_THRESH and pos[1] < true_pos[1] + PIECE_CLICK_THRESH:
                        toggle_piece(sect,col)

    #Check click on possible piece
    print POSSIBLE_PIECES
    for i in range(len(POSSIBLE_PIECES)):
        sect = POSSIBLE_PIECES[i]['sect']
        col = POSSIBLE_PIECES[i]['col']
        num = POSSIBLE_PIECES[i]['num']
        if POSSIBLE_PIECES[i]['col'] == 6:
            continue
        true_pos = scn2xy(sect,col,num)
        if pos[0] > true_pos[0] - PIECE_CLICK_THRESH and pos[0] < true_pos[0] + PIECE_CLICK_THRESH:
            if pos[1] > true_pos[1] - PIECE_CLICK_THRESH and pos[1] < true_pos[1] + PIECE_CLICK_THRESH:
                move_selected(sect,col) #assuming that the piece being moved is the SELECTED PIECE
                break

    #Check click on Roll
    if pos[0] < COL_MID_PTS[NUM_COLS/2-1] + COL_WIDTH/2 and pos[0] > COL_MID_PTS[NUM_COLS/2-1] - COL_WIDTH/2:
        if pos[1] > 0 and pos [1] < int(PIECE_RAD):
            roll_dice()
            draw_board()

def roll_dice():
    print "ROLLING"
    global DICE_NUMS
    #hack to get the numbers to disappear
    DICE_NUMS = [0,0]
    draw_board()
    DICE_NUMS[0] = random.randint(1,6)
    DICE_NUMS[1] = random.randint(1,6)
    time.sleep(1)

def draw_roll():
    print "DRAWING ROLL"
    global DISPLAYWINDOW
    die_1surf,rect_1 = make_text_objs(str(DICE_NUMS[0]),roll_font,(255,255,255))
    die_2surf,rect_2 = make_text_objs(str(DICE_NUMS[1]),roll_font,(255,255,255))
    rect_1.center = (COL_MID_PTS[NUM_COLS/2-1],PIECE_RAD)
    rect_2.center = (COL_MID_PTS[NUM_COLS/2-1],int(PIECE_RAD*3./2.))
    DISPLAYWINDOW.blit(die_1surf,rect_1)
    DISPLAYWINDOW.blit(die_2surf,rect_2)

def draw_board():
    global DISPLAYWINDOW,BOARD_STATUS,COL_MID_PTS,COL_WIDTH,COL_HEIGHT,SECTOR_START,DICE_NUMS,num_font,roll_font,SELECTED_PIECE,SELECTED_COLOR

    #blank out the board behind - sorta hacky
    DISPLAYWINDOW.fill((255,255,120))

    #Create board
    for i in range(NUM_COLS):
        COL_MID_PTS += [COL_WIDTH/2 + i*COL_WIDTH]
        if i == NUM_COLS-1:
            #draw endzones and mid-line
            pygame.draw.polygon(DISPLAYWINDOW,(255,255,255),[(COL_MID_PTS[i] - COL_WIDTH/2,WINDOWHEIGHT),(COL_MID_PTS[i]+COL_WIDTH/2,WINDOWHEIGHT), (COL_MID_PTS[i] + COL_WIDTH/2,0),(COL_MID_PTS[i] - COL_WIDTH/2,0)])
        elif i == NUM_COLS/2 - 1:
            pygame.draw.polygon(DISPLAYWINDOW,(0,0,0),[(COL_MID_PTS[i] - COL_WIDTH/2,WINDOWHEIGHT),(COL_MID_PTS[i]+COL_WIDTH/2,WINDOWHEIGHT), (COL_MID_PTS[i] + COL_WIDTH/2,0),(COL_MID_PTS[i] - COL_WIDTH/2,0)])
            pygame.draw.polygon(DISPLAYWINDOW,(255,255,255),[(COL_MID_PTS[i] - COL_WIDTH/2,WINDOWHEIGHT),(COL_MID_PTS[i]+COL_WIDTH/2,WINDOWHEIGHT), (COL_MID_PTS[i] + COL_WIDTH/2,0),(COL_MID_PTS[i] - COL_WIDTH/2,0)],2)
        else:
            pygame.draw.polygon(DISPLAYWINDOW,((i%2)*140 + 80,(i%2)*140 + 80,(i%2)*140 + 80),[(COL_MID_PTS[i] - COL_WIDTH/2,WINDOWHEIGHT),(COL_MID_PTS[i],WINDOWHEIGHT - COL_HEIGHT), (COL_MID_PTS[i] + COL_WIDTH/2,WINDOWHEIGHT)], 0)
            pygame.draw.polygon(DISPLAYWINDOW,(((i+1)%2)*140 + 80,((i+1)%2)*140 + 80,((i+1)%2)*140 + 80),[(COL_MID_PTS[i] - COL_WIDTH/2,0),(COL_MID_PTS[i],COL_HEIGHT), (COL_MID_PTS[i] + COL_WIDTH/2,0)], 0)

    SECTOR_START = [COL_MID_PTS[NUM_COLS/2], COL_MID_PTS[0], COL_MID_PTS[0], COL_MID_PTS[NUM_COLS/2]]

    #Update home global. It will be changed if needed in the loop below
    BOARD_STATUS[DARK_COLOR]['home'] = 1
    BOARD_STATUS[LIGHT_COLOR]['home'] = 1

    # Draw pieces
    for sect in range(4):
        for col in range(6):
            for num in range(BOARD_STATUS[sect][col]['num']):
                draw_piece(sect,col,num,BOARD_STATUS[sect][col]['color'])
                if sect == 2 or sect == 1:
                    BOARD_STATUS[BOARD_STATUS[sect][col]['color']]['home'] = 0
                elif sect == 3 and BOARD_STATUS[sect][col]['color'] == LIGHT_COLOR:
                    BOARD_STATUS[BOARD_STATUS[sect][col]['color']]['home'] = 0
                elif sect == 0 and BOARD_STATUS[sect][col]['color'] == DARK_COLOR:
                    BOARD_STATUS[BOARD_STATUS[sect][col]['color']]['home'] = 0
                if num >= MAX_PER_COLUMN: #TODO: change this 2 to variable based on number there
                    numtext,numtext_rect = make_text_objs('2',num_font,(0,0,0))
                    numtext_rect.center = scn2xy(sect,col,num)
                    DISPLAYWINDOW.blit(numtext,numtext_rect)

    draw_selected_piece(SELECTED_PIECE['sect'],SELECTED_PIECE['col'])

    print POSSIBLE_PIECES
    for i in range(len(POSSIBLE_PIECES)):
        print POSSIBLE_PIECES
        draw_possible_piece(POSSIBLE_PIECES[i]['sect'],POSSIBLE_PIECES[i]['col'],POSSIBLE_PIECES[i]['num'])

    #draw dice roll text
    rolltext,rolltext_rect = make_text_objs('ROLL!', roll_font, (255,255,255))
    rolltext_rect.center = (COL_MID_PTS[NUM_COLS/2 - 1], PIECE_RAD/2)
    DISPLAYWINDOW.blit(rolltext,rolltext_rect)

    #draw dice roll numbers if applicable
    if DICE_NUMS != [0,0]:
        draw_roll()

    if BOARD_STATUS[DARK_COLOR]['jailed'] > 0:
        draw_jail(DARK_COLOR)

    if BOARD_STATUS[LIGHT_COLOR]['jailed'] > 0:
        draw_jail(LIGHT_COLOR)

    pygame.display.flip()

def main():
    global DISPLAYWINDOW, num_font, roll_font, COL_MID_PTS, SECTOR_START
    pygame.init()
    DISPLAYWINDOW = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    num_font = pygame.font.Font('freesansbold.ttf',40)
    roll_font = pygame.font.Font('freesansbold.ttf',18)

    #initialize board status
    BOARD_STATUS[DARK_COLOR] = {'jailed':0, 'off':0, 'home':0}
    BOARD_STATUS[LIGHT_COLOR] = {'jailed':0, 'off':0, 'home':0}
    BOARD_STATUS[0] = {
    0:{'num': 5,'color': LIGHT_COLOR},
    1:{'num': 0,'color': -1},
    2:{'num': 0,'color': -1},
    3:{'num': 0,'color': -1},
    4:{'num': 0, 'color': -1},
    5:{'num': 2, 'color': DARK_COLOR}}
    BOARD_STATUS[1] = {
    0:{'num': 5,'color': DARK_COLOR},
    1:{'num': 0,'color': -1},
    2:{'num': 0,'color': -1},
    3:{'num': 0,'color': -1},
    4:{'num': 3,'color': LIGHT_COLOR},
    5:{'num': 0,'color': -1}}
    BOARD_STATUS[2] = {
    0:{'num': 5,'color': LIGHT_COLOR},
    1:{'num': 0,'color': -1,},
    2:{'num': 0,'color': -1},
    3:{'num': 0,'color': -1},
    4:{'num': 3,'color': DARK_COLOR},
    5:{'num': 0,'color': -1}}
    BOARD_STATUS[3] = {
    0:{'num': 5,'color': DARK_COLOR},
    1:{'num': 0,'color': -1},
    2:{'num': 0,'color': -1},
    3:{'num': 0,'color': -1},
    4:{'num': 0,'color': -1},
    5:{'num': 2, 'color': LIGHT_COLOR}}

    draw_board()

    #Run game on loop
    while True:
        run_game()

def run_game():
    for event in pygame.event.get():
        if event.type == (KEYDOWN):
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            check_click(event.pos)
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

main()
