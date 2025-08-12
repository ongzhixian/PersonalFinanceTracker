\# AWS MCP Server



A comprehensive Model Context Protocol (MCP) server for interacting with AWS services using FastMCP.



\## Features



This MCP server provides tools and resources for interacting with various AWS services:



\### Supported AWS Services



\- \*\*S3\*\* - Simple Storage Service

&nbsp; - List buckets and objects

&nbsp; - Create buckets

&nbsp; - Get bucket information and metadata



\- \*\*EC2\*\* - Elastic Compute Cloud

&nbsp; - List instances across regions

&nbsp; - Get detailed instance information

&nbsp; - Instance state and metadata



\- \*\*Lambda\*\* - Serverless Functions

&nbsp; - List functions across regions

&nbsp; - Get function configuration and details

&nbsp; - Function metadata and tags



\- \*\*DynamoDB\*\* - NoSQL Database

&nbsp; - List tables across regions

&nbsp; - Get table schema and configuration

&nbsp; - Table metadata and indexes



\- \*\*IAM\*\* - Identity and Access Management

&nbsp; - List users and roles

&nbsp; - Get user/role metadata

&nbsp; - Access information



\- \*\*CloudWatch\*\* - Monitoring and Observability

&nbsp; - List metrics by namespace

&nbsp; - Get log groups

&nbsp; - Monitoring data access



\- \*\*Cost Explorer\*\* - Cost Analysis (optional)

&nbsp; - Get cost estimates by service

&nbsp; - Historical cost data



\## Installation



1\. Install the required dependencies:

```bash

pip install -r aws\_mcp\_requirements.txt

```



2\. Configure your AWS credentials using one of these methods:

&nbsp;  - AWS CLI: `aws configure`

&nbsp;  - Environment variables: `AWS\_ACCESS\_KEY\_ID` and `AWS\_SECRET\_ACCESS\_KEY`

&nbsp;  - IAM roles (if running on EC2)

&nbsp;  - AWS SSO



3\. Test your AWS connection:

```bash

aws sts get-caller-identity

```



\## Usage



\### 1. Standalone MCP Server (for MCP clients)



Run the server in standalone mode for use with MCP-compatible clients:



```bash

python example\_aws\_fastmcp.py

```



Or with custom AWS profile:

```bash

python example\_aws\_fastmcp.py --aws-profile my-profile

```



\### 2. FastAPI Mode (with web interface)



Run with FastAPI for HTTP endpoints and web interface:



```bash

python example\_aws\_fastmcp.py --mode fastapi --host 0.0.0.0 --port 8000

```



Access the server at:

\- Main interface: http://localhost:8000

\- Health check: http://localhost:8000/health

\- MCP endpoints: http://localhost:8000/mcp



\### 3. Using with MCP Inspector



For development and testing:



```bash

\# Install MCP Inspector

npm install -g @modelcontextprotocol/inspector



\# Run with MCP Inspector

npx @modelcontextprotocol/inspector python example\_aws\_fastmcp.py

```



\### 4. Integration with MCP Clients



Configure in your MCP client (like Claude Desktop):



```json

{

&nbsp; "mcpServers": {

&nbsp;   "aws": {

&nbsp;     "command": "python",

&nbsp;     "args": \["/path/to/example\_aws\_fastmcp.py"],

&nbsp;     "env": {

&nbsp;       "AWS\_PROFILE": "default"

&nbsp;     }

&nbsp;   }

&nbsp; }

}

```



\## Available Tools



\### S3 Tools

\- `list\_s3\_buckets()` - List all S3 buckets

\- `list\_s3\_objects(bucket\_name, prefix, max\_keys)` - List objects in bucket

\- `create\_s3\_bucket(bucket\_name, region)` - Create new bucket



\### EC2 Tools

\- `list\_ec2\_instances(region)` - List EC2 instances

\- `get\_ec2\_instance\_details(instance\_id, region)` - Get instance details



\### Lambda Tools

\- `list\_lambda\_functions(region)` - List Lambda functions

\- `get\_lambda\_function\_details(function\_name, region)` - Get function details



\### DynamoDB Tools

\- `list\_dynamodb\_tables(region)` - List DynamoDB tables

\- `get\_dynamodb\_table\_details(table\_name, region)` - Get table details



\### IAM Tools

\- `list\_iam\_users()` - List IAM users

\- `list\_iam\_roles()` - List IAM roles



\### CloudWatch Tools

\- `get\_cloudwatch\_metrics(namespace, metric\_name, start\_time\_hours\_ago, region)` - Get metrics

\- `list\_cloudwatch\_log\_groups(region, prefix)` - List log groups



\### Utility Tools

\- `get\_aws\_account\_info()` - Get account information

\- `estimate\_aws\_costs(service, region, days)` - Get cost estimates



\## Available Resources



\### Static Resources

\- `aws-mcp://version` - Server version

\- `aws-mcp://aws-regions` - List of AWS regions

\- `aws-mcp://aws-services` - Supported services



\### Dynamic Resources

\- `aws-mcp://s3/bucket/{bucket\_name}/info` - S3 bucket information



\## Configuration



\### AWS Profile

Set your AWS profile in the script or via command line:

```bash

python example\_aws\_fastmcp.py --aws-profile production

```



\### Configuration File

Modify `aws\_mcp\_config.json` to customize:

\- AWS services to enable/disable

\- Default regions

\- Service-specific settings

\- FastAPI configuration



\### Environment Variables

\- `AWS\_PROFILE` - AWS profile to use

\- `AWS\_DEFAULT\_REGION` - Default AWS region

\- `AWS\_ACCESS\_KEY\_ID` - AWS access key

\- `AWS\_SECRET\_ACCESS\_KEY` - AWS secret key



\## Example Usage



\### Using the Examples Script

```bash

python example\_aws\_mcp\_usage.py

```



\### Python Client Example

```python

from fastmcp import Client

import asyncio



async def example():

&nbsp;   async with Client("stdio", "python", "example\_aws\_fastmcp.py") as client:

&nbsp;       # List S3 buckets

&nbsp;       result = await client.call\_tool("list\_s3\_buckets")

&nbsp;       print("S3 Buckets:", result)

&nbsp;       

&nbsp;       # Get EC2 instances

&nbsp;       result = await client.call\_tool("list\_ec2\_instances", {"region": "us-east-1"})

&nbsp;       print("EC2 Instances:", result)

&nbsp;       

&nbsp;       # Read server version

&nbsp;       resource = await client.read\_resource("aws-mcp://version")

&nbsp;       print("Version:", resource.contents\[0].text)



asyncio.run(example())

```



\## Security Considerations



1\. \*\*AWS Credentials\*\*: Use IAM roles with least privilege principle

2\. \*\*Network Access\*\*: Restrict FastAPI mode to trusted networks

3\. \*\*Cost Monitoring\*\*: Be aware that some operations may incur AWS costs

4\. \*\*Rate Limiting\*\*: Implement rate limiting for production use



\## Error Handling



The server includes comprehensive error handling:

\- Graceful degradation when AWS services are unavailable

\- Detailed error messages for troubleshooting

\- Fallback responses for missing credentials



\## Development



\### Adding New Services

1\. Create new client in the initialization section

2\. Add tools using `@mcp.tool()` decorator

3\. Add resources using `@mcp.resource()` decorator

4\. Update configuration file and documentation



\### Testing

```bash

\# Test AWS connectivity

aws sts get-caller-identity



\# Test MCP server

python example\_aws\_mcp\_usage.py



\# Test with specific AWS profile

AWS\_PROFILE=test python example\_aws\_fastmcp.py

```



\## Troubleshooting



\### Common Issues



1\. \*\*AWS Credentials Not Found\*\*

&nbsp;  ```

&nbsp;  Solution: Configure AWS credentials using aws configure or environment variables

&nbsp;  ```



2\. \*\*Permission Denied\*\*

&nbsp;  ```

&nbsp;  Solution: Ensure your AWS user/role has necessary permissions for the services you're accessing

&nbsp;  ```



3\. \*\*Region Errors\*\*

&nbsp;  ```

&nbsp;  Solution: Specify the correct region or ensure the service is available in your region

&nbsp;  ```



4\. \*\*Cost Explorer Access Denied\*\*

&nbsp;  ```

&nbsp;  Solution: Cost Explorer requires special permissions and may not be available in all accounts

&nbsp;  ```



\### Debug Mode

Run with debug logging:

```bash

python -c "import logging; logging.basicConfig(level=logging.DEBUG); import example\_aws\_fastmcp; example\_aws\_fastmcp.main()"

```



\## License



This project is provided as-is for educational and development purposes.



\## Contributing



1\. Fork the repository

2\. Create a feature branch

3\. Add tests for new functionality

4\. Submit a pull request



\## Changelog



\### v1.0.0

\- Initial release

\- Support for S3, EC2, Lambda, DynamoDB, IAM, CloudWatch

\- FastAPI integration

\- Comprehensive error handling

\- MCP Inspector compatibility



Usage 

Next steps:

1\. Run: python example\_aws\_fastmcp.py --mode fastapi

2\. Access: http://localhost:8000

3\. Or run: python example\_aws\_mcp\_usage.py

