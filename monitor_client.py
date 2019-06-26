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

NUM_CLIENT = 3 
LEN_DATA = 300

UNIT_SECOND = 1000
UNIT_PERIOD = 5 * UNIT_SECOND
UNIT_B = 8
UNIT_K = 1024
MAX_THROUGHPUT = 5000

CONST_CLIENT = 10

def getTraffic():
    result = subprocess.check_output("curl -s http://127.0.0.1:8181/onos/v1/statistics/ports --user karaf:karaf", shell = True)
    return json.loads(result)

def getFlow(id):
    result = subprocess.check_output("curl -s http://127.0.0.1:8181/onos/v1/flows/" + id + " --user karaf:karaf", shell = True)
    return json.loads(result)

"""
Initialize throughput data
"""
list_data = [deque([0] * LEN_DATA, maxlen = LEN_DATA) for i in range(NUM_CLIENT)]
before_data = []

"""
Fetch information about forbidden client
"""
list_forbidden = []
with open('forbidden.json') as json_file:
    json_data = json.load(json_file)
    for client in json_data['client']:
        list_forbidden.append(client['mac'])
print("\n")
print(str(len(list_forbidden)) + " forbidden client:", list_forbidden)

"""
Setting Graph
"""
fig = plt.figure()
plt.subplots_adjust(hspace = 1)

ax = []
line = []
for i in range(NUM_CLIENT):
    ax.append(None)
    line.append(None)

    ax[i] = fig.add_subplot((NUM_CLIENT * 100) + 10 + (i + 1))
    ax[i].set_xlim(0, LEN_DATA)
    ax[i].set_ylim(0, MAX_THROUGHPUT)
    line[i], = ax[i].plot([], [], '-')

"""
Fetch initial information
"""
list_ap = {}
list_client = {}
json_data = getTraffic()
for element in json_data['statistics']:
    id = element['device']
    port = element['ports'][0]
    list_ap[id] = {'second(b)': int(port['durationSec']), 'data(b)': int(port['bytesSent'])}

print("\n")
print(str(len(list_ap)) + " AP:", list_ap)

for ap in list_ap:
    json_data = getFlow(ap)
    i = 0
    for data in json_data['flows']:
        if data['priority'] != CONST_CLIENT:
            continue
        mac = data['selector']['criteria'][1]['mac']
        
        if mac in list_forbidden:
            continue

        list_client[mac] = {'index': i, 'ap': data['deviceId'], 'packet(b)': data['packets']}
        ax[i].title.set_text("Client " + mac)
        i += 1

print("\n")
print(str(len(list_client)) + " client:", list_client)
time.sleep(5)

"""
Update function for graph
"""
def update(time):
    json_data = getTraffic()
   
    throughput = {} 

    for element in json_data['statistics']:
        id = element['device']
        port = element['ports'][0]
        list_ap[id]['second(c)'] = int(port['durationSec'])
        list_ap[id]['data(c)'] = int(port['bytesSent'])
        throughput[id] = (list_ap[id]['data(c)'] - list_ap[id]['data(b)']) * UNIT_B / ((list_ap[id]['second(c)'] - list_ap[id]['second(b)']) * UNIT_K)

        list_ap[id]['second(b)'] = list_ap[id]['second(c)']
        list_ap[id]['data(b)'] = list_ap[id]['data(c)']
        list_ap[id]['packets'] = 0

    for ap in list_ap:
        json_data = getFlow(ap)
        for data in json_data['flows']:
            if data['priority'] != CONST_CLIENT:
                continue

            mac = data['selector']['criteria'][1]['mac']

            if mac in list_forbidden:
                continue

            list_client[mac]['packet(c)'] = data['packets']
            list_client[mac]['diff'] = list_client[mac]['packet(c)'] - list_client[mac]['packet(b)']

            list_ap[ap]['packets'] += list_client[mac]['diff']
            list_client[mac]['ap'] = data['deviceId']
            list_client[mac]['packet(b)'] = list_client[mac]['packet(c)']
            list_client[mac]['diff'] = list_client[mac]['diff']

    for ap in list_ap:
        json_data = getFlow(ap)
        for data in json_data['flows']:
            if data['priority'] != CONST_CLIENT:
                continue
            mac = data['selector']['criteria'][1]['mac']
            id = data['deviceId']
            index = list_client[mac]['index']
            if list_ap[id]['packets'] == 0:
                cal = 0
            else:
                cal = throughput[id] * float(list_client[mac]['diff']) / list_ap[id]['packets']
            if cal < 0:
                cal = 0
            list_data[index].append(cal)
            print(mac, cal)
            line[index].set_data(range(0, LEN_DATA), list_data[index])

result = animation.FuncAnimation(fig, update, interval = UNIT_PERIOD)

plt.show()
