"""
Reference:
https://gongnorina.tistory.com/81
https://stackoverflow.com/questions/37111571/passing-arguments-in-animation-funcanimation/37121201
"""
import random
import time
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_CLIENT = 3
LEN_DATA = 300
UNIT_SECOND = 1000
UNIT_PERIOD = 0.5 * UNIT_SECOND

data = [deque([0] * LEN_DATA, maxlen = LEN_DATA) for i in range(NUM_CLIENT)]

fig = plt.figure()
plt.subplots_adjust(hspace = 1)

ax = []
line = []
for i in range(NUM_CLIENT):
    ax.append(None)
    line.append(None)

    ax[i] = fig.add_subplot(310 + (i + 1))
    ax[i].set_xlim(0, LEN_DATA)
    ax[i].set_ylim(0, 1)
    ax[i].title.set_text("Client " + str(i + 1))
    line[i], = ax[i].plot([], [], '-')

def update(time):
    for i in range(NUM_CLIENT):
        data[i].append(random.random())
        line[i].set_data(range(0, LEN_DATA), data[i])

result = animation.FuncAnimation(fig, update, interval = UNIT_PERIOD)

plt.show()
