from util.response import Response
# This path is provided as an example of how to use the router
def hello_path(request, handler):
    res = Response()
    res.text("hello")
    print('I got the hello text')
    handler.request.sendall(res.to_data())