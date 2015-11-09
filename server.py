# Tcp Chat server


import socket
import select
import sys


class ChatServer:

    def __init__(self, host, port=5000):
        self.host = host
        self.port = port
        self.__connection_list = []
        self.max_recv_buffer = 4096
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this has no effect, why ?
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.connection_list.append(self.server_socket)
        self.server_socket.listen(10)
        print("Chat server started on port " + str(port))

    @property
    def connection_list(self):
        return self.__connection_list

    def broadcast_data(self, sock, message):
        # Do not send the message to master socket and the client who has send us the message
        for socket in self.connection_list:
            if socket != self.server_socket and socket != sock:
                try:
                    socket.send(message)
                except:
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    socket.close()
                    self.remove(socket)

    def remove(self, sock):
        sockfd, addr = self.server_socket.accept()
        self.broadcast_data(sock, "Client (%s, %s) is offline" % addr)
        print("Client (%s, %s) is offline" % addr)
        sock.close()
        self.__connection_list.remove(sock)

    def add(self, sock):
        # Handle the case in which there is a new connection recieved through server_socket
        sockfd, addr = self.server_socket.accept()
        self.__connection_list.append(sockfd)
        print("Client (%s, %s) connected" % addr)
        self.broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)

    def read_available_sockets(self):
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = \
            select.select(self.__connection_list, [], [])
        return read_sockets


def main():
    chat_server = ChatServer(sys.argv[1], int(sys.argv[2]))
    while True:
        read_sockets = chat_server.read_available_sockets()
        for sock in read_sockets:
            # New connection
            if sock == chat_server.server_socket:
                chat_server.add(sock)
            # Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    # attempt to recieve and broadcast a message from this client
                    data = sock.recv(chat_server.max_recv_buffer)
                    if data:
                        chat_server.broadcast_data(sock,
                                '\r' + '<' + str(sock.getpeername()) + '> ' + \
                                        str(data))
                except:
                    # this client has signed off
                    chat_server.remove(sock)
                    continue
    chat_server.server_socket.close()


if __name__ == "__main__":
    main()
