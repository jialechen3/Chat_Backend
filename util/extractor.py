import json

from util.response import Response
# This will be the funtion to handle correct MIME type and extract from the public file
MIME_TYPES = {
    "html": "text/html",
    "css": "text/css",
    "js": "text/javascript",
    "jpg": "image/jpg",
    "webp": "image/webp",
    "gif": "image/gif",
    "ico": "image/x-icon",
    "svg": "image/svg+xml"
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
        print(mime_type)
        res.headers(mime_type)


        #if 'image' == _type.split('/')[0]:
            #res.bytes(out_file)
        #if 'javascript' == _type.split('/')[1]:
        #    print(out_file)
         #   res.json(json.loads(out_file))
        #if 'text' == _type.split('/')[0]:
           # content = out_file
           # res.bytes(content)



    res.headers(mime_type)
    handler.request.sendall(res.to_data())








