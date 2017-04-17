# views.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release

from flask import render_template, request, Response
from serial import Serial

from lockout import app
from lockout.forms import *
from lockout.functions import *

import sys
import datetime

LOG_MSGCODE_AUTH_DENY  = 1
LOG_MSGCODE_AUTH_GRANT = 2
LOG_MSGCODE_UNKNOWN_ID = 3 
LOG_MSGCODE_LOCK_NODE  = 4 

@app.route('/')
@app.route('/index')
@app.route('/systemstatus')
def index():
    return render_template('systemstatus.html')

def decode_mach_status(mach_status):
    if(mach_status == 0):
        return "Locked"
    elif(mach_status == 1):
        return "Unlocked"
    else:
        return "Error"

@app.route('/machines')
def machines():
    machs = get_machs()
    machs = [m + (decode_mach_status(m[2]),) for m in machs]

    return render_template('machines.html', machs=machs)

def make_timestamp(unixTime):
    return datetime.datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d %H:%M:%S') 

def decode_msgcode(msgCode):
    if(msgCode == LOG_MSGCODE_LOCK_NODE):
        return "Machine Locked"
    elif(msgCode == LOG_MSGCODE_AUTH_GRANT):
        return "Machine Unlocked"   
    elif(msgCode == LOG_MSGCODE_AUTH_DENY):
        return "Failed Authentication"   
    elif(msgCode == LOG_MSGCODE_UNKNOWN_ID):
        return "Unrecognized ID"   
    else:
        return "Invalid MessageCode" 

@app.route('/systemlog')
def systemlog():
    log = get_log()
    log = [l + (make_timestamp(l[3]),decode_msgcode(l[4])) for l in log]
    return render_template('systemlog.html', log=log)


@app.route('/users')
def users():
    users = get_users()

    usrs = [usr + (get_auth_by_user(usr[0]),) for usr in users]
    
    return render_template('users.html', users=usrs)


@app.route('/logfile.csv')
def logfile():

    log = get_log_all()
    log = [l + (make_timestamp(l[3]),decode_msgcode(l[4])) for l in log]
    
    def generate():
        yield 'log_id,user_id,node_id,unix_time,msgcode,msgdata,username,nodename,timestamp,message\n'
        for l in log:
            yield ','.join(map(str, l)) + '\n'

    return Response(generate(), mimetype='text/csv')
