#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import logging
import os
from p2 import data_eng as data_eng

"""
Unit Test - Module Level
python -m pytest -s --log-cli-level=INFO tests/test_data_eng.py
"""

log = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Before Test
    # yield
    # After Test
    pass


def test_fetch_data_from_mssql():
    """
    Command:
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_data_eng.py::test_fetch_data_from_mssql
    """
    result = data_eng.fetch_data_from_mssql()
    log.debug(result)
    assert result is not None
    assert result['status'] is True
    assert os.path.exists(result['path'])


def test_data_file_check():
    """
    Command:
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_data_eng.py::test_data_file_check
    """
    test_data_file = '../Q6_data.csv'
    result, df = data_eng.data_file_check(data_file_path=test_data_file)
    log.debug(result)
    assert result is not None
    assert df is not None
    assert result['status'] is True


def test_process_data():
    """
    Command:
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_data_eng.py::test_process_data
    """
    test_data_file = '../Q6_data.csv'
    result, X, y = data_eng.process_data(data_file_path=test_data_file)
    log.debug(result)

    assert result is not None
    assert result['status'] is True
    assert X is not None
    assert y is not None
