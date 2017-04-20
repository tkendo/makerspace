import server_actors
import sqlite3
import pykka
import SocketServer
import sys
from datetime import datetime

DATABASE = '../maker.sqlite'

db = None

def get_db():
    global db
    if db is None:
        db = sqlite3.connect(DATABASE)
    return db 

def close_db():
    global db
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_node_status(nd_ip_addr):
    t = (nd_ip_addr,)
    res = query_db('SELECT status FROM nodes WHERE ip_addr = ?', t)

    return res[0][0] if len(res) > 0 else -1

class nodeHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print "Request from: {}".format(self.client_address[0])
        print str(datetime.now()) 
        client_ip = self.client_address[0]

        status = get_node_status(client_ip)

        reply = "status:0"
        if status == -1:
            print "Machine not found!"
        else:
           reply = "status:" + str(status)

        sys.stdout.write("reply=" + reply + "\n") 
        self.request.sendall(reply) 
 
def init_node_server():
    HOST, PORT = "192.168.2.6", 6000 

    SocketServer.TCPServer.allow_resuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), nodeHandler)

    server.serve_forever()
     
