# views.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release

from flask import render_template, request
from serial import Serial

from lockout import app
from lockout.forms import *
from lockout.functions import *

import sys


#@app.route('/')
#def index():
#    return render_template('index.html')


@app.route('/unlock', methods=['POST'])
def send_unlock():
    if request.method == 'POST':
        sys.stdout.write("RX Request: ip=" + request.remote_addr)
        sys.stdout.write(" data=" + request.get_data(as_text=True) + "\n")
        sys.stdout.write("arg=" + request.form['arg'] + "\n")

        status = get_node_status(request.remote_addr)

        reply = "status\n0"
        
        if status == None:
            print "Machine not found!" # TODO handle error
        else:
            reply = "status\n" + str(status[0])

        sys.stdout.write("reply=" + reply + "\n")
        return reply

#        return "beepflash\n1" 

@app.route('/setlock', methods=['POST'])
def set_lock():
    if request.method == 'POST':
        sys.stdout.write("SetLock Request. ip=" + request.remote_addr)
        sys.stdout.write(" node=" + request.form['node'])
        sys.stdout.write(" lock=" + request.form['lock'] + "\n")

        node = int(request.form['node'])
        setval = int(request.form['lock'])

        if setval == 1 or setval == 0:
            retval = set_node_status(node, setval)
            if retval != 1:
                print "Database error"
        else:
            retval = 0
            print "Invalid lock value specified"

        return str(retval) 

