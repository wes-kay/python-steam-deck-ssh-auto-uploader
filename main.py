import os
import time
import paramiko
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def load_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

class SSHUploader:
    def __init__(self, ssh_host, ssh_port, ssh_user, ssh_key_path, destination_folder):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_key_path = ssh_key_path
        self.destination_folder = destination_folder

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(
            hostname=self.ssh_host,
            port=self.ssh_port,
            username=self.ssh_user,
            key_filename=self.ssh_key_path
        )
        self.sftp_client = self.ssh_client.open_sftp()

    def upload_file(self, local_file):
        filename = os.path.basename(local_file)
        remote_file = os.path.join(self.destination_folder, filename)
        self.sftp_client.put(local_file, remote_file)
        print(f"Uploaded {local_file} to {remote_file}")

    def close(self):
        self.sftp_client.close()
        self.ssh_client.close()

class FolderMonitorHandler(FileSystemEventHandler):
    def __init__(self, uploader):
        self.uploader = uploader

    def on_created(self, event):
        if not event.is_directory:
            self.uploader.upload_file(event.src_path)

def start_monitoring(local_folder, ssh_uploader):
    event_handler = FolderMonitorHandler(ssh_uploader)
    observer = Observer()
    observer.schedule(event_handler, local_folder, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    config = load_config()

    local_folder = config["watch_folder"]

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    uploader = SSHUploader(
        ssh_host=config["ssh_host"],
        ssh_port=config["ssh_port"],
        ssh_user=config["ssh_user"],
        ssh_key_path=config["ssh_key_path"],
        destination_folder=config["destination_folder"]
    )

    start_monitoring(local_folder, uploader)

    uploader.close()
