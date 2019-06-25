"""
Reference: https://gongnorina.tistory.com/81
"""
import random
import time
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_CLIENT = 3
LEN_DATA = 20
UNIT_SECOND = 1000
UNIT_PERIOD = 0.5 * UNIT_SECOND

data = [deque([0] * LEN_DATA, maxlen = LEN_DATA) for i in range(NUM_CLIENT)]

def update(fn, l2d):
    data[0].append(random.random())
    l2d.set_data(range(0, LEN_DATA), data[0])

fig = plt.figure()
ax = plt.axes(xlim = (0, LEN_DATA), ylim = (0, 1))
l1, = ax.plot([], [])
ani = animation.FuncAnimation(fig, update, fargs=(l1,), interval = UNIT_PERIOD)

plt.show()
