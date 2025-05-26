$diff_file_name = "diff-to-notes-filelist.txt"
$out_file_path = Join-Path $PSScriptRoot $diff_file_name
$encoding = New-Object System.Text.UTF8Encoding $False
$repo_root_path = git rev-parse --show-toplevel

Write-Host Repo root path is $repo_root_path

$content = git diff --name-only | ForEach-Object { Join-Path $repo_root_path $_ }
[System.IO.File]::WriteAllLines($out_file_path, $content, $encoding)

$content = git ls-files --others --exclude-standard --full-name | Where-Object {$_ -notlike "*$diff_file_name*"} | ForEach-Object { Join-Path $repo_root_path $_ }
if ($null -ne $content) {
    [System.IO.File]::AppendAllLines($out_file_path, [string[]]$content, $encoding)
}

# python.exe .\shared_note.py
