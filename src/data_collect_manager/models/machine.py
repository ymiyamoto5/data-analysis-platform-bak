from data_collect_manager.models.db import db


class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(db.Integer, primary_key=True)
    machine_name = db.Column(db.String(255), unique=True, nullable=False)
