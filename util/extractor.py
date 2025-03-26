import json

from util.response import Response
# This will be the funtion to handle correct MIME type and extract from the public file
MIME_TYPES = {
    "html": "text/html",
    "css": "text/css",
    "js": "text/javascript",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "png": "image/png",
    "ico": "image/x-icon",
    "svg": "image/svg+xml",
    "mp4": "video/mp4"
}
def extractor(request, handler):
    res = Response()
    #ex/ .public/img/dog.jpg
    path = request.path.strip('/public')
    #now only .jpg left
    _type = MIME_TYPES.get(path.split('.')[1])
    #match the jpg to corresponding value
    mime_type = {"Content-Type": _type}
    file_path = "." + request.path

    with open(file_path, "rb") as out_file:
        content = out_file.read()
        res.bytes(content)
        mime_type["Content-Length"] = str(len(content))
        res.headers(mime_type)

    res.headers(mime_type)
    handler.request.sendall(res.to_data())








