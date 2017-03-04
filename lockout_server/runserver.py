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

#app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(host='192.168.2.5', port=80, debug = True)
    # app.run()
