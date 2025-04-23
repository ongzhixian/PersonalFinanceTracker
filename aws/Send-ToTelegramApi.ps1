# plato_dev_bot
# /slack/emptool/artemis
# /telegram/plato_dev_bot

$secretsJsonPath = [System.Environment]::ExpandEnvironmentVariables("%APPDATA%\Microsoft\UserSecrets\47df7034-c1c1-4b87-8373-89f5e42fc9ec\secrets.json")
$secretsJson = Get-Content $secretsJsonPath | ConvertFrom-Json
if ($secretsJson.PSobject.Properties.Name -contains "telegram_bot_plato_dev_bot_token") {
    Set-Variable api_token -Option Constant -Value $secretsJson.telegram_bot_plato_dev_bot_token
}

if ($api_token -eq $null) {
    Write-Error "``api_token`` is not defined in secrets.json"
    return
}

Set-Variable bot_api_base_url -Option Constant -Value "https://api.telegram.org/bot$api_token"


$headers = @{
    "Content-type" = "application/json; charset=utf-8"
}

function Get-BotInfo {
    param ()
    $url = "$bot_api_base_url/getMe"
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    $response
}

function Get-WebhookInfo {
    param ()
    $url = "$bot_api_base_url/getWebhookInfo"
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    $response
}

function Set-Webhook {
    param (
        [string] $message
    )
    $url = "$bot_api_base_url/setWebhook"
    $body = @{
        "url" = "https://flikx8i3c2.execute-api.us-east-1.amazonaws.com/telegram/plato_dev_bot"
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -Verbose
    $response
}

function Send-Message {
    param (
        [string] $message
    )
    $url = "$bot_api_base_url/sendMessage"
    $body = @{
        "chat_id" = "53274105"
        "text" = $message
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -Verbose
    $response
}

function Get-BotCommands {
    param (
        [string] $message
    )
    $url = "$bot_api_base_url/getMyCommands"
#     $body = @{
#         "chat_id" = "53274105"
#         "text" = $message
#     } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers # -Body $body -Verbose
    $response
}

# Get-BotInfo
#Get-WebhookInfo
#Set-Webhook
#Send-Message "Mesage received"
Get-BotCommands
