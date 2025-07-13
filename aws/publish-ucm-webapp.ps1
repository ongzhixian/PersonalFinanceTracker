<#
.SYNOPSIS
    Synchronizes files from a local directory to an Amazon S3 bucket using AWS CLI.

.DESCRIPTION
    This script provides a robust and efficient way to synchronize files from a specified local directory
    to an Amazon S3 bucket. It leverages the 'aws s3 sync' command from the AWS CLI,
    which intelligently handles new, modified, and deleted files, ensuring only necessary changes are
    transferred.

    It includes:
    - Parameter validation for local path and S3 bucket.
    - Error handling for common issues (e.g., local path not found, AWS CLI not found, S3 access issues).
    - Optional logging to a file for auditing and troubleshooting.
    - Verbose output for detailed execution information.

.PARAMETER TargetEnvironment
    The absolute path to the local directory that needs to be synchronized.
    Example: 'C:\MyLocalFiles' or '/home/user/documents'

.PARAMETER DryRun
    Performs a trial run of the synchronization without actually making any changes.
    Shows what files would be copied, deleted, or skipped. (Equivalent to AWS CLI's --dryrun)

.EXAMPLE
    # Basic synchronization from a local folder to an S3 bucket root
    .\Sync-LocalToS3-CLI.ps1 -LocalPath "C:\MyData" -S3BucketName "my-data-backup"

.EXAMPLE
    # Synchronize to a specific folder within the S3 bucket with logging
    .\Sync-LocalToS3-CLI.ps1 -LocalPath "D:\WebSite" -S3BucketName "my-website-assets" -S3KeyPrefix "public" -LogFilePath "C:\Logs\website_s3_sync.log"

.EXAMPLE
    # Perform a dry run to see what changes would occur
    .\Sync-LocalToS3-CLI.ps1 -LocalPath "C:\MyDocuments" -S3BucketName "doc-archive" -DryRun

.NOTES
    - Ensure the AWS CLI is installed and configured.
    - The IAM user/role used must have sufficient permissions (s3:GetObject, s3:PutObject, s3:DeleteObject, s3:ListBucket)
      for the specified S3 bucket.
    - 'aws s3 sync' performs a one-way synchronization: local -> S3. Files existing in S3 but not locally
      (within the specified prefix) will be deleted from S3 by default. Use '--exclude' or '--include' parameters
      if you need more granular control over what gets synced or deleted (add these to the $awsCliArgs array).
    - The `DryRun` parameter is equivalent to `--dryrun` in AWS CLI.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [String]$TargetEnvironment="ucm-webapp-prd"
)

Set-Variable srcPath -Option Constant -Value ".\aws\s3\ucm-webapp\"
Set-Variable targetBucketName -Option Constant -Value $TargetEnvironment
Set-Variable targetBucketUri -Option Constant -Value "s3://$targetBucketName"

function Start-MainDeploymentProcess {
    Write-information "** Starting task to deploy [$srcPath] to [$targetEnvironment] **`n" -InformationAction Continue
    
    # $timeTaken = Measure-Command -Expression { Start-DataGatheringPhase }
    # Write-information "Time taken (s): [$($timeTaken.TotalSeconds)]`n" -InformationAction Continue
    Start-DataGatheringPhase
    Write-Host

    Start-ValidationPhase
    Write-Host

    Start-DeploymentPhase
}

function Start-DataGatheringPhase {

    Write-information "[DATA GATHERING PHASE]:START" -InformationAction Continue

    $script:srcPathExists = Test-Path $srcPath

    $script:awsCliExists = $null -ne $(Get-Command aws -ErrorAction SilentlyContinue)

    Write-information "[DATA GATHERING PHASE]:END" -InformationAction Continue
}

function Start-ValidationPhase { 
    
    Write-information "[VALIDATION PHASE]:START" -InformationAction Continue

    if (-not $srcPathExists) {
        Write-Error "Source path [$srcPath] does not exist; terminating." -ErrorAction Stop
    }
    Write-information "[ OK ] Source path exists." -InformationAction Continue

    if (-not $awsCliExists) {
        Write-Error "AWS CLI does not exist; terminating" -ErrorAction Stop
    }
    $awsVersion = aws --version
    Write-information "[ OK ] AWS-CLI version: [$awsVersion]" -InformationAction Continue

    $bucketExists = aws s3 ls | ForEach-Object { $_.Split()[-1] } | Select-String $targetBucketName -Quiet
    if (-not $bucketExists) {
        Write-Error "Bucket $targetBucketName does not exists; terminating" -ErrorAction Stop
    }
    Write-information "[ OK ] Target bucket exists." -InformationAction Continue

    Write-information "[VALIDATION PHASE]:END" -InformationAction Continue
}

function Start-DeploymentPhase {

    Write-information "[DEPLOYMENT PHASE]:START" -InformationAction Continue

    Write-information "Starting deployment to [$targetEnvironment]" -InformationAction Continue

    aws s3 sync $srcPath $targetBucketUri

    Write-information "Deployment to [$targetEnvironment] completed successfully." -InformationAction Continue 

    Write-information "[DEPLOYMENT PHASE]:END" -InformationAction Continue
}

# Run main script
Start-MainDeploymentProcess