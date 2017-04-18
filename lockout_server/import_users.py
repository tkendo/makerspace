# import_users.csv
# Used to import users into the system and authorize them
# for access to specific machines
#
# Input File Format:
# CSV, where 1 header row will be ignored.
# Each of the remaining rows should be of the format:
#
# username, email_address, student_ID_number, machines
#
# where machines is a spaced seperated list containing each of the 
# node numbers that the user should be allowed access to.

import csv
import sys
import sqlite3

DATABASE = 'maker.sqlite'

def write_db(query, args=(), one=False):
    cur = db.execute(query, args)
    rv = cur.fetchall()
    db.commit()
    cur.close()
    return cur.rowcount

def query_db(query, args=(), one=False):
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


if len(sys.argv) < 2:
    print 'Error! Requires CSV input filename as argument'
    print 'Sample usage: python', str(sys.argv[0]), 'inputfile.csv'
    sys.exit()

# connect to database
db = sqlite3.connect(DATABASE)

# open and parse file
with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    next(reader, None) # skip header row

    for row in reader:
        
        print 'Adding User | uname:', row[0], ' email:', row[1], ' ID:', row[2]  

        # check to see if the user already exists in the database        
        t = (row[2],)
        res = query_db('SELECT user_id FROM users WHERE stu_id_hash = ?', t)
        if len(res) > 0:
            print 'Error! Duplicate Student ID value exists in database'
            print 'User add failed'
            continue

        t = (row[2], row[0], row[1])
        write_db('INSERT INTO users VALUES (null, ?, ?, ?, 0)', t)

        # get user_id of user we just added above based on username
        t = (row[0],)
        res = query_db('SELECT user_id FROM users WHERE uname = ? ORDER BY user_id DESC', t)
 
        if len(res) < 1:
            print 'Error! User add failed'
            continue
           
        user_id = res[0][0]

        # tokenize space delimited list of nodes
        toks = row[3].split()
        for tok in toks:
            print '  Authorizing Node:', tok

            # get node_id from database based on node_num
            t = (int(tok),)
            res = query_db('SELECT node_id from nodes where node_num = ?', t)

            if len(res) < 1:
                print 'Warning! Unrecognized Node:', tok
                continue
           
            node_id = res[0][0]

            # write the authentication record to the database
            t = (user_id, node_id)
            res = write_db('INSERT INTO auth VALUES (null, ?, ?, 0, 0)', t)
            if res != 1:
                print 'Warning! Database error writing authentication record'

