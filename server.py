import socketserver

from util.chat_create import chat_create
from util.chat_delete import chat_delete
from util.chat_get import chat_get
from util.chat_update import chat_update
from util.extractor import extractor
from util.render import render
from util.request import Request
from util.router import Router
from util.hello_path import hello_path


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)
        # TODO: Add your routes here

        self.router.add_route("GET", "/public", extractor, False)
        self.router.add_route("GET", "/", render, True)
        self.router.add_route("GET", "/chat", render, True)
        self.router.add_route("POST", "/api/chats", chat_create, True)
        self.router.add_route("GET", "/api/chats", chat_get, True)
        self.router.add_route("PATCH", "/api/chats", chat_update, False)
        self.router.add_route("DELETE", "/api/chats", chat_delete, False)
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
