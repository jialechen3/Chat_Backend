from util.response import Response
def render(request, handler):
    res = Response()
    h = {"Content-Type": "text/html"}
    res.headers(h)
    with open("public/layout/layout.html", "r") as layout_file:
        layout_content = layout_file.read()

    if request.path == '/':
        file_name = 'public/index.html'
    elif request.path == '/chat':
        file_name = 'public/chat.html'
    elif request.path == '/register':
        file_name = 'public/register.html'
    elif request.path == '/login':
        file_name = 'public/login.html'
    elif request.path == '/settings':
        file_name = 'public/settings.html'
    elif request.path == '/search-users':
        file_name = 'public/search-users.html'
    else:
        handler.request.sendall(b"HTTP/1.1 404 Not Found\r\n\r\nPage not found")
        return


    with open(file_name, "r") as page_file:
        page_content = page_file.read()

    new_content = layout_content.replace("{{content}}", page_content)
    res.bytes(new_content.encode())
    handler.request.sendall(res.to_data())
"""
"/register" - Render register.html
"/login" - Render login.html
"/settings" - Render settings.html
"/search-users" - Render search-users.html
"""
