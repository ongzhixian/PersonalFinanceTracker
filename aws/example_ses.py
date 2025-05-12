import json
import boto3
from botocore.exceptions import ClientError
import pdb

boto3.setup_default_session(profile_name='default')
client = boto3.client('ses')

def list_identities():
    response = client.list_identities(IdentityType='EmailAddress')
    print(response)

def list_domains():
    response = client.list_identities(IdentityType='Domain')
    print(response)


if __name__ == '__main__':
    #list_identities()
    list_domains()