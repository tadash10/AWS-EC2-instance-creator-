This script allows you to create and manage EC2 instances on AWS with a specified AMI, security group, and user data script. It includes functionalities for setting up a security group, creating an EC2 instance, and handling various exceptions during the process.
Features

    Creates a security group that allows SSH and HTTP access.
    Launches an EC2 instance with a specified AMI.
    Applies user data scripts for additional instance configuration.
    Handles existing security group checks and exceptions.

Prerequisites

    Python 3.x
    boto3 library
    AWS CLI configured with appropriate IAM permissions

Installation

    Clone the repository:

    sh

git clone https://github.com/yourusername/ec2-instance-manager.git
cd ec2-instance-manager

Install dependencies:

sh

pip install boto3

Configure AWS CLI:
Ensure that your AWS CLI is configured with the necessary permissions to create security groups and EC2 instances.

sh

    aws configure

Usage

    Run the script:

    sh

    python ec2_instance_manager.py

    Choose an AMI:
    The script will prompt you to choose an AMI to launch an EC2 instance. Options include:
        1: Kali Linux
        2: Ubuntu
        3: Windows
        4: Arch Linux

    Monitor the logs:
    The script uses logging to provide information about the process, including the creation of the security group, the launching of the instance, and any errors encountered.

Example

When prompted, enter the number corresponding to the desired AMI:

plaintext

Choose an AMI to launch an EC2 instance:
1. Kali
2. Ubuntu
3. Windows
4. Arch

Enter the number of your choice: 2

Customization

    Modify AMI IDs:
    Update the ami_dict dictionary in the script to include your desired AMI IDs.

    User Data Scripts:
    Customize the get_user_data_script function to include additional user data scripts for different AMIs.

Troubleshooting

    Invalid AMI Choice:
    Ensure that you enter a valid number corresponding to the available AMI choices.

    AWS Permissions:
    Ensure your AWS CLI is configured correctly and has the necessary permissions.

    Security Group Conflicts:
    The script handles existing security groups with the same name, but ensure there are no conflicting security group rules.

License

This project is licensed under the MIT License. See the LICENSE file for details.
Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.
