import numpy as np
import time
import pickle
import math
import os
import keras
from keras.models import load_model
from keras.layers import Dense, LSTM
from keras import Sequential
import random
from keras.optimizers import Adam


class keras_bot(object):
    def __init__(self, name=None, manual=False):
        self.insize = 1944
        self.manual = manual
        cfile = open('allowedkeys.conf')
        self.turn = 0
        self.allowed_commands = []
        self.learning_rate = 0.001
        try:
            self.memory = pickle.load(open('../model.memory','rb'))
            self.rewards = pickle.load(open('../model.rewards','rb'))
        except:
            self.memory = []
            self.rewards = []
        self.gamma = 0.95
        self.epsilon = 0.5  # exploration rate
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        for line in cfile.readlines():
            if not '#' in line and not 'Elbereth' in line:
                self.allowed_commands.append(line.replace('\n',''))
            else:
                self.allowed_commands.append(line)
    def num_to_key(self, num):
        if num == -1:
            return '\n'
        return self.allowed_commands[num]
    def random_start(self):
        try:
            self.model = load_model('../model.keras')
        except:
            print('failed to load model')
            self.model = Sequential()
            self.model.add(Dense(1944, activation='relu'))
            #self.model.add(LSTM(1944))
            self.model.add(Dense(1944, activation='relu'))
            #self.model.add(Dense(1944, activation='relu'))
            self.model.add(Dense(len(self.allowed_commands), activation='linear'))
            self.model.compile(loss='categorical_crossentropy',optimizer=Adam(lr=self.learning_rate))
        #self.model.load_weights('model.md5')
        #self.dqnagent = DQNAgent(self.model)
        #optimizer = Adam(lr, self.learning_rate)
        #self.dqnagent.compile(optimizer)
    
    def remember(self, state, action, reward):
        if action < 0:
            return
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
            return -1
        if inputs.isspace() or inputs == '':
            return -1
        if self.manual:
            cin = input(':')
            if cin == 'auto':
                self.manual = False
            else:
                while not cin in self.allowed_commands:
                    print('Key not allowed')
                    cin = input(':')
                for i, key in enumerate(self.allowed_commands):
                    if key == cin:
                        #print(cin + ' ' + key + ' ' + str(i))
                        ckey = i
                        break
                return ckey
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
        states = np.zeros(shape=(len(minibatch), self.insize))
        rewards = np.zeros(shape=(len(minibatch), len(self.allowed_commands)))
        i = 0
        for sact, reward in minibatch:
            state = sact[0]
            action = sact[1]
            target = reward
            #target = reward + self.gamma * \
            #           np.argmax(self.model.predict(next_state)[0])
            rewards[i,:] = self.model.predict(state.reshape(1, self.insize))
            states[i,:] = state
            #rewards.append(target_f)
            #target_f[0][action] = target
            rewards[i, action] = reward
            i += 1
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.model.fit(states, rewards, epochs=10, verbose=1)
        #time.sleep(2) # reduce the cpu load
    def save_model(self):
        self.model.save('../model.keras')
        if len(self.rewards) > 1000:
            pickle.dump(self.memory[-1000:], open('../model.memory','wb'))
            pickle.dump(self.rewards[-1000:], open('../model.rewards','wb'))
        else:
            pickle.dump(self.memory, open('../model.memory','wb'))
            pickle.dump(self.rewards, open('../model.rewards','wb'))
