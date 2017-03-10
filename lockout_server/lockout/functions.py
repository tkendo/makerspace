# functions.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release

from sqlite3 import connect

from lockout import max_rows

# TODO tk: is this really the best way to establish the DB connection ?
conn = connect('maker.sqlite')
cur = conn.cursor()

# Creates initial database tables
def create_tables():
    cur.execute('CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY,'
                'stu_id_hash TEXT, uname TEXT, email TEXT, is_admin INT)')
    
    cur.execute('CREATE TABLE IF NOT EXISTS nodes(node_id INTEGER PRIMARY KEY NOT NULL,'
                'node_num INT, node_type INT, ip_addr TEXT, timeout INT,'
                'name TEXT, status INT)')
    
    cur.execute('CREATE TABLE IF NOT EXISTS auth(auth_id INT PRIMARY KEY,'
                'user_id INT, node_id INT,'
                'FOREIGN KEY(user_id) REFERENCES users(user_id),'
                'FOREIGN KEY(node_id) REFERENCES nodes(node_id))')
    
    cur.execute('CREATE TABLE IF NOT EXISTS checkouts(checkout_id INT PRIMARY KEY,'
                'user_id INT, node_id INT,'
                'start_time INT, end_time INT,'
                'FOREIGN KEY(user_id) REFERENCES users(user_id),'
                'FOREIGN KEY(node_id) REFERENCES nodes(node_id))')

    cur.execute('CREATE TABLE IF NOT EXISTS log(log_id INT PRIMARY KEY,'
                'user_id INT, node_id INT,'
                'timestamp INT, msgcode INT,'
                'FOREIGN KEY(user_id) REFERENCES users(user_id),'
                'FOREIGN KEY(node_id) REFERENCES nodes(node_id))')

def add_node(nd_num, nd_type, ip_addr, name, timeout = 0):
    t = (nd_num, nd_type, ip_addr, name, timeout)
    cur.execute('INSERT INTO nodes'
                '(node_id, node_num, node_type, ip_addr, name, timeout, status)'
                'VALUES (NULL,?,?,?,?,?,0)', t)
    conn.commit()

def get_node_status(nd_ip_addr):
    t = (nd_ip_addr,)
    cur.execute('SELECT status from nodes WHERE ip_addr = ?', t)
    res = cur.fetchone()
    return res
    
def set_node_status(nd_num, status):
    t = (status, nd_num)
    cur.execute('UPDATE nodes SET status = ? WHERE node_num = ?', t)
    
    conn.commit()
    return cur.rowcount


