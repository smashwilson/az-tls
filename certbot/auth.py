#!/usr/bin/env python3

import os
import time
import json
import boto3
from pprint import pprint

client = boto3.client('route53')

domain = os.environ['CERTBOT_DOMAIN']
validation = os.environ['CERTBOT_VALIDATION']

job_number = os.environ.get('TRAVIS_JOB_NUMBER')

# Isolate "domain.tld." from the full domain name
parts = domain.split('.')
if parts[-1] != '':
    parts.append('')
zone_name = '.'.join(parts[-3:])

# Discover the hosted zone
zones = client.list_hosted_zones()
for zone in zones['HostedZones']:
    if zone['Name'] == zone_name:
        zone_id = zone['Id']
        break
else:
    pprint(zones)
    raise RuntimeError('Unable to find hosted zone for {}'.format(domain))

response = client.change_resource_record_sets(
    HostedZoneId=zone_id,
    ChangeBatch={
        'Comment': "Let's Encrypt auth challenge from Travis job {}".format(job_number),
        'Changes': [
            {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': '_acme-challenge.{}'.format(domain),
                    'Type': 'TXT',
                    'TTL': 120,
                    'ResourceRecords': [
                        {'Value': '"{}"'.format(validation)}
                    ]
                }
            }
        ]
    }
)
change_id = response['ChangeInfo']['Id']

for i in range(60):
    if response['ChangeInfo']['Status'] == 'INSYNC':
        break

    print('Waiting for changes to sync. Attempt #{}'.format(i))
    time.sleep(30)

    response = client.get_change(Id=change_id)
else:
    raise RuntimeError('Timed out waiting for record change {} to sync'.format(change_id))

with open('.certbot.{}.json'.format(domain), 'w') as outf:
    payload = {
        'zone_id': zone_id,
        'value': validation,
    }
    json.dump(payload, outf)
