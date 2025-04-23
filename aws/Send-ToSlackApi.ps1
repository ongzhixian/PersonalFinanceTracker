Set-Variable artemisBot -Option Constant -Value "@U08A4N0ULUR"

$secretsJsonPath = [System.Environment]::ExpandEnvironmentVariables("%APPDATA%\Microsoft\UserSecrets\47df7034-c1c1-4b87-8373-89f5e42fc9ec\secrets.json")
$secretsJson = Get-Content $secretsJsonPath | ConvertFrom-Json
if ($secretsJson.PSobject.Properties.Name -contains "slack_bot_artemis_token") {
    Set-Variable bot_api_token -Option Constant -Value $secretsJson.slack_bot_artemis_token
}

if ($bot_api_token -eq $null) {
    Write-Error "``bot_api_token`` is not defined in secrets.json"
    return
}

$headers = @{
    'Content-type' = "application/json; charset=utf-8"
    'Authorization' = "Bearer $bot_api_token"
}

Write-Host $headers
return

function Get-ConversationList {
    param ()
    $url = "https://slack.com/api/conversations.list?foo=bar&qwe=zxc&pretty=1"
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers #-Body $body
    $response
}

function Send-MessageToTestChannel {
    param (
        [string] $message
    )
    $url = "https://slack.com/api/chat.postMessage"
    $body = @{
        'channel' = "C08AEQW444Q"
        'text' = $message
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -Verbose
    $response
}

function Send-MessageToGeneralChannel {
    param (
        [string] $message
    )
    $url = "https://slack.com/api/chat.postMessage"
    $body = @{
        'channel' = "C04HATYTA2D"
        'text' = $message
    } | ConvertTo-Json
    #$response = Invoke-WebRequest -Uri $url -Method Post -Headers $headers -Body $body -Verbose
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -Verbose
    $response
}

# Incoming webhooks
# Sends messages to channels representing a specific app/bot

function Send-MessageToTestHook {
    param (
        [string] $message
    )
    $url = "https://hooks.slack.com/services/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"
    $body = @{
        'text' = $message
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
    $response
}

function Send-MessageToGeneralHook {
    param (
        [string] $message
    )
    $url = "https://hooks.slack.com/services/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"
    $body = @{
        'text' = $message
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
    $response
}


function Get-AuthTest {
    param (
        [string] $message
    )
    $url = "https://slack.com/api/auth.test"
    $body = @{
        'text' = $message
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
    $response
}

function Get-ConversationInfo {
    param (
        [string] $channel
    )
    $url = "https://slack.com/api/conversations.info?channel=$channel"
    # $body = @{
    #     'channel' = $channel
        
    # } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    $response
}



function Get-ConversationHistory {
    param (
        [string] $channel
    )
    $url = "https://slack.com/api/conversations.history?pretty=1&channel=$channel"
    # $body = @{
    #     'channel' = $channel
        
    # } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    $response
}

function Remove-MessageFromChannel {
    param (
        [string] $channel,
        [string] $timestamp
    )
    $url = "https://slack.com/api/chat.delete"
    $body = @{
        'channel' = $channel
        'ts' = $timestamp
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
    $response
}



function Test-SettingUrl {
    param (
        [string] $message
    )
    $url = "https://flikx8i3c2.execute-api.us-east-1.amazonaws.com/slack/emptool/artemis"
    $body = @{
        "type" = "url_verification"
        "token" = "some token"
        "challenge" = "some challenge"
    } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
    $response
}



#Send-MessageToTestChannel "Some message"
#Send-MessageToGeneralChannel "<@U08A4N0ULUR> Hello to myself!"
#Send-MessageToTestHook "Sent a messaage to webhook for test channel https://flikx8i3c2.execute-api.us-east-1.amazonaws.com/slack/emptool/artemis"
#Send-MessageToGeneralHook "Sent a messaage to webhook for general channel"
#Get-AuthTest
#Test-SettingUrl
#Get-ConversationInfo 'D08AERL1CRE'
$message_history = Get-ConversationHistory 'D08AERL1CRE'
$message_history
#return
foreach ($item in $message_history.messages) {
    if ($item.text -eq "send some reply from lambda") {
        Write-Host 'TODO: REMOVE' $item.ts
        Remove-MessageFromChannel 'D08AERL1CRE' $item.ts
    }
    else {
        $item.ts
    }
}


#Remove-MessageFromChannel 'D08AERL1CRE' '1745397807.875579'