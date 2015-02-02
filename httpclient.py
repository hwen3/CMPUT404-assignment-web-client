#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Copyright 2015 Han Wen
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
import urllib
import urlparse
from time import ctime

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body



class HTTPClient(object):
    #def get_host_port(self,url):

    ACCEPT_TYPES = "text/html,text/plain,application/xhtml+xml,application/xml"
    REQUEST_LINE_FORMAT = "{} {} HTTP/1.1 \r\n"
    GENERAL_HEADER_FORMAT = "Date: {} \r\nConnection: close \r\n"
    REQUEST_HEADER_FORMAT = "Host: {} \r\nAccept: {} \r\nUser-Agent: custom python browser\r\nCache-Control: no-cache\r\n"
    ENTITY_HEADER_FORMAT = "Content-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n"
    CRLF = "\r\n"

    def get_HTTPRequest(self, data):
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def parse_url(self, url):
        net_url = urlparse.urlparse(url)
        host = net_url.hostname
        port = net_url.port
        if (port == None):
            port = 80
        path = net_url.path
        if (path == ""):
            path = "/"

        return (path, host, port)

    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    def get_code(self, data):
        str_array = data.split()
        return int(str_array[1])

    def get_headers(self, method, path, host, data=None):
        request_str = self.REQUEST_LINE_FORMAT.format(method, path) + \
                      self.GENERAL_HEADER_FORMAT.format(ctime()) + \
                      self.REQUEST_HEADER_FORMAT.format(host, self.ACCEPT_TYPES)

        if (method == "POST"):
            request_str += self.ENTITY_HEADER_FORMAT.format(len(data)) + self.CRLF + data
        else:
            request_str += self.CRLF

        return request_str

    def get_body(self, data):
        data = data.split(self.CRLF)
        if ("" in data):
            body_newline_index = data.index("")
            return self.CRLF.join(data[body_newline_index+1:len(data)]) #get the body only
        else:
            return self.CRLF.join(data) # error in header normally should not be coming here

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
        sock.shutdown(1)
        sock.close()

        return str(buffer)

    def GET(self, url, args=None):
        path, host, port = self.parse_url(url)

        request = self.get_headers("GET", path, host)
        sock = self.connect(host, port)
        sock.send(request)

        return self.get_HTTPRequest(self.recvall(sock))

    def POST(self, url, args=None):
        encoded_args = ""

        path, host, port = self.parse_url(url)

        if (args != None):
            encoded_args = urllib.urlencode(args)

        request = self.get_headers("POST", path, host, encoded_args)
        sock = self.connect(host, port)
        sock.send(request)


        return self.get_HTTPRequest(self.recvall(sock))

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
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
