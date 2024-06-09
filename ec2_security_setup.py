import boto3
from botocore.exceptions import ClientError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_security_group(client):
    try:
        response = client.create_security_group(
            Description='Allow SSH and HTTP',
            GroupName='SecGroup'
        )
        security_group_id = response['GroupId']
        client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
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

def create_ec2_instance(ami_choice, user_data_script):
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')

    ami_dict = {
        'kali': 'ami-0aef57767f5404a3c',
        'ubuntu': 'ami-0c55b159cbfafe1f0',
        'windows': 'ami-0d8f6eb4f641ef691',
        'arch': 'ami-0cc75a8978fbbc188'  # Example AMI ID for Arch Linux
    }

    if ami_choice not in ami_dict:
        raise ValueError("Invalid AMI choice. Valid choices are: 'kali', 'ubuntu', 'windows', 'arch'.")

    ami_id = ami_dict[ami_choice]

    # Create security group with restricted access
    security_group_id = create_security_group(client)

    try:
        instances = ec2.create_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
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

def get_user_data_script(ami_choice):
    if ami_choice == 'arch':
        return """#!/bin/bash
        # Update package list and install security updates
        pacman -Syu --noconfirm
        
        # Configure firewall to allow only necessary traffic
        iptables -A INPUT -p tcp --dport 22 -j ACCEPT
        iptables -A INPUT -p tcp --dport 80 -j ACCEPT
        iptables -A INPUT -j DROP
        
        # Install necessary packages securely
        pacman -S --noconfirm pacman-contrib
        echo 'Server = https://archlinux.org/repos/$repo/os/$arch' > /etc/pacman.d/mirrorlist
        pacman -Sy --noconfirm gnupg archlinux-keyring
        pacman-key --init
        pacman-key --populate archlinux
        pacman -S --noconfirm xorg gnome gnome-extra gnome-tweaks gdm
        
        # Enable and start GDM
        systemctl enable gdm
        systemctl start gdm
        """
    return ""

def main():
    ami_choice_map = {
        '1': 'kali',
        '2': 'ubuntu',
        '3': 'windows',
        '4': 'arch'
    }

    print("Choose an AMI to launch an EC2 instance:")
    for key, value in ami_choice_map.items():
        print(f"{key}. {value.capitalize()}")

    choice = input("Enter the number of your choice: ")

    ami_choice = ami_choice_map.get(choice)

    if not ami_choice:
        print("Invalid choice. Exiting.")
        return

    try:
        user_data_script = get_user_data_script(ami_choice)
        create_ec2_instance(ami_choice, user_data_script)
    except ClientError as e:
        logger.error(f"AWS error occurred: {e}")
    except ValueError as e:
        logger.error(f"Value error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
