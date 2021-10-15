import cbpro, time, websocket
import json
import kraberV1
import matplotlib.pyplot as plt
# import asyncio
# import threading
import multiprocessing as mp
from multiprocessing import Manager

# from clients import WebsocketClient

# *********************************************#
# THIS IS THE REAL ONE, TEST ON SANDBOX FIRST #
# *********************************************#

authFile = open("auth.txt", "r")
authLines = authFile.readlines()

# Credentials
API_PASS = str(authLines[0])[:-1]
API_KEY = str(authLines[1])[:-1]
API_SECRET = str(authLines[2])

client = cbpro.AuthenticatedClient(
    API_KEY,
    API_SECRET,
    API_PASS
)

# Variables for set up
coin_to_use = "BTC"
message_count = 0
failure_flag = True


# Setting up websocket
def on_open(ws):
    print("socket opened")

    subscribe_message = {
        "type": "subscribe",
        "channels": [
            {"name": "ticker",
             "product_ids": [(coin_to_use) + "-USD"]}
        ]
    }
    ws.send(json.dumps(subscribe_message))


def on_message(ws, message):
    global message_count, messages_to_gather
    global price_log
    global m_avg_log
    global failure_flag

    print(message_count)

    message_data = json.loads(message)
    if (message_count == 0 and len(message_data)<=2):
        print("Confirmation message acquired")
    else:
        recent_datapoint = message_data["price"]
        # print(message)
        # print(recent_datapoint)
        price_log.append(float(str(recent_datapoint)))
        m_avg_log.append(kraberBTC.calcMovingAvg(price_log, 200))
        trend_log.append(kraberBTC.calcTrendDirection(m_avg_log, 100))
    
    if (message_count % 5 == 0 and message_count > 0):
        print(trend_log[-1])
    
    if (message_count >= messages_to_gather):
        ws.close()
    message_count += 1


def on_close(ws):
    global failure_flag, messages_to_gather

    if (message_count >= messages_to_gather):
        failure_flag = False

    if(failure_flag):
        print("socket closed due to error")
    else:
        print("socket closed after collecting all messages requested")
        print(price_log)
        print(m_avg_log)


def collect_data(ws):
    global failure_flag
    while(failure_flag):
        ws.run_forever()


def timer(p):
    for i in range(10):
        time.sleep(1)


# Initializing bot
# Other working currency is ETH right now.
kraberBTC = kraberV1.kraberBot(client, coin_to_use)

"""
for i in range(10):
    kraberBTC.addSeenPrice()
    time.sleep(3)

print(kraberBTC.seen_prices)
"""

"""
print(kraberBTC.getCurrentPrice())

print(kraberBTC.getHistoricData(1))
"""

price_log = Manager().list()
m_avg_log = Manager().list()
trend_log = Manager().list()
socket = "wss://ws-feed.pro.coinbase.com"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

messages_to_gather = -1
while messages_to_gather < 0:
    try:
        temp_message_input_count = int(input("How many messages to collect? "))
        if(temp_message_input_count > 0):
            messages_to_gather = temp_message_input_count
    except:
        print("Please input an integer!")

p1 = mp.Process(target=collect_data, args=(ws,))
p2 = mp.Process(target=timer, args=(price_log,))
# TODO Do I actually need p2?
# Only if running on two different currencies, or is that still not needed?
# Could run two different websockets at once, one for each currency and then need both processes.
# Would need to rework price_log and other shared lists to be different for each currency. Dictionary with lists in it?

p1.start()
p2.start()
p1.join()
p2.join()

plot1 = plt.figure(1)
plt.plot(price_log)
plt.plot(m_avg_log)

slope_log = []
for trend_tuple in trend_log:
    slope_log.append(trend_tuple[1])

plot2 = plt.figure(2)
plt.plot(slope_log)
# print(slope_log)

plt.show()
