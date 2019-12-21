#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio OSC module (with pyOSC)
#install pyOSC from https://pypi.org/project/pyOSC/
#auther: mizumasa

import os
import sys
import time, threading
import OSC

class TOIO_OSC:
    def __init__(self):
        self.ip = ""
        self.host = ""
        self.dst = []
        self.serverMode = False
        self.clientMode = False
        self.bArrived = False
        self.serverFunc = {}
        return

    def setServerFunc(self,funcName,func):
        self.serverFunc[funcName] = func

    def workAsServer(self,ip,host):
        self.serverMode = True
        self.ip = ip
        self.host = host
        print "work as remote server",ip,host
        return
    def workAsLocalServer(self,host):
        self.serverMode = True
        self.ip = "127.0.0.1"
        self.host = host
        print "server works in localhost"
        return

    def addDst(self,ip,host):
        self.clientMode = True
        self.dst.append((ip,host))
    def addLocalDst(self,host):
        print "client works in localhost"
        self.clientMode = True
        self.dst.append(("127.0.0.1", host))
    def clearDst(self):
        self.dst = []
        return

    def light_handler(self, addr, tags, data, client_address):
        print "(tags, data): (%s, %s)" % (tags, data)
        if "light" in self.serverFunc:
            self.serverFunc["light"](0,0,data[0],data[1],data[2])
 
    def touch_handler(self, addr, tags, data, client_address):
        print "touch_handler (tags, data): (%s, %s)" % (tags, data)
        self.bArrived = True
        self.recv = ["touch",]+data
    def myMsg_handler(self, addr, tags, data, client_address):
        print "(tags, data): (%s, %s)" % (tags, data)
        self.bArrived = True
        self.recv = data[0]

    def setup(self):
        if self.serverMode:
            print "setup server",self.ip,self.host
            self.server = OSC.OSCServer((self.ip,self.host))
            self.server.addDefaultHandlers()
            self.server.addMsgHandler("/light", self.light_handler)
            #self.server.addMsgHandler("/msg", self.myMsg_handler)
            #self.server.addMsgHandler("/touch/position", self.touch_handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.start()
        if self.clientMode:
            print "setup client",self.dst
            self.client = OSC.OSCClient()
        return

    def get(self):
        if self.serverMode:
            if self.bArrived:
                print "got",self.recv
                ret = self.recv
                self.recv = ""
                self.bArrived = False
                return ret
            return None
    def kill(self):
        if self.serverMode:
            try:
                self.server.close()
                print "server closed 1"
                self.server_thread.join()
            except:
                print "first error"
                try:
                    self.server.close()
                    print "server closed 2"
                    self.server_thread.join()
                except:
                    print "seccond error"
                    pass
                pass
    def sendMsg(self,content):
        if self.clientMode:
            msg = OSC.OSCMessage("/msg")
            msg.append(content)
            for i in self.dst:
                try:
                    print "send to ",i
                    self.client.sendto(msg, i)
                except:
                    print "first error"
                    try:
                        self.client.sendto(msg, i)
                    except:
                        print "seccond error"
                        pass
        else:
            print "not client mode"
        return
    def send(self):
        if self.clientMode:
            msg = OSC.OSCMessage("/print")
            msg.append(int(time.time()))
            for i in self.dst:
                try:
                    self.client.sendto(msg, i)
                except:
                    print "first error"
                    try:
                        self.client.sendto(msg, i)
                    except:
                        print "seccond error"
                        pass
        else:
            print "not client mode"
        return

def main():
    pass

if __name__ == '__main__':
    main()


