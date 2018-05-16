#!/usr/bin/env python

from __future__ import print_function
import os
import sys
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
size_incr = int(os.getenv('SIZE_INCR', '100')) * 1024 ** 2

memory_stat = {}
with open('/sys/fs/cgroup/memory/memory.stat') as file:
    for line in file:
        key, value = line.split(' ')
        memory_stat[key] = int(value)

reserved = max(psutil.virtual_memory().total - memory_stat['hierarchical_memory_limit'], 0)
if reserved == 0:
    print("No reserved memory detected. Assuming 2 GiB!")
    reserved = 2 * 1024 ** 3

if size == 0:
    size = psutil.virtual_memory().available
elif size < 0:
    size = psutil.virtual_memory().available - reserved

buffers = [bytearray(size)]

while run:
    print("Allocated %d MiB, available memory: %d MiB, reserved memory: %d MiB" % (size / 1024 ** 2, psutil.virtual_memory().available / 1024 ** 2, reserved / 1024 ** 2))
    time.sleep(1)
    size += size_incr
    buffers.append(bytearray(size_incr))


#size = psutil.virtual_memory().available - 2048 * 1024 ** 2
#print("Allocating %d MiB" % (size / 1024 ** 2))
#buffer = bytearray(size)

#while run:
#    time.sleep(1)
