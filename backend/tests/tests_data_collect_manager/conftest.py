# """
#  ==================================
#   conftest.py
#  ==================================

#   Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
#   CONFIDENTIAL
#   Author: UNIADEX, Ltd.

# """

import pytest

from backend.data_collect_manager.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()

    yield client
