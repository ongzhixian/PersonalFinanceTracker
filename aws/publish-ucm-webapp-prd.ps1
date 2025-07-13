param(
    [Parameter(Mandatory=$false)]
    [String]$targetEnvironment="ucm-webapp-prd"
)

Write-Host Publish C:\src\github.com\ongzhixian\pft-aws\aws\s3
aws s3 ls
Write-Host Deploying $targetEnvironment
Write-Host Deployment complete.