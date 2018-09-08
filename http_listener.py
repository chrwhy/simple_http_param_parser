import socket
import sys
import parser


def response():
    print('\nResponse sent')
    return ("HTTP/1.1 200 OK\r\n".encode()
            + "Content-Length: 14\r\n".encode()
            + "Server: Simple HTTP Parser\r\n".encode()
            + "Date: Sat, 25 Aug 2018 14:04:43 GMT\r\n".encode()
            + "Content-Type: application/json; charset=utf-8\r\n".encode()
            + "Connection: close\r\n".encode()
            + "\r\n".encode()
            + '{\"code\":\"0\"}\r\n'.encode())
    # + "\r\n".encode())


def start_tcp_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(1)
    server_address = (ip, port)
    sock.bind(server_address)
    try:
        sock.listen(1)
    except:
        sys.exit(1)

    request = parser.SimpleRequest()

    while True:
        print("Waiting for connection...")
        client, addr = sock.accept()
        print('Got connection')

        print('=============START LINE=============')
        line = ''
        while True:
            bt = read_data(client, 1)
            if bt[0].__eq__(0x0D):
                print(line, '\n')
                break
            else:
                line += bt.decode()
        parser.parse_start_line(request, line)

        print('=============HEADER=============')
        line = ''
        while True:
            bt = read_data(client, 1)
            if bt[0].__eq__(0x0D):
                print(line)
                if line != '':
                    key = line.split(': ', 1)[0]
                    value = line.split(': ', 1)[1]
                    request.add_header(key, value)
                if line == '':
                    read_data(client, 1)
                    break
                line = ''
            else:
                if not bt[0].__eq__(0x0A):
                    line += bt.decode()

        content_len = int(request.get_header('Content-Length'))

        print('=============BODY=============')
        body = read_data(client, content_len)
        parser.parse_body(request, body)
        print_req_params(request)
        client.send(response())


def print_req_params(request):
    print('Request params: ')
    for k, v in request.params.items():
        print(k, ':', v)


def read_data(client, expect):
    data = client.recv(expect)
    if len(data) == expect:
        return data
    left = expect - len(data)
    while left > 0:
        data += client.recv(left)
        left = expect - (len(data))
    return data


if __name__ == '__main__':
    start_tcp_server('localhost', 8080)
    print(0x0A)
    print(0x0D)
