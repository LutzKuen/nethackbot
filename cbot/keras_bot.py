import numpy as np
import time
import pickle
import math
import os
import keras
from keras.models import load_model
from keras.layers import Dense
from keras import Sequential
import random
from keras.optimizers import Adam


class keras_bot(object):
    def __init__(self, name=None):
        self.insize = 1944
        cfile = open('allowedkeys.conf')
        self.turn = 0
        self.allowed_commands = []
        self.learning_rate = 0.01
        self.memory = []
        self.rewards = []
        self.gamma = 0.95
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.2
        self.epsilon_decay = 0.995
        for line in cfile.readlines():
            self.allowed_commands.append(line)
        self.allowed_commands.append('\n')
    def num_to_key(self, num):
        return self.allowed_commands[num]
    def random_start(self):
        try:
            self.model = load_model('model.keras')
        except:
            print('failed to load model')
            self.model = Sequential()
            self.model.add(Dense(1944, activation='relu'))
            #self.model.add(Dense(1944, activation='relu'))
            #self.model.add(Dense(1944, activation='relu'))
            self.model.add(Dense(len(self.allowed_commands), activation='linear'))
            self.model.compile(loss='mse',optimizer=Adam(lr=self.learning_rate))
        #self.model.load_weights('model.md5')
        #self.dqnagent = DQNAgent(self.model)
        #optimizer = Adam(lr, self.learning_rate)
        #self.dqnagent.compile(optimizer)
    
    def remember(self, state, action, reward):
        num_inputs = np.zeros(shape=(self.insize,))
        i = 0
        for ch in state:
            num_inputs[i] = float(ord(ch))
            i += 1
        num_inputs /= 255.0
        self.memory.append((num_inputs, action))
        self.rewards.append(0)
        for i in range(len(self.rewards)): # write back the discounted reward
            self.rewards[i] += reward * self.gamma**i
        
    def get_response(self, inputs): # input is 24x81 chars long
        num_inputs = np.zeros(shape=(self.insize,))
        i = 0
        # heuristic menu stuff
        if '--More--' in inputs:
            return self.allowed_commands.index('\n')
        if inputs.isspace() or inputs == '':
            return self.allowed_commands.index('\n')
        i = 0
        for ch in inputs:
            num_inputs[i] = float(ord(ch))
            i += 1
        num_inputs /= 255.0
        if np.random.rand() <= self.epsilon:
            return math.floor(np.random.rand()*len(self.allowed_commands))
        pred = self.model.predict(num_inputs.reshape(1, self.insize))
        return np.argmax(pred)
    def replay(self, batch_size):
        rewards = self.rewards - np.mean(self.rewards)
        rewards = rewards / np.std(rewards)
        print('Reward statistics: ' + str(np.mean(rewards)) + ' - ' + str(min(rewards)) + ' - ' + str(max(rewards)))
        minibatch = random.sample(list(zip(self.memory, rewards)), min(batch_size, len(self.memory)))
        for sact, reward in minibatch:
            state = sact[0]
            action = sact[1]
            target = reward
            #target = reward + self.gamma * \
            #           np.argmax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state.reshape(1, self.insize))
            target_f[0][action] = target
            self.model.fit(state.reshape(1, self.insize), target_f, epochs=1, verbose=0)
            time.sleep(1) # reduce the cpu load
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    def save_model(self):
        self.model.save('model.keras')
