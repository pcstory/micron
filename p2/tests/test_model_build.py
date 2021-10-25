#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import logging
import os
from p2 import util
from p2 import const as C
from p2 import model_build as mb
from p2 import data_eng as de

"""
python -m pytest -s --log-cli-level=DEBUG tests/test_model_build.py
"""

log = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    de.fetch_data_from_mssql()
    de.process_data()
    yield
    util.delete_file(C.DATA_FILE_PATH)
    util.delete_file(C.DF_Y_TMP_PATH)
    util.delete_file(C.DF_X_TMP_PATH)
    util.delete_file(C.MD_FILE_PATH)
    pass


def test_build_model():
    """
    # Unit Test
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_model_build.py::test_build_model
    """
    mb.build_model(enable_tunning=False)


def test_build_model_tunning():
    """
    # Unit Test
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_model_build.py::test_build_model_tunning
    """
    mb.build_model(enable_tunning=True)


def test_build_model_with_df_override():
    """
    # Unit Test
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_model_build.py::test_build_model_with_df_override
    """
    test_data_file = '../Q6_data.csv'
    _, X, y = de.process_data(data_file_path=test_data_file)
    result, classifier = mb.build_model(X_override=X, y_override=y)

    # Check result list
    assert result is not None
    assert classifier is not None

    # Check model save
    assert result['model_save_path'] is not None
    assert os.path.exists(result['model_save_path']) is True

    # Check metrics
    assert result['confusion_matrix'] is not None
    assert result['score'] is not None

