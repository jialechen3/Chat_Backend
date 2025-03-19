from util.parts_class import PartOfMulti


def parse_multipart(request):
    print("yes")
    strl = request.decode()
    full_str = strl.split("\r\n\r\n")
    str1 = full_str[0]

    #headers in before multipart
    lists = str1.split("\r\n")

    #content length
    length = lists[1].split(" ")
    content_length = length[1]

    #Content-Type: multipart/form-data; boundary=----WebKitFormBoundarycriD3u6M0UuPR1ia
    #split(" ") ->

    #content-type and boundary
    con_type = lists[2].split(" ")
    content_type = con_type[1].strip(';')
    boundary = con_type[2].strip("boundary=")

    #now get the multipart, we stored the full_str split by \r\n\r\n now we use the second split of it
    #(full_str[1])
    full_boundary = "--" + boundary
    multi = full_str[1].split(full_boundary)

    full_multiparts = {}
    #now we go through each of the multi parts and stores its headers
    for part in multi:
        headers = {}
        name = ""
        content = b""

        #the headers
        heads = part.split("\r\n\r\n")
        #divide by each line
        head = heads.split("\r\n")

        one_of_the_part = PartOfMulti(headers, name, content)

        #add into all parts
        full_multiparts.append(one_of_the_part)






