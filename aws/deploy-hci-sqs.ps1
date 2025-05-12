param (
    # Name of function in $PythonScriptPath
    [Alias("function", "fn")]
    [Parameter(Position=1,mandatory=$true)]
    [string] $FunctionName
)

# Usage: .\deploy-hci-sqs.ps1 update_hci_blazer_google_sheet

########################################
# UTILITARIAN FUNCTIONS

Set-Variable package_name -Option Constant -Value 'hci'
Set-Variable package_zip_file_name -Option Constant -Value "$package_name.zip"
Set-Variable package_file_list_path -Option Constant -Value "$($package_name)_sqs_lambda_file_list.txt"
Set-Variable publish_folder_path -Option Constant -Value './publish'
$awsProfile = 'default'

if ($null -ne $env:USERDNSDOMAIN) {
    $awsProfile = 'stub-dev'
}

function Set-PublishFolder {
    param (
        [Parameter(Mandatory=$true)]
        [string] $publish_folder_path
    )

    if (-not (Test-Path $publish_folder_path))
    {
        Write-Debug "Create missing publish folder."
        New-Item -ItemType Directory -Path $publish_folder_path
    }
}

function Get-FunctionNameList {
    param (
        [Parameter(Mandatory=$false)]
        [switch] $UseCache = $false
    )
    
    $listFunctionsResponse = aws lambda list-functions --profile $awsProfile | ConvertFrom-Json
    $functionNameList = $listFunctionsResponse.Functions | Select-Object -ExpandProperty FunctionName
    return $functionNameList
}

# PRODUCTION FUNCTIONS

function Update-LambdaFunction {
    param (
        [Parameter(Mandatory=$true)]
        [string] $FunctionName,
        [Parameter(Mandatory=$true)]
        [string] $ZipFilePath
    )

    Write-Host "Function [$FunctionName] updated using AWS-CLI"

    $response = aws lambda update-function-code `
    --function-name $FunctionName `
    --zip-file fileb://$ZipFilePath `
    --profile $awsProfile | ConvertFrom-Json

    Write-Host $response

}

function Update-LambdaConfiguration {
    param (
        [Parameter(Mandatory=$true)]
        [string] $FunctionName
    )
    # KIV for for now; haven't have a proper use case for this
    # aws lambda update-function-configuration --function-name dump_event_context --description "Dump event and context"
    # --description
    # --memory-size 128
    # --timeout 3
}

function Get-LambdaConfiguration {
    param (
        [Parameter(Mandatory=$true)]
        [string] $FunctionName
    )

    Write-Debug "Get function configuration for $FunctionName using AWS-CLI"

    $response = aws lambda get-function --function-name dump_event_context | ConvertFrom-Json
    return $response.Configuration
}

function Publish-LambdaFunction {
    param (
        [Parameter(Mandatory=$true)]
        [string] $FunctionName,
        [Parameter(Mandatory=$true)]
        [string] $ZipFilePath,
        [Parameter(Mandatory=$true)]
        [string] $HandlerName
    )
    # Write-Host TODO: Publish-LambdaFunction
    # Write-Host function-name:   $FunctionName
    # Write-Host zip-file:        $ZipFilePath
    # Write-Host handler:         $HandlerName
    # --description "some desc"
    # --memory-size 128
    # --timeout 3
    # --tags KeyName1=string,KeyName2=string

    Write-Debug "Create function for $FunctionName using AWS-CLI"

    return aws lambda create-function `
    --function-name $FunctionName `
    --runtime python3.10 `
    --zip-file fileb://$ZipFilePath `
    --handler $HandlerName `
    --role arn:aws:iam::009167579319:role/ProjectAppRole `
    --profile $awsProfile

}

########################################
# PREPARATION SCRIPT
Set-PublishFolder $publish_folder_path
# $publish_filename = "$($FunctionName).zip"
$publish_file_path = Join-Path $publish_folder_path $package_zip_file_name


########################################
# MAIN SCRIPT

# Usage: .\deploy-hci.ps1 put_user_credential

Write-Host Grab the files in $($package_file_list_path) and package it into $($package_zip_file_name)
[string[]]$file_list = $(Get-Content $package_file_list_path)
$archive_specs = @{
  Path = $file_list
  DestinationPath = $publish_file_path
}
Compress-Archive @archive_specs -Force

# Example $FunctionName = 'put_user_credential'
$LambdaName = "hci_$FunctionName"
$moduleName = "hci_blazer_sqs"
$handlerName = "$moduleName.$FunctionName"

Write-Host "Deploying Lambda $LambdaName (Handler: $handlerName)"

$functionNameList = Get-FunctionNameList
if ($functionNameList.Contains($LambdaName)) {
    Update-LambdaFunction $LambdaName $publish_file_path
} else {
    Publish-LambdaFunction $LambdaName $publish_file_path $handlerName
}