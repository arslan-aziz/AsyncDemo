import socket
import select
import sys
import queue
import os
import io
import argparse

"""
Client connects to SINGLE server and prints diagnostics.
"""

HOST = "127.0.0.1"
PORT = ""

def parse_args():
    global PORT
    parser = argparse.ArgumentParser(description='Connect to server and receive text')
    parser.add_argument('port',metavar='port',type=int,nargs=1,
            help='Port to connect',default='sample.txt')
    args = parser.parse_args()
    PORT = args.port[0]

def run():

    inputs = []
    outputs = []
    text = ""

    print(f'Connecting to server at {HOST} on port {PORT}')
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    inputs.append(s)

    while len(inputs)>0:
        readable,writeable,exceptional = select.select(inputs,outputs,[])

        for sock in readable:
            data = sock.recv(256)
            if(not data == b''):
                print('Receiving bytes...')
                print(data)
                text += data.decode()
            else:
                print('Socket is complete')
                sock.close()
                inputs.remove(sock)
                
    
    print(text)

parse_args()
run()
