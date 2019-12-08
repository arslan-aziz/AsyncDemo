import socket
import select
import sys
import queue
import os
import io

HOST = '127.0.0.1'
PORT = 0
BYTES = 0
FILE = ""
TOTBYTES = os.stat(FILE).st_size

#parse command line arguments
def parse_args():
    pass


def run():
    sListen = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print >>sys.stderr, f'starting up Text server on {HOST} port {PORT}'
    sListen.bind(HOST,PORT)
    sListen.listen(5)

    #streams from which we read
    inputs = [sListen]
    #streams to which we write
    outputs = []
    fileStreams = dict()
    queues = dict()
    sentBytes = dict()

    def EOF(s):
        if(sentBytes[s] >= TOTBYTES):
            return True
        else:
            return False

    while True:
        #block until I/O available
        readable, writeable, exceptional = select.select(inputs,outputs,[])
        #Handle inputs
        for s in readable:
            #if listening server is "readable", then new connection is available
            if s is sListen:
                conn, addr = s.accept()
                print >>sys.stderr, f'new connection from {addr}'
                conn.setblocking(0)
                outputs.append(conn)
                #create queue for this connection
                queues.update({conn:queue.Queue()})
                #create file stream for this connection
                fileStreams.update({conn:io.BytesIO(FILE)})
                sentBytes.update({conn:0})
                #add file stream to inputs
                inputs.append(fileStreams[conn])
            else:
                queues[s].put(s.recv(BYTES))

        for s in writeable:
            #if something is in the queue, send it
            if not queues[s].empty():
                s.send(queues[s].pop())
                sentBytes[s] += BYTES
            #if the queue is empty and we've sent the entire file, send empty bytes to signal client to close conn
            elif queues[s].empty() and EOF(s):
                s.send()
                queues[conn].pop()
                fileStreams[conn].close()
                fileStreams[conn].pop()
                conn.close()
                outputs.remove(conn)
            

if __name__ == "__main__":
    run()