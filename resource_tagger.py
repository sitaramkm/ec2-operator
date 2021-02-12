import boto3
import json


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    # print( 'Hello-json  {}'.format(message))

    # -------------------- Debug ---------------------------
    # print( 'Hello  {}'.format(event))
    # print( 'User Name- {}'.format(message['detail']['userIdentity']['principalId']))
    # print( 'Instance ID- {}'.format(message['detail']['responseElements']['instancesSet']['items'][0]['instanceId']))

    # Variables
    instanceId = message['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
    userNameSTring = message['detail']['userIdentity']['principalId']
    region = message['region']

    # Checks if the user is an okta user
    if ":" in userNameSTring:
        userName = userNameSTring.split(":")[1]
    else:
        userName = message['detail']['userIdentity']['userName']

    print('Instance Id - ', instanceId)
    print('User Name - ', userName)

    tagKey = 'owner'
    tagValue = userName

    # ---------------------- Body  ----------------------

    # EC2 tagging
    client = boto3.client('ec2', region_name=region)
    response = client.create_tags(
        Resources=[
            instanceId
        ],
        Tags=[
            {
                'Key': tagKey,
                'Value': tagValue
            },
            {
                'Key': 'auto:stop',
                'Value': '0 1 * * SAT'
            },

        ]
    )

    # Volume tagging
    ec2 = boto3.resource('ec2', region_name=region)
    instance = ec2.Instance(instanceId)
    volumes = instance.volumes.all()
    for volume in volumes:
        volID = volume.id
        print("volume - ", volID)
        volume = ec2.Volume(volID)
        tag = volume.create_tags(
            Tags=[
                {
                    'Key': tagKey,
                    'Value': tagValue
                },
            ]
        )

    print(response)