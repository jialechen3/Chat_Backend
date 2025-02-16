import re

from util.response import Response


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        self.routes.append({
            'method': method,
            'path': path,
            'action': action,
            'exact_path': exact_path
        })


    def route_request(self, request, handler):
        method = request.method
        path = request.path
        for route in self.routes:
            if method == route['method']:

                if (route['exact_path'] and path == route['path']) or (
                        not route['exact_path'] and path.startswith(route['path'])):
                    route['action'](request, handler)
                    return


        #If there is no path matching the request, send a 404 Not Found response over the handler.
        res = Response()
        res.set_status(404, "Not Found")
        res.text("404 Not Found")
        handler.request.sendall(res.to_data())