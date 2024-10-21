import os
import shutil
import paramiko
import json
import tarfile

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

    def upload_compressed(self, local_path, remote_tar):
        with tarfile.open(f"{local_path}.tar.gz", "w:gz") as tar:
            tar.add(local_path, arcname=os.path.basename(local_path))
        print(f"Compressed {local_path} to {local_path}.tar.gz")

        self.sftp_client.put(f"{local_path}.tar.gz", remote_tar)
        print(f"Uploaded compressed file: {local_path}.tar.gz to {remote_tar}")

        self._decompress_remote_tar(remote_tar)

        os.remove(f"{local_path}.tar.gz")

    def _decompress_remote_tar(self, remote_tar):
        command = f"tar -xzf {remote_tar} -C {self.destination_folder} && rm {remote_tar}"
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdout.channel.recv_exit_status()  
        print(f"Decompressed {remote_tar} on the remote server")

    def close(self):
        self.sftp_client.close()
        self.ssh_client.close()

def move_and_upload_folders(local_folder, uploader):
    directories = [d for d in os.listdir(local_folder) if os.path.isdir(os.path.join(local_folder, d))]
    
    for directory in directories:
        local_path = os.path.join(local_folder, directory)
        remote_tar = os.path.join(uploader.destination_folder, f"{directory}.tar.gz")
        
        uploader.upload_compressed(local_path, remote_tar)
        
        shutil.rmtree(local_path)
        print(f"Removed local directory: {local_path}")

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

    move_and_upload_folders(local_folder, uploader)

    uploader.close()
