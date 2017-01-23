# runserver.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release


from lockout import app

if __name__ == "__main__":
    app.run(host='192.168.1.2', port=80)
    # app.run()
