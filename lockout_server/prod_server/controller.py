
import sqlite3

DATABASE = '../maker.sqlite'

# TODO this probably shouldn't be a global.. 
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

def get_authorization(user_id, node_id):
    t = (user_id, node_id)
    res = query_db('SELECT start_date, end_date FROM auth WHERE user_id = ? AND node_id = ?', t)

    return res[0] if len(res) > 0 else -1

def set_node_status(node_id, status):
    t = (status, node_id)
    res = write_db('UPDATE nodes SET status = ? WHERE node_id = ?', t)
    
    return res

def handle_auth_req(auth_req):
#    print 'Controller: handle_auth_req'
#    print auth_req
    stu_id = auth_req[1]
    node_num = auth_req[0]

    uid = get_userid(stu_id)
    if uid == -1:
        print 'Unrecognized student ID'
        # TODO signal error to UI and log to database
        return

    nid = get_nodeid(node_num)
    if nid == -1:
        print 'Unrecognized node ID'
        # TODO signal to UI and log to DB
        return

    auth = get_authorization(uid, nid)
    if auth == -1:
        print 'User not authorized for this training level'
        # TODO signal to UI and log to DB
    else:
        print 'Access Granted!'
        # TODO signal to UI and log to DB
        
        set_node_status(nid, 1) 
     
