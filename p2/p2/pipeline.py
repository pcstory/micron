#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import traceback
from . import data_eng, model_build, util as ut
from . import inference as inf
import pprint


log = logging.getLogger(__name__)


def setup_logging(log_option: str):
    """
    Setup Logger

    Parameters:
        log_option (str):
            Optional. Logging Option.
    """
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }
    level = levels.get(log_option.lower())
    if level is None:
        raise ValueError(
            f'log level given: {options.log}'
            f" -- must be one of: {' | '.join(levels.keys())}")
    log_format_pattern = '%(asctime)s %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
    logging.basicConfig(
        # Configure Logging message to start with date time and line number for logging purpose.
        format=log_format_pattern,
        level=level)
    # File Logger
    from logging.handlers import TimedRotatingFileHandler
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(log_format_pattern)
    fileHandler = TimedRotatingFileHandler(
                                    "{0}/{1}.log".format('./', 'pipeline'),
                                    when="m",
                                    interval=1,
                                    backupCount=5)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


def publish_error_to_sns(error_msg):
    pass
    # Configure AWS SNS topic for error support personel email subscription
    # sns_client = boto3.client('sns')
    # sns_topic = os.getenv('ECS_SNS_ERROR_TOPIC_ARN','arn:aws:sns:ap-southeast-1:<account-id>:<topic>')
    # print('Send Error To SNS' , sns_topic)
    # print('Error', error_msg)
    # sns_client.publish(
    #     TargetArn = sns_topic,
    #     Subject='Miron Q6 Pipeline Error',
    #     Message = 'Error Found in \n' + error_msg
    # )


def execute_full_pipeline():
    """
    Full Pipeline Execution

    Output will be store in tmp directory for each step.
    """
    log.info('Pipeline Start')
    # Fetch Data
    result = data_eng.fetch_data_from_mssql()
    validate(result)

    # Data File Check
    result, df = data_eng.data_file_check()
    validate(result)

    # Data Processing
    # Use dataset in memory for dataset_override to improve speed
    result, X, y = data_eng.process_data(dataset_override=df)
    validate(result)

    # Build Model
    result, model = model_build.build_model(X_override=X, y_override=y)
    validate(result)

    # Inference
    result, _, _ = inf.batch_inference(model_override=model)
    validate(result)
    log.info('Pipeline Completed')


def validate(data: dict, raise_exception=True):
    log.info('validate and store metric')
    ut.store_metric(data)
    # TODO Store the status as json or database's table
    if data is None:
        raise Exception('No Validation Result')
    if data['status'] is False and raise_exception:
        pretty_dict_str = pprint.pformat(data)
        log.error('Pipeline Stop ------------')
        log.error('\n' + pretty_dict_str)
        raise Exception(data)
    return data['status']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Command:
    # python -m p2.pipeline -h
    #
    # Full Pipeline:
    # python -m p2.pipeline -log INFO -a full-pipeline
    #
    # Custom Action. Ex. inference
    # python -m p2.pipeline -log DEBUG -a data-fetch
    #
    #
    # Data Pipeline access
    parser.add_argument('-a', '--action',
                        choices=[
                            'data-fetch',
                            'data-check',
                            'data-process',
                            'model-build',
                            'inference',
                            'full-pipeline'
                        ],
                        default='debug-info')

    # Log Option
    parser.add_argument('-log', '--log',
                        default='warning')
    options = parser.parse_args()
    setup_logging(options.log)

    # Action Processing
    action = options.action
    log.info(('Action:', action))
    try:
        if action == 'full-pipeline':
            execute_full_pipeline()
        # For Troubleshooting, invoke manually. Data will be fetch from cache - /tmp folder
        if action == 'data-fetch':
            data_eng.fetch_data_from_mssql()
        if action == 'data-check':
            data_eng.data_file_check()
        if action == 'data-process':
            data_eng.process_data()
        if action == 'model-build':
            model_build.build_model()
        if action == 'inference':
            inf.batch_inference()
    except (OSError, Exception):
        traceback.print_exc()
        tb = traceback.format_exc()
        # Pass error to topic
        log.error('error to SNS topic Q')
        publish_error_to_sns(tb)
