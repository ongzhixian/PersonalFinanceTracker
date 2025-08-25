
function main {
    # Get list of Athena Accounts from 
    
    $json = ConvertFrom-Json "$(Get-Content 'N:\Downloads\response_1755058902397.json')"
    $streetAccountList = $json.streetAccount
    $streetAccountList.length

    $accountTable = [System.Data.DataTable]::new();
    $accountTable.Columns.Add("AthenaAccount", [System.String]);

   foreach ($account in $streetAccountList) {
       $row = $accountTable.NewRow();
       $row["AthenaAccount"] = $account;
       $accountTable.Rows.Add($row);
   }

   Write-Host "Rows count: " $accountTable.Rows.Count

   $connection = [System.Data.SqlClient.SqlConnection]::new("Data Source=BROKERSQLUAT;Initial Catalog=Financing;trustServerCertificate=true;Trusted_Connection=True")
   $sqlBulkCopy = [System.Data.SqlClient.SqlBulkCopy]::new($connection)
   $sqlBulkCopy.DestinationTableName = "Financing..tmp_athena_account"

   $connection.Open()
   $sqlBulkCopy.WriteToServer($accountTable)
   $connection.Close()
}

function ConnectTo-BrokerSql {
    param (
    )
    
    try {
        $connection = [System.Data.SqlClient.SqlConnection]::new("Data Source=BROKERSQLUAT;Initial Catalog=Financing;trustServerCertificate=true;Trusted_Connection=True")
        $connection.Open()

        Write-Host "Succcess"
        $connection.Close()
    }
    catch {
        Write-Error $?
    }
}

try {
    & main
}
catch {
    # Print exception
    Write-Error $_
}
