#!/usr/bin/python

import boto3
import croniter
import datetime
from botocore.exceptions import ClientError

# regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2",
#           "ap-northeast-1", "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1",
#           "sa-east-1"]

regions = ["us-east-1"]

bo
# return true if the cron schedule falls between now and now+seconds
def time_to_action(sched, time_now, seconds):
    try:
        cron = croniter.croniter(sched, time_now)
        d1 = time_now + datetime.timedelta(0, seconds)
        if seconds > 0:
            d2 = cron.get_next(datetime.datetime)
            ret = (time_now < d2 < d1)
        else:
            d2 = cron.get_prev(datetime.datetime)
            ret = (d1 < d2 < time_now)
        print("now %s" % time_now)
        print("d1 %s" % d1)
        print("d2 %s" % d2)
    except:
        ret = False
    print("time_to_action %s" % ret)
    return ret



# time_to_action("0 0 * * SAT", now, 31 * 60)

now = datetime.datetime.now()
instances = []
for region in regions:
    try:
        ec2 = boto3.resource('ec2', region_name=region)
        print('region={}'.format(region))
        start_list = []
        stop_list = []
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            for tag in instance.tags:
                if 'Name' in tag['Key']:
                    name = tag['Value']
                else:
                    name = 'Unknown'

                # check auto:start and auto:stop tags
                if 'auto:start' in tag['Key']:
                    start_sched = tag['Value']
                else:
                    start_sched = None

                if 'auto:stop' in tag['Key']:
                    stop_sched = tag['Value']
                else:
                    stop_sched = None

            state = instance.state['Name']
            #  print('region={}'.format(region), 'instance-name={}'.format(name),
            #        'instance-type={}'.format(instance.instance_type), 'instance-id={}'.format(instance.id),
            #        'instance-state={}'.format(state))
            print('instance-laumch-time={}'.format(instance.launch_time))
            print('instance-tags={}'.format(instance.tags))
            # print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %  name, instance.id, instance.instance_type,
            #     instance.launch_time, state, start_sched, stop_sched, instance.tags)

            # queue up instances that have the start time falls between now and the next 30 minutes
            # Starting instances won't work as the filter specifically is looking for running instances and
            # will not find anything to start. This is as-designed at this time.

            if start_sched != None and state == "stopped" and time_to_action(start_sched, now, 31 * 60):
                start_list.append(instance.id)

            # queue up instances that have the stop time falls between 30 minutes ago and now
            # if stop_sched != None and state == "running" and time_to_action(stop_sched, now, 31 * -60):
            if stop_sched != None and state == "running":
                stop_list.append(instance.id)

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

    # most likely will get exception on new beta region and gov cloud
    except Exception as e:
        print('Error {}}',  e)
