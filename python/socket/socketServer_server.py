#!/usr/bin/env python
#coding=utf8
import SocketServer

class MyTcpHandler(SocketServer.BaseRequestHandler):
    """
	The RequestHandler class for our server.
    It is instandiated once per connection to the server,and mustoverride the handle() method to implement communication to the client.
    """

    def handle(self):
	while 1:
	    #self.request is the TCP socket connected to the client 
	    self.data = self.request.recv(1024).strip()
	    print "{} wrote:".format(self.clent_address[0])
	    print self.data
	    #中just send back the same data ,but upper-cased


if __name__ == "__main__":
    HOST,PORT="localhost",24055

    #Create the server,binding to localhoston port 24055
    server=SocketServer.TCPServer((HOST,PORT),MyTcpHandler)

    #Activate the server,this will keep running until you interrupt the program with Ctrl-C
    server.serve_forever()
