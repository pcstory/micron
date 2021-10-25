#!/usr/bin/env bash

export AWS_PROFILE=default

# Import configuration
. ./.cf_env

# Deploy the workshop
aws cloudformation deploy \
  --template-file ./cf.yml \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region ${REGION} \
  --stack-name ${STACK_NAME} \
  --parameter-overrides \
        PROJECT_NAME=${PROJECT_NAME}
