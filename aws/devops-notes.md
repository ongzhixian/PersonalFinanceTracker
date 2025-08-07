\# Overview

\# GROUP
Groups:
aws-administrators      
   Policies:
   -- AdministratorAccess (built-in)
iam-administrators      -- All IAM
   Policies:
   -- IAMFullAccess (built-in)
group-administrators
   Policies: (can perform)
   -- group-administration
user-group-administrators
   Policies: (can perform)
   -- user-group-administration
developers
   Policies: (can perform ..10)
   -- modify-resources ()
architects
   Policies: (can perform ..10)
   -- compute-administration
   -- storage-administration
   -- datastore-administration
   
operations-administrators
   Policies: (can perform ..10)
   -- scheduler-administration
   -- secrets-administration
   -- endpoint-administration
release-administrators
   Policies: (can perform ..10)
   -- resources-administration
   -- endpoint-administration
   -- integration-administration


tech-notes-press

\# POLICIES (PERMISSIONS)

\* group-administration
   CRUD <group>
\* user-group-administration
   -R-- <group>
   CRUD <user>
   Add/Remove user to group
\* compute-administration
   <lambda>
\* storage-administration
   <s3>
\* datastore-administration
   <dyanamoDb>
\* resources-modification
   <lambda>
   <s3>
   <dyanamoDb>
   <sqs>
   <sns>
\* read-application
   <event-bridge>
\* resources-administration
   <lambda>
   <s3>
   <dyanamoDb>
   

\* system-assets-administration
   <lambda>
   <s3>
   <dyanamoDb>

\* integration-services 
   (https://docs.aws.amazon.com/whitepapers/latest/aws-overview/amazon-web-services-cloud-platform.html)
   <sqs>
   <sns>
   <event-bridge>
   
\* scheduler-administration
   <event-bridge>
\* secrets-administration
   <event-bridge>
\* endpoint-administration (content-delivery)
   <cloudfront>
   <api-gateway>
   <certificate manager>

\* analytics
   <athena>
   <glueDb>

   


\# USERS

\# ROLES

IAM roles:
   -- primarily use by services (example: Lambda has execution role)
   -- we should mirror roles based on some defined user

IAM Roles: 
AWSServiceRoleForAPIGateway
AWSServiceRoleForApplicationAutoScaling\_DynamoDBTable
AWSServiceRoleForSchemas
AWSServiceRoleForSupport
AWSServiceRoleForTrustedAdvisor
cdk-hnb659fds-cfn-exec-role-009167579319-us-east-1
cdk-hnb659fds-deploy-role-009167579319-us-east-1
cdk-hnb659fds-file-publishing-role-009167579319-us-east-1
cdk-hnb659fds-image-publishing-role-009167579319-us-east-1
cdk-hnb659fds-lookup-role-009167579319-us-east-1
EimaAwsStack-HelloLambdaFunctionServiceRole82D29796-036OtBMj7zMl
Amazon\_EventBridge\_Scheduler\_LAMBDA\_751adab8ab
athenafederatedcatalog-eima-test-FunctionRole-a8o2gze1ybRD
UcmApplicationRole

AWSGlueServiceRole-lab1-bucket
eima-helloworld-lambda
   AWSLambdaRole
       {
           "Version": "2012-10-17",
           "Statement": \[
               {
                   "Effect": "Allow",
                   "Action": \[
                       "lambda:InvokeFunction"
                   ],
                   "Resource": \[
                       "\*"
                   ]
               }
           ]
       }
   Trust relationship:
   {
       "Version": "2012-10-17",
       "Statement": \[
           {
               "Sid": "",
               "Effect": "Allow",
               "Principal": {
                   "Service": "lambda.amazonaws.com"
               },
               "Action": "sts:AssumeRole"
           }
       ]
   }

ProjectAppRole
   Trust relationship:
   {
       "Version": "2012-10-17",
       "Statement": \[
           {
               "Effect": "Allow",
               "Principal": {
                   "Service": "lambda.amazonaws.com"
               },
               "Action": "sts:AssumeRole"
           },
           {
               "Effect": "Allow",
               "Principal": {
                   "Service": "scheduler.amazonaws.com"
               },
               "Action": "sts:AssumeRole",
               "Condition": {
                   "StringEquals": {
                       "aws:SourceAccount": "009167579319"
                   }
               }
           }
       ]
   }


lambda-developer
   Policy: AWSLambdaBasicExecutionRole
   Trust relationship:
   {
       "Version": "2012-10-17",
       "Statement": \[
           {
               "Sid": "",
               "Effect": "Allow",
               "Principal": {
                   "Service": "lambda.amazonaws.com"
               },
               "Action": "sts:AssumeRole"
           }
       ]
   }
react-todo-list-app
   AmazonDynamoDBFullAccess
   AWSLambdaBasicExecutionRole
   {
       "Version": "2012-10-17",
       "Statement": \[
           {
               "Action": \[
                   "dynamodb:GetItem",
                   "dynamodb:PutItem"
               ],
               "Resource": "arn:aws:dynamodb:us-east-1:009167579319:table/user",
               "Effect": "Allow"
           }
       ]
   }
   Trust relationship:
   {
       "Version": "2012-10-17",
       "Statement": \[
           {
               "Effect": "Allow",
               "Principal": {
                   "Service": "lambda.amazonaws.com"
               },
               "Action": "sts:AssumeRole"
           }
       ]
   }


Policies:
tech-notes-press
application\_administrator
AWSGlueServiceRole-lab1-bucket-EZCRC-s3Policy
AWSGlueServiceRole-DynamoDbCrawler-EZCRC-dynamoDBPolicy
ManageSimpleSystemsManagementParameterStore
Amazon-EventBridge-Scheduler-Execution-Policy-4d746049-4dc2-457d-b124-a2b70a9178b3
lambda-dev
group-administration



Groups:
aws-administrators
developers
tech-notes-press


Users:
basic\_cdk2\_developer
pgi\_dev 
s3tester
zhixian
github-deploy
mlp-dev



Users/Roles
Groups
Policies()
static-website-provisioning (policy)
Static-Content-Delivery
    - S3
    - CloudFront
    - Certificate Manager
Api-Delivery
    - Api Gateway
    - Lambda