import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from data_collect_manager.models.machine import Machine
from data_collect_manager.models.db import db, register_db
from flask import Flask

app = Flask("app")
db = register_db(app)
db.create_all()

machine_01 = Machine(id=1, machine_name="test_machine_01")
machine_02 = Machine(id=2, machine_name="test_machine_02")

db.session.add(machine_01)
db.session.add(machine_02)
db.session.commit()

for m in Machine.query.all():
    print(vars(m))
