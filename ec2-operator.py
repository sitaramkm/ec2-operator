#!/usr/bin/python

import datetime
import json
import sys
import random

import boto3
import croniter

regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2",
           "ap-northeast-1", "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1",
           "sa-east-1"]


# regions = ["us-east-2"]


# return true if the cron schedule falls between now and now+seconds
def time_to_action(ec2_schedule, time_now, seconds):
    try:
        cron = croniter.croniter(ec2_schedule, time_now)
        d1 = time_now + datetime.timedelta(0, seconds)
        if seconds > 0:
            d2 = cron.get_next(datetime.datetime)
            ret = (time_now < d2 < d1)
        else:
            d2 = cron.get_prev(datetime.datetime)
            ret = (d1 < d2 < time_now)
        # print("now %s" % time_now)
        # print("d1 %s" % d1)
        # print("d2 %s" % d2)
    except:
        ret = False
    print("time_to_action %s" % ret)
    return ret


def log_cloudwatch_metrics(instance_name, instance_id, ec2_region, launch_time, desired_state):
    cloudwatch_client = boto3.client('cloudwatch', region_name=region)
    response = cloudwatch_client.put_metric_data(
        Namespace='EC2 Operator',
        MetricData=[
            {
                'MetricName': desired_state + ' Instance',
                'Dimensions': [
                    {
                        'Name': 'Instance Name',
                        'Value': instance_name
                    },
                    {
                        'Name': 'Instance Id',
                        'Value': instance_id
                    },
                    {
                        'Name': 'Instance Region',
                        'Value': ec2_region
                    },
                    {
                        'Name': 'Instance Launch Time',
                        'Value': launch_time
                    },
                ],
                'Value': random.randint(1, 500),
                'Unit': 'None'
            },
        ]
    )
    print(response)


now = datetime.datetime.now()
print('Script exec time is ' + now.strftime("%m-%d-%Y, %H:%M:%S") + ' and python version used is ' + sys.version + '!')
instances = []
for region in regions:

    ec2 = boto3.resource('ec2', region_name=region)
    start_list = []
    stop_list = []
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        state = instance.state['Name']
        print(instance.id, region)
        tags = []
        if instance.tags is not None:
            tags = instance.tags
        for tag in tags:
            if 'Name' in tag['Key']:
                name = tag['Value']
            else:
                name = 'Unknown'

            # check auto:start and auto:stop tags
            if 'auto:start' in tag['Key'] and state == 'stopped':
                defined_schedule = tag['Value']
                if time_to_action(defined_schedule, now, 31 * 60):
                    start_list.append(instance.id)
                    log_cloudwatch_metrics(name, instance.id, region,
                                           datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S"), 'Started')

            if 'auto:stop' in tag['Key'] and state == 'running':
                defined_schedule = tag['Value']
                if time_to_action(defined_schedule, now, 31 * 60):
                    stop_list.append(instance.id)
                    log_cloudwatch_metrics(name, instance.id, region,
                                           instance.launch_time.strftime("%m-%d-%Y, %H:%M:%S"), 'Stopped')

    #        print(instance.id, instance.tags)

    # start instances
    client = boto3.client('ec2', region_name=region)

    if len(start_list) > 0:
        print('start_list={}'.format(start_list))
        ret = client.start_instances(InstanceIds=start_list, DryRun=False)
        print("start_instances %s" % ret)

    # stop instances
    if len(stop_list) > 0:
        print('stop_list={}'.format(stop_list))
        ret = client.stop_instances(InstanceIds=stop_list, DryRun=False)
        print("stop_instances %s" % ret)
now = datetime.datetime.now()
print('Script exec time is ' + now.strftime("%m-%d-%Y, %H:%M:%S") + ' and python version used is ' + sys.version + '!')