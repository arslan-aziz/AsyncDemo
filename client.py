import socket
import select
import sys
import queue
import os
import io


HOST = "127.0.0.1"
PORT = ""

def run():

    inputs = []
    outputs = []
    text = dict()

    for p in PORT:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        inputs.append(s)
        text.update({s:""})
    
    while True:
        readable,writeable,exceptional = select.select(inputs,outputs,[])

        for sock in readable:
            data = sock.recv(1024)
            if(not data == None):
                text[sock] += sock.recv(1024)
            else:
                print >>sys.stderr, 'socket is complete'
                sock.close()


if __name__ == "__main__":
    run()