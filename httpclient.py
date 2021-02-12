#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, Joe Ha, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, header="", body=""):
        self.code = code
        self.header = header
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    # Connect with server given the host and port.
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    #Given data extract the status code.
    def get_code(self, data):
        status_code = data.split()[1]
        return status_code
    
    #Given data extract headers.
    def get_headers(self,data):
        header = data.split('\r\n\r\n')[0]
        return header

    #Given data extract the body.
    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    '''
        GET_request creates the request payload for an HTTP GET.
        Parameter: parsed url using urllib.parse.urlparse.
        Return: str HTTP GET payload

        Referenced:
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
    '''
    def GET_request(self, split_url):
        path = '/'
        if (split_url.path != ''):
            path = split_url.path
        request = 'GET '
        request += path
        request += ' HTTP/1.1\r\n'
        request += 'Host: ' + split_url.hostname + '\r\n'
        request += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n'
        request += 'Connection: close\r\n\r\n'
        # print(request)
        return request
    
    '''
        POST_request creates the request payload for an HTTP POST.
        Parameters: parsed url using urllib.parse.urlparse and optional arguments.
        Return: str HTTP POST payload

        Referenced:
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
    '''
    def POST_request(self, split_url, parameters=None):
        path = '/'
        if (split_url.path != ''):
            path = split_url.path
        request = 'POST '
        request += path
        request += ' HTTP/1.1\r\n'
        request += 'Host: ' + split_url.hostname + '\r\n'
        request += 'Content-Type: application/x-www-form-urlencoded\r\n'
        if (parameters != None):
            request += 'Content-Length: ' + str(len(parameters)) + '\r\n'
        else:
            request += 'Content-Length: 0\r\n'
        request += 'Connection: close\r\n\r\n'
        if (parameters != None):
            request += parameters
            request += '\r\n'
        return request

    '''
        GET method handles HTTP GET.
        Parameters: url and optional arguments.
        Return: HTTPResponse Object.

        Referenced:
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
        https://docs.python.org/3.7/library/urllib.parse.html
        https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python
    '''
    def GET(self, url, args=None):
        # default values
        code = 500
        body = ""
        port = 80

        #parse the url
        split_url = urllib.parse.urlparse(url)
        request = self.GET_request(split_url)
        #if port is different than 80.
        if (split_url.port != None):
            port = split_url.port

        self.connect(split_url.hostname, port)

        #Encode request payload and send it off
        self.sendall(request)
        data = self.recvall(self.socket)

        header = self.get_headers(data)
        header += '\r\n'
        code = int(self.get_code(data))
        body = self.get_body(data)
        self.close()

        #Printout GET to stdout.
        print(header)
        print(body)
        return HTTPResponse(code, header, body)

    '''
        POST method handles HTTP POST.
        Parameters: url and optional arguments.
        Return: HTTPResponse Object.

        Referenced:
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
        https://docs.python.org/3.7/library/urllib.parse.html
    '''
    def POST(self, url, args=None):
        #default values
        code = 500
        body = ""
        parameters = None

        #check if arguments exist.
        if (args != None):
            parameters = urllib.parse.urlencode(args)

        #parse the url
        split_url = urllib.parse.urlparse(url)
        # print(split_url)
        request = self.POST_request(split_url, parameters)
        self.connect(split_url.hostname, split_url.port)

        #Encode request payload and send it off
        self.sendall(request)
        data = self.recvall(self.socket)

        header = self.get_headers(data)
        header += '\r\n\r\n'
        code = int(self.get_code(data))
        body = self.get_body(data)

        #close connection
        self.close()
        #Printout POST to stdout.
        print(header)
        print(body)
        return HTTPResponse(code, header, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
