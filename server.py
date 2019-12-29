import socket
import select
import sys
import os
import io
import argparse

HOST = '127.0.0.1'
PORT = 0
BYTES = 0
FILE = ''
TOTBYTES = 0

#parse command line arguments
def parse_args():
    global PORT
    global BYTES
    global FILE
    global TOTBYTES
    parser = argparse.ArgumentParser(description='Create text server.')
    parser.add_argument('--file',metavar='file',type=str,nargs=1,
            help='Name of text file to send',default='sample.txt',
            choices=['sample.txt','foo.txt','blah.txt'])
    parser.add_argument('--bytes',metavar='bytes',type=int,nargs=1,
            help='Num bytes to send per cycle',default=2)
    parser.add_argument('--port',metavar='port',type=int,nargs=1,
            help='Port to connect',default=1234)     
    args = parser.parse_args()
    
    if isinstance(args.file,list):
        FILE = os.path.join('data',args.file[0])
    else:
        FILE = os.path.join('data',args.file)

    if isinstance(args.bytes,list):
        BYTES = args.bytes[0]
    else:
        BYTES = args.bytes

    if isinstance(args.port,list):
        PORT = args.port[0]
    else:
        PORT = args.port

    print(PORT)
    print(FILE)
    print(BYTES)
    TOTBYTES = os.stat(FILE).st_size
    print(TOTBYTES)
    
def run():
    sListen = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print(f'starting up Text server on {HOST} port {PORT}')
    sListen.bind((HOST,PORT))
    sListen.listen(5)

    #streams from which we read
    inputs = [sListen]
    #streams to which we write
    outputs = []
    fileStreams = dict()
    queues = dict()
    sentBytes = dict()
    address = dict()

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
                print(f'new connection from {addr} will receive {FILE}')
                conn.setblocking(0)
                #add client to list of outputs
                outputs.append(conn)
                #store client address
                address.update({conn:addr})
                #create file stream for this connection
                filestr = open(FILE,'rb')
                fileStreams.update({conn:filestr})
                sentBytes.update({conn:0})
                #create queue for this file stream
                queues.update({filestr:[]})
                #add file stream to inputs
                inputs.append(fileStreams[conn])
            #if input is filestream
            else:
                tr = s.read(BYTES)
                print(f'reading {tr}')
                queues[s].append(tr)

        for s in writeable:
            #if something is in the queue, send it
            #go from socket s to associated filestream 
            filestr = fileStreams[s]
            if(not len(queues[filestr]) == 0):
                toSend = queues[filestr].pop()
                if not toSend == b'':
                    print(f'Sending {toSend} to {address[s]}')
                    s.send(toSend)
                    sentBytes[s] += BYTES
                    print(f'{sentBytes[s]} bytes have been sent.')

                #if the queue is empty and we've sent the entire file, send empty bytes to signal client to close conn
                else:
                    print(f'Done sending to {address[s]}')
                    s.send(toSend)
                    del queues[filestr]
                    filestr.close()
                    del fileStreams[s]
                    del address[s]
                    inputs.remove(filestr)
                    s.close()
                    outputs.remove(s)
            

if __name__ == "__main__":
    parse_args()
    run()