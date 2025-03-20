import unittest

from util.parts_class import PartOfMulti, Multipart


def parse_multipart(request):
    print("yes")
    req = request
    byte_str = req.split(b"\r\n\r\n", 1)

    str1 = byte_str[0].decode()

    #headers in before multipart
    lists = str1.split("\r\n")

    #content length
    #print(lists[1])
    length = lists[1].split(" ")

    content_length = length[1]

    #Content-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia
    #split(" ") ->

    #content-type and boundary
    con_type = lists[2].split(" ")
    content_type = con_type[1].strip(';')
    boundary = con_type[2].split("boundary=")[-1]
    #now get the multipart, we stored the full_str split by \r\n\r\n now we use the second split of it
    #(full_str[1])
    full_boundary = "--" + boundary + "\r\n"
    #print(full_boundary)
    boundary_bytes = full_boundary.encode()
    multi = request.split(boundary_bytes)
    full_multiparts = []
    #now we go through each of the multi parts and stores its headers
    #part is in bytes
    for part in multi[1:]:
        headers = {}
        name = ""
        content = b""
        #the headers
        byte_heads = part.split(b"\r\n\r\n", 1)
        print(part)
        heads = byte_heads[0].decode()

        #divide by each line
        head = heads.split("\r\n")

        for line in head:
            #print(line)
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


class TestMultipartParsing(unittest.TestCase):
    def test_provided_request(self):
        """
        Test parsing the provided multipart request.
        """
        request_body = b"""POST /form-path HTTP/1.1\r\nContent-Length: 9937\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia\r\n\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia\r\nContent-Disposition: form-data; name="upload"; filename="discord.png"\r\nContent-Type: image/png\r\n\r\n<bytes_of_the_file>\r\n------WebKitFormBoundarycriD3u6M0UuPR1ia--\r\n"""
        parsed = parse_multipart(request_body)

        # Check boundary
        self.assertEqual(parsed.boundary, "----WebKitFormBoundarycriD3u6M0UuPR1ia")

        # Check parts
        self.assertEqual(len(parsed.parts), 2)

        # Check first part (commenter)
        self.assertEqual(parsed.parts[0].name, "commenter")
        self.assertEqual(parsed.parts[0].headers["Content-Disposition"], 'form-data; name="commenter"')
        self.assertEqual(parsed.parts[0].content, b"Jesse")

        # Check second part (upload)
        self.assertEqual(parsed.parts[1].name, "upload")
        self.assertEqual(parsed.parts[1].headers["Content-Disposition"],
                         'form-data; name="upload"; filename="discord.png"')
        self.assertEqual(parsed.parts[1].headers["Content-Type"], "image/png")
        self.assertEqual(parsed.parts[1].content, b"<bytes_of_the_file>")


# Run the tests
if __name__ == "__main__":
    unittest.main()


