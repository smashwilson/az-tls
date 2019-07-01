#!/usr/bin/env python3

import os
import json
import boto3

domain = os.environ['CERTBOT_DOMAIN']

with open('.certbot.{}.json'.format(domain)) as inf:
    payload = json.load(inf)

zone_id = payload['zone_id']
value = payload['value']

client = boto3.client('route53')

client.change_resource_record_sets(
    HostedZoneId=zone_id,
    ChangeBatch={
        'Comment': "Let's Encrypt auth cleanup",
        'Changes': [
            {
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': '_acme-challenge.{}'.format(domain),
                    'Type': 'TXT',
                    'TTL': 120,
                    'ResourceRecords': [
                        {'Value': '"{}"'.format(value)}
                    ]
                }
            }
        ]
    }
)
