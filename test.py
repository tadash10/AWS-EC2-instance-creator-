import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_security_group(client):
    try:
        response = client.create_security_group(
            Description='allow SSH and HTTP',
            GroupName='SecGroup'
        )
        security_group_id = response['GroupId']
        client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
            ]
        )
        return security_group_id
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            logger.info("Security group already exists. Retrieving the existing security group.")
            response = client.describe_security_groups(GroupNames=['SecGroup'])
            return response['SecurityGroups'][0]['GroupId']
        else:
            logger.error(f"Unexpected error: {e}")
            raise

def create_ec2_instance(ami_choice):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')

    ami_dict = {
        'kali': 'ami-0aef57767f5404a3c',
        'ubuntu': 'ami-0c55b159cbfafe1f0',
        'windows': 'ami-0d8f6eb4f641ef691'
    }

    if ami_choice not in ami_dict:
        raise ValueError("Invalid AMI choice. Valid choices are: 'kali', 'ubuntu', 'windows'.")

  
