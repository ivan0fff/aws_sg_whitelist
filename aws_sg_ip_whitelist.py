import boto3
import subprocess
import sys
import requests

def check_aws_session(profile):
    try:
        subprocess.check_output(['aws', 'sts', 'get-caller-identity', '--profile', profile])
    except FileNotFoundError:
        print("Error: aws-cli no está instalado. Por favor, instala aws-cli.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        if 'The security token included in the request is expired' in str(e):
            print(f"Error: El token SSO ha expirado para el perfil '{profile}'.")
            print("Por favor, renueva el token usando el siguiente comando:")
            print(f"aws sso login --profile {profile}")
        else:
            print(f"Error: No se encontró una sesión de AWS activa para el perfil '{profile}'.")
            print("Por favor, autentícate usando el siguiente comando:")
            print(f"aws sso login --profile {profile}")
        sys.exit(1)

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        return response.json()['ip'] + '/32'
    except requests.RequestException as e:
        print(f"Error al obtener la IP pública: {e}")
        sys.exit(1)

def ask_user_confirmation():
    while True:
        response = input("Do you want to continue with the whitelist modification? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Invalid response. Please enter 'yes' or 'no'.")

def revoke_security_group_rule(ec2, sg_id, ip_permissions):
    try:
        ec2.revoke_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=ip_permissions
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Error al eliminar la regla del grupo de seguridad: {e}")
        sys.exit(1)

def create_security_group_rule(ec2, sg_id, ip_permissions):
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=ip_permissions
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Error al crear la regla del grupo de seguridad: {e}")
        sys.exit(1)

# Verify AWS Session
profile = 'default'  # Change 'default' for the AWS profile you want to use
check_aws_session(profile)

# Create a boto3 session with the specified profile
session = boto3.Session(profile_name=profile)
ec2 = session.client('ec2')

new_ip = get_public_ip()

# Getting all Security Groups
security_groups = ec2.describe_security_groups()

# Iterate over the rule IDs of the security groups
cidr_ip_description_search_pattern = 'PATTERN'  # Replace 'PATTERN' with the word or pattern you want to search for
for sg in security_groups['SecurityGroups']:
    sg_id = sg['GroupId']
    sg_name = sg.get('GroupName', 'N/A')
    sg_description = sg.get('Description', 'N/A')
    for rule in sg['IpPermissions']:
        for ip_range in rule.get('IpRanges', []):
            cidr_ip = ip_range.get('CidrIp')
            ip_range_description = ip_range.get('Description')
            # It will check if the search pattern is in the IP range description
            if ip_range_description and cidr_ip_description_search_pattern.lower() in ip_range_description.lower():
                print(f"Security Group ID: {sg_id}, Name: {sg_name}, Description: {sg_description}, IP Range: {cidr_ip}, Description: {ip_range_description}")
                ip_permissions = [{'FromPort': rule['FromPort'], 'ToPort': rule['ToPort'],'IpProtocol': rule['IpProtocol'],'IpRanges': [{'CidrIp': cidr_ip,'Description': ip_range_description}]}]
                new_ip_permissions = [{'FromPort': rule['FromPort'], 'ToPort': rule['ToPort'],'IpProtocol': rule['IpProtocol'],'IpRanges': [{'CidrIp': new_ip,'Description': ip_range_description}]}]
                if (ask_user_confirmation()):
                    revoke_security_group_rule(ec2,sg_id,ip_permissions)
                    create_security_group_rule(ec2,sg_id,new_ip_permissions)