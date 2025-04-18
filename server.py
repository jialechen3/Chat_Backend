import socketserver

from util.user_actions import avatar_upload
from util.github import authcallback,authgithub
from util.chat import chat_create
from util.chat import chat_get
from util.chat import chat_delete
from util.chat import chat_update
from util.user_actions import emoji_create
from util.user_actions import emoji_delete
from util.extractor import extractor
from util.user_actions import nickname
from util.render import render
from util.request import Request
from util.router import Router
from util.tube_clone import video_upload, video_get_all, video_get_one, endpoint_transcription, set_thumbnail
from util.user_actions import register, logout, login, get_me, search_user, update_profile
from util.websockets import socket_function
from util.zoom_clone import videocall


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
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
        self.router.add_route("GET", "/videotube/videos/", render, False)
        self.router.add_route("GET", "/videotube/set-thumbnail", render, False)
        self.router.add_route("GET", "/test-websocket", render, True)
        self.router.add_route("GET", "/drawing-board", render, True)
        self.router.add_route("GET", "/direct-messaging", render, True)
        self.router.add_route("GET", "/video-call/", render, False)
        self.router.add_route("GET", "/video-call", render, True)






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


        ######################Youtube Clone#####################################
        self.router.add_route("POST", "/api/videos", video_upload, True)
        self.router.add_route("GET", "/api/videos", video_get_all, True)
        self.router.add_route("GET", "/api/videos/", video_get_one, False)
        self.router.add_route("PUT", "/api/thumbnails/", set_thumbnail, False)

        #######################Generate subtitle#################################
        self.router.add_route("GET", "/api/transcriptions/", endpoint_transcription, False)

        #######################Route websocket#################################
        self.router.add_route("GET", "/websocket", socket_function, True)
        #######################Drawing Board##############################
        self.router.add_route("GET", "/drawing-board", socket_function, True)


        ########################Zoom#########################################
        self.router.add_route("POST", "/api/video-call", videocall, False)






        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)

        request = Request(received_data)

        if "Content-Length" in request.headers:
            length = int(request.headers['Content-Length'])

            while len(request.body) < length:
                chunk = self.request.recv(2048)
                received_data += chunk
                request = Request(received_data)

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()

