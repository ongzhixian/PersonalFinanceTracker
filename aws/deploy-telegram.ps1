# Deployment script
$awsProfile = "default"
$functionRole = "arn:aws:iam::009167579319:role/ProjectAppRole"
$functionName = "handle-telegram-plato_dev_bot"
$functionDescription = "Handle posts to plato_dev_bot Telegram bot"

function Compress-ToZipFile {
    Compress-Archive .\telegram_plato_dev_bot.py -DestinationPath .\publish\telegram_plato_dev_bot.zip -Force
}

function New-AwsLambda {
    param ()
        
    aws lambda create-function `
    --profile $awsProfile `
    --function-name $functionName `
    --description $functionDescription `
    --role $functionRole `
    --runtime python3.10 `
    --zip-file fileb://publish/telegram_plato_dev_bot.zip `
    --handler telegram_plato_dev_bot.lambda_handler
}

function Update-AwsLambdaConfiguration {
    param ()
    
    aws.exe lambda update-function-configuration `
    --profile $awsProfile `
    --environment 'Variables={bot_api_token=xxxx,version=1.0.1}' `
    --function-name $functionName
    #--description $functionDescription
}

function Update-AwsLambda {
    param ()
    
    aws.exe lambda update-function-code `
    --profile $awsProfile `
    --zip-file fileb://publish/telegram_plato_dev_bot.zip `
    --function-name $functionName
}


# MAIN SCRIPT

#Update-AwsLambdaConfiguration
Compress-ToZipFile
#New-AwsLambda
Update-AwsLambda