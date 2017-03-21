import server_actors
import sqlite3
import pykka

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

def log_event():
    print 'log'


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
    

def handle_auth_req(auth_req):
#    print 'Controller: handle_auth_req'
#    print auth_req
    stu_id = auth_req[1]
    node_num = auth_req[0]

    uid = get_userid(stu_id)
    if uid == -1:
        #print 'controller: Unrecognized student ID'
        # TODO log to database
        response = server_actors.AuthDeny
        reply_to_ui(server_actors.UIActor_auth, response)
        return

    nid = get_nodeid(node_num)
    if nid == -1:
        #print 'controller: Unrecognized node ID'
        # TODO log to DB
        response = server_actors.AuthError
        reply_to_ui(server_actors.UIActor_auth, response)
        return

    auth = get_authorization(uid, nid)
    if auth == -1:
        #print 'controller: User not authorized for this training level'
        # TODO log to DB
        response = server_actors.AuthDeny
    else:
        #print 'controller: Access Granted!'
        # TODO log to DB
        set_node_status(nid, 1) 
        response = server_actors.AuthApprove

    reply_to_ui(server_actors.UIActor_auth, response)

def relock_mach(mach_num):
    #print 'controller: relock'
    #print mach_num
    res = set_node_status(get_nodeid(mach_num), 0)
    
    if res != 1:
        print 'controller: Failed to set node status'

     
