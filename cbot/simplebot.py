import numpy as np
import math

class simplebot(object):
    def __init__(self):
        cfile = open('allowedkeys.conf')
        
        self.allowed_commands = []
        
        for line in cfile.readlines():
            self.allowed_commands.append(line)
    def get_response(self, inputs): # input is 24x81 chars long
        # heuristic menu stuff
        if '--More--' in inputs:
            return '\n'
        if 'Shall I pick ' in inputs:
            return 'y'
        if inputs.isspace() or inputs == '':
            return '\n'
        rint = math.floor(np.random.rand()*len(self.allowed_commands))
        print(self.allowed_commands[rint])
        return self.allowed_commands[rint]
