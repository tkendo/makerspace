import server_actors
import sqlite3
import pykka
import time
from threading import Timer,Thread,Event
import os
import sys

DATABASE = '/home/pi/makerspace/lockout_server/maker.sqlite'

db = None

LOG_MSGCODE_AUTH_DENY  = 1
LOG_MSGCODE_AUTH_GRANT = 2
LOG_MSGCODE_UNKNOWN_ID = 3 
LOG_MSGCODE_LOCK_NODE  = 4 

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

def write_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    get_db().commit()
    cur.close()
    return cur.rowcount

# Returns the first integer record ID for a user corresponding to the string
# student ID passed as a parameter.
# Returns -1 if the student ID was not found in the database.
def get_userid(stu_id):
    t = (stu_id,)
    res = query_db('SELECT user_id FROM users WHERE stu_id_hash = ?', t)
    
    return res[0][0] if len(res) > 0 else -1

# Returns the first integer record ID for a node corresponding to the
# node number passed as node_num.
# Returns -1 if the node is not found in the database.
def get_nodeid(node_num):
    t = (node_num,)
    res = query_db('SELECT node_id FROM nodes WHERE node_num = ?', t)
    
    return res[0][0] if len(res) > 0 else -1

def get_node_type_and_timeout(node_id):
    t = (node_id,)
    res = query_db('SELECT node_type, timeout FROM nodes WHERE node_id = ?', t)
   
    return res[0] if len(res) > 0 else -1

def log_event(user_id, node_id, msgcode, msgdata):
    #print 'log> user:' + str(user_id) + ' node:' + str(node_id) + ' msgcode:' + str(msgcode) +  ' msgdata: ' + msgdata
    timestamp = int(time.time())
    t = (user_id, node_id, timestamp, msgcode, msgdata)
    res = write_db('INSERT INTO log VALUES (null, ?, ?, ?, ?, ?)', t)

    return res

# Returns -1 if the node is not found in the database.
def get_node_status(node_num):
    t = (node_num,)
    res = query_db('SELECT status FROM nodes WHERE node_num = ?', t)
    
    return res[0][0] if len(res) > 0 else -1

def get_authorization(user_id, node_id):
    t = (user_id, node_id)
    res = query_db('SELECT start_date, end_date FROM auth WHERE user_id = ? AND node_id = ?', t)

    return res[0] if len(res) > 0 else -1

def set_node_status(node_id, status):
    t = (status, node_id)
    res = write_db('UPDATE nodes SET status = ? WHERE node_id = ?', t)
    
    return res

def set_checkout(user_id, node_id):
    timestamp = int(time.time())
    t = (user_id, node_id, timestamp)
    res = write_db('INSERT INTO checkouts VALUES (null, ?, ?, ?, 0)', t)

    return res

def clear_checkout(node_id):
    t = (node_id,)
    res = write_db('DELETE FROM checkouts WHERE node_id = ?', t)

    return res

def reply_to_ui(msgtype, msgdata):
    ui_actor = pykka.ActorRegistry.get_by_class_name ( "UIActor" )
    
    for actor in ui_actor:
        actor.tell ( {'type' : msgtype, 'data' : msgdata} )
    

def get_mach_status(mach_num):
    status = get_node_status(mach_num)
     
    if status == -1:
        #print 'mach not found'
        response = server_actors.MachineInvalid 
    else:
        #print 'mach status' + str(status) 
        if status == 0:
            response = server_actors.MachineUnlock
        else:
            response = server_actors.MachineLock

    reply_to_ui(server_actors.UIActor_receive_mach_status, response)
    
# this will be in a child process !!
def relock_callback(node_id, timeout_secs):
    
    print 'Running callback: node = ' + str(node_id) + ' in time = ' + str(timeout_secs)
    time.sleep(timeout_secs)
    
    res = set_node_status(node_id, 0)
    log_event(None, node_id, LOG_MSGCODE_LOCK_NODE, 'Locked via timeout')
    if(res < 0):
        print 'Error clearing node'

    clear_checkout(node_id)

    # kill child process
    sys.exit(0) 

def handle_auth_req(auth_req):
    stu_id = auth_req[1]
    node_num = auth_req[0]

    uid = get_userid(stu_id)
    nid = get_nodeid(node_num)
 
    if uid == -1:
        #print 'controller: Unrecognized student ID'
        log_event(None, nid, LOG_MSGCODE_UNKNOWN_ID, ('Unknown User: ' + str(stu_id)))
        response = server_actors.AuthDeny
        reply_to_ui(server_actors.UIActor_auth, response)
        return

    #nid = get_nodeid(node_num)
    if nid == -1:
        #print 'controller: Unrecognized node ID'
        response = server_actors.AuthError
        reply_to_ui(server_actors.UIActor_auth, response)
        return

    (ntyp,timeout) = get_node_type_and_timeout(nid)

    # if node type is SOLENOID, we have to relock automatically
    if(ntyp == 1):
        ret = os.fork()
        if(ret == 0): # if child, run relock callback
            relock_callback(nid, timeout)
 
    auth = get_authorization(uid, nid)
    if auth == -1:
        #print 'controller: User not authorized for this training level'
        log_event(uid, nid, LOG_MSGCODE_AUTH_DENY, 'Denied')
        response = server_actors.AuthDeny
    else:
        #print 'controller: Access Granted!'
        log_event(uid, nid, LOG_MSGCODE_AUTH_GRANT, 'Authorized')
        set_node_status(nid, 1) 
        response = server_actors.AuthApprove
        set_checkout(uid, nid)

    reply_to_ui(server_actors.UIActor_auth, response)

def relock_mach(mach_num):
    #print 'controller: relock'
    #print mach_num
    nid = get_nodeid(mach_num)
    res = set_node_status(nid, 0)
    log_event(None, nid, LOG_MSGCODE_LOCK_NODE, 'Locked')
    
    clear_checkout(nid)   
 
    if res != 1:
        print 'controller: Failed to set node status'

     
