# """
#  ==================================
#   conftest.py
#  ==================================

#   Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
#   CONFIDENTIAL
#   Author: UNIADEX, Ltd.

# """

# import pytest
# import os
# import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
# from backend.data_collect_manager import app


# @pytest.fixture
# def client():
#     app.config["TESTING"] = True
#     client = app.test_client()

#     yield client
