import numpy as np
import pickle
import math
import os


class simplebot(object):
    def __init__(self, name=None):
        self.layers = []
        if name:
            try:
                filename = 'bot_save/' + name
                self.layers = pickle.load(open(filename,'rb'))
                for layer in self.layers:
                    layer[5] = -1
            except:
                print('Could not load previous')
        
        self.insize = 1944
        cfile = open('allowedkeys.conf')
        self.turn = 0
        self.allowed_commands = []
        
        for line in cfile.readlines():
            self.allowed_commands.append(line)
    def random_start(self):
        # add a random mult layer
        for i in range(10): # make 10 random rules
<<<<<<< HEAD
            #nr1 = np.array(np.ones(shape=(self.insize,))*0).astype('int')
            nr1 = np.array(np.random.rand(self.insize)*255).astype('int')
            #nr2 = np.array(np.ones(shape=(self.insize,))*255).astype('int')
            nr2 = np.array(np.random.rand(self.insize)*255).astype('int')
            result = 'y'#self.allowed_commands[math.floor(np.random.rand()*len(self.allowed_commands))]
=======
            nr1 = np.array(np.random.rand(self.insize)*255).astype('int')
            nr2 = np.array(np.random.rand(self.insize)*255).astype('int')
            result = self.allowed_commands[math.floor(np.random.rand()*len(self.allowed_commands))]
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
            self.layers.append((nr1, nr2, result, 0, 0, -1))
        self.layers = sorted(self.layers, key=lambda x: x[3])
    def adjust_layers(self):
        self.layers = sorted(self.layers, key=lambda x: x[3])
        done = False
        while not done and len(self.layers) > 0:
            if (self.layers[0][3] == 0):
                self.layers.pop(0)
            else:
                done = True
            for i, layer in enumerate(self.layers):
                if layer[4] < 0:
                    self.layers.pop(i)
                    done = False
                    break
    def send_reward(self, reward):
<<<<<<< HEAD
        #print('Received reward ' + str(reward))
        new_layers = []
        for i, layer in enumerate(self.layers):
            if layer[5] >= 0:
                distance = float(self.turn - layer[5])
                new_reward = layer[4] + float(reward)/distance
                new_layer = [layer[0], layer[1], layer[2], layer[3], new_reward, layer[5]]
                #print(new_layer[4])
                new_layers.append(new_layer)
            else:
                #print(layer[5])
                new_layers.append(layer)
        self.layers = new_layers
=======
        for layer in self.layers:
            if layer[5] >= 0:
                distance = float(self.turn - layer[5])
                layer[4] += float(reward)/distance
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
    def get_response(self, inputs): # input is 24x81 chars long
        num_inputs = np.zeros(shape=(self.insize,))
        i = 0
        # heuristic menu stuff
        if '--More--' in inputs:
            return '\n'
        if 'Shall I pick ' in inputs:
            return 'y'
        if inputs.isspace() or inputs == '':
            return '\n'
<<<<<<< HEAD
        shift_idx = 0
        for ch in inputs:
            num_inputs[i] = ord(ch)
            if num_inputs[i] == 64:
                shift_idx = i
            i += 1
        #print('Shifting by ' + str(shift_idx))
        num_inputs = np.roll(num_inputs, -shift_idx)
        for i, layer in enumerate(self.layers):
            if np.all(layer[0] <= num_inputs) and np.all(layer[1] >= num_inputs):
                #print('Layer activated!!')
                new_layer = [layer[0], layer[1], layer[2], layer[3]+1, layer[4], self.turn]
                self.layers.pop(i)
                self.layers.append(new_layer)
=======
        for ch in inputs:
            num_inputs[i] = ord(ch)
            i += 1
        for layer in self.layers:
            if np.all(layer[0] <= num_inputs) and np.all(layer[1] >= num_inputs):
                layer[3] += 1
                layer[5] = self.turn
>>>>>>> b82aa04ee6351e51476e058fc28cc4db0f54176d
                self.turn += 1
                return layer[2]
        return '.'
    def save_bot(self, name):
        filename = 'bot_save/' + name + '.tmp'
        filename2 = 'bot_save/' + name
        pickle.dump(self.layers, open(filename,'wb'))
        os.rename(filename, filename2)
