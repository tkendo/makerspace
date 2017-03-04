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

i = 0

#@app.route('/')
#def index():
#    return render_template('index.html')


@app.route('/unlock', methods=['POST'])
def send_unlock():
    global i
#    print "%d" % i
    if request.method == 'POST':
        sys.stdout.write("RX Request: ip=" + request.remote_addr)
        sys.stdout.write(" data=" + request.get_data(as_text=True) + "\n")
        print request.form['arg']
        i = not i 
    
        if i == 1:
            return "status\n1"
        return "beepflash\n1" 
    else:
        print "not post"

