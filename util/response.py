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
        self.cookie.update(cookies)
        return self

    def bytes(self, data: bytes):
        self.body += data

        return self

    def text(self, data: str):
        self.body += data.encode('utf-8')
        self.heads.update({"Content-Type": "text/plain; charset=utf-8"})
        #print('hello is in the response.text()')
        return self


    def json(self, data):
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

        for key, value in self.cookie.items():
            response_lines.append(f"Set-Cookie: {key}={value}\r\n")
        #disable MIME type sniffing
        response_lines.append("X-Content-Type-Options: nosniff\r\n")
        print(self.heads)
        #\r\n\r\n
        response_lines.append("\r\n")

        response_header = "".join(response_lines)
        print(response_header.encode('utf-8'))
        response_bytes = response_header.encode('utf-8') + self.body
        #print(response_bytes)
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

def test3():
    res = Response()
    res.text("multiple cookies test")
    cookie1 = "session=abc123; Expires=Wed, 21 Oct 2025 07:28:00 GMT; HttpOnly"
    cookie2 = "user_id=12345; Path=/; Secure"
    res.cookies({"session": cookie1, "user_id": cookie2})
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 21\r\nSet-Cookie: session=' + cookie1.encode('utf-8') + b'\r\nSet-Cookie: user_id=' + cookie2.encode('utf-8') + b'\r\nX-Content-Type-Options: nosniff\r\n\r\nmultiple cookies test'
    actual = res.to_data()
    print(actual)
    assert actual == expected, f"Actual: {actual}\nExpected: {expected}"


if __name__ == '__main__':
    #test1()
    #test2()
    test3()


