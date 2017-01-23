from flask import render_template, request
from serial import Serial

from lockout import app
from lockout.forms import *
from lockout.functions import *


@app.route('/')
def index():
    return render_template('index.html')


# Handle all incoming requests from client machines
# HTTP method expected: POST ?userid=USERID&machineid=MACHINEID
@app.route('/request', methods=['POST'])
def send_request():
    if request.method == 'POST':
        if request.form['userid'] != '':
            log_checkout(request.form['userid'], request.form['machineid'])
            if is_checked_out(request.form['userid'], request.form['machineid']):
                transact_checkin(request.form['machineid'])
                return '1'
            else:
                if valid_checkout(request.form['userid'], request.form['machineid']):
                    transact_checkout(request.form['userid'], request.form['machineid'])
                    return '1'
                else:
                    return '0'


# Interface to add users
# Displays a web form to add users, a table of all users, and a web form to delete users
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    adduserform = AddUserForm()
    removeuserform = RemoveUserForm()
    status = ''

    if request.method == 'POST':
        t = (request.form['userid'], request.form['username'], request.form['email'])
        cur.execute('INSERT INTO users (userid, username, email) VALUES (?, ?, ?)', t)
        conn.commit()
        status = 'Added user'

    cur.execute('SELECT * FROM users')
    table = cur.fetchall()
    return render_template('add-user.html', adduserform=adduserform, removeuserform=removeuserform, status=status,
                           table=table)


# Handles requests to remove users
@app.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
    adduserform = AddUserForm()
    removeuserform = RemoveUserForm()
    status = ''

    if request.method == 'POST':
        t = (request.form['userid'],)
        cur.execute('DELETE FROM users WHERE userid=?', t)
        conn.commit()
        status = 'Removed user'

    cur.execute('SELECT * FROM users')
    table = cur.fetchall()
    return render_template('add-user.html', adduserform=adduserform, removeuserform=removeuserform, status=status,
                           table=table)


# Different path to handle requests to scan cards on the add user page
# Allows users to scan cards over a serial interface, and will input that data into the form
# Renders the same page as the add user page
@app.route('/scan', methods=['GET'])
def scan():
    form = AddUserForm()
    status = ''

    rfid = ''
    data = ''
    serial = Serial("/dev/ttyUSB0", baudrate=9600)
    while data != b'\r':
        data = serial.read()
        rfid += data.decode(encoding='UTF-8')

    form.userid.data = rfid[1:]
    cur.execute('SELECT * FROM users')
    table = cur.fetchall()

    return render_template('add-user.html', form=form, status=status, table=table)


# Interface to add training records
# Displays a web form to lookup userids, a lookup result table,
# a web form to add training records, a table of all training records,
# and a web form to delete training records.
@app.route('/add_training', methods=['GET', 'POST'])
def add_training():
    addtrainingform = AddOrRemoveTrainingForm()
    removetrainingform = AddOrRemoveTrainingForm()
    lookupform = LookupUserForm()
    status = ''
    if request.method == 'POST':
        t = (request.form['userid'], request.form['machineid'])
        cur.execute('INSERT INTO training (userid, machineid) VALUES (?, ?)', t)
        conn.commit()
        status = 'Added training'
    cur.execute("""SELECT training.userid, users.username, users.email, machines.machineid, machines.machinename
                   FROM training
                   INNER JOIN users ON training.userid = users.userid
                   INNER JOIN machines ON training.machineid = machines.machineid""")
    table = cur.fetchall()
    lookuptable = []
    return render_template('add-training.html', addtrainingform=addtrainingform, removetrainingform=removetrainingform,
                           lookupform=lookupform, status=status, table=table, lookuptable=lookuptable)


# Handles requests to remove machines
@app.route('/remove_training', methods=['GET', 'POST'])
def remove_training():
    addtrainingform = AddOrRemoveTrainingForm()
    removetrainingform = AddOrRemoveTrainingForm()
    lookupform = LookupUserForm()
    status = ''
    if request.method == 'POST':
        t = (request.form['userid'], request.form['machineid'])
        cur.execute('DELETE FROM training WHERE userid=? AND machineid=?', t)
        conn.commit()
        status = 'Removed training'
    cur.execute("""SELECT training.userid, users.username, users.email, machines.machineid, machines.machinename
                   FROM training
                   INNER JOIN users ON training.userid = users.userid
                   INNER JOIN machines ON training.machineid = machines.machineid""")
    table = cur.fetchall()
    lookuptable = []
    return render_template('add-training.html', addtrainingform=addtrainingform, removetrainingform=removetrainingform,
                           lookupform=lookupform, status=status, table=table, lookuptable=lookuptable)


# Different path to handle requests made by the lookup user interface on the add training page
# Renders exactly the same page as the add training page
@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    addtrainingform = AddOrRemoveTrainingForm()
    removetrainingform = AddOrRemoveTrainingForm()
    lookupform = LookupUserForm()
    status = ''
    cur.execute("""SELECT training.userid, users.username, users.email, machines.machineid, machines.machinename
                   FROM training
                   INNER JOIN users ON training.userid = users.userid
                   INNER JOIN machines ON training.machineid = machines.machineid""")
    table = cur.fetchall()
    t = ("%" + request.form['username'] + "%", "%" + request.form['email'] + "%",)
    cur.execute("""SELECT * FROM users
                   WHERE users.username LIKE ? AND users.email LIKE ? COLLATE NOCASE""", t)
    lookuptable = cur.fetchall()
    return render_template('add-training.html', addtrainingform=addtrainingform, removetrainingform=removetrainingform,
                           lookupform=lookupform, status=status, table=table, lookuptable=lookuptable)


# Displays interface to add machines
# Shows a web form to add machines, a table of all machine records, and a form to delete machines
@app.route('/add_machine', methods=['GET', 'POST'])
def add_machine():
    addmachineform = AddMachineForm()
    removemachineform = RemoveMachineForm()
    status = ''
    if request.method == 'POST':
        t = (request.form['machineid'], request.form['machinename'])
        cur.execute('INSERT INTO machines (machineid, machinename) VALUES (?, ?)', t)
        conn.commit()
        status = 'Added machine'
    cur.execute('SELECT * FROM machines')
    table = cur.fetchall()
    return render_template('add-machine.html', addmachineform=addmachineform, removemachineform=removemachineform,
                           status=status, table=table)


# Handles requests to remove machines
@app.route('/remove_machine', methods=['GET', 'POST'])
def remove_machine():
    addmachineform = AddMachineForm()
    removemachineform = RemoveMachineForm()
    status = ''
    if request.method == 'POST':
        t = (request.form['machineid'],)
        cur.execute('DELETE FROM machines WHERE machineid=?', t)
        conn.commit()
        status = 'Removed machine'
    cur.execute('SELECT * FROM machines')
    table = cur.fetchall()
    return render_template('add-machine.html', addmachineform=addmachineform, removemachineform=removemachineform,
                           status=status, table=table)


# Displays the complete log of all requests
@app.route('/view_log', methods=['GET', 'POST'])
def view_log():
    cur.execute("""SELECT log.requesttime, log.userid, users.username, users.email, log.machineid, machines.machinename FROM log
                   INNER JOIN users ON log.userid = users.userid
                   INNER JOIN machines ON log.machineid = machines.machineid
                   ORDER BY requesttime DESC""")
    table = cur.fetchall()
    return render_template('view-log.html', table=table)
