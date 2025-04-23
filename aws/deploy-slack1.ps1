# Deployment script
$awsProfile = "stub-dev"
$functionRole = "arn:aws:iam::009167579319:role/ProjectAppRole"
$functionName = "handle-slack-artemis-post"
$functionDescription = "Handle posts to Artemis Slack bot"

function Compress-ToZipFile {
    Compress-Archive .\sample-slack\slack_artemis_bot.py -DestinationPath .\sample-slack\slack_artemis_bot.zip -Force
}

function New-AwsLambda {
    param ()
        
    aws lambda create-function `
    --profile $awsProfile `
    --function-name $functionName `
    --description $functionDescription `
    --role $functionRole `
    --runtime python3.10 `
    --zip-file fileb://sample-slack/slack_artemis_bot.zip `
    --handler slack_artemis_bot.lambda_handler
}

function Update-AwsLambdaConfiguration {
    param ()
    
    aws.exe lambda update-function-configuration `
    --profile $awsProfile `
    --environment 'Variables={bot_token=xxxx,bot_user_id=U08A4N0ULUR,version=1.0.1}' `
    --function-name $functionName
    #--description $functionDescription
}

function Update-AwsLambda {
    param ()
    
    aws.exe lambda update-function-code `
    --profile $awsProfile `
    --zip-file fileb://sample-slack/slack_artemis_bot.zip `
    --function-name $functionName
}


# MAIN SCRIPT

#Update-AwsLambdaConfiguration
Compress-ToZipFile
#New-AwsLambda
Update-AwsLambda
