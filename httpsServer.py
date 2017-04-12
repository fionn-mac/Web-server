import socket
import os.path
from threading import Thread 
import base64
import ssl

HOST, PORT = '', 8888

class server(Thread) :
    def __init__(self, client_connection, client_address) : 
        Thread.__init__(self) 
        self.client_connection = client_connection
        self.client_address = client_address
        # self.connstream = connstream

    def parseRequest(self, request) :
        request_head, request_body = request.split('\r\n', 1)
        request_head = request_head.splitlines()
        request_headline = request_head[0]
        fileName = '.' + request_headline.split(' ')[1]
        return request_head, request_body, request_headline, fileName


    def auth(self, request_body) :
        request_body = request_body.split('\r\n')
        flag = 0
        s = ''
        for request in request_body :
            if request.split(':')[0] == "Authorization" :
                s = base64.b64decode(request.split(':')[1].split(' ')[2])
                flag = 1
                break
        
        if flag == 1 and s.split(':')[0] == "aashay" and  s.split(':')[1] == "password" :
            return True
        return False    


    def putResponse(self, request) :
        request_head, request_body, request_headline, fileName = parseRequest(request)

        if self.auth(request_body) == False :
            http_response1 = """HTTP/1.1 401 Unauthorized\n"""
            response_headers = {
                'WWW-Authenticate': 'Basic',
                'Content-Type': 'text/html; encoding=utf8',
                'Content-Length': 0,
                'Connection': 'close',
            }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())
            sendData = http_response1+response_headers_raw+'\n'
            self.client_connection.sendall(sendData)

        else :
            request_message = request.split('\r\n\r\n')[1]
            f = open(fileName, 'w')
            f.write(request_message)
            http_response1 = """HTTP/1.1 200 OK\n"""
            request_method, request_uri, request_proto = request_headline.split(' ', 3)
            response_headers = {
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': 0,
                    'Connection': 'close',
                }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())
            sendData = http_response1+response_headers_raw+'\n'
            self.client_connection.sendall(sendData)


    def postResponse(self, request) :
        request_head, request_body, request_headline, fileName = parseRequest(request)
        paramURL = request_headline.split(' ')[1]
        paramURL = paramURL.split('/')
        paramURL = paramURL[1]
        request_message = request.split('\r\n')
        params = paramURL.split('&')
        for p in params:
            x = p.split('=')
            exec(x[0] + '=' + 'x[1]')
        # print username , password
        # if username == "asd" and password == "123":
        if self.auth(username,password) :
            http_response1 = """HTTP/1.1 200 OK\n"""
            request_method, request_uri, request_proto = request_headline.split(' ', 3)
            response_headers = {
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': 0,
                    'Connection': 'close',
                }

            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())
            sendData = http_response1 + '\n'
            self.client_connection.sendall(sendData)


    def getResponse(self, request) :
        request_head, request_body, request_headline, fileName = self.parseRequest(request)
        
        if self.auth(request_body) == False :
            http_response1 = """HTTP/1.1 401 Unauthorized\n"""
            response_headers = {
                'WWW-Authenticate': 'Basic',
                'Content-Type': 'text/html; encoding=utf8',
                'Content-Length': 0,
                'Connection': 'close',
            }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())
            sendData = http_response1+response_headers_raw+'\n'
            self.client_connection.sendall(sendData)

        # Checking if file is in the current directory
        elif os.path.isfile(fileName)  :
            http_response1 = """HTTP/1.1 200 OK\n"""
            # Making a dict with headers and their values
            request_headers = dict(x.split(': ', 1) for x in request_head[1:])

            f = open(fileName,'rb')
            l = f.read(1024)
            http_responseFile = ''
            http_responseFile = http_responseFile + l
            f.close()
            request_method, request_uri, request_proto = request_headline.split(' ', 3)
            response_headers = {
                    'WWW-Authenticate': 'Basic',
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': len(http_responseFile),
                    'Connection': 'close',
                }

            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())
            sendData = http_response1+response_headers_raw+'\n'+http_responseFile
            print "data ",sendData
            self.client_connection.sendall(sendData)
        else:
            http_response1 = """HTTP/1.1 404 Not Found\n"""
            http_response2 = '\n'
            response_headers = {
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': len(http_response2),
                    'Connection': 'close',
                }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())

            sendData = http_response1 + response_headers_raw + '\n' + http_response2
            self.client_connection.sendall(sendData)


    def respond(self, request):
        request_head, request_body = request.split('\r\n', 1)
        request_head = request_head.splitlines()

        requestType = request_head[0].split(' ')[0]
        print requestType
        if requestType == "GET" :
            print "getting"
            self.getResponse(request)
        elif requestType == "POST" :
            self.postResponse(request)
        elif requestType == "PUT" :
            self.putResponse(request)
        # else :


    def run(self):
        while True:
            request = self.client_connection.recv(102400)
            # request = self.connstream.read(1024)
            # print "new = ", request
			# Checking the condition for empty requests (which we were getting while testing)
            if len(request) == 0:
                continue
            print request
            self.respond(request)

        self.client_connection.close()
        print "closing the connection"

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket = ssl.wrap_socket(listen_socket,
                             server_side=True,
                             certfile="cert.pem",
                             keyfile="cert.pem",
                             ssl_version=ssl.PROTOCOL_SSLv23) 
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))

print 'Serving HTTP on port %s ...' % PORT
threads = []
requesting_clients = dict()
list_client = []
blacklist = []
while True: 
    listen_socket.listen(4) 
    # print "Multithreaded Python server : Waiting for connections from TCP clients..."  
    client_connection, client_address = listen_socket.accept()
    # r = connstream.read()

    # print "r = ", r
    if client_address[0] in blacklist :
        client_connection.close()
        continue
    newthread = server(client_connection, client_address) 

    if client_address[0] in list_client : 
        requesting_clients[client_address[0]] +=  1
    else:
        requesting_clients[client_address[0]] = 1
        list_client.append(client_address[0])

    print requesting_clients
    for value in list_client : 
        if requesting_clients[value] > 300 : 
            blacklist.append(value)
    newthread.start()
    threads.append(newthread) 
 
for t in threads: 
    t.join() 