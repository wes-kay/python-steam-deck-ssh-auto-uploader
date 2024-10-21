# Folder Watcher and SSH Uploader

This Python application monitors a specified folder for new files and uploads them via SSH to a Steam Deck (or any other SSH-enabled device) using SSH key-based authentication. This guide will walk you through enabling SSH on your Steam Deck, setting up SSH key-based authentication, and configuring the application.

## Prerequisites

- Steam Deck or any SSH-enabled device (tested with Steam Deck running Arch Linux)
- Python 3.x installed on your local machine
- SSH access to the target device

## 1. Enable SSH on Steam Deck

To enable SSH on your Steam Deck, follow these steps:

1. Open a terminal on the Steam Deck (Desktop Mode or via SSH).
2. Enable the SSH service by running:

    ```
    sudo systemctl enable sshd
    sudo systemctl start sshd
    ```

3. Check the status of the SSH service to ensure it's running:

    ```
    sudo systemctl status sshd
    ```

## 2. Set Up SSH Key-Based Authentication

To avoid entering a password for every file transfer, use SSH key-based authentication:

1. Generate an SSH key pair on your local machine if you don't have one:

    ```
    ssh-keygen -t rsa -b 4096
    ```

    This will generate a public/private key pair in `~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`.

2. Copy the public key to your Steam Deck:

    ```
    ssh-copy-id deck@steamdeck_ip_address
    ```

    Replace `deck` with your username (usually `deck` on a Steam Deck) and `steamdeck_ip_address` with the IP address of your Steam Deck.

3. Verify that SSH key-based login works by connecting to the Steam Deck:

    ```
    ssh deck@steamdeck_ip_address
    ```

## 3. Create and Configure a Python Virtual Environment

It is recommended to run this application in a virtual environment to manage dependencies:

1. Navigate to the directory where your project is located.
2. Create a virtual environment:

    ```
    python3 -m venv venv
    ```

3. Activate the virtual environment:

    - On Linux/macOS:
    
        ```
        source venv/bin/activate
        ```

    - On Windows:
    
        ```
        venv\Scripts\activate
        ```

4. Install the required Python packages:

    ```
    pip install -r requirements.txt
    ```

    Your `requirements.txt` should contain the following:

    ```
    paramiko
    watchdog
    ```

## 4. Configure the Application

1. There is a sample configuration file provided: `config_example.json`. Copy this file and rename it to `config.json`:

    ```
    cp config_example.json config.json
    ```

2. Open `config.json` and set the following values:

    ```json
    {
        "ssh_host": "steamdeck_ip",
        "ssh_port": 22,
        "ssh_user": "deck",
        "ssh_key_path": "/path/to/your/private/key",
        "destination_folder": "/path/on/steamdeck",
        "watch_folder": "/path/to/watch/folder"
    }
    ```

    - **ssh_host**: The IP address of your Steam Deck.
    - **ssh_port**: Usually `22` for SSH.
    - **ssh_user**: The username on the Steam Deck (typically `deck`).
    - **ssh_key_path**: The path to your private SSH key.
    - **destination_folder**: The folder on the Steam Deck where files will be uploaded.
    - **watch_folder**: The folder on your local machine that will be monitored for new files.

## 5. Run the Application

Once everything is configured, you can run the Python application to start monitoring the folder and upload new files:

