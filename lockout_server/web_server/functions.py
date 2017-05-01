# functions.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release

import sqlite3
from flask import g

from web_server import app

DATABASE = 'maker.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
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

# Creates initial database tables
def create_tables():
    write_db('CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY NOT NULL,'
                'stu_id_hash TEXT, uname TEXT, email TEXT, is_admin INTEGER)')
    
    write_db('CREATE TABLE IF NOT EXISTS nodes(node_id INTEGER PRIMARY KEY NOT NULL,'
                'node_num INTEGER, node_type INTEGER, ip_addr TEXT, timeout INTEGER,'
                'name TEXT, status INTEGER)')
    
    write_db('CREATE TABLE IF NOT EXISTS auth(auth_id INTEGER PRIMARY KEY NOT NULL,'
                'user_id INTEGER, node_id INTEGER,'
                'start_date INTEGER, end_date INTEGER,'
                'FOREIGN KEY(user_id) REFERENCES users(user_id),'
                'FOREIGN KEY(node_id) REFERENCES nodes(node_id))')
    
    write_db('CREATE TABLE IF NOT EXISTS checkouts(checkout_id INTEGER PRIMARY KEY NOT NULL,'
                'user_id INTEGER, node_id INTEGER,'
                'start_time INTEGER, end_time INTEGER,'
                'FOREIGN KEY(user_id) REFERENCES users(user_id),'
                'FOREIGN KEY(node_id) REFERENCES nodes(node_id))')

    write_db('CREATE TABLE IF NOT EXISTS log(log_id INTEGER PRIMARY KEY NOT NULL,'
                'user_id INTEGER, node_id INTEGER,'
                'timestamp INTEGER, msgcode INTEGER, msgdata TEXT,'
                'FOREIGN KEY(user_id) REFERENCES users(user_id),'
                'FOREIGN KEY(node_id) REFERENCES nodes(node_id))')

def add_node(nd_num, nd_type, ip_addr, name, timeout = 0):
    t = (nd_num, nd_type, ip_addr, name, timeout)
    res = write_db('INSERT INTO nodes'
                '(node_id, node_num, node_type, ip_addr, name, timeout, status)'
                'VALUES (NULL,?,?,?,?,?,0)', t)
    return res


def get_node_status(nd_ip_addr):
    t = (nd_ip_addr,)
    res = query_db('SELECT status from nodes WHERE ip_addr = ?', t)
    return res

def get_log(record_limit):
    t = (record_limit,)

    res = query_db('SELECT log_id, log.user_id, log.node_id, timestamp, msgcode, msgdata, users.uname, nodes.name from log LEFT OUTER JOIN users ON users.user_id = log.user_id LEFT OUTER JOIN nodes ON nodes.node_id = log.node_id ORDER BY log_id DESC LIMIT ?', t)
    return res

def get_log_all():
    res = query_db('SELECT log_id, log.user_id, log.node_id, timestamp, msgcode, msgdata, users.uname, nodes.name from log LEFT OUTER JOIN users ON users.user_id = log.user_id LEFT OUTER JOIN nodes ON nodes.node_id = log.node_id ORDER BY log_id ASC')
    return res

def get_users():
    res = query_db('SELECT user_id, uname, email from users')

    return res

def get_machs():
    res = query_db('SELECT node_num, name, status FROM nodes ORDER BY node_num ASC')

    return res
    
   
def get_auth_by_user(user_id):
    t = (user_id,)
    res = query_db('SELECT nodes.node_num from auth LEFT OUTER JOIN nodes ON nodes.node_id = auth.node_id WHERE user_id = ? ORDER BY nodes.node_num ASC', t)

    return res
 
def set_node_status(nd_num, status):
    t = (status, nd_num)
    res = write_db('UPDATE nodes SET status = ? WHERE node_num = ?', t)
    return res



