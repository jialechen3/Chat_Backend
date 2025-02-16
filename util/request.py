class Request:

    def __init__(self, request):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""  # bytes
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        strl = request.decode()
        str1 = strl.split("\r\n\r\n")[0]

        #set body as bytes
        get_body = strl.split("\r\n\r\n")
        if len(get_body) > 1 and get_body[1] != "":
            self.body = get_body[1].encode()

        #headers
        lists = str1.split("\r\n")
        self.method = lists[0].split(" ")[0]
        if self.method == "GET" or self.method == "POST" or self.method == "PATCH" or self.method == "DELETE":
            self.path = lists[0].split(" ")[1]
        self.http_version = "HTTP/1.1"

        #iterate through all the headers
        for line in lists[1:]:
            #if no headers; skip
            if line == "": continue

            header_key = line.split(":")[0]
            header_value = line.split(":",1)[1]
            self.headers[header_key] = header_value.strip()
            # if encounters cookie
            # split each cookie  by ';'
            # key=value  split by '='
            if header_key == "Cookie":
                for item in header_value.split(";"):
                    cookie_parts = item.split("=", 1)
                    if len(cookie_parts) == 2:
                        cookie_key = cookie_parts[0].strip()
                        cookie_value = cookie_parts[1].strip()
                        self.cookies[cookie_key.strip()] = cookie_value.strip()
        #if lists[0].split(" ")[0] == "POST":



def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    print(request.headers)
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct
def test2():
    request = Request(b"PATCH /api/chat/{id} HTTP/1.1\r\nHost: localhost:8080\r\nCookie: session=X6kAwpgW29M; visits=4\r\n\r\nUpdated Content")
    print(request.cookies)
    print(request.body)
    print(request.path)
    assert request.method == "PATCH"
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b"Updated Content"

if __name__ == '__main__':
    #test1()
    test2()

