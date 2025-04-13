


########################################
# UTILITARIAN FUNCTIONS

Set-Variable temp_layer_folder_path -Option Constant -Value './temp-layer'

function Resolve-TempLayerFolder {
    param (
        [Parameter(Mandatory=$true)]
        [string] $temp_layer_folder_path
    )

    if (-not (Test-Path $temp_layer_folder_path))
    {
        Write-Debug "Create missing temp layer folder."
        New-Item -ItemType Directory -Path $temp_layer_folder_path
    }
}

########################################
# MAIN SCRIPT

Resolve-TempLayerFolder $temp_layer_folder_path
# $publish_filename = "$($FunctionName).zip"
# $publish_file_path = Join-Path $publish_folder_path $publish_filename

# .\deploy-layers.ps1
# pip install requests --target python
# pip.exe install -r .\layer_http_requirements.txt --target 
# pip.exe install -r .\layer_http_requirements.txt --target .\temp-layer\layer_http\python

#Compress-Archive $PythonScriptPath -DestinationPath $publish_file_path -Force
#Compress-Archive .\temp-layer\layer_http\python\ -DestinationPath .\publish\layer_http.zip -Force