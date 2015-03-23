#! /usr/bin/env python3

import random
import sys

import zmq

context = zmq.Context()

print("Conecting to log aggregator server...")
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5555")

# possible log messages for randomly constructing
log_messages = ["successful login",
                "unsuccessful login",
                "logout",
                "posted status",
                "changed profile"]

# get client ID number using sys args
client_id = sys.argv[1] if len(sys.argv) > 1 else random.randint(10000,100000) 

for request in range(100000):
    # Construct Log Message
    log_message = "Server {} : User {} {}".format(client_id,
                                                  random.randint(0,1000),
                                                  random.choice(log_messages))
    # Send Log Message
    print("Server {} sending log {} ...".format(client_id, request))
    sender.send(log_message.encode('utf-8'))

