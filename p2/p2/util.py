#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import psutil
import os

log = logging.getLogger(__name__)


def get_duration_msg(start_time: time):
    end_time = time.time()
    return '{} seconds'.format(round(end_time - start_time))


def store_metric(metrics: dict):
    log.info(('metrics:', metrics))


def file_exists_check(path, error_msg='File Not Found'):
    if path and not os.path.exists(path):
        raise Exception('{} - {}'.format(error_msg, path))
    return True


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)


def get_memroy_percent():
    return psutil.virtual_memory()[2]