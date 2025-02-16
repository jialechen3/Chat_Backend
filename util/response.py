import json
import uuid


class Response:
    def __init__(self):
        self.code = 200
        self.status = "OK"
        self.heads = {}
        self.cookie = {}
        self.body = b""

    def set_status(self, code: int, text:str):
        self.code = code
        self.status = text
        return self

    def headers(self, headers:dict):
        self.heads.update(headers)
        return self


    def cookies(self, cookies:dict):
        cookie_header = ""
        for key, value in cookies.items():
            cookie_header = f"{key}={value}"

        if "Set-Cookie" not in self.heads:
            self.heads["Set-Cookie"] = ""
        self.heads["Set-Cookie"] = cookie_header

        return self

    def bytes(self, data: bytes):
        self.body += data

        return self

    def text(self, data: str):
        self.body += data.encode('utf-8')
        self.heads.update({"Content-Type": "text/plain; charset=utf-8"})
        #print('hello is in the response.text()')
        return self


    def json(self, data:list):
        self.body = json.dumps(data).encode('utf-8')
        self.heads.update({"Content-Type": "application/json"})
        return self

    def to_data(self):
        if 'Content-Type' not in self.heads:
            self.heads['Content-Type'] = 'text/plain; charset=utf-8'

        self.heads['Content-Length'] = str(len(self.body))

        response_lines = []

        status_line = f"HTTP/1.1 {self.code} {self.status}"+ "\r\n"
        response_lines.append(status_line)

        for key, value in self.heads.items():
            header_line = f"{key}: {value}"
            response_lines.append(header_line + "\r\n")

        for cook in self.cookie:
            cookie_line = f"Set-Cookie: {cook}"
            response_lines.append(cookie_line + "\r\n")

        #disable MIME type sniffing
        response_lines.append("X-Content-Type-Options: nosniff\r\n")
        print(self.heads)
        #\r\n\r\n
        response_lines.append("\r\n")

        response_header = "".join(response_lines)

        response_bytes = response_header.encode('utf-8') + self.body

        return response_bytes



def test1():
    res = Response()
    res.text("hello")
    author_id = uuid.uuid4()
    session_cookie = str(author_id)
    cookie_str = session_cookie + "; Expires=Wed, 21 Oct 2025 07:28:00 GMT; HttpOnly"
    res.cookies({"session": cookie_str})
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: application/json;\r\nContent-Length: 5\r\nSet_Cookie: session=wqrdsv12314l\r\n\r\nhello'
    print(res.heads)
    actual = res.to_data()
    #assert actual == expected, f"Actual: {actual}\nExpected: {expected}"

def test2():
    res = Response()
    h = {"Content-Type": "image/x-icon"}
    res.headers(h)
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\n\r\n'
    actual = res.to_data()
    #assert actual == expected, f"Actual: {actual}\nExpected: {expected}"



if __name__ == '__main__':
    test1()
    test2()
