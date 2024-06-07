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

def get_latest_arch_linux_ami(region_name):
    client = boto3.client('ec2', region_name=region_name)
    try:
        response = client.describe_images(
            Filters=[
                {'Name': 'name', 'Values': ['*Arch Linux*']},
                {'Name': 'state', 'Values': ['available']}
            ],
            Owners=['amazon']  # Assuming the official Arch Linux AMIs are owned by 'amazon'
        )
        images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
        if images:
            return images[0]['ImageId']
        else:
            raise ValueError("No Arch Linux AMI found in this region.")
    except ClientError as e:
        logger.error(f"Error fetching Arch Linux AMI: {e}")
        raise

def create_ec2_instance(ami_choice, user_data_script, region_name, instance_type='t2.micro'):
    ec2 = boto3.resource('ec2', region_name=region_name)
    client = boto3.client('ec2', region_name=region_name)

    ami_dict = {
        'kali': None,  # Fetch dynamically
        'ubuntu': 'ami-0c55b159cbfafe1f0',
        'windows': 'ami-0d8f6eb4f641ef691',
    }

    if ami_choice == 'arch':
        ami_id = get_latest_arch_linux_ami(region_name)
    else:
        ami_id = ami_dict.get(ami_choice)
        if not ami_id:
            raise ValueError("Invalid AMI choice. Valid choices are: 'kali', 'ubuntu', 'windows', 'arch'.")

    security_group_id = create_security_group(client)

    try:
        instances = ec2.create_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            KeyName='your-key-pair-name',
            SecurityGroupIds=[security_group_id],
            UserData=user_data_script
        )
        instance_id = instances[0].id
        logger.info(f'Created instance with ID: {instance_id}')

        # Wait for the instance to be running
        instances[0].wait_until_running()
        instances[0].reload()
        logger.info(f'Instance {instance_id} is running at {instances[0].public_dns_name}')
        return instance_id
    except ClientError as e:
        logger.error(f"Failed to create instance: {e}")
        raise

def get_user_data_script(ami_choice, secure_config=False, install_gui=False):
    if ami_choice == 'arch':
        user_data_script = """#!/bin/bash
        # Update the package list
        pacman -Syu --noconfirm
        """
        if secure_config:
            user_data_script += """
            # Additional secure configurations
            # Add your secure configurations here
            """
        if install_gui:
            user_data_script += """
            # Install KDE Plasma GUI
            pacman -S plasma kde-applications --noconfirm
            # Enable SDDM to start on boot
            systemctl enable sddm
            # Start SDDM
            systemctl start sddm
            """
        return user_data_script
    return ""

def main():
    print("Choose an AMI to launch an EC2 instance:")
    print("1. Kali Linux")
    print("2. Ubuntu")
    print("3. Windows")
    print("4. Arch Linux")
    choice = input("Enter the number of your choice: ")

    ami_choice_map = {
        '1': 'kali',
        '2': 'ubuntu',
        '3': 'windows',
        '4': 'arch'
    }

    ami_choice = ami_choice_map.get(choice)

    if not ami_choice:
        logger.error("Invalid choice. Exiting.")
        return

    region_name = input("Enter your AWS region (e.g., us-west-1): ")
    secure_config = input("Do you want to apply secure configurations? (y/n): ").lower() == 'y'
    install_gui = input("Do you want to install KDE Plasma GUI? (y/n): ").lower() == 'y'

    try:
        user_data_script = get_user_data_script(ami_choice, secure_config, install_gui)
        create_ec2_instance(ami_choice, user_data_script, region_name)
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS credentials not found. Please configure your AWS credentials.")
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
