# TCP Char Server

import socket
import select
import sys


class ChatServer:

    def __init__(self, host=None, port=5000):
        self.host = host
        self.port = port
        self.__connections = []
        self.server_socket = socket.socket(socket.AF_INET,
                                           socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,
                                      socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(10)
        self.__connections.append(self.server_socket)
        self.is_running = True

    @property
    def connections(self):
        return self.__connections

    def add_connection(self, connection):
        self.__connections.append(connection)

    # remove connection
    def remove(self, connection):
        self.__connections.remove(connection)

    def broadcast_message(self, sock, message):
        print("broadcasting message")
        for connection in self.__connections:
            if connection != self.server_socket and connection != sock:
                try:
                    connection.send(message)
                except:
                    print("connection was closed")
                    connection.close()
                    self.__connections.remove(connection)

    def listen(self):
        # return the read from all the sockets in the connection list
        read_sockets, write_sockets, error_sockets \
            = select.select(self.connections, [], [])
        return read_sockets

    def accept_new_connection(self, connection):
        sockfd, addr = self.server_socket.accept()
        self.add_connection(sockfd)
        print("Client ({0},{0}) connected".format(addr))
        self.broadcast_message(sockfd, "[{0}:{0}] entered the room".format(addr))


    def receive_message(self, sock):
        print("trying to receive a message")
        data = sock.recv(4096)
        print(str(data))
        if data:
            self.broadcast_message(sock, 
                    "\r<{0}> {1}".format((str(sock.getpeername()), str(data))))


    def broadcast_signoff(self, sock): 
        print("tring to broadcast a signoff")
        # addr = self.server_socket.getpeername()
        # self.broadcast_message(sock,
        #    "Client ({0}, {0}) is offline\n".format(addr))
        # print("Client ({0}, {0}) is offline\n".format(addr))
        sock.close()
        self.remove(sock)


    def kill_server(self):
        self.server_socket.close()
        self.is_running = False


def main():
    h = socket.gethostbyname(socket.gethostname())
    if len(sys.argv) < 2:
        chat_server = ChatServer(host=h)
    else:
        chat_server = ChatServer(host=sys.argv[1])
    print("Chat server started: host {0}, port {1}".format( \
        str(chat_server.host), str(chat_server.port)))

    while chat_server.is_running:
        print("listening for stuff")
        read_sockets = chat_server.listen()
        print("heard stuff")
        for sock in read_sockets:
            # new connection
            print("seeking new connection")
            if sock == chat_server.server_socket:
                chat_server.accept_new_connection(sock)
            else:
                # some incoming message from the client
                print("seeking message to broadcast")
                try:
                    chat_server.receive_message(sock)
                except:
                    "this particular socket has signed off"
                    chat_server.broadcast_signoff(sock)
                    continue

    chat_server.kill_server()

if __name__ == "__main__":
    main()
