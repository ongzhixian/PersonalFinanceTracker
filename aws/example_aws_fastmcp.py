"""
AWS MCP Server using FastMCP
Provides comprehensive AWS service integration via Model Context Protocol
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP, Context
from botocore.exceptions import ClientError, NoCredentialsError
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
URI_SCHEME = 'aws-mcp'
AWS_PROFILE = 'stub-dev'  # Change this to your preferred AWS profile
from example_common_aws import setup_aws_profile

# Initialize AWS clients
try:
    # boto3.setup_default_session(profile_name=AWS_PROFILE)
    setup_aws_profile()

    
    # Core AWS clients
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    ec2_client = boto3.client('ec2')
    lambda_client = boto3.client('lambda')
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb')
    iam_client = boto3.client('iam')
    cloudwatch_client = boto3.client('cloudwatch')
    logs_client = boto3.client('logs')
    
    logger.info("AWS clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AWS clients: {e}")
    # Initialize empty clients for testing
    s3_client = None
    ec2_client = None
    lambda_client = None
    dynamodb_client = None
    iam_client = None
    cloudwatch_client = None
    logs_client = None

# Create FastMCP instance
mcp = FastMCP(
    name="AWS MCP Server",
    instructions="""
    AWS Model Context Protocol Server providing comprehensive AWS service integration.
    
    This server provides tools and resources for interacting with various AWS services including:
    - S3 bucket and object management
    - EC2 instance management
    - Lambda function operations
    - DynamoDB table operations
    - IAM user and role management
    - CloudWatch metrics and logs
    
    All operations respect AWS IAM permissions and will fail gracefully if credentials are not configured.
    """)

########################################
# STATIC RESOURCES
########################################

@mcp.resource(
    uri=f"{URI_SCHEME}://version",
    name="AWS MCP Server Version",
    description="Returns the version of this AWS MCP server",
    mime_type="text/plain",
    tags={"info", "version"}
)
def get_version():
    """Get server version"""
    return "1.0.0"

@mcp.resource(
    uri=f"{URI_SCHEME}://aws-regions",
    name="AWS Regions",
    description="List of all AWS regions",
    mime_type="application/json",
    tags={"aws", "regions"}
)
def get_aws_regions():
    """Get list of AWS regions"""
    try:
        regions = boto3.Session().get_available_regions('ec2')
        return {
            "regions": regions,
            "count": len(regions)
        }
    except Exception as e:
        return {"error": str(e), "regions": []}

@mcp.resource(
    uri=f"{URI_SCHEME}://aws-services",
    name="Supported AWS Services",
    description="List of AWS services supported by this MCP server",
    mime_type="application/json",
    tags={"aws", "services"}
)
def get_supported_services():
    """Get list of supported AWS services"""
    return {
        "services": [
            {"name": "S3", "description": "Simple Storage Service - Object storage"},
            {"name": "EC2", "description": "Elastic Compute Cloud - Virtual servers"},
            {"name": "Lambda", "description": "Serverless compute functions"},
            {"name": "DynamoDB", "description": "NoSQL database service"},
            {"name": "IAM", "description": "Identity and Access Management"},
            {"name": "CloudWatch", "description": "Monitoring and observability"},
            {"name": "CloudWatch Logs", "description": "Log management service"}
        ],
        "count": 7
    }

########################################
# S3 TOOLS
########################################

@mcp.tool()
def list_s3_buckets() -> Dict[str, Any]:
    """List all S3 buckets in the account"""
    try:
        if not s3_client:
            raise Exception("S3 client not initialized")
        
        response = s3_client.list_buckets()
        buckets = []
        
        for bucket in response['Buckets']:
            bucket_info = {
                "name": bucket['Name'],
                "creation_date": bucket['CreationDate'].isoformat()
            }
            
            # Try to get bucket region
            try:
                location = s3_client.get_bucket_location(Bucket=bucket['Name'])
                bucket_info["region"] = location.get('LocationConstraint', 'us-east-1')
            except:
                bucket_info["region"] = "unknown"
            
            buckets.append(bucket_info)
        
        return {
            "buckets": buckets,
            "count": len(buckets)
        }
    except Exception as e:
        return {"error": str(e), "buckets": []}

@mcp.tool()
def list_s3_objects(bucket_name: str, prefix: str = "", max_keys: int = 100) -> Dict[str, Any]:
    """List objects in an S3 bucket"""
    try:
        if not s3_client:
            raise Exception("S3 client not initialized")
        
        kwargs = {
            'Bucket': bucket_name,
            'MaxKeys': max_keys
        }
        
        if prefix:
            kwargs['Prefix'] = prefix
        
        response = s3_client.list_objects_v2(**kwargs)
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "etag": obj['ETag'].strip('"'),
                    "storage_class": obj.get('StorageClass', 'STANDARD')
                })
        
        return {
            "bucket": bucket_name,
            "prefix": prefix,
            "objects": objects,
            "count": len(objects),
            "truncated": response.get('IsTruncated', False)
        }
    except Exception as e:
        return {"error": str(e), "objects": []}

@mcp.tool()
def create_s3_bucket(bucket_name: str, region: str = "us-east-1") -> Dict[str, Any]:
    """Create a new S3 bucket"""
    try:
        if not s3_client:
            raise Exception("S3 client not initialized")
        
        # Create bucket configuration
        create_bucket_config = {}
        if region != 'us-east-1':
            create_bucket_config['LocationConstraint'] = region
        
        if create_bucket_config:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=create_bucket_config
            )
        else:
            s3_client.create_bucket(Bucket=bucket_name)
        
        return {
            "bucket_name": bucket_name,
            "region": region,
            "status": "created"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}

########################################
# EC2 TOOLS
########################################

@mcp.tool()
def list_ec2_instances(region: str = "us-east-1") -> Dict[str, Any]:
    """List EC2 instances in a specific region"""
    try:
        ec2_regional = boto3.client('ec2', region_name=region)
        response = ec2_regional.describe_instances()
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Get instance name from tags
                name = "N/A"
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                
                instances.append({
                    "instance_id": instance['InstanceId'],
                    "name": name,
                    "instance_type": instance['InstanceType'],
                    "state": instance['State']['Name'],
                    "launch_time": instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None,
                    "availability_zone": instance['Placement']['AvailabilityZone'],
                    "private_ip": instance.get('PrivateIpAddress', 'N/A'),
                    "public_ip": instance.get('PublicIpAddress', 'N/A')
                })
        
        return {
            "region": region,
            "instances": instances,
            "count": len(instances)
        }
    except Exception as e:
        return {"error": str(e), "instances": []}

@mcp.tool()
def get_ec2_instance_details(instance_id: str, region: str = "us-east-1") -> Dict[str, Any]:
    """Get detailed information about a specific EC2 instance"""
    try:
        ec2_regional = boto3.client('ec2', region_name=region)
        response = ec2_regional.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations']:
            return {"error": "Instance not found"}
        
        instance = response['Reservations'][0]['Instances'][0]
        
        # Parse tags
        tags = {}
        if 'Tags' in instance:
            tags = {tag['Key']: tag['Value'] for tag in instance['Tags']}
        
        # Parse security groups
        security_groups = []
        if 'SecurityGroups' in instance:
            security_groups = [
                {"id": sg['GroupId'], "name": sg['GroupName']} 
                for sg in instance['SecurityGroups']
            ]
        
        return {
            "instance_id": instance['InstanceId'],
            "instance_type": instance['InstanceType'],
            "state": instance['State']['Name'],
            "launch_time": instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None,
            "availability_zone": instance['Placement']['AvailabilityZone'],
            "vpc_id": instance.get('VpcId', 'N/A'),
            "subnet_id": instance.get('SubnetId', 'N/A'),
            "private_ip": instance.get('PrivateIpAddress', 'N/A'),
            "public_ip": instance.get('PublicIpAddress', 'N/A'),
            "key_name": instance.get('KeyName', 'N/A'),
            "security_groups": security_groups,
            "tags": tags,
            "monitoring": instance.get('Monitoring', {}).get('State', 'N/A')
        }
    except Exception as e:
        return {"error": str(e)}

########################################
# LAMBDA TOOLS
########################################

@mcp.tool()
def list_lambda_functions(region: str = "us-east-1") -> Dict[str, Any]:
    """List Lambda functions in a specific region"""
    try:
        lambda_regional = boto3.client('lambda', region_name=region)
        response = lambda_regional.list_functions()
        
        functions = []
        for func in response['Functions']:
            functions.append({
                "function_name": func['FunctionName'],
                "runtime": func['Runtime'],
                "handler": func['Handler'],
                "code_size": func['CodeSize'],
                "description": func.get('Description', ''),
                "timeout": func['Timeout'],
                "memory_size": func['MemorySize'],
                "last_modified": func['LastModified'],
                "role": func['Role'],
                "version": func['Version']
            })
        
        return {
            "region": region,
            "functions": functions,
            "count": len(functions)
        }
    except Exception as e:
        return {"error": str(e), "functions": []}

@mcp.tool()
def get_lambda_function_details(function_name: str, region: str = "us-east-1") -> Dict[str, Any]:
    """Get detailed information about a specific Lambda function"""
    try:
        lambda_regional = boto3.client('lambda', region_name=region)
        
        # Get function configuration
        config_response = lambda_regional.get_function(FunctionName=function_name)
        config = config_response['Configuration']
        code = config_response['Code']
        
        # Get function tags if available
        try:
            tags_response = lambda_regional.list_tags(Resource=config['FunctionArn'])
            tags = tags_response.get('Tags', {})
        except:
            tags = {}
        
        return {
            "function_name": config['FunctionName'],
            "function_arn": config['FunctionArn'],
            "runtime": config['Runtime'],
            "role": config['Role'],
            "handler": config['Handler'],
            "code_size": config['CodeSize'],
            "description": config.get('Description', ''),
            "timeout": config['Timeout'],
            "memory_size": config['MemorySize'],
            "last_modified": config['LastModified'],
            "code_sha256": config['CodeSha256'],
            "version": config['Version'],
            "state": config.get('State', 'N/A'),
            "environment_variables": config.get('Environment', {}).get('Variables', {}),
            "vpc_config": config.get('VpcConfig', {}),
            "layers": [layer['Arn'] for layer in config.get('Layers', [])],
            "tags": tags,
            "repository_type": code.get('RepositoryType', 'N/A')
        }
    except Exception as e:
        return {"error": str(e)}

########################################
# DYNAMODB TOOLS
########################################

@mcp.tool()
def list_dynamodb_tables(region: str = "us-east-1") -> Dict[str, Any]:
    """List DynamoDB tables in a specific region"""
    try:
        dynamodb_regional = boto3.client('dynamodb', region_name=region)
        response = dynamodb_regional.list_tables()
        
        tables_info = []
        for table_name in response['TableNames']:
            # Get table details
            try:
                table_response = dynamodb_regional.describe_table(TableName=table_name)
                table = table_response['Table']
                
                tables_info.append({
                    "table_name": table['TableName'],
                    "table_status": table['TableStatus'],
                    "creation_date": table['CreationDateTime'].isoformat(),
                    "item_count": table.get('ItemCount', 0),
                    "table_size_bytes": table.get('TableSizeBytes', 0),
                    "read_capacity": table.get('ProvisionedThroughput', {}).get('ReadCapacityUnits', 'N/A'),
                    "write_capacity": table.get('ProvisionedThroughput', {}).get('WriteCapacityUnits', 'N/A'),
                    "billing_mode": table.get('BillingModeSummary', {}).get('BillingMode', 'N/A')
                })
            except:
                tables_info.append({
                    "table_name": table_name,
                    "table_status": "Unknown",
                    "error": "Unable to get table details"
                })
        
        return {
            "region": region,
            "tables": tables_info,
            "count": len(tables_info)
        }
    except Exception as e:
        return {"error": str(e), "tables": []}

@mcp.tool()
def get_dynamodb_table_details(table_name: str, region: str = "us-east-1") -> Dict[str, Any]:
    """Get detailed information about a specific DynamoDB table"""
    try:
        dynamodb_regional = boto3.client('dynamodb', region_name=region)
        response = dynamodb_regional.describe_table(TableName=table_name)
        table = response['Table']
        
        # Parse key schema
        key_schema = []
        for key in table.get('KeySchema', []):
            key_schema.append({
                "attribute_name": key['AttributeName'],
                "key_type": key['KeyType']
            })
        
        # Parse attribute definitions
        attributes = []
        for attr in table.get('AttributeDefinitions', []):
            attributes.append({
                "attribute_name": attr['AttributeName'],
                "attribute_type": attr['AttributeType']
            })
        
        # Parse global secondary indexes
        gsi = []
        for index in table.get('GlobalSecondaryIndexes', []):
            gsi.append({
                "index_name": index['IndexName'],
                "index_status": index['IndexStatus'],
                "key_schema": index['KeySchema'],
                "projection": index['Projection']
            })
        
        return {
            "table_name": table['TableName'],
            "table_arn": table['TableArn'],
            "table_status": table['TableStatus'],
            "creation_date": table['CreationDateTime'].isoformat(),
            "item_count": table.get('ItemCount', 0),
            "table_size_bytes": table.get('TableSizeBytes', 0),
            "key_schema": key_schema,
            "attributes": attributes,
            "provisioned_throughput": table.get('ProvisionedThroughput', {}),
            "billing_mode": table.get('BillingModeSummary', {}).get('BillingMode', 'N/A'),
            "global_secondary_indexes": gsi,
            "stream_specification": table.get('StreamSpecification', {}),
            "sse_description": table.get('SSEDescription', {})
        }
    except Exception as e:
        return {"error": str(e)}

########################################
# IAM TOOLS
########################################

@mcp.tool()
def list_iam_users() -> Dict[str, Any]:
    """List IAM users in the account"""
    try:
        if not iam_client:
            raise Exception("IAM client not initialized")
        
        response = iam_client.list_users()
        
        users = []
        for user in response['Users']:
            users.append({
                "user_name": user['UserName'],
                "user_id": user['UserId'],
                "arn": user['Arn'],
                "path": user['Path'],
                "create_date": user['CreateDate'].isoformat(),
                "password_last_used": user.get('PasswordLastUsed', '').isoformat() if user.get('PasswordLastUsed') else 'Never'
            })
        
        return {
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        return {"error": str(e), "users": []}

@mcp.tool()
def list_iam_roles() -> Dict[str, Any]:
    """List IAM roles in the account"""
    try:
        if not iam_client:
            raise Exception("IAM client not initialized")
        
        response = iam_client.list_roles()
        
        roles = []
        for role in response['Roles']:
            roles.append({
                "role_name": role['RoleName'],
                "role_id": role['RoleId'],
                "arn": role['Arn'],
                "path": role['Path'],
                "create_date": role['CreateDate'].isoformat(),
                "description": role.get('Description', ''),
                "max_session_duration": role.get('MaxSessionDuration', 3600)
            })
        
        return {
            "roles": roles,
            "count": len(roles)
        }
    except Exception as e:
        return {"error": str(e), "roles": []}

########################################
# CLOUDWATCH TOOLS
########################################

@mcp.tool()
def get_cloudwatch_metrics(namespace: str, metric_name: str = "", start_time_hours_ago: int = 24, region: str = "us-east-1") -> Dict[str, Any]:
    """Get CloudWatch metrics for a specific namespace"""
    try:
        cloudwatch_regional = boto3.client('cloudwatch', region_name=region)
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=start_time_hours_ago)
        
        # List metrics in namespace
        list_kwargs = {'Namespace': namespace}
        if metric_name:
            list_kwargs['MetricName'] = metric_name
        
        response = cloudwatch_regional.list_metrics(**list_kwargs)
        
        metrics_info = []
        for metric in response['Metrics']:
            metrics_info.append({
                "metric_name": metric['MetricName'],
                "namespace": metric['Namespace'],
                "dimensions": metric.get('Dimensions', [])
            })
        
        return {
            "namespace": namespace,
            "region": region,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "metrics": metrics_info,
            "count": len(metrics_info)
        }
    except Exception as e:
        return {"error": str(e), "metrics": []}

@mcp.tool()
def list_cloudwatch_log_groups(region: str = "us-east-1", prefix: str = "") -> Dict[str, Any]:
    """List CloudWatch log groups"""
    try:
        logs_regional = boto3.client('logs', region_name=region)
        
        kwargs = {}
        if prefix:
            kwargs['logGroupNamePrefix'] = prefix
        
        response = logs_regional.describe_log_groups(**kwargs)
        
        log_groups = []
        for group in response['logGroups']:
            log_groups.append({
                "log_group_name": group['logGroupName'],
                "creation_time": datetime.fromtimestamp(group['creationTime']/1000).isoformat(),
                "retention_in_days": group.get('retentionInDays', 'Never expires'),
                "stored_bytes": group.get('storedBytes', 0),
                "arn": group.get('arn', ''),
                "metric_filter_count": group.get('metricFilterCount', 0)
            })
        
        return {
            "region": region,
            "prefix": prefix,
            "log_groups": log_groups,
            "count": len(log_groups)
        }
    except Exception as e:
        return {"error": str(e), "log_groups": []}

########################################
# UTILITY TOOLS
########################################

@mcp.tool()
def get_aws_account_info() -> Dict[str, Any]:
    """Get AWS account information"""
    try:
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        
        return {
            "account_id": response.get('Account', 'Unknown'),
            "user_id": response.get('UserId', 'Unknown'),
            "arn": response.get('Arn', 'Unknown'),
            "profile": AWS_PROFILE
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def estimate_aws_costs(service: str, region: str = "us-east-1", days: int = 30) -> Dict[str, Any]:
    """Get estimated AWS costs for a service (requires Cost Explorer API access)"""
    try:
        # Note: This requires Cost Explorer API which may not be available in all accounts
        ce_client = boto3.client('ce', region_name='us-east-1')  # Cost Explorer is only in us-east-1
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        # Filter for the specific service
        service_costs = []
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                if service.lower() in group['Keys'][0].lower():
                    service_costs.append({
                        "date": result['TimePeriod']['Start'],
                        "service": group['Keys'][0],
                        "cost": float(group['Metrics']['BlendedCost']['Amount']),
                        "currency": group['Metrics']['BlendedCost']['Unit']
                    })
        
        total_cost = sum(cost['cost'] for cost in service_costs)
        
        return {
            "service": service,
            "region": region,
            "period_days": days,
            "total_cost": total_cost,
            "currency": service_costs[0]['currency'] if service_costs else 'USD',
            "daily_costs": service_costs
        }
    except Exception as e:
        return {"error": str(e), "note": "Cost Explorer API access may not be available"}

########################################
# DYNAMIC RESOURCES
########################################

@mcp.resource(
    uri=f"{URI_SCHEME}://s3/bucket/{{bucket_name}}/info",
    name="S3 Bucket Information",
    description="Get information about a specific S3 bucket",
    mime_type="application/json",
    tags={"aws", "s3", "bucket"}
)
async def get_s3_bucket_info(bucket_name: str, ctx: Context) -> Dict[str, Any]:
    """Get detailed information about a specific S3 bucket"""
    try:
        if not s3_client:
            raise Exception("S3 client not initialized")
        
        # Get bucket location
        location_response = s3_client.get_bucket_location(Bucket=bucket_name)
        region = location_response.get('LocationConstraint', 'us-east-1')
        
        # Get bucket versioning
        try:
            versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
            versioning_status = versioning_response.get('Status', 'Disabled')
        except:
            versioning_status = 'Unknown'
        
        # Get bucket encryption
        try:
            encryption_response = s3_client.get_bucket_encryption(Bucket=bucket_name)
            encryption_enabled = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                encryption_enabled = False
            else:
                encryption_enabled = 'Unknown'
        
        # Get bucket policy
        try:
            policy_response = s3_client.get_bucket_policy(Bucket=bucket_name)
            has_policy = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                has_policy = False
            else:
                has_policy = 'Unknown'
        
        return {
            "bucket_name": bucket_name,
            "region": region,
            "versioning": versioning_status,
            "encryption_enabled": encryption_enabled,
            "has_bucket_policy": has_policy,
            "request_id": ctx.request_id,
            "accessed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "bucket_name": bucket_name}

########################################
# MAIN APPLICATION
########################################

def main():
    """Run the MCP server standalone"""
    print("Starting AWS MCP Server...")
    print(f"AWS Profile: {AWS_PROFILE}")
    print("Available tools:", [tool for tool in dir() if not tool.startswith('_')])
    
    # Run the MCP server
    # mcp.run(transport="sse", host="127.0.0.1", port=8000)
    mcp.run()

def create_fastapi_app() -> FastAPI:
    """Create FastAPI application with MCP server mounted"""
    # Mount the MCP app as a sub-application
    mcp_app = mcp.http_app()
    
    # Create FastAPI app
    app = FastAPI(
        title="AWS MCP Service",
        description="A comprehensive AWS service integration via Model Context Protocol",
        version="1.0.0",
        lifespan=mcp_app.lifespan
    )
    
    app.mount("/mcp", mcp_app, name="mcp")
    
    # Root endpoint
    @app.get("/")
    async def root() -> Dict[str, str]:
        """Root endpoint showing service information"""
        return {
            "service": "AWS MCP Service",
            "version": "1.0.0",
            "status": "running",
            "aws_profile": AWS_PROFILE,
            "mcp_endpoint": "/mcp"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health() -> Dict[str, str]:
        """Health check endpoint"""
        try:
            # Test AWS connectivity
            sts_client = boto3.client('sts')
            sts_client.get_caller_identity()
            aws_status = "healthy"
        except:
            aws_status = "aws_connection_failed"
        
        return {
            "status": "healthy",
            "aws_status": aws_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return app

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AWS MCP Server")
    parser.add_argument(
        "--mode", 
        choices=["standalone", "fastapi"], 
        default="standalone",
        help="Run mode: standalone MCP server or FastAPI with MCP mounted"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to bind to (FastAPI mode only)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind to (FastAPI mode only)"
    )
    parser.add_argument(
        "--aws-profile",
        default="stub-dev",
        help="AWS profile to use"
    )
    
    args = parser.parse_args()
    
    # Update AWS profile
    AWS_PROFILE = args.aws_profile
    
    if args.mode == "fastapi":
        print(f"Starting AWS MCP Server with FastAPI on {args.host}:{args.port}")
        app = create_fastapi_app()
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        main()