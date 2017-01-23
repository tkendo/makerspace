from flask import Flask

app = Flask(__name__)

max_rows = 3

import lockout.views
