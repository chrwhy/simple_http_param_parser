import sys


class SimpleRequest:
    headers = {}
    params = {}
    body = ''
    boundary = ''

    def __init__(self):
        pass

    def get_param_by_name(self, name):
        return self.params[name]

    def add_header(self, key, value):
        self.headers[key.upper()] = value

    def contains_header(self, key):
        return self.headers.__contains__(key.upper())

    def get_header(self, key):
        if not self.headers.__contains__(key.upper()):
            return ''
        return self.headers[key.upper()]


def parse_url_param(request, url_params):
    if url_params.find('?') == -1:
        return
    pairs = url_params.split('?')[1].split('&')
    for pair in pairs:
        key = pair.split('=', 1)[0]
        value = pair.split('=', 1)[1]
        request.params[key] = value


def parse_body_param(request, body):
    if '' == body:
        return
    pairs = body.split('&')
    for pair in pairs:
        key = pair.split('=', 1)[0]
        value = pair.split('=', 1)[1]
        print(key, ': ', value)
        request.params[key] = value


def parse_body_part(request, body):
    # print('form-data/mutipart ', 'way', '\n')
    part = []
    pos = 0
    i = 0
    while i < (len(body) - 3):
        # \r\n--
        if body[i].__eq__(0x0D) and body[i + 1].__eq__(0x0A) and body[i + 2].__eq__(0x2D) and body[
            i + 3].__eq__(0x2D):
            parse_mutipart(request, part, pos)
            pos += 1
            part.clear()
            i = i + 2
        else:
            part.append(body[i])
            i += 1


def save_orig_part(part, idx):
    f = open('orig_multipart_' + str(idx) + '.txt', 'wb+')
    f.write(bytes(part))
    f.close()


def parse_mutipart_param(request, headers, content):
    # TBC, I have to go out for a while
    disposition = headers['Content-Disposition'.upper()]
    params = {}
    for param in disposition.split('; '):
        param = param.replace('\"', '')
        pairs = param.split('=')
        if len(pairs) > 1:
            pass
            k = pairs[0]
            v = pairs[1]
            # print(pairs[0], ": ", pairs[1])
            params[k] = v

    if headers.__contains__('Content-Type'.upper()):
        try:
            f = open(params['filename'], 'wb+')
            f.write(bytes(content))
            f.close()
        except:
            print("Unexpected error:", sys.exc_info()[0])
    else:
        print(bytes(content).decode())
        name = params['name']
        request.params[name] = bytes(content).decode()

    print('\n')


def parse_mutipart(request, part, idx):
    save_orig_part(part, idx)

    pos = 0
    while pos < len(part):
        if part[pos].__eq__(0x0D) and part[pos + 1].__eq__(0x0A):
            pos = pos + 2
            # end of Boundary line, jump out to parse the 'REAL' part
            break
        pos += 1
    line = []

    headers = {}
    content_start_pos = 0
    while pos < len(part):
        if part[pos].__eq__(0x0D) and part[pos + 1].__eq__(0x0A) and part[pos + 2].__eq__(0x0D) and part[
            pos + 3].__eq__(0x0A):
            # The multipart 'content', could be the key-value form, or attachment binaries, parse it according to the Content-Type
            print(bytes(line).decode())
            header_line = bytes(line).decode()
            k = header_line.split(": ")[0]
            y = header_line.split(": ")[1]
            headers[k.upper()] = y
            content_start_pos = pos + 4
            break

        if part[pos].__eq__(0x0D) and part[pos + 1].__eq__(0x0A):
            # Header line of the multipart
            if len(line) == 0:
                pos += 2
                break

            print(bytes(line).decode())

            header_line = bytes(line).decode()
            k = header_line.split(": ")[0]
            y = header_line.split(": ")[1]
            headers[k.upper()] = y
            pos += 2
            line.clear()
        else:
            line.append(part[pos])
            pos += 1

    parse_mutipart_param(request, headers, part[content_start_pos:])


def parse_body(request, body):
    content_type = request.get_header('Content-Type')
    if content_type.find('multipart/form-data') > -1:
        parse_body_part(request, body)
        return

    if content_type == 'application/x-www-form-urlencoded':
        parse_body_param(request, body.decode())
    elif content_type == 'application/octet-stream':
        f = open('octet-stream_data', 'wb+')
        f.write(bytes(body))
        f.close()
        pass
    else:
        pass
        # print(body.decode())

    print('\n')


def parse_start_line(request, start_line):
    method = start_line.split(' ', 2)[0]
    url = start_line.split(' ', 2)[1]
    protocol = start_line.split(' ', 2)[2]
    parse_url_param(request, url)
    request.method = method
