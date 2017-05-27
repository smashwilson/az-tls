#!/usr/bin/env python

import os
import boto3

key_id = os.environ['KMS_KEY_ID']
bucket_name = os.environ['S3_BUCKET_NAME']

s3 = boto3.resource('s3')
kms = boto3.client('kms')

with open('/out/tls-certificates.tar.gz', 'rb') as inf:
    tarball = inf.read()

response = kms.encrypt(KeyId=key_id, Plaintext=tarball)

s3.Bucket(bucket_name).put_object(
    Key='tls-certificates.tar.enc',
    Body=response['CiphertextBlob']
)

print('Encrypted certificate bundle uploaded to S3.')
