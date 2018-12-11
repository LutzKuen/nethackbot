# WandOfDiscord
# Created by Tymewalk
# https://github.com/Tymewalk
import pexpect, inspect, traceback, asyncio, subprocess, vscreen, os, json, re
from cbot import keras_bot
import time
import numpy as np
import sys
import os
import pandas as pd
import code
import datetime

pointer_x = 0
pointer_y = 0

def isfloat(st):
    try:
        i = float(st)
        return True
    except:
        return False

def get_attributes(state):
    p_split = state.split(' ')
    p_att = {}
    for p_s in p_split:
        try:
            _p = p_s.split(':')
            if _p[0] == 'St':
                if '/' in _p[1]:
                    p_att['st'] = float(_p[1].split('/')[0])
                else:
                    p_att['st'] = float(_p[1])
            if _p[0] == 'Dx':
                p_att['dx'] = float(_p[1])
            if _p[0] == '$':
                p_att['cash'] = float(_p[1])
            if _p[0] == 'In':
                p_att['in'] = float(_p[1])
            if _p[0] == 'Wi':
                p_att['wi'] = float(_p[1])
            if _p[0] == 'Ch':
                p_att['ch'] = float(_p[1])
            if _p[0] == 'Dlvl':
                p_att['dlvl'] = float(_p[1])
            if _p[0] == 'HP':
                p_att['hp'] = float(_p[1].split('(')[0])
            if _p[0] == 'PW':
                p_att['pw'] = float(_p[1].split('(')[0])
            if _p[0] == 'AC':
                p_att['ac'] = float(_p[1])
            if _p[0] == 'Exp':
                p_att['exp'] = float(_p[1])
            if _p[0] == 'T':
                p_att['t'] = float(_p[1])
        except:
            pass # no worries. this is dirty stuff and it fails at times
    return p_att

def get_scouted_area(state):
    xx = 24
    yy = 81
    lst = [ord(ch) for ch in state]
    lst = np.array(lst).reshape(xx, yy)
    #print(lst)
    running = True
    while running:
        running = False
        for x in range(1,(xx-1)):
            for y in range(1,(yy-1)):
                if lst[x,y] != 32 and lst[x,y] != 64 and np.any(lst[(x-1):(x+1),(y-1):(y+1)]==64): # is not blank and is @
                    lst[x,y] = 64
                    running = True
    scouted = np.sum(lst == 64)
    #print('Scouted: ' + str(scouted))
    return scouted

                


def get_reward(prev_state, next_state):
    if not next_state:
        return -10, True
    reward = 0
    if 'You die' in next_state:
        return -100, False
    if 'You starved' in next_state:
        return -100, False
    if 'Unknown direction' in next_state:
        return -5, True
    if 'That door is closed' in prev_state and 'That door is closed' in next_state: # punish knocking twice
        reward -= 1
    if 'is killed' in next_state:# you killed something. Great success
        reward += 100
    if prev_state == next_state:
        return -1, True
    # check wether stats or level improved
    p_att = get_attributes(prev_state)
    n_att = get_attributes(next_state)
    s_p = get_scouted_area(prev_state)
    s_n = get_scouted_area(next_state)
    if s_p > 0:
        reward += abs(s_n - s_p)
    #for key in ['t']:
    #    if key in n_att.keys() and key in p_att.keys():
    #        if n_att[key] > p_att[key]:
    #            for c1, c2 in zip(prev_state[160:], next_state[100:]):
    #                if not (c1 == c2):
    #                    reward += 1
    for key in ['st', 'dx', 'in', 'wi', 'ch', 'hp', 'ac']:
        if key in n_att.keys() and key in p_att.keys():
            reward += 10*(n_att[key] - p_att[key])
    for key in ['exp', 'cash']:
        if key in n_att.keys() and key in p_att.keys():
            reward += 100*(n_att[key] - p_att[key])
    for key in ['dlvl']:
        if key in n_att.keys() and key in p_att.keys():
            reward += 10000*(n_att[key] - p_att[key])
    print('Reward ' + str(reward))
    return reward, True
    

def run_game(bot):
    # Load the settings - we need this for the token and player name
    playername = 'sgs'
    
    print("Setting up VScreen... ")
    nethack_screen = vscreen.VScreen(80, 24)
    print("VScreen set up successfully.")
    
    print("Spawning NetHack... ")
    nh = pexpect.spawn("nethack", ["-u", playername])
    print("Spawned.")
    line = nh.read_nonblocking(size=999999, timeout=5).decode()
    
    print("Reading screen... ", end='')
    def parse_nethack_output(output, message=False):
        global pointer_x, pointer_y
        # Strip the garbage.
        # [Xm and [XXm are ANSI formatting, we don't print those since Discord code tags don't support them.
        # [?1049h enables the alternate screen buffer. We don't care about that at all because Discord's surely not gonna use it.
        # Newlines are handled via \r.
        #stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output))
        #stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output))
        stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output)).replace('^[M','')
        counter = 0
        # skip_to allows us to skip instructions we've already processed.
        skip_to = 0
        for i in stripped:
            # Check - if counter >= skip_to, we've skipped the instructions
            # we've already processed and are ready to start reading new
            # instructions
            if counter >= skip_to:
                # These instructions are all ANSI escape codes
                # https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences
                try:
                    # Normally I would strip the \x1b here, but unfortunately for us, Nethack uses [ as armor.
                    # So to avoid having any conflict, we check for it.
                    if i == "" and stripped[counter + 1] == "[":
                        #code.interact(banner = '', local=locals())
                        #if isfloat(stripped[counter+2]) and stripped[counter+3] == 'm':
                            #skip_to = counter + 4
                        #if isfloat(stripped[counter+2]) and isfloat(stripped[counter+3]) and stripped[counter+4] == 'm':
                            #skip_to = counter + 5
                        #if stripped[counter + 2] == 'M': # this is some key redefine stuff. skip it for now
                        #    #nethack_screen.blit('.', pointer_x, pointer_y)
                        #    #pointer_x = pointer_x + 1
                        #    #nethack_screen.blit('.', pointer_x, pointer_y)
                        #    #pointer_x = pointer_x + 1
                        #        #print('send return')
                        #    #pointer_x += 1 # this is a green color. Skip this position on the board
                        #    skip_to = counter + 4
                        if stripped[counter + 2] == "H":
                            # [H alone means go to 0,0
                            # You'll notice it being printed when we use the status bar
                            pointer_x = 0
                            pointer_y = 0
                            skip_to = counter + 3
                        elif stripped[counter + 2] == "C":
                            # Move right
                            pointer_x += 1
                            skip_to = counter + 3
                        elif stripped[counter + 2] == "D":
                            # Move left
                            pointer_x += -1
                            skip_to = counter + 3
                        elif stripped[counter + 2] == "A":
                            # Move up
                            pointer_y += -1
                            skip_to = counter + 3
                        elif stripped[counter + 2] == "B":
                            # Move down
                            pointer_y += 1
                            skip_to = counter + 3
                        elif stripped[counter + 2] == "K":
                            # [K means clear the rest of this line
                            # It's used in the upper status bar
                            nethack_screen.blit(" "*(80 - pointer_x), pointer_x, pointer_y)
                            skip_to = counter + 3
                        elif stripped[counter + 3] == "K":
                            # However, other [nK for values of n can change what is cleared
                            if stripped[counter + 2] == "1":
                                # [1K means clear the beginning of this line
                                nethack_screen.blit(" "*pointer_x, pointer_x, pointer_y)
                                skip_to = counter + 4
                            elif stripped[counter + 2] == "2":
                                # [2K means clear all of this line.
                                nethack_screen.blit(" "*80, pointer_y)
                                skip_to = counter + 4
                        elif stripped[counter + 3] == ";":
                            # [XX;YYH tells the pointer to go to XX, YY.
                            # The different checks just figure how long those numbers are.
                            if not counter + 6 > len(stripped) - 1:
                                if stripped[counter + 6] == "H":
                                    pointer_y = int(str(stripped[counter + 2])) - 1
                                    pointer_x = int(str(stripped[counter + 4]) + str(stripped[counter + 5])) - 1
                                    skip_to = counter + 7
    
                            if not counter + 5 > len(stripped) - 1:
                                if stripped[counter + 5] == "H":
                                    pointer_y = int(str(stripped[counter + 2])) - 1
                                    pointer_x = int(str(stripped[counter + 4])) - 1
                                    skip_to = counter + 6
                        elif stripped[counter + 4] == ";":
                            # We have to check if we're not going past the end of the string. Otherwise, it's gonna skip the
                            # instruction and blit it to the screen instead.
                            if not counter + 7 > len(stripped) - 1:
                                if stripped[counter + 7] == "H":
                                    pointer_y = int(str(stripped[counter + 2]) + str(stripped[counter + 3])) - 1
                                    pointer_x = int(str(stripped[counter + 5]) + str(stripped[counter + 6])) - 1
                                    skip_to = counter + 8
                            if not counter + 6 > len(stripped) - 1:
                                if stripped[counter + 6] == "H":
                                    pointer_y = int(str(stripped[counter + 2]) + str(stripped[counter + 3])) - 1
                                    pointer_x = int(str(stripped[counter + 5])) - 1
                                    skip_to = counter + 7
                        elif stripped[counter + 3] == "J":
                            # [nJ clears part of the screen. n changes how it works.
                            if stripped[counter + 2] == "2":
                                # [2J clears the whole screen.
                                # This is the only one I've seen NetHack use
                                nethack_screen.clear()
                            skip_to = counter + 4
                        else:
                            # If none of these worked, we do nothing. This way we don't have any wrong usage.
                            #nethack_screen.blit(i, pointer_x, pointer_y)
                            #pointer_x = pointer_x + 1
                            pass
                    elif i == chr(13):
                        # 0x0d, or \r, is a carriage return
                        pointer_y = pointer_y + 1
                    elif i == "":
                        # 0x08, or \b, is a backspace
                        pointer_x = pointer_x - 1
                    else:
                        if nethack_screen.blit(i, pointer_x, pointer_y):
                            pointer_x = pointer_x + 1
                        else:
                            #print('send return')
                            nh.send('\r')
                            #time.sleep(1)
                except IndexError:
                    print("Hit end of line unexpectedly - ignoring commands")
                    #print(stripped)
                    #pass
                finally:
                    pass
            counter += 1
    
    def show_current_board():
        timeout_achieved = False
        line = None
        while not timeout_achieved:
            try:
                line = nh.read_nonblocking(size=999999, timeout=2).decode()
                parse_nethack_output(line)
            except:
                timeout_achieved = True
        if not line:
            return False
        print(chr(27) + "[2J") # clear the screen
        nh_screen = nethack_screen.get_screen()
        print(nh_screen)
        num_m = np.sum([1 for ch in nh_screen if ch == 'M']) # the capital M's come from an annoying issue with a cursor in the screen
        if num_m > 2:
            return False
        else:
            return True
    disp_line = ''
    game_running = True
    turns = 0
    logfile = open('plog.log','w')
    max_waiting = 5 # at most 15 round of nothing allowed
    while game_running:
        if show_current_board():
            if turns > 0:
                prev_state_ = current_state
            current_state = nethack_screen.get_screen()
            if turns > 0:
                prev_state = prev_state_
        else:
            current_state = prev_state
            # respawn game
            nh.kill(0)
            nethack_screen.clear()
            nh = pexpect.spawn("nethack", ["-u", playername])
            print("Spawned.")
            line = nh.read_nonblocking(size=999999, timeout=5).decode()
            #line = None
        #logfile.write(current_state + '\n----------------------------------\n')
        if turns > 0:
            reward, game_running = get_reward(prev_state, current_state)
            bot.remember(current_state, next_key, reward)
        turns += 1
        next_key = bot.get_response(nethack_screen.get_screen())
        #nethack_screen.clear()
        print('You pressed ' + bot.num_to_key(next_key) + ' ' + str(next_key))
        #logfile.write(bot.num_to_key(next_key) + '\n')
        #time.sleep(1)
        if game_running:
            nh.send(bot.num_to_key(next_key))
        else:
            nh.send('\n')
        if turns % 32 == 0:
            bot.replay(32)
            bot.save_model()
    nh.kill(0)
    logfile.close()
    return turns # score for now 

if __name__ == '__main__':
    try:
        if sys.argv[1] == 'manual':
            bot = keras_bot.keras_bot(manual = True)
        else:
            bot = keras_bot.keras_bot()
    except:
        bot = keras_bot.keras_bot()
    bot.random_start()#load or new
    while True:
        turns = run_game(bot)
        logfile = open('logfile.log','a')
        logfile.write('Survived for ' + str(turns) + ' turns\n')
        logfile.close()
        bot.replay(1000)
        bot.save_model()
