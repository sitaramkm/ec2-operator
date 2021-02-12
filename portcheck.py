import sys, json

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("Could not import 'boto3', please install this package.")

# first and only argument is the security group id
#if (len(sys.argv) != 2):
#    sys.exit("USAGE: python ipme.py [security-group-id]")
#else:
#    group_id = str(sys.argv[1])

# set up client object
client = boto3.client('ec2')

# find security group by that id
try:
    response = client.describe_security_groups(
        Filters=[
            # only concerned with ssh
            {
                'Name': 'ip-permission.from-port',
                'Values': ['22']
            },
            {
                'Name': 'ip-permission.cidr',
                'Values': ['0.0.0.0/0', '0.0.0.0', '0.0.0.0/*']
            },
            {
                'Name': 'ip-permission.protocol',
                'Values': ['tcp']
            },
        ],
#        GroupIds=[
#            group_id,
#        ],
        DryRun=False
    )
# throw error or exception, whatever comes first
except ClientError as e:
    sys.exit(e)
except Exception as ex:
    sys.exit(ex)
# finally, update the security group to authorize ingress traffic over 22 (SSH) from this device's external ip
else:
    if response['SecurityGroups']:
        print(response)
        # used to print informative message
        info = response['SecurityGroups'][0]
        # used later in this script
        old_access = response['SecurityGroups'][0]['IpPermissions'][0]
        print('Found security group (id={0[GroupId]}) named {0[GroupName]}'.format(info))
    else:
        sys.exit('Nothing found matching that criteria (SSH rule).')


#try:
    # first revoke ingress for old ip,
#    data = client.revoke_security_group_ingress(
#        GroupId=group_id,
#        IpPermissions=[
#            old_access
#        ]
#    )


    # then authorize ingress for new one
#    data = client.authorize_security_group_ingress(
#        GroupId=group_id,
#        IpPermissions=[
#            {
#                'IpProtocol': 'tcp',
#                'FromPort': 22,
#                'ToPort': 22,
#                'IpRanges': [{'CidrIp': ext_ip}]
#            }
#        ]
#    )


# throw error or exception, whatever comes first
#except ClientError as e:
#    sys.exit(e)
#except Exception as ex:
#    sys.exit(ex)
#else:
#    print('Ingress Successfully Set %s' % data)