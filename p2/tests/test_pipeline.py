#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import logging
from p2 import util
from p2 import const as C
from p2 import pipeline as pl

"""
python -m pytest -s --log-cli-level=DEBUG tests/test_pipeline.py
"""

log = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Before Test
    yield
    util.delete_file(C.DATA_FILE_PATH)
    util.delete_file(C.DF_Y_TMP_PATH)
    util.delete_file(C.DF_X_TMP_PATH)
    util.delete_file(C.MD_FILE_PATH)


def test_full_pipeline():
    """
    # Unit Test
    python -m pytest -s --log-cli-level=DEBUG \
        tests/test_pipeline.py::test_full_pipeline
    """
    pl.execute_full_pipeline()
