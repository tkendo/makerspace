# runserver.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release


from lockout import app
#import logging
#from lockout.functions import *

#app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(host='192.168.2.5', port=80, debug = True)

    # this probably needs to go somewhere else TODO tk
#    create_tables()

    #app.run(host='127.0.0.1', port=80) #, debug = True)
    # app.run()
