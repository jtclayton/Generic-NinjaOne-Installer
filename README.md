# Generic NinjaOne Installer
## Introduction
This repository contains configuration .csv fies and some PowerShell and Python scripts.

It is designed to create your own brandable NinjaOne installer that can be used to install to any company with just one .exe file, featuring a sign in screen where attempts are logged and a menu of Companies/Locations to install the correct NinjaOne Agent.

This is designed to be kept in a private repository and accessed using a git personal access token.

## Configuration
### CSV Files Configuration
Before using this project, ensure the following .csv files are correctly configured:
- config.csv – Contains essential Company, Location and Token parameters. Modify these fields - you can export a .csv of this information from NinjaOne. To do this ensure Automatic token creation and Installer Management are set to Enabled in your NinjaOne account settings. The Agent Installers tab will then be available in the Dashboard under the Devices dropdown.
- credentials.csv – Stores login credentials for the installer application. Ensure correct formatting and encoding to prevent errors.
- activitylog.csv – This requires no configuration, login attempts for the installer are written to here.
Refer to the .csv files for expected formats and examples.

### Python Installation
A Python interpreter is required to run the NinjaOneInstallerBuilder.pyw script, I've used the standard Python package.
There are three prerequesite modules required to package the installer, Pillow is used within the created executable so is passed through when built.
- You will need to install pyinstaller from a terminal - `pip install pyinstaller`.
- You will need to install Pillow from a terminal - `pip install Pillow`.
- You will need to install requests from a terminal - `pip install requests`.

### Ninja Agent Installation Script
The script ninjainstallation.ps1 needs to be added to the repo, but no configuration in the script is required.

### Creating the personal access token
You'll need to create a fine-grained private access token in git for the private repo you create with the Read/Write permissions for Contents (the write is required for logging sign in attempts back to git).

## Building the custom installer
Run the 'NinjaOneInstallerBuilder.pyw' script on a device with Python and the other modules installed.
You'll have five options, the first four are mandatory.
- Git username
- Git private repo name
- Git personal access token
- Logo URL - this will appear in each section of the installer and resizes an image to a maximum of 1000 x 300 with same image ratios kept.
- Icon URL - if you want the .exe file to have a custom icon, you can specify the url here.

  The builder takes a couple of minutes to create the package and will create a folder with the .exe file in the same directory you run the builder script.

## End Result
The generated installer will be named ninjaoneinstaller.exe, it will present a login screen with your logo, one successful sign in, company and drop down location fields will appear with information added to the config.csv.
Once the company and location is selected and the install initialised, the ninjainstallation .ps1 script will be called and the token of the company/location that was selected passed through so it's installed to the correct location.


# Automating device provisioning further
IF you wish to automate device provisioning further and use a USB provisioning method like OSCloud, or something with an unattend.xml file. Upload the created installer .exe to your private git repo, and set the script 'NinjaOne Generic Installer - USB Provisioning Deployment' in the unattend.xml to run on first user sign in. This should download and execute the installer when first signed in and enable a technican to select the correct company.
