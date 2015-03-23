# Log Aggregator

A log aggregator written in python3 with zeroMQ.

Uses the zeromq built-in pipeline patter.
Clients "push" log messages to aggregator.
Aggregator "pulls" in messages.

After pulling in messages, aggregator writes to a log file in local logs/ directory.
Logs are rotated over time and compressed.

Log messages are currently timestamped on write to file.

## Dependencies

- python3
- zeroMQ
- tested on Linux

## Installation

    $ git clone https://github.com/hwchen/log-agg-py.git
    $ pip3 install pyzmq

## Run the program

The server and client currently listen on port 5555.
(hardcoded on client, default with CLI option for server)

Start the server (aggregator):

    $ cd log-agg-py
    $ python3 server.py

Start some clients for testing (numbers are arbitrary ID#):

    $ python3 client.py 12345 & python3 client.py 54321 & python3 client.py 23456

Stdout should show messages that the clients are sending logs, and that the server is receiving logs.

Logs are rolled over and compressed. Log files can be found in the logs/ directory.

Rollover time is currently set at 10 seconds so it's easy to see the functionality.

