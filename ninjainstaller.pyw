import tkinter as tk
from tkinter import messagebox, ttk
import csv
import subprocess
import os
import requests
import tempfile
import shutil
import base64
from datetime import datetime

# GitHub repository details
repo_owner = "{repo_owner}"
repo_name = "{repo_name}"
git_token = "{git_token}"
logo_url = "{logo_url}"

# Function to download a file from GitHub
def download_file_from_github(file_path, local_path):
    url = f"https://api.github.com/repos/{{repo_owner}}/{{repo_name}}/contents/{{file_path}}"
    headers = {{"Authorization": f"token {{git_token}}"}}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_content = response.json()["content"]
        with open(local_path, "wb") as file:
            file.write(base64.b64decode(file_content))
    else:
        raise Exception(f"Failed to download {{file_path}} from GitHub")

# Function to download a file from a URL
def download_file_from_url(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, "wb") as file:
            file.write(response.content)
    else:
        raise Exception(f"Failed to download {{url}}. Status code: {{response.status_code}}")

# Function to log activity to GitHub
def log_activity_to_github(username, status):
    log_file_path = 'activitylog.csv'
    timestamp = datetime.utcnow().isoformat() + "Z"
    ip_address = requests.get('https://api.ipify.org').text  # Get public IP address
    user_agent = "NinjaOne Installer"  # Example user agent, replace with actual if available

    log_entry = [timestamp, username, status, ip_address, user_agent]

    # Get the current file details from GitHub
    url = f"https://api.github.com/repos/{{repo_owner}}/{{repo_name}}/contents/{{log_file_path}}"
    headers = {{
        "Authorization": f"token {{git_token}}",
        "Accept": "application/vnd.github.v3+json"
    }}
    response = requests.get(url, headers=headers)
    response_json = response.json()

    # Read the existing log file content from GitHub
    if response.status_code == 200:
        existing_content = requests.get(response_json['download_url']).text.splitlines()
        existing_content.append(','.join(log_entry))
        updated_content = '\\n'.join(existing_content)
    else:
        # If the file does not exist, create it with a header row and the first log entry
        updated_content = "Timestamp,Username,Status,IP Address,User Agent\\n" + ','.join(log_entry)

    # Encode the updated content to base64
    encoded_content = base64.b64encode(updated_content.encode()).decode()

    # Prepare the data for the PUT request to update the file on GitHub
    data = {{
        "message": "Logging sign-in attempt",
        "content": encoded_content,
        "sha": response_json.get("sha"),
        "branch": "main"
    }}

    # Update the file on GitHub
    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Log entry added successfully.")
    else:
        print(f"Failed to add log entry. Status code: {{response.status_code}}")

# Create a temporary directory to store downloaded files
temp_dir = tempfile.mkdtemp()
from PIL import Image
try:
    # Function to resize the image to fit within the specified maximum width and height while maintaining its aspect ratio
    def resize_image_to_max_size(input_path, output_path, max_width, max_height):
        with Image.open(input_path) as img:
            aspect_ratio = img.width / img.height
            if aspect_ratio > (max_width / max_height):
                new_width = min(img.width, max_width)
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min(img.height, max_height)
                new_width = int(new_height * aspect_ratio)
            resized_img = img.resize((new_width, new_height))
            resized_img.save(output_path)

    # Download necessary files
    download_file_from_github("credentials.csv", os.path.join(temp_dir, "credentials.csv"))
    download_file_from_github("config.csv", os.path.join(temp_dir, "config.csv"))
    download_file_from_github("ninjainstallation.ps1", os.path.join(temp_dir, "ninjainstallation.ps1"))
    logo_path = os.path.join(temp_dir, "logo.png")
    download_file_from_url(logo_url, logo_path)
    resize_image_to_max_size(logo_path, logo_path, 1000, 300)


    # Read credentials
    credentials = {{}}
    with open(os.path.join(temp_dir, 'credentials.csv'), mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'Username' in row and 'Password' in row:
                credentials[row['Username']] = row['Password']

    # Read config
    config = []
    with open(os.path.join(temp_dir, 'config.csv'), mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            config.append(row)

    # Run PowerShell script and check for NinjaRMM Agent running
    def run_powershell_script(company, token):
        script_path = os.path.join(temp_dir, 'ninjainstallation.ps1')
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path, company, token], capture_output=True, text=True)
        return result.stdout

    # Main window
    def open_main_window(config):
        def on_company_selected(event):
            company = company_combobox.get()
            locations = [row['Location'] for row in config if row['Company'] == company]
            location_combobox['values'] = locations

        def on_location_selected(event):
            pass  # No action needed here
        def on_submit():
            company = company_combobox.get()
            location = location_combobox.get()
            token = next(row['Token'] for row in config if row['Company'] == company and row['Location'] == location)
            output = run_powershell_script(company, token)

            # Display output in the main window with confirmation and exit button
            for widget in center_frame_main.winfo_children():
                widget.destroy()

            tk.Label(center_frame_main, text="Installation Output", font=("Helvetica", 14), bg="white").pack(pady=10)
            output_text = tk.Text(center_frame_main, wrap=tk.WORD)
            output_text.insert(tk.END, output)
            output_text.pack(expand=True, fill=tk.BOTH)

            def on_exit():
                login_window.destroy()

            exit_button = tk.Button(center_frame_main, text="Exit", command=on_exit, bg="#026CB5", fg="white", font=("Helvetica", 14), activebackground="#028BBB", activeforeground="white", height=2, width=20)
            exit_button.pack(pady=10)

        # Clear the login window content and update it for the main window content
        for widget in login_window.winfo_children():
            widget.destroy()

        login_window.title("NinjaOne Generic Installer")

        # Create a frame to center all elements
        center_frame_main = tk.Frame(login_window, bg="white")
        center_frame_main.pack(expand=True)

        # Add banner image/logo to the main window
        logo_image_main = tk.PhotoImage(file=os.path.join(temp_dir, 'logo.png'))
        logo_label_main = tk.Label(center_frame_main, image=logo_image_main, bg="white")
        logo_label_main.image = logo_image_main  # Keep a reference to avoid garbage collection
        logo_label_main.pack(pady=20)

        tk.Label(center_frame_main, text='Please choose the correct company, location and select "Install Now" to start the Ninja One installation process.', font=("Helvetica", 14), bg="white").pack(pady=10)

        tk.Label(center_frame_main, text="Please ensure you accept the UAC prompt to start the installation.", font=("Helvetica", 14), bg="white").pack(pady=5)

        tk.Label(center_frame_main, text="Company", font=("Helvetica", 14), bg="white").pack(pady=5)

        company_combobox_style = ttk.Style()
        company_combobox_style.configure('TCombobox', font=('Helvetica', 14), padding=10)

        companies = sorted(list(set([row['Company'] for row in config])))

        company_combobox = ttk.Combobox(center_frame_main, values=companies, width=50, style='TCombobox')
        company_combobox.pack(pady=5)
        company_combobox.bind("<<ComboboxSelected>>", on_company_selected)

        def filter_companies(event):
            typed_text = company_combobox.get().lower()
            filtered_companies = [company for company in companies if typed_text in company.lower()]
            company_combobox['values'] = filtered_companies

        company_combobox.bind("<KeyRelease>", filter_companies)

        tk.Label(center_frame_main, text="Location", font=("Helvetica", 14), bg="white").pack(pady=5)

        location_combobox_style = ttk.Style()
        location_combobox_style.configure('TCombobox', font=('Helvetica', 14), padding=10)

        location_combobox = ttk.Combobox(center_frame_main, width=50, style='TCombobox')
        location_combobox.pack(pady=5)
        location_combobox.bind("<<ComboboxSelected>>", on_location_selected)

        submit_button = tk.Button(center_frame_main, text="Install Now", command=on_submit, bg="#026CB5", fg="white", font=("Helvetica", 14), activebackground="#028BBB", activeforeground="white", height=2, width=20)

        def submit_on_enter(event):
            submit_button.invoke()

        login_window.bind('<Return>', submit_on_enter)
        submit_button.pack(pady=20)

    # Login window
    def login():
        username = username_entry.get()
        password = password_entry.get()

        if username in credentials and credentials[username] == password:
            log_activity_to_github(username, "successful")
            open_main_window(config)
        else:
            log_activity_to_github(username, "unsuccessful")
            messagebox.showerror("Login Failed", "Invalid username or password")

    login_window = tk.Tk()
    login_window.title("NinjaOne Generic Installer")
    login_window.geometry("1600x900")
    login_window.minsize(1600, 900)
    login_window.maxsize(1600, 900)
    login_window.resizable(False, False)
    login_window.configure(bg="white")

    # Create a frame to center all elements
    center_frame_login = tk.Frame(login_window, bg="white")
    center_frame_login.pack(expand=True)

    # Add banner image/logo to the login window
    logo_path_login = os.path.join(temp_dir, 'logo.png')
    logo_image_login = tk.PhotoImage(file=logo_path_login)
    logo_label_login = tk.Label(center_frame_login, image=logo_image_login, bg="white")
    logo_label_login.image = logo_image_login  # Keep a reference to avoid garbage collection
    logo_label_login.pack(pady=20)

    tk.Label(center_frame_login, text="NinjaOne Generic Installer", font=("Helvetica", 24), bg="white").pack(pady=10)
    tk.Label(center_frame_login, text="This service is only to be used by technicians, all activity is logged", font=("Helvetica", 14), bg="white").pack(pady=10)

    tk.Label(center_frame_login, text="Username", font=("Helvetica", 14), bg="white").pack(pady=5)
    username_entry = tk.Entry(center_frame_login, font=("Helvetica", 14))
    username_entry.pack(pady=5)

    tk.Label(center_frame_login, text="Password", font=("Helvetica", 14), bg="white").pack(pady=5)
    password_entry = tk.Entry(center_frame_login, show="*", font=("Helvetica", 14))
    password_entry.pack(pady=5)

    login_button = tk.Button(center_frame_login, text="Login", command=login, bg="#026CB5", fg="white", font=("Helvetica", 14), activebackground="#028BBB", activeforeground="white", height=2, width=20)

    def login_on_enter(event):
        login_button.invoke()

    login_window.bind('<Return>', login_on_enter)
    login_button.pack(pady=20)

    login_window.mainloop()

finally:
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
'''
