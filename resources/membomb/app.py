#!/usr/bin/env python

from __future__ import print_function
import os
import time
import signal
import psutil

run = True

def handler_stop_signals(signum, frame):
    global run
    run = False

    if signum == 15:
        print('Received SIGTERM, shutting down!')
    else:
        print('Received SIGINT, shutting down!')

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

size = int(os.getenv('START_SIZE', '0')) * 1024 ** 2
size_incr = int(os.getenv('SIZE_INCR', '200')) * 1024 ** 2

if size < 0:
    size += psutil.virtual_memory().available
    if size < 0:
        size = 0

buffers = [bytearray(size)]

while run:
    size += size_incr
    buffers.append(bytearray(size_incr))
    print("Allocated %d MiB, available memory: %d MiB" % (size / 1024 ** 2, psutil.virtual_memory().available / 1024 ** 2))
    time.sleep(1)

#size = psutil.virtual_memory().available - 2048 * 1024 ** 2
#print("Allocating %d MiB" % (size / 1024 ** 2))
#buffer = bytearray(size)

#while run:
#    time.sleep(1)
