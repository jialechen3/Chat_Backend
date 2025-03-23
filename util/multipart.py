import unittest

from util.parts_class import PartOfMulti, Multipart


def parse_multipart(request):

    req = request.body

    content_type = request.headers['Content-Type']
    boundary = '--' + content_type.strip().split('boundary=')[-1]
    boundary = boundary.encode() + b'\r\n'

    #------WebKitFormBoundaryv1tp9x8MX628OUBX
    multi = req.split(boundary)

    full_multiparts = []
    #now we go through each of the multi parts and stores its headers
    #part is in bytes
    for part in multi[1:]:
        headers = {}
        name = ""
        content = b""
        #the headers
        byte_heads = part.split(b"\r\n\r\n", 1)

        heads = byte_heads[0].decode()

        #divide by each line
        head = heads.split("\r\n")

        for line in head:

            header_key = line.split(":")[0]
            header_value = line.split(":",1)[1]
            headers[header_key] = header_value.strip()
            if header_key == "Content-Disposition":
                name = header_value.split("name=")[1].split(";")[0].strip('"')


        #the body content
        #print(byte_heads[0])
        content = byte_heads[1].split(b"\r\n",1)[0]


        one_of_the_part = PartOfMulti(headers, name, content)

        #add into all parts
        full_multiparts.append(one_of_the_part)

    return Multipart(boundary, full_multiparts)





