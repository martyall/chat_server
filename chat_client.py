import socket
import select
import string
import sys
import argparse


def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()

class ChatClient:

    def __init__(self, host, port=5000):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET,
                socket.SOCK_STREAM)
        self.client_socket.settimeout(2)
        self.is_connected = True

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print "Connect to chat server, start sending messsages."
        except:
            print "Unable to connect"
            sys.exit()

    def send(self, message):
        self.client_socket.send(message)

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    print "Attempting to connect to host: %s, port %d" % (host, port)
    client = ChatClient(host, port)
    try:
        client.connect()
        print "Connected to the remote host, start sending messages."
        prompt()
    except :
        print "Unable to connect"
        sys.exit()

    while client.is_connected:
        socket_list = [sys.stdin, client.client_socket]
        read_sockets, write_sockets, error_sockets \
                = select.select(socket_list, [], [])

        for sock in read_sockets:
            if sock == client.client_socket:
                data = sock.recv(4096)
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                else:
                    sys.stdout.write(data)
                    prompt()

            else:
                msg = sys.stdin.readline()
                client.send(msg)
                prompt()


if __name__ == "__main__":
    main()
