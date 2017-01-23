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

conn = connect('/home/pi/server/lockout.sqlite')
cur = conn.cursor()


# Adds a checkout to the log
def log_checkout(userid, machineid):
    t = (userid, machineid,)
    cur.execute('INSERT INTO log (requesttime, userid, machineid) VALUES (CURRENT_TIMESTAMP, ?, ?)', t)
    conn.commit()


# Checks to see if a checkout is valid
def valid_checkout(userid, machineid):
    if trained(userid, machineid):
        cur.execute('SELECT * FROM checkouts WHERE userid=?', (userid,))
        if len(cur.fetchall()) < max_rows:
            return True
        else:
            return False
    else:
        return False


# Checks to see it a user is trained
def trained(userid, machineid):
    t = (userid, machineid,)
    cur.execute('SELECT * FROM training WHERE userid=? AND machineid=?', t)
    if cur.fetchone():
        return True
    else:
        return False


# Adds a checkout to the checkouts table
def transact_checkout(userid, machineid):
    t = (userid, machineid,)
    if is_checked_out(userid, machineid):
        return
    else:
        cur.execute('INSERT INTO checkouts (checkouttime, userid, machineid) VALUES (CURRENT_TIMESTAMP, ?, ?)', t)
        conn.commit()


# Checks to see if a user already has a particular machine checked out
def is_checked_out(userid, machineid):
    t = (userid, machineid,)
    cur.execute('SELECT * FROM checkouts WHERE userid=? AND machineid=?', t)
    if cur.fetchone():
        return True
    else:
        return False


# Removes a checkout from the checkouts table
def transact_checkin(machineid):
    t = (machineid,)
    cur.execute('DELETE FROM checkouts WHERE machineid=?', t)
    conn.commit()
