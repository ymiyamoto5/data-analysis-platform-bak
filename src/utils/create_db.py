import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from data_collect_manager.models.machine import Machine
from data_collect_manager.models.machine_type import MachineType
from data_collect_manager.models.db import register_db
from flask import Flask

app = Flask("app")
db = register_db(app)
db.drop_all()
db.create_all()

machine_type_01 = MachineType(machine_type_name="プレス")
machine_type_02 = MachineType(machine_type_name="圧力プレート")

db.session.add(machine_type_01)
db.session.add(machine_type_02)

machine_01 = Machine(machine_name="テストプレス01", machine_type_id=1)
machine_02 = Machine(machine_name="テストプレス02", machine_type_id=1)
machine_03 = Machine(machine_name="テスト圧力プレート01", machine_type_id=2)

db.session.add(machine_01)
db.session.add(machine_02)
db.session.add(machine_03)
db.session.commit()

for m in Machine.query.all():
    print(vars(m))
