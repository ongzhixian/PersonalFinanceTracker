<#
    .SYNOPSIS
        Packages a Python function into a zip file for deployment to AWS Lambda.
        
    .DESCRIPTION
        Given:
        1. a path to a Python script file 
        2. a function name that is defined within the Python script file

        Then script will:
        1. create a `publish` folder (if not exist)
        2. create a zip file based on the function name argument in publish folder
        3. 

        Particularly when the comment must be frequently edited,
        as with the help and documentation for a function or script.
        
    .EXAMPLE
        Deploy using an relative script path

        .\deploy-lambda.ps1 .\explore.py dump_event_context

    .EXAMPLE
        Deploy using an absolute script path

        This deploys 

        .\deploy-lambda.ps1 C:\src\github.com\ongzhixian\pft-aws\aws\explore.py dump_event_context

    .INPUTS
    
    .OUTPUTS

    .LINK

    .NOTES
        Test deployed AWS Lambda function

        aws lambda invoke --function-name dump_event_context .\response.json

        Detail on what the script does, if this is needed.
        Get-Help .\deploy-lambda.ps1
        Get-Help .\deploy-lambda.ps1 -Full

        # Usage:
        #   deploy-lambda.ps1 <filename>   <function_name>
        # .\deploy-lambda.ps1 .\explore.py dump_event_context
        # .\deploy-lambda.ps1 C:\src\github.com\ongzhixian\pft-aws\aws\explore.py dump_event_context
        # Get-Help .\deploy-lambda.ps1
        # Test deployed function
        # aws lambda invoke --function-name dump_event_context .\response.json
#>

param (
    # Path to Python script file that contains $FunctionName
    [Alias("script", "path", "f")]
    [Parameter(Position=0,mandatory=$true)]
    [string] $PythonScriptPath,

    # Name of function in $PythonScriptPath
    [Alias("function", "fn")]
    [Parameter(Position=1,mandatory=$true)]
    [string] $FunctionName,
    
    # Whethher to use cached function name list; default $true
    [Alias("cache")]
    [Parameter(Position=2,mandatory=$false)]
    [switch] $UseCache
)

########################################
# UTILITARIAN FUNCTIONS

Set-Variable publish_folder_path -Option Constant -Value './publish'

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
    
    $listFunctionsResponse = aws lambda list-functions | ConvertFrom-Json
    $functionNameList = $listFunctionsResponse.Functions | Select-Object -ExpandProperty FunctionName
    return $functionNameList
}


# function Update-Lambda {
#     param ()
#     Write-Host "Updating function $functionName"

#     Compress-Archive .\main.py -DestinationPath main.zip  -Force
    
#     aws.exe lambda update-function-code `
#     --profile $profile `
#     --zip-file fileb://main.zip `
#     --function-name $functionName `
# }

# function FunctionName2 {
#     Compress-Archive .\main.py -DestinationPath main.zip -Force
#     aws lambda update-function-code --function-name basic-lambda2 --zip-file fileb://main.zip
# }

# function FunctionName {
#     aws lambda create-function `
#     --function-name basic-lambda2 `
#     --runtime python3.10 `
#     --zip-file fileb://main.zip `
#     --handler main.lambda_handler `
#     --role arn:aws:iam::009167579319:role/ProjectAppRole
# }

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
    --zip-file fileb://$ZipFilePath | ConvertFrom-Json
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
    --role arn:aws:iam::009167579319:role/ProjectAppRole
}

########################################
# MAIN SCRIPT

#Write-Host Ok. So we want to deploy function [$FunctionName] that can be found in [$PythonScriptPath]
Write-Debug "Deploy function [$FunctionName] that can be found in [$PythonScriptPath]"

Set-PublishFolder $publish_folder_path
$publish_filename = "$($FunctionName).zip"
$publish_file_path = Join-Path $publish_folder_path $publish_filename

# Write-Host Target $publish_file_path
Compress-Archive $PythonScriptPath -DestinationPath $publish_file_path -Force
#Write-Debug "Ok2. So we want to deploy function "
# Compress-Archive creates dump_event_context.zip file containing explore.py

# $listFunctionsResponse = aws lambda list-functions | ConvertFrom-Json
# $functionNameList = $listFunctionsResponse.Functions | Select-Object -ExpandProperty FunctionName
#$functionNameList = Get-FunctionNameList -UseCache:$false
$functionNameList = Get-FunctionNameList

$moduleName = Split-Path $PythonScriptPath -LeafBase
$handlerName = "$moduleName.$FunctionName"

#Write-Host Ok. So we want to deploy function [$FunctionName] that can be found in [$PythonScriptPath]
if ($functionNameList.Contains($FunctionName)) {
    Update-LambdaFunction $FunctionName $publish_file_path
} else {
    Publish-LambdaFunction $FunctionName $publish_file_path $handlerName
}



# Usage:
#   deploy-lambda.ps1 <filename>   <function_name>
# .\deploy-lambda.ps1 .\explore.py dump_event_context
# .\deploy-lambda.ps1 C:\src\github.com\ongzhixian\pft-aws\aws\explore.py dump_event_context
# Get-Help .\deploy-lambda.ps1
# Test deployed function
# aws lambda invoke --function-name dump_event_context .\response.json
# update-function-configuration