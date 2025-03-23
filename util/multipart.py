import unittest

from util.parts_class import PartOfMulti, Multipart


def parse_multipart(request):

    req = request.body

    content_type = request.headers['Content-Type']
    orig_boundary = content_type.strip().split('boundary=')[-1]
    boundary = '--' + orig_boundary
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
            header_key = line.split(":")[0].strip()
            header_value = line.split(":",1)[1]
            headers[header_key] = header_value.strip()
            if header_key == "Content-Disposition":
                name = header_value.split("name=")[1].split(";")[0].strip('"')


        #the body content
        content = byte_heads[1]
        if content.endswith(b'\r\n'):
            content = content[:-2]

        #check if the content has the closing boundary marker
        closing_boundary = b'\r\n--' + orig_boundary.encode() + b'--'
        if content.endswith(closing_boundary):
            content = content[: -len(closing_boundary)]

        one_of_the_part = PartOfMulti(headers, name, content)

        #add into all parts
        full_multiparts.append(one_of_the_part)

    return Multipart(orig_boundary, full_multiparts)


class MockRequest:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body


class TestMultipartParsing(unittest.TestCase):
    def test_parse_multipart(self):
        # Example boundary
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

        # Sample headers and body for a multipart request
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }

        # Sample image data (just some bytes for testing)
        image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10"

        # Multipart body mimicking a form submission with text and image parts
        body = (
                   f"--{boundary}\r\n"
                   "Content-Disposition: form-data; name=\"text_field\"\r\n\r\n"
                   "Hello, World!\r\n"
                   f"--{boundary}\r\n"
                   "Content-Disposition: form-data; name=\"file\"; filename=\"test.png\"\r\n"
                   "Content-Type: image/png\r\n\r\n"
               ).encode() + image_data + (
                   f"\r\n--{boundary}--\r\n"
               ).encode()

        # Create a mock request object
        request = MockRequest(headers, body)

        # Call the parse_multipart function
        result = parse_multipart(request)

        # Check the parsed boundary
        self.assertEqual(result.boundary, boundary)

        # Check the number of parts
        self.assertEqual(len(result.parts), 2)

        # Check the first part (text field)
        text_part = result.parts[0]
        self.assertEqual(text_part.name, "text_field")
        self.assertEqual(text_part.content, b"Hello, World!")

        # Check the second part (image file)
        image_part = result.parts[1]
        self.assertEqual(image_part.name, "file")
        self.assertEqual(image_part.content, image_data)

        # Print results for visual confirmation (Optional)
        print(f"Boundary: {result.boundary}")
        for i, part in enumerate(result.parts):
            print(f"Part {i + 1}:")
            print(f"  Name: {part.name}")
            print(f"  Headers: {part.headers}")
            print(f"  Content Length: {len(part.content)}")


if __name__ == "__main__":
    unittest.main()


