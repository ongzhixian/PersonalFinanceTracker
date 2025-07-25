\# Overview



\# GROUP

Groups:

aws-administrators      

&nbsp;   Policies:

&nbsp;   -- AdministratorAccess (built-in)

iam-administrators      -- All IAM

&nbsp;   Policies:

&nbsp;   -- IAMFullAccess (built-in)

group-administrators

&nbsp;   Policies: (can perform)

&nbsp;   -- group-administration

user-group-administrators

&nbsp;   Policies: (can perform)

&nbsp;   -- user-group-administration

developers

&nbsp;   Policies: (can perform ..10)

&nbsp;   -- modify-resources ()

architects

&nbsp;   Policies: (can perform ..10)

&nbsp;   -- compute-administration

&nbsp;   -- storage-administration

&nbsp;   -- datastore-administration

&nbsp;   

operations-administrators

&nbsp;   Policies: (can perform ..10)

&nbsp;   -- scheduler-administration

&nbsp;   -- secrets-administration

&nbsp;   -- endpoint-administration

release-administrators

&nbsp;   Policies: (can perform ..10)

&nbsp;   -- resources-administration

&nbsp;   -- endpoint-administration

&nbsp;   -- integration-administration





tech-notes-press



\# POLICIES (PERMISSIONS)



\* group-administration

&nbsp;   CRUD <group>

\* user-group-administration

&nbsp;   -R-- <group>

&nbsp;   CRUD <user>

&nbsp;   Add/Remove user to group

\* compute-administration

&nbsp;   <lambda>

\* storage-administration

&nbsp;   <s3>

\* datastore-administration

&nbsp;   <dyanamoDb>

\* resources-modification

&nbsp;   <lambda>

&nbsp;   <s3>

&nbsp;   <dyanamoDb>

&nbsp;   <sqs>

&nbsp;   <sns>

\* read-application

&nbsp;   <event-bridge>

\* resources-administration

&nbsp;   <lambda>

&nbsp;   <s3>

&nbsp;   <dyanamoDb>

&nbsp;   



\* system-assets-administration

&nbsp;   <lambda>

&nbsp;   <s3>

&nbsp;   <dyanamoDb>



\* integration-services 

&nbsp;   (https://docs.aws.amazon.com/whitepapers/latest/aws-overview/amazon-web-services-cloud-platform.html)

&nbsp;   <sqs>

&nbsp;   <sns>

&nbsp;   <event-bridge>

&nbsp;   

\* scheduler-administration

&nbsp;   <event-bridge>

\* secrets-administration

&nbsp;   <event-bridge>

\* endpoint-administration (content-delivery)

&nbsp;   <cloudfront>

&nbsp;   <api-gateway>

&nbsp;   <certificate manager>



\* analytics

&nbsp;   <athena>

&nbsp;   <glueDb>



&nbsp;   





\# USERS



\# ROLES



IAM roles:

&nbsp;   -- primarily use by services (example: Lambda has execution role)

&nbsp;   -- we should mirror roles based on some defined user



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

&nbsp;   AWSLambdaRole

&nbsp;       {

&nbsp;           "Version": "2012-10-17",

&nbsp;           "Statement": \[

&nbsp;               {

&nbsp;                   "Effect": "Allow",

&nbsp;                   "Action": \[

&nbsp;                       "lambda:InvokeFunction"

&nbsp;                   ],

&nbsp;                   "Resource": \[

&nbsp;                       "\*"

&nbsp;                   ]

&nbsp;               }

&nbsp;           ]

&nbsp;       }

&nbsp;   Trust relationship:

&nbsp;   {

&nbsp;       "Version": "2012-10-17",

&nbsp;       "Statement": \[

&nbsp;           {

&nbsp;               "Sid": "",

&nbsp;               "Effect": "Allow",

&nbsp;               "Principal": {

&nbsp;                   "Service": "lambda.amazonaws.com"

&nbsp;               },

&nbsp;               "Action": "sts:AssumeRole"

&nbsp;           }

&nbsp;       ]

&nbsp;   }



ProjectAppRole

&nbsp;   Trust relationship:

&nbsp;   {

&nbsp;       "Version": "2012-10-17",

&nbsp;       "Statement": \[

&nbsp;           {

&nbsp;               "Effect": "Allow",

&nbsp;               "Principal": {

&nbsp;                   "Service": "lambda.amazonaws.com"

&nbsp;               },

&nbsp;               "Action": "sts:AssumeRole"

&nbsp;           },

&nbsp;           {

&nbsp;               "Effect": "Allow",

&nbsp;               "Principal": {

&nbsp;                   "Service": "scheduler.amazonaws.com"

&nbsp;               },

&nbsp;               "Action": "sts:AssumeRole",

&nbsp;               "Condition": {

&nbsp;                   "StringEquals": {

&nbsp;                       "aws:SourceAccount": "009167579319"

&nbsp;                   }

&nbsp;               }

&nbsp;           }

&nbsp;       ]

&nbsp;   }





lambda-developer

&nbsp;   Policy: AWSLambdaBasicExecutionRole

&nbsp;   Trust relationship:

&nbsp;   {

&nbsp;       "Version": "2012-10-17",

&nbsp;       "Statement": \[

&nbsp;           {

&nbsp;               "Sid": "",

&nbsp;               "Effect": "Allow",

&nbsp;               "Principal": {

&nbsp;                   "Service": "lambda.amazonaws.com"

&nbsp;               },

&nbsp;               "Action": "sts:AssumeRole"

&nbsp;           }

&nbsp;       ]

&nbsp;   }

react-todo-list-app

&nbsp;   AmazonDynamoDBFullAccess

&nbsp;   AWSLambdaBasicExecutionRole

&nbsp;   {

&nbsp;       "Version": "2012-10-17",

&nbsp;       "Statement": \[

&nbsp;           {

&nbsp;               "Action": \[

&nbsp;                   "dynamodb:GetItem",

&nbsp;                   "dynamodb:PutItem"

&nbsp;               ],

&nbsp;               "Resource": "arn:aws:dynamodb:us-east-1:009167579319:table/user",

&nbsp;               "Effect": "Allow"

&nbsp;           }

&nbsp;       ]

&nbsp;   }

&nbsp;   Trust relationship:

&nbsp;   {

&nbsp;       "Version": "2012-10-17",

&nbsp;       "Statement": \[

&nbsp;           {

&nbsp;               "Effect": "Allow",

&nbsp;               "Principal": {

&nbsp;                   "Service": "lambda.amazonaws.com"

&nbsp;               },

&nbsp;               "Action": "sts:AssumeRole"

&nbsp;           }

&nbsp;       ]

&nbsp;   }





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



