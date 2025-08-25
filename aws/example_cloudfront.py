import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='default')
cloudfront_client = boto3.client('cloudfront')


def display_distribution_list():
    distributions = cloudfront_client.list_distributions()
    print("CloudFront distributions:\n")
    print(distributions)


def list_cache_policies():
    response = cloudfront_client.list_cache_policies()
    print(response)

def create_distribution():
    distribution_config = {
        'CallerReference': 'unique-string-12345',
        'Comment': 'My CloudFront distribution',
        'Enabled': True,
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'test-aug-2025.s3.amazonaws.com',
                    'DomainName': 'test-aug-2025.s3.amazonaws.com',
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'test-aug-2025.s3.amazonaws.com',
            "ViewerProtocolPolicy": "redirect-to-https",
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {
                    'Forward': 'none'
                }
            },
            'MinTTL': 0
        }
    }

    # Create the distribution
    response = cloudfront_client.create_distribution(
        DistributionConfig=distribution_config
    )

    # Print the distribution ID and domain name
    print("Distribution ID:", response['Distribution']['Id'])
    print("Domain Name:", response['Distribution']['DomainName'])
    print("Full Response:", response)



def main():
    # display_distribution_list()
    # Define the distribution configuration
    # create_distribution()
    list_cache_policies()

if __name__ == '__main__':
    main()
    