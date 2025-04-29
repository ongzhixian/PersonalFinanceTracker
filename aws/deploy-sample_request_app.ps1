# Deployment script
$awsProfile = "stub-dev"
$functionRole = "arn:aws:iam::009167579319:role/ProjectAppRole"
$functionName = "send-to-slack-test"
$functionDescription = "Send to Slack test channel"

function Compress-ToZipFile {
    Compress-Archive .\sample_request_app.py -DestinationPath .\sample-request-app.zip -Force
}

function New-AwsLambda {
    param ()
        
    aws lambda create-function `
    --profile $awsProfile `
    --function-name $functionName `
    --description $functionDescription `
    --role $functionRole `
    --runtime python3.10 `
    --zip-file fileb://sample-request-app.zip `
    --handler sample_request_app.lambda_handler
}

function Update-AwsLambdaConfiguration {
    param ()
    
    aws.exe lambda update-function-configuration `
    --profile $awsProfile `
    --environment 'Variables={bot_token=xxxx,bot_user_id=U08A4N0ULUR,version=1.0.1}' `
    --handler "sample_request_app.lambda_handler" `
    --function-name $functionName
    
    #--description $functionDescription
}

function Update-AwsLambda {
    param ()
    
    aws.exe lambda update-function-code `
    --profile $awsProfile `
    --zip-file fileb://sample-request-app.zip `
    --function-name $functionName
    
}


# MAIN SCRIPT

Update-AwsLambdaConfiguration
Compress-ToZipFile
#New-AwsLambda
#Update-AwsLambda
