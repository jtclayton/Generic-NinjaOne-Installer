param (
    [string]$companyname,
    [string]$token
)

# Create a temporary directory in the AppData\Roaming\Temp folder
$tempDir = New-Item -ItemType Directory -Path ([System.IO.Path]::Combine($env:APPDATA, 'Temp', [System.IO.Path]::GetRandomFileName()))

# Define the installer path
$installerPath = [System.IO.Path]::Combine($tempDir.FullName, 'NinjaOneAgent-x86.msi')

# Download the installer
Write-Host "Downloading the latest NinjaOne Agent for: $companyname" -ForegroundColor Green
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri "https://fluent.rmmservice.eu/ws/api/v2/generic-installer/NinjaOneAgent-x86.msi" -OutFile $installerPath

# Execute the installer with the provided token
Write-Host "Latest NinjaOne Agent downloaded, running installer." -ForegroundColor Green
Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" TOKENID=`"$token`"" -Wait

# Check for the NinjaRMM Agent service
$maxTries = 10
$tries = 0
while ($tries -lt $maxTries) {
    $service = Get-Service -Name 'NinjaRMMAgent' -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq 'Running') {
        Write-Host "Installation is complete. The NinjaRMM Agent service is running." -ForegroundColor Green
        break
    } else {
        Write-Host "Waiting for the NinjaRMM Agent service to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        $tries++
    }
}

# Remove the installer
Remove-Item -Path $installerPath -Force
# Remove the temporary directory
Remove-Item -Path $tempDir.FullName -Force -Recurse
