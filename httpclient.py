#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

import re
import socket
import sys
# you may use urllib to encode data appropriately
from urllib.parse import urlencode, urlparse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split("\r\n")[-1]
    
    def sendall(self, data):
        """Sends data to the socket"""
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        """Closes the socket"""
        self.socket.close()

    def recvall(self, sock):
        """Receive all data from the socket"""
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        # return the decoded bytearray
        return buffer.decode('utf-8')

    def parse_url(self, url):
        """parses url to extract hostname, port, and path
        @params: url:str
        @return: tuple - (host:str, port:int, path:str)
        """
        o = urlparse(url)
        host = o.hostname
        path = o.path
        query = o.query
        port = o.port
        if not port:
            port = 80
        if not path:
            path = "/" #TODO: Handle 301 for this?
        if query:
            path += f"?{query}"
        return host, port, path

    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)
        try:
            self.connect(host, port)
        except:
            print(f"Error. Cannot connect to {host}:{port}.")
            return
        data = f"GET {path} HTTP/1.1\r\n"
        data+= f"Host: {host}\r\n"
        data+= "Accept: */*\r\n"
        data+= "Connection: Close\r\n\r\n"
        self.sendall(data)
        result = self.recvall(self.socket)
        self.close()
        print("\r\n",result, "\n\n")
        code = self.get_code(result)
        body = self.get_body(result)
        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        host, port, path = self.parse_url(url)
        try:
            self.connect(host, port)
        except:
            print(f"Error. Cannot connect to {host}:{port}.")
            return
        data = f"POST {path} HTTP/1.1\r\n"
        data+= f"Host: {host}\r\n"
        data+= f"Content-Type: application/x-www-form-urlencoded\r\n"
        body = ""
        if args:
            body += urlencode(args)
        data+=f"Content-Length: {len(body)}\r\n\r\n"
        data+=body
        self.sendall(data)
        result = self.recvall(self.socket)
        self.close()
        print("\r\n",result, "\n\n")
        code = self.get_code(result)
        body = self.get_body(result)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args ) 
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    # command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
