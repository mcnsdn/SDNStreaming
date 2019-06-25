"""
Reference:
https://gongnorina.tistory.com/81
https://stackoverflow.com/questions/37111571/passing-arguments-in-animation-funcanimation/37121201
"""
import random
import time
import subprocess
import json

from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_CLIENT = 2
LEN_DATA = 300
UNIT_SECOND = 1000
UNIT_PERIOD = 5 * UNIT_SECOND
UNIT_B = 8
UNIT_K = 1024

def useAPI():
    result = subprocess.check_output("curl http://127.0.0.1:8181/onos/v1/statistics/ports --user karaf:karaf", shell = True)
    return json.loads(result)



list_data = [deque([0] * LEN_DATA, maxlen = LEN_DATA) for i in range(NUM_CLIENT)]
before_data = []

fig = plt.figure()
plt.subplots_adjust(hspace = 1)

ax = []
line = []
for i in range(NUM_CLIENT):
    ax.append(None)
    line.append(None)

    ax[i] = fig.add_subplot((NUM_CLIENT * 100) + 10 + (i + 1))
    ax[i].set_xlim(0, LEN_DATA)
    ax[i].set_ylim(0, 1)
    ax[i].title.set_text("Client " + str(i + 1))
    line[i], = ax[i].plot([], [], '-')

json_data = useAPI()
for element in json_data['statistics']:
    for ports in element['ports']:
        before_data.append((int(ports['durationSec']),int(ports['bytesSent'])))
time.sleep(5)

def update(time):
    json_data = useAPI()
   
    temp = []
    temp.append(0)
    temp.append(0)
    current = []
    current.append(0)
    current.append(0)

    i = 0
    for element in json_data['statistics']:
        for ports in element['ports']:
            current[0] = int(ports['durationSec'])
            current[1] = int(ports['bytesSent'])
            temp[i] = (current[1] - before_data[i][1]) * UNIT_B / ((current[0] - before_data[i][0]) * UNIT_K)
            before_data[i] = (current[0], current[1])
        i += 1

    for i in range(NUM_CLIENT):
        list_data[i].append(temp[i])
        print(temp[i])
        line[i].set_data(range(0, LEN_DATA), list_data[i])

result = animation.FuncAnimation(fig, update, interval = UNIT_PERIOD)

plt.show()
