import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../../"))

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal


def main(machine_id: str):
    db = SessionLocal()

    machine = CRUDMachine.select_by_id(db, machine_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--machine", help="set machine_id", required=True)
    args = parser.parse_args()
    machine_id: str = args.machine

    main(machine_id)
