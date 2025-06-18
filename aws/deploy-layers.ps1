


########################################
# UTILITARIAN FUNCTIONS

Set-Variable temp_layer_folder_path -Option Constant -Value './temp-layer'
Set-Variable publish_folder_path -Option Constant -Value './publish'

function Resolve-Folder {
    param (
        [Parameter(Mandatory=$true)]
        [string] $folder_path
    )

    if (-not (Test-Path $folder_path))
    {
        Write-Debug "Create missing folder $folder_path"
        New-Item -ItemType Directory -Path $folder_path
    }
}



function Publish-LambdaLayer {
    param (
        [Parameter(Mandatory=$true)]
        [string] $LayerName,
        [Parameter(Mandatory=$true)]
        [string] $ZipFilePath
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

    # return aws lambda create-function `
    # --function-name $FunctionName `
    # --runtime python3.10 `
    # --zip-file fileb://$ZipFilePath `
    # --handler $HandlerName `
    # --role arn:aws:iam::009167579319:role/ProjectAppRole

    return aws lambda publish-layer-version `
    --layer-name $LayerName `
    --zip-file fileb://$ZipFilePath `
    --description "Layer for sending HTTP requests" `
    --compatible-runtimes python3.10 `
    --compatible-architectures x86_64 `
    --license-info AGPL-3.0-or-later
}


########################################
# MAIN SCRIPT

$layer_name = "http_layer"
$layer_name = "google_api_layer"
$layer_name = "graphql_layer"
$pip_output_path = Join-Path $temp_layer_folder_path "$layer_name/python"
Resolve-Folder $pip_output_path

$publish_filename = "$($layer_name).zip"
$publish_file_path = Join-Path $publish_folder_path $publish_filename

# LAYERS

#pip.exe install -r .\$($layer_name)_requirements.txt --target $pip_output_path --platform manylinux2014_x86_64 --python-version 3.10 --only-binary=:all:
pip.exe install -r .\$($layer_name)_requirements.txt --target $pip_output_path
Compress-Archive $pip_output_path -DestinationPath $publish_file_path -Force

Write-Host "Deploying..."
Publish-LambdaLayer $layer_name $publish_file_path