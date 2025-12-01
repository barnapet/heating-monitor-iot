import boto3
import json
import os
import urllib.request

# --- CONFIGURATION ---
THING_NAME = "heating-pump-pi-01"
POLICY_NAME = "HeatingSystemPolicy"
REGION = "eu-west-2"  # London region
CERTS_DIR = "hardware/certs"

# Initialize AWS IoT Client
iot_client = boto3.client('iot', region_name=REGION)

def create_directory():
    if not os.path.exists(CERTS_DIR):
        os.makedirs(CERTS_DIR)
        print(f"Directory created: {CERTS_DIR}")

def create_policy():
    """Creates the policy (with least privilege permissions)"""
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["iot:Connect"],
                "Resource": f"arn:aws:iot:{REGION}:*:client/{THING_NAME}"
            },
            {
                "Effect": "Allow",
                "Action": ["iot:Publish"],
                "Resource": f"arn:aws:iot:{REGION}:*:topic/home/heating/status"
            },
            {
                "Effect": "Allow",
                "Action": ["iot:Subscribe", "iot:Receive"],
                "Resource": f"arn:aws:iot:{REGION}:*:topicfilter/home/heating/commands" 
            }
        ]
    }
    
    try:
        iot_client.create_policy(
            policyName=POLICY_NAME,
            policyDocument=json.dumps(policy_document)
        )
        print(f"Policy created: {POLICY_NAME}")
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Policy already exists: {POLICY_NAME}")

def create_thing():
    """Creates the digital device (Thing)"""
    try:
        iot_client.create_thing(thingName=THING_NAME)
        print(f"Thing created: {THING_NAME}")
    except iot_client.exceptions.ResourceAlreadyExistsException:
        print(f"Thing already exists: {THING_NAME}")

def create_certificates():
    """Generates keys and certificate, then saves them"""
    response = iot_client.create_keys_and_certificate(setAsActive=True)
    certificate_arn = response['certificateArn']
    certificate_pem = response['certificatePem']
    key_public = response['keyPair']['PublicKey']
    key_private = response['keyPair']['PrivateKey']

    # Save files
    with open(f"{CERTS_DIR}/certificate.pem.crt", "w") as f:
        f.write(certificate_pem)
    with open(f"{CERTS_DIR}/private.pem.key", "w") as f:
        f.write(key_private)
    with open(f"{CERTS_DIR}/public.pem.key", "w") as f:
        f.write(key_public)
        
    print(f"Certificates saved to: {CERTS_DIR}")
    return certificate_arn

def attach_everything(cert_arn):
    """Attaches Policy, Thing, and Cert"""
    # Attach Policy to Certificate
    iot_client.attach_policy(policyName=POLICY_NAME, target=cert_arn)
    print("Policy attached to certificate")

    # Attach Thing to Certificate
    iot_client.attach_thing_principal(thingName=THING_NAME, principal=cert_arn)
    print("Thing attached to certificate")

def download_root_ca():
    """Downloads Amazon Root CA 1 (required for TLS handshake)"""
    url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
    destination = f"{CERTS_DIR}/AmazonRootCA1.pem"
    urllib.request.urlretrieve(url, destination)
    print(f"Root CA downloaded: {destination}")

def get_iot_endpoint():
    """Retrieves the unique IoT endpoint"""
    response = iot_client.describe_endpoint(endpointType='iot:Data-ATS')
    endpoint = response['endpointAddress']
    print(f"\nYOUR ENDPOINT (Save it!): {endpoint}")
    # Save to a config file so the Pi code can find it
    with open(f"{CERTS_DIR}/iot_config.json", "w") as f:
        json.dump({"endpoint": endpoint, "thing_name": THING_NAME}, f, indent=4)

if __name__ == "__main__":
    print("Starting IoT Provisioning...")
    create_directory()
    create_policy()
    create_thing()
    cert_arn = create_certificates()
    attach_everything(cert_arn)
    download_root_ca()
    get_iot_endpoint()
    print("\nSUCCESS! Hardware keys are ready in the 'hardware/certs' folder.")