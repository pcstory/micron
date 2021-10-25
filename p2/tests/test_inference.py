#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import logging
from p2 import data_eng as de
from p2 import model_build as mb
from p2 import inference as inf
from p2 import util
from p2 import const as C

"""
# Module Unit Test Command:
python -m pytest -s --log-cli-level=DEBUG tests/test_inference.py
"""

log = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    de.fetch_data_from_mssql()
    de.process_data()
    mb.build_model()
    yield
    util.delete_file(C.DATA_FILE_PATH)
    util.delete_file(C.DF_Y_TMP_PATH)
    util.delete_file(C.DF_X_TMP_PATH)
    util.delete_file(C.MD_FILE_PATH)


def test_inference():
    """
    # Unit Test Command:
    python -m pytest -s tests/test_inference.py::test_inference \
    --log-cli-level=DEBUG
    """
    inf.batch_inference(is_test=True)

