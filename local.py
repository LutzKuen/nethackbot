# WandOfDiscord
# Created by Tymewalk
# https://github.com/Tymewalk
import pexpect, inspect, traceback, asyncio, subprocess, vscreen, os, json, re
from cbot import genetic_bot
<<<<<<< HEAD
from cbot import keras_bot
import time
import os
import pandas as pd
import code
=======
import time
import os
import pandas as pd
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
import datetime

pointer_x = 0
pointer_y = 0

<<<<<<< HEAD
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

def get_reward(prev_state, next_state):
    if not next_state:
        return -10, True
    if not prev_state:
        return 1, True
    if 'You die' in next_state:
        return -1, False
    if 'You starved' in next_state:
        return -1, False
    if 'Unknown direction' in next_state:
        return -0.5, True
    if prev_state == next_state:
        return -0.1, True
    # check wether stats or level improved
    p_att = get_attributes(prev_state)
    n_att = get_attributes(next_state)
    reward = 0
    for key in ['st', 'dx', 'in', 'wi', 'ch', 'dlvl', 'hp', 'ac', 'exp', 't']:
        if key in n_att.keys() and key in p_att.keys():
            reward += n_att[key] - p_att[key]
    if abs(reward) > 0:
        return reward, True
    for c1, c2 in zip(prev_state, next_state):
        if not (c1 == c2):
            reward += 1.0/1944.0
    return reward, True
    

def run_game(bot):
    # Load the settings - we need this for the token and player name
    playername = 'sgs'
=======
def run_game(bot):
    # Load the settings - we need this for the token and player name
    playername = 'nethackplayer'
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
    
    print("Setting up VScreen... ")
    nethack_screen = vscreen.VScreen(80, 24)
    print("VScreen set up successfully.")
    
    print("Spawning NetHack... ")
<<<<<<< HEAD
    nh = pexpect.spawn("nethack", ["-u", playername])
    print("Spawned.")
    line = nh.read_nonblocking(size=999999, timeout=5).decode()
=======
    nh = pexpect.spawn("nethack", ["-u", playername, " -n"])
    print("Spawned.")
    line = nh.read_nonblocking(size=99999, timeout=5).decode()
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
    
    print("Reading screen... ", end='')
    def parse_nethack_output(output, message=False):
        global pointer_x, pointer_y
        # Strip the garbage.
        # [Xm and [XXm are ANSI formatting, we don't print those since Discord code tags don't support them.
        # [?1049h enables the alternate screen buffer. We don't care about that at all because Discord's surely not gonna use it.
        # Newlines are handled via \r.
<<<<<<< HEAD
        #stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output))
        #stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output))
        stripped = output
=======
        stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output))
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
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
<<<<<<< HEAD
                        #code.interact(banner = '', local=locals())
                        if isfloat(stripped[counter+2]) and stripped[counter+3] == 'm':
                            skip_to = counter + 4
                        if isfloat(stripped[counter+2]) and isfloat(stripped[counter+3]) and stripped[counter+4] == 'm':
                            skip_to = counter + 5
                        if stripped[counter + 2] == 'M': # this is some key redefine stuff. skip it for now
                            skip_to = counter + 2
=======
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
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
<<<<<<< HEAD
        line = nh.read_nonblocking(size=999999, timeout=5).decode()
=======
        line = nh.read_nonblocking(size=99999, timeout=5).decode()
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
        parse_nethack_output(line)
        print(nethack_screen.get_screen())
    disp_line = ''
    game_running = True
    turns = 0
    times_waited = 0
<<<<<<< HEAD
    #logfile = open('plog.log','w')
    max_waiting = 5 # at most 15 round of nothing allowed
    while game_running:
        #print(chr(27) + "[2J")
        try:
            show_current_board()
            if turns > 0:
                prev_state_ = current_state
            current_state = nethack_screen.get_screen()
            if turns > 0:
                prev_state = prev_state_
        except Exception as e:
            print('Can not show board ' + str(e))
            current_state = prev_state
            #line = None
        #logfile.write(current_state + '\n----------------------------------\n')
        if turns > 0:
            reward, game_running = get_reward(prev_state, current_state)
            bot.remember(current_state, next_key, reward)
        turns += 1
        next_key = bot.get_response(nethack_screen.get_screen())
        time.sleep(1)
        if game_running:
            nh.sendline(bot.num_to_key(next_key))
        else:
            nh.sendline('\n')
        print(bot.num_to_key(next_key))
        if turns % 32 == 0:
            bot.replay(32)
=======
    max_waiting = 5 # at most 15 round of nothing allowed
    while game_running:
        print(chr(27) + "[2J")
        try:
            #line = nh.read_nonblocking(size=9999, timeout=5).decode()
            #disp_line = line
            show_current_board()
        except Exception as e:
            print('Can not show board ' + str(e))
            game_running = False
            #line = None
        if 'You die...' in nethack_screen.get_screen():
            game_running = False
        if game_running:
            turns += 1
            next_key = bot.get_response(nethack_screen.get_screen())
            print(next_key)
            if next_key == '.':
                times_waited += 1
            else:
                times_waited = 0
            if times_waited > max_waiting:
                game_running = False
                nh.sendline('#quit')
                time.sleep(1)
                nh.sendline('y')
                time.sleep(1)
                nh.sendline('n')
                time.sleep(1)
                nh.sendline('n')
                time.sleep(1)
                nh.sendline('n')
                time.sleep(1)
                nh.sendline('\n')
            time.sleep(1)
            nh.sendline(next_key)
            bot.send_reward(1)
        else:
            bot.send_reward(-1)
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
    nh.kill(0)
    return turns # score for now 

if __name__ == '__main__':
    botname = 'mybot'
<<<<<<< HEAD
    bot = keras_bot.keras_bot()
    #bot.random_start()
    bot.random_start()
    while True:
        turns = run_game(bot)
        logfile = open('logfile.log','a')
        logfile.write('Survived for ' + str(turns) + ' turns\n')
        logfile.close()
        bot.replay(32)
        bot.save_model()
=======
    bot = genetic_bot.simplebot(name='mybot')
    #bot.random_start()
    while True:
        turns = run_game(bot)
        bot.save_bot(botname)
        bot.adjust_layers()
        turns = run_game(bot) # calc the rounds without the random layers
        logfile = open('logfile.log','a')
        logfile.write('Survived for ' + str(turns) + ' turns with ' + str(len(bot.layers)) + ' layers\n')
        logfile.close()
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
