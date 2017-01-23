# __init__.py
#
# Authors: Evan Cooper
#          Jack Watkin
#
#   Date    Version   Initials  Comments
#-------------------------------------------
#  20Jan17  01.00.00  EC       Initial release


from flask import Flask

app = Flask(__name__)

max_rows = 3

import lockout.views
