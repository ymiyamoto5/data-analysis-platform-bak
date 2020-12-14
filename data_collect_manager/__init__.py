from flask import Flask

app = Flask(__name__)
app.config.from_object("data_collect_manager.config")

import data_collect_manager.views
