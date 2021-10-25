#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import time
import logging
import numpy as np
import pandas as pd
from . import const as C
from . import util as ut
from sqlalchemy import create_engine
from sklearn.impute import SimpleImputer


log = logging.getLogger(__name__)


def batch_inference(model_save_path=C.MD_FILE_PATH,
                    model_override=None,
                    is_test=False):
    """
    Model inference.
    Fetch Batch Input Data from MSSQL and store the result back to DB.

    Parameters:
        model_save_path (str):
            Model file that save during model building.

        model_override (str):
            Model overrride.
            `model_save_path` will be ignored if value is not None.

        is_test (bool):
            To skip save result in DB if value is true.
            For Unit Test purpose

    Returns:
        result (dict):
            Dictionary with metrics and status

        y
    """
    log.info('Batch Inference Start')
    if model_override is not None:
        model = model_override
    else:
        ut.file_exists_check(model_save_path,
                             error_msg='Model File not Found')
        model = pickle.load(open(model_save_path, 'rb'))

    sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/micron',
                              pool_recycle=3600)
    with sqlEngine.connect() as db_connection:
        # Fetch input from DB
        time_start = time.time()

        # TODO, To implment feature reduction and drop selecting all columns
        df = pd.read_sql('select * from q6_data', db_connection)
        df.drop(['target'], axis=1, inplace=True)
        X = df

        # Fill NA
        imputer = SimpleImputer(missing_values=np.nan, strategy='median')
        imputer.fit(X)

        X = imputer.transform(X)
        y = model.predict(X)
        df['target'] = y

        # Store Result back to DB
        if not is_test:
            df.to_sql('q6_data_result', db_connection, if_exists='replace')

        duration = ut.get_duration_msg(time_start)
        result = {
            'func_name': batch_inference.__name__,
            'data_input_shape': df.shape,
            'data_output_shape': y.shape,
            'status': df.shape[0] > 0 and df.shape[1] > 0 and
                      y is not None and y.shape[0] > 0,
            'duration': duration,
            'ram_usage_percent': ut.get_memroy_percent()
        }
        log.info('Batch Inference Completed')
        return result, y, df