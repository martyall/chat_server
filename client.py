# telnet program example
import socket
import select
import sys
import argparse


def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


class ChatClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))
        except:
            print("Unable to connect")
            sys.exit()
        self.client_socket.settimeout(2)

    def get_readable_sockets(self):
        socket_list = [sys.stdin, self.client_socket]
        read_sockets, write_sockets, error_sockets = \
                select.select(socket_list, [], [])
        return read_sockets

p = argparse.ArgumentParser()
p.add_argument("--host")
p.add_argument("--port", type=int)


def main():
    opts = vars(p.parse_args())
    chat_client = ChatClient(**opts)
    print('Connected to remote host. Start sending messages')
    prompt()

    while True:
        # Get the list sockets which are readable
        read_sockets = chat_client.get_readable_sockets()
        for sock in read_sockets:
            # incoming message from remote server
            if sock == chat_client.client_socket:
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from chat server')
                    sys.exit()
                else:
                    # print data
                    sys.stdout.write(data.decode('utf8'))
                    prompt()

            # user entered a message
            else:
                msg = sys.stdin.readline().encode()
                chat_client.client_socket.send(msg)
                prompt()


if __name__ == "__main__":
    main()
