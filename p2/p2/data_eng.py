#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import time
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from sqlalchemy import create_engine
from . import util as ut
from . import const as C

log = logging.getLogger(__name__)


def fetch_data_from_mssql(data_file_path=C.DATA_FILE_PATH):
    """
    Fetch Data from MSSQL.
    Convert the file to store in local drive.

    Parameters:
        data_file_path (str):
            Save Data File location. (Default value refer to const.py)

    Returns:
        result (dict):
            Dictionary with metrics and status
    """
    time_start = time.time()
    log.info('Fetch Data from MSSQL')
    sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/micron',
                              pool_recycle=3600)
    with sqlEngine.connect() as db_connection:
        # Fetch input from DB
        df = pd.read_sql('select * from q6_data', db_connection)
        df.to_csv(data_file_path, index=False, mode='w')
    duration = ut.get_duration_msg(time_start)
    log.info('Fetch Data from MSSQL Completed')
    return {
        'func_name': fetch_data_from_mssql.__name__,
        'status': os.path.exists(data_file_path),
        'path': data_file_path,
        'duration': duration,
        'ram_usage_percent': ut.get_memroy_percent()
    }


def data_file_check(data_file_path=C.DATA_FILE_PATH):
    """
    Data File Check

    Parameters:
        data_file_path (str):
            Data File location. (Default value refer to const.py)

    Returns:
        result (dict):
            Dict contains metrics and status

        df (Dataframe):
            DataFrame loaded from input param - `data_file_path`

    """
    time_start = time.time()
    log.info('Data File Check Start')
    log.debug(('data_file_path', data_file_path))
    ut.file_exists_check(data_file_path)

    # Collect Data Metrics
    df = pd.read_csv(data_file_path)
    row_count = df.shape[0]
    col_count = df.shape[1]
    file_size = os.stat(data_file_path).st_size

    # Metrics Checking
    status = row_count > C.DATA_FILE_MIN_ROW_COUNT \
        and col_count == C.DATA_FILE_COL_COUNT \
        and file_size > C.DATA_FILE_MIN_FILE_SIZE_MB

    # TODO validate value range of critical column etc.
    duration = ut.get_duration_msg(time_start)
    result = {
        'func_name': data_file_check.__name__,
        'path': data_file_path,
        'row_count': (row_count, row_count > C.DATA_FILE_MIN_ROW_COUNT),
        'col_count': (col_count, col_count == C.DATA_FILE_COL_COUNT),
        'file_zie': (file_size > C.DATA_FILE_MIN_FILE_SIZE_MB),
        'status': status,
        'duration': duration,
        'ram_usage_percent': ut.get_memroy_percent()
    }
    log.info('Data File Check Completed')
    return result, df


def process_data(data_file_path=C.DATA_FILE_PATH,
                 training_data_path=C.DF_X_TMP_PATH,
                 label_data_path=C.DF_Y_TMP_PATH,
                 dataset_override=None):
    """
    Data Processing.

    Parameters:
        data_file_path (str):
            Data File Path (Default value refer to const.py)

        training_data_path (str):
            Save Traing Data Path (Default value refer const.py)

        predict_data_path (str):
            Save Predict Data Path (Default value refer const.py)

        dataset (dataframe):
            Optional. If value is none.
            Data will be loaded from `data_file_path`.

    Returns:
        result (dict):
            Status and Metrics

        X (dataframe):
            Traing DataFrame

        y (dataframe):
            Predict DataFrame

    """
    log.info('Data Processing Start')
    time_start = time.time()
    # Log all input param
    log.debug(process_data.__code__.co_varnames)
    dataset = dataset_override if dataset_override is not None else \
        pd.read_csv(data_file_path)

    target_group_metric = dataset.groupby(['target']).size().to_string()

    # Store data metric - label group
    log.debug(('target_group_metrics', target_group_metric))

    # Shuffle rows
    dataset = dataset.sample(frac=1)

    # Split Train and Test Data
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values

    # Data Cleaning. Fill NaN
    imputer = SimpleImputer(missing_values=np.nan, strategy='median')
    imputer.fit(X)
    X = imputer.transform(X)

    # Handle Data Imbalance
    smote = SMOTE(random_state=31)
    X, y = smote.fit_resample(X, y)

    # Store Data in temp directory
    np.savetxt(training_data_path, X)
    np.savetxt(label_data_path, y)

    duration = ut.get_duration_msg(time_start)
    result = {
        'func_name': process_data.__name__,
        'X_shape': X.shape,
        'y_shape': y.shape,
        'status':
            os.path.exists(training_data_path) and
            os.path.exists(label_data_path),
        'X_data_path': training_data_path,
        'Y_data_path': label_data_path,
        'duration': duration,
        'ram_usage_percent': ut.get_memroy_percent()
    }
    log.info('Data Processing Completed')
    return result, X, y
