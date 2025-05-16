# Define the GitHub username and repository name
$username = "USERNAMEHERE"
$repoName = "REPOHERE"

# Define the .exe installer file
$filePath = "INSTALLERHERE.exe"

# Define your personal access token
$token = "TOKENHERE"

# Construct the URL of the file to download from the private Git repository
$repoUrl = "https://raw.githubusercontent.com/$username/$repoName/main/$filePath"

# Get the path to the user's AppData Temp folder
$tempFolder = [System.IO.Path]::GetTempPath()

# Define the path where the file will be saved
$outputPath = Join-Path -Path $tempFolder -ChildPath "$filePath"

# Output message to indicate the start of the download process
Write-Host "Starting the download from $repoUrl..."

# Download the file from the private Git repository
try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $repoUrl -Headers @{Authorization = "token $token"} -OutFile $outputPath
    Write-Host "Download complete. File saved to $outputPath."
} catch {
    Write-Host "Error downloading the file: $($_.Exception.Message)"
    exit 1
}

# Check if the file exists and is a valid executable
if (Test-Path $outputPath) {
    try {
        # Output message to indicate the start of the execution process
        Write-Host "Executing the downloaded file..."

        # Execute the downloaded file and wait for it to exit
        $process = Start-Process -FilePath $outputPath -PassThru
        $process.WaitForExit()

        # Output message to indicate the executable has finished running
        Write-Host "Execution complete. Process exited with code $($process.ExitCode)."

        # Delete the file after the process has exited
        Remove-Item -Path $outputPath -Force

        # Output message to indicate the file has been deleted
        Write-Host "Downloaded file has been deleted from $outputPath."
    } catch {
        Write-Host "Error executing the file: $($_.Exception.Message)"
    }
} else {
    Write-Host "Error: The downloaded file does not exist or is not a valid executable."
}
