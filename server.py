import socketserver

from util.avatar_upload import avatar_upload
from util.github import authcallback,authgithub
from util.totp import generateTwoFac
from util.chat import chat_create
from util.chat import chat_get
from util.chat import chat_delete
from util.chat import chat_update
from util.emoji import emoji_create
from util.emoji import emoji_delete
from util.extractor import extractor
from util.nickname import nickname
from util.render import render
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
from util.user_actions import register, logout, login, get_me, search_user, update_profile


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)
        # TODO: Add your routes here

        ########This is where all the rendering goes#########################################
        self.router.add_route("GET", "/public", extractor, False)
        self.router.add_route("GET", "/", render, True)
        self.router.add_route("GET", "/chat", render, True)
        self.router.add_route("GET", "/register", render, True)
        self.router.add_route("GET", "/login", render, True)
        self.router.add_route("GET", "/settings", render, True)
        self.router.add_route("GET", "/search-users", render, True)
        self.router.add_route("GET", "/change-avatar", render, True)
        self.router.add_route("GET", "/videotube", render, True)
        self.router.add_route("GET", "/videotube/upload", render, True)
        self.router.add_route("GET", "/videotube/videos", render, False)



        #####################The basic function of the chat#####################################
        self.router.add_route("POST", "/api/chats", chat_create, True)
        self.router.add_route("GET", "/api/chats", chat_get, True)
        self.router.add_route("PATCH", "/api/chats", chat_update, False)
        self.router.add_route("DELETE", "/api/chats", chat_delete, False)
        self.router.add_route("PATCH", "/api/reaction", emoji_create, False)
        self.router.add_route("DELETE", "/api/reaction", emoji_delete, False)
        self.router.add_route("PATCH", "/api/nickname", nickname, True)


        ##############################User functions#########################################
        self.router.add_route("POST", "/register", register, True)
        self.router.add_route("GET", "/logout", logout, True)
        self.router.add_route("POST", "/login", login, True)
        self.router.add_route("GET", "/api/users/@me", get_me, True)
        self.router.add_route("GET", "/api/users/search", search_user, False)
        self.router.add_route("POST", "/api/users/settings", update_profile, True)
        ################################Avatar upload##################################
        self.router.add_route("POST", "/api/users/settings", update_profile, True)
        ####################Avatar upload###############################
        self.router.add_route("POST", "/api/users/avatar", avatar_upload, True)

        ########################GITHUB Login#######################################
        self.router.add_route("GET", "/authgithub", authgithub, True)
        self.router.add_route("GET", "/authcallback", authcallback, False)







        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(4096)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        if "Content-Length" in request.headers:
            length = int(request.headers['Content-Length'])
            print("Length in server:", length)
            while len(received_data) < length:
                chunk = self.request.recv(4096)
                received_data += chunk
            print("FINAL length in server:", len(received_data))

        request2 = Request(received_data)
        self.router.route_request(request2, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()

