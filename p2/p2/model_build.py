#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import logging
import pickle
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import RandomizedSearchCV
from . import const as C
from . import util as ut


log = logging.getLogger(__name__)


def build_model(X_file=C.DF_X_TMP_PATH,
                y_file=C.DF_Y_TMP_PATH,
                model_save_path=C.MD_FILE_PATH,
                enable_tunning=C.MD_TUNNING,
                X_override=None,
                y_override=None):
    """
    Model Buidling - RandomForest

    Parameters:
        X_file (str):
            Optional. Training Data File Path (Default value refer to const.py)

        y_file (str):
            Optional. Label Data File Path (Default value refer to const.py)

        model_save_path (str):
            Optional. Model pickle file save path (Default value refer const.py)

        X_override (str):
            Optional. Override Traning Data (Panda Series)
            If this param has set, `X_file` will be ignored.

        y_override (str):
            Optional. Override Label Data (Panda Series)
            If this param has set, `y_file` will be ignored.

    Returns:
        result (dict):
            Status and Metrics

        classifier (model):
            Sklearn RandomForest Model

    """
    log.info('Build Model Start')
    time_start = time.time()
    log.debug(('X_file', X_file, 'y_file', y_file))
    log.debug(('model_save_path', model_save_path))
    log.debug(('X_override is None', X_override is None))
    log.debug(('y_override is None', y_override is None))

    # Load Train Test Data
    X = X_override if X_override is not None else np.loadtxt(X_file)
    y = y_override if y_override is not None else np.loadtxt(y_file)
    log.debug(('X y Shapes:', X.shape, y.shape))

    # Split Test Data
    X_train, X_test, y_train, y_test = \
        train_test_split(X, y,
                         test_size=C.MD_TEST_SIZE,
                         random_state=C.MD_RANDOM_STATE)

    # Scale Data
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    if enable_tunning:
        log.debug('RandomSearch Tunning Model Building')
        n_estimators = [int(x) for x in range(10, 30, 5)]
        max_features = ['auto', 'sqrt']
        max_depth = \
            [int(x) for x in np.linspace(10, 30, num=11)]
        max_depth.append(None)
        min_samples_split = [2, 5, 10]
        min_samples_leaf = [1, 2, 4]
        bootstrap = [True, False]

        random_grid = {'n_estimators': n_estimators,
                       'max_features': max_features,
                       'max_depth': max_depth,
                       'min_samples_split': min_samples_split,
                       'min_samples_leaf': min_samples_leaf,
                       'bootstrap': bootstrap,
                       'criterion': ['entropy']}

        rf_random_search = RandomizedSearchCV(
            estimator=RandomForestClassifier(),
            param_distributions=random_grid,
            n_iter=3,
            cv=3,
            verbose=2,
            random_state=42,
            n_jobs=-1)

        rf_random_search.fit(X_train, y_train)
        classifier = rf_random_search.best_estimator_

    else:
        log.debug('Vanilla Model Building')
        # Model Training
        classifier = RandomForestClassifier(
            n_estimators=C.MD_n_estimators,
            min_samples_split=C.MD_min_samples_split,
            min_samples_leaf=C.MD_min_samples_leaf,
            max_depth=C.MD_max_depth,
            criterion='entropy',
            random_state=C.MD_RANDOM_STATE)

    classifier.fit(X_train, y_train)

    # Check Accuracy
    log.debug('Check Accuracy')
    y_pred = classifier.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    score = accuracy_score(y_test, y_pred)

    # Save model to file
    log.debug('Save Model to drive')
    pickle.dump(classifier, open(model_save_path, 'wb'))

    # Result
    duration = ut.get_duration_msg(time_start)
    result = {
        'func_name': build_model.__name__,
        'confusion_matrix': cm,
        'score': score,
        'tunning_enable': enable_tunning,
        'model_save_path': model_save_path,
        'status': os.path.exists(model_save_path),
        'duration': duration,
        'ram_usage_percent': ut.get_memroy_percent()
    }
    log.debug(result)
    log.info('Build Model Completed')
    return result, classifier

