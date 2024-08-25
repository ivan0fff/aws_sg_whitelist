# AWS Security Group Whitelist Script

This script allows you to modify the whitelist of an AWS security group by adding specific IP permissions. It interacts with AWS using the boto3 library and requires an active AWS session.

## Requirements

- Python 3.x
- `boto3` library
- `requests` library
- `aws-cli` installed and configured with SSO

## Installation

1. **Install Python dependencies**:
    ```sh
    pip install boto3 requests
    ```

2. **Install AWS CLI**:
    Follow the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) to install the AWS CLI.

3. **Configure AWS CLI with SSO**:
    ```sh
    aws configure sso
    ```
    Follow the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) to configure the AWS SSO.

## Usage

1. **Set the AWS profile**:
    Modify the `profile` variable in the script to match your AWS profile name:
    ```python
    profile = 'your-profile-name'
    ```

2. **Set the Security Group Rule CidrIp Description PATTERN in existing Secuirities Groups**
    Modify the `cidr_ip_description_search_pattern` variable in the script to match your sgr CidrIp that contains the desired PATTERN:
    ```python
    cidr_ip_description_search_pattern = 'PATTERN'
    ```

3. **Run the script**:
    ```sh
    python aws_sg_ip_whitelist.py
    ```

4. **Follow the prompts**:
    The script will prompt you to confirm the whitelist modification. Respond with `yes` or `no`.

## Error Handling

- **AWS Session Errors**: The script checks for an active AWS session and prompts you to renew the token if it has expired.
- **Network Errors**: The script handles errors when fetching the public IP address.
- **AWS API Errors**: The script handles errors when interacting with AWS services using boto3.
- **User Input Errors**: The script validates user input for confirmation prompts.

## License

This project is licensed under the MIT License.