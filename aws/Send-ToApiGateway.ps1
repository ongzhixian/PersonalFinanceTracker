Set-Variable artemisBot -Option Constant -Value "@U08A4N0ULUR"

#$secretsJsonPath = [System.Environment]::ExpandEnvironmentVariables("%APPDATA%\Microsoft\UserSecrets\47df7034-c1c1-4b87-8373-89f5e42fc9ec\secrets.json")
#$secretsJson = Get-Content $secretsJsonPath | ConvertFrom-Json
#if ($secretsJson.PSobject.Properties.Name -contains "slack_bot_artemis_token") {
#    Set-Variable bot_api_token -Option Constant -Value $secretsJson.slack_bot_artemis_token
#}

$authorizationSecretToken = "secretTokenS"

$headers = @{
    'Content-type' = "application/json; charset=utf-8"
    'Authorization' = $authorizationSecretToken
}

function Test-SettingUrl {
    param (
        [string] $message
    )
    $url = "https://flikx8i3c2.execute-api.us-east-1.amazonaws.com/test-authz"
#    $body = @{
#        "type" = "url_verification"
#        "token" = "some token"
#        "challenge" = "some challenge"
#    } | ConvertTo-Json
    #$response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body

    try
    {
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers #-Body $body
        Write-Host "Response:"
        Write-Host $response | ConvertFrom-Json
    }
    catch
    {
        # Using $_.Exception.Message to get detailed error information
        Write-Host "Error occurred: $($_.Exception.Message)"

        # Using $PSItem (same as $_) to display full error details
        Write-Host "Full Error Details: $PSItem"
    }

}


Test-SettingUrl "hello world"


#Send-MessageToTestChannel "Some message"
#Send-MessageToGeneralChannel "<@U08A4N0ULUR> Hello to myself!"
#Send-MessageToTestHook "Sent a messaage to webhook for test channel https://flikx8i3c2.execute-api.us-east-1.amazonaws.com/slack/emptool/artemis"
#Send-MessageToGeneralHook "Sent a messaage to webhook for general channel"
#Get-AuthTest
#Test-SettingUrl
#Get-ConversationInfo 'D08AERL1CRE'
#$message_history = Get-ConversationHistory 'D08AERL1CRE'
#$message_history
##return
#foreach ($item in $message_history.messages) {
#    if ($item.text -eq "send some reply from lambda") {
#        Write-Host 'TODO: REMOVE' $item.ts
#        Remove-MessageFromChannel 'D08AERL1CRE' $item.ts
#    }
#    else {
#        $item.ts
#    }
#}


#Remove-MessageFromChannel 'D08AERL1CRE' '1745397807.875579'