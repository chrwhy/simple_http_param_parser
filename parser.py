class SimpleRequest:
    headers = {}
    params = {}
    body = ''
    boundary = ''

    def __init__(self):
        pass


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
    print('form-data/mutipart ', 'way', '\n')
    part = []
    pos = 0
    i = 0
    while i < (len(body) - 3):
        # \r\n--
        if body[i].__eq__(0x0D) and body[i + 1].__eq__(0x0A) and body[i + 2].__eq__(0x2D) and body[
            i + 3].__eq__(0x2D):
            parse_mutipart(part, pos)
            pos += 1
            part.clear()
            i = i + 2
        else:
            part.append(body[i])
            i += 1


def save_orig_part(part, idx):
    f = open('orig_mutipart_' + str(idx) + '.txt', 'wb+')
    f.write(bytes(part))
    f.close()


def parse_mutipart(part, idx):
    save_orig_part(part, idx)

    pos = 0
    while pos < len(part):
        if part[pos].__eq__(0x0D) and part[pos + 1].__eq__(0x0A):
            pos = pos + 2
            print('Boundary line end.\n')
            break
        pos += 1

    headers = {}
    line = []

    print('Mutipart header start\n')
    while pos < len(part):
        if part[pos].__eq__(0x0D) and part[pos + 1].__eq__(0x0A):
            if len(line) == 0:
                pos += 2
                break
            print('Mutipart header line: ', bytes(line).decode())
            header_line = bytes(line).decode()
            k = header_line.split(": ")[0]
            y = header_line.split(": ")[1]
            headers[k] = y

            pos += 2
            line.clear()
        else:
            line.append(part[pos])
            pos += 1

    disposiition = headers['Content-Disposition']
    if disposiition.find('filename') > -1:
        params = disposiition.split('; ')
        for param in params:
            pairs = param.split('=')
            if len(pairs) > 1:
                print(pairs[0], ": ", pairs[1])
    else:
        print('form-value: ', bytes(part[pos:]).decode())


def parse_body(request, body):
    content_type = request.headers['Content-Type']
    print('Content-Type: ', content_type)
    if content_type.find('multipart/form-data') > -1:
        parse_body_part(request, body)
        return

    if content_type == 'application/x-www-form-urlencoded':
        parse_body_param(request, body.decode())
    else:
        print(body.decode())


def parse_start_line(request, data_in_str, pos, total_length):
    print('*****Start line*****')
    start_line = ''
    while pos < total_length:
        if '\r' == data_in_str[pos] and data_in_str[pos + 1] == '\n':
            pos += 2
            print(start_line)
            print('$$$$$Start line$$$$$\n')

            method = start_line.split(' ', 2)[0]
            url = start_line.split(' ', 2)[1]
            protocol = start_line.split(' ', 2)[2]

            parse_url_param(request, url)

            print('METHOD: ', method)
            print('URL: ', url)
            print('PROTOCOL: ', protocol)

            request.method = method
            return pos
        else:
            start_line += data_in_str[pos]
            pos += 1


def parse_header(request, data_in_str, pos, total_length):
    print('*****Header*****')
    line = ''
    while pos < total_length:
        if '\r' == data_in_str[pos] and data_in_str[pos + 1] == '\n':
            pos += 2
            print(line)
            if line == '':
                break
            else:
                key = line.split(': ', 1)[0]
                value = line.split(': ', 1)[1]
                request.headers[key] = value
            line = ''
        else:
            line += data_in_str[pos]
            pos += 1
    print('$$$$$Header$$$$$\n')
    print(line)
    return pos
