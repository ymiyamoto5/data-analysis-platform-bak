"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
from backend.app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    client = TestClient(app)

    yield client
