#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Data file verification threshold checking
DATA_FILE_MIN_ROW_COUNT = 1000
DATA_FILE_MIN_FILE_SIZE_MB = 10 * 1000 * 1000  # 10MB
DATA_FILE_COL_COUNT = 152
DATA_FILE_PATH = '/tmp/Q6_data.csv'

# Data Processing Related
DF_X_TMP_PATH = '/tmp/X.csv'
DF_Y_TMP_PATH = '/tmp/y.csv'

# Model Training Related
MD_TEST_SIZE = 0.25
MD_RANDOM_STATE = 4
MD_FILE_PATH = '/tmp/model.sav'
MD_TUNNING = True
MD_n_estimators = 25
MD_min_samples_split = 5
MD_min_samples_leaf = 2
MD_max_depth = 26
