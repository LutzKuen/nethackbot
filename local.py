# WandOfDiscord
# Created by Tymewalk
# https://github.com/Tymewalk
import pexpect, inspect, traceback, asyncio, subprocess, vscreen, os, json, re
from cbot import genetic_bot
from cbot import keras_bot
import time
import os
import pandas as pd
import datetime

pointer_x = 0
pointer_y = 0

def run_game(bot):
    # Load the settings - we need this for the token and player name
    playername = 'nethackplayer'
    
    print("Setting up VScreen... ")
    nethack_screen = vscreen.VScreen(80, 24)
    print("VScreen set up successfully.")
    
    print("Spawning NetHack... ")
    nh = pexpect.spawn("nethack", ["-u", playername, " -n"])
    print("Spawned.")
    line = nh.read_nonblocking(size=99999, timeout=5).decode()
    
    print("Reading screen... ", end='')
    def parse_nethack_output(output, message=False):
        global pointer_x, pointer_y
        # Strip the garbage.
        # [Xm and [XXm are ANSI formatting, we don't print those since Discord code tags don't support them.
        # [?1049h enables the alternate screen buffer. We don't care about that at all because Discord's surely not gonna use it.
        # Newlines are handled via \r.
        stripped = str(re.sub("(\[[0-9](|[0-9])m|\[\?1049h|\n)", "", output))
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
        line = nh.read_nonblocking(size=99999, timeout=5).decode()
        parse_nethack_output(line)
        print(nethack_screen.get_screen())
    disp_line = ''
    game_running = True
    turns = 0
    times_waited = 0
    max_waiting = 5 # at most 15 round of nothing allowed
    while game_running:
        #print(chr(27) + "[2J")
        try:
            #line = nh.read_nonblocking(size=9999, timeout=5).decode()
            #disp_line = line
            show_current_board()
            #pass
        except Exception as e:
            print('Can not show board ' + str(e))
            game_running = False
            #line = None
        if 'You die...' in nethack_screen.get_screen():
            game_running = False
        if game_running:
            if turns > 0:
                prev_state = current_state
            current_state = nethack_screen.get_screen()
            if turns > 0:
                if prev_state == current_state:
                    bot.remember(current_state, next_key, 0.0)
                else:
                    bot.remember(current_state, next_key, 1.0)
            turns += 1
            next_key = bot.get_response(nethack_screen.get_screen())
            time.sleep(1)
            nh.sendline(bot.num_to_key(next_key))
            print(bot.num_to_key(next_key))
            if bot.num_to_key(next_key) == '.':
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
        if not game_running:
            bot.remember(current_state, next_key, -1.0)
    nh.kill(0)
    return turns # score for now 

if __name__ == '__main__':
    botname = 'mybot'
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
