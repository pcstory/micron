#!/usr/bin/env sh

export AWS_PROFILE=default

export tag_name=micron-q6-ml-pipeline
export account_id=12345678
export region=us-east-1

docker build \
    -t $account_id.dkr.ecr.$region.amazonaws.com/$tag_name \
    --force-rm \
    .

# aws ecr get-login-password \
#     --region $region \
# | docker login \
#     --username AWS \
#     --password-stdin "$account_id.dkr.ecr.$region.amazonaws.com"

# docker push "$account_id.dkr.ecr.$region.amazonaws.com/$tag_name"