#!/usr/bin/env python3

import os
import json
import urllib.request
import base64

log_handler = urllib.request.HTTPSHandler()
opener = urllib.request.build_opener(log_handler)

def generate_auth_header():
    pair = '{}:{}'.format('az-tls', os.environ['AZ_COORDINATOR_TOKEN']).encode('utf-8')
    return 'Basic {}'.format(base64.b64encode(pair).decode('utf-8'))

auth_header = generate_auth_header()

tls_locations = {
    'TLS_DH_PARAMS': '/etc/letsencrypt/live/dhparams.pem',
    'TLS_CERTIFICATE': '/etc/letsencrypt/live/backend.azurefire.net/fullchain.pem',
    'TLS_KEY': '/etc/letsencrypt/live/backend.azurefire.net/privkey.pem'
}

tls_secrets_payload = {}
for varname, filepath in tls_locations.items():
    with open(filepath, encoding='utf8') as f:
        tls_secrets_payload[varname] = f.read()

print('Uploading TLS certificate secrets to the coordinator')
secrets_req = urllib.request.Request(
    method='POST',
    url='{}/secrets'.format(os.environ['AZ_COORDINATOR_ADDR']),
    headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
    data=json.dumps(tls_secrets_payload).encode('utf-8')
)
opener.open(secrets_req)

print('Triggering a coordinator sync')
sync_req = urllib.request.Request(
    method='POST',
    headers={'Authorization': auth_header},
    url='{}/sync'.format(os.environ['AZ_COORDINATOR_ADDR'])
)
opener.open(sync_req)

print('Upload complete.')
