#!/usr/bin/env python

import io
import struct
import os
import boto3
from Crypto.Hash import AES
from Crypto import Random

VERSION = 0


def pad(s):
    return s + (AES.block_size - len(s) % AES.block_size) * b'\x00'


key_id = os.environ['KMS_KEY_ID']
bucket_name = os.environ['S3_BUCKET_NAME']

s3 = boto3.resource('s3')
kms = boto3.client('kms')

with open('/out/tls-certificates.tar.gz', 'rb') as inf:
    tarball = inf.read()

data_key = kms.generate_data_key(KeyId=key_id, KeySpec='AES_128')
data_key_enc = data_key.get('CiphertextBlob')

iv = Random.new().read(AES.block_size)
aes = AES.new(data_key.get('Plaintext'), AES.MODE_CBC, iv)

ciphertext = io.BytesIO()
ciphertext.write(struct.pack('>LL', VERSION, len(data_key_enc)))
ciphertext.write(data_key_enc)
ciphertext.write(iv)
ciphertext.write(aes.encrypt(pad(tarball)))

s3.Bucket(bucket_name).put_object(
    Key='tls-certificates.tar.enc',
    Body=ciphertext.getvalue()
)

print('Encrypted certificate bundle uploaded to S3.')
