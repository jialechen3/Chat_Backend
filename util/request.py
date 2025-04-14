class Request:

    def __init__(self, request):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""  # bytes
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        header_part, _, body_part = request.partition(b'\r\n\r\n')
        str1 = header_part.decode()

        #set body as bytes

        self.body = body_part

        #headers
        lists = str1.split("\r\n")
        str0 = lists[0].split(" ")
        self.method = str0[0]

        if str0 == ['']:
            self.path = ''
        else:
            self.path = str0[1]
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




