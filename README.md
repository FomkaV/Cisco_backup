# Cisco Backup Script

This project contains a Python script to automatically back up Cisco router configurations over SSH.

It uses the [`paramiko`](https://www.paramiko.org/) library to connect, run commands, and save the resulting configuration files locally.

---

## Features

- Connects to Cisco devices via SSH
- Enters enable (privileged) mode
- Executes `show running-config` command
- Saves backups in a specified directory with timestamped filenames
- Deletes old backups older than a specified number of days
- Fully configurable via command-line arguments

---

## Requirements

- Python 3.x
- `paramiko` library

Install dependencies:

```bash
pip install paramiko
```

## Usage Example
```bash
python3 cisco_backup_run.py \
  --ip 192.168.10.5 \
  --user admin \
  --password "MySshPassword123" \
  --enable "EnableSecret!" \
  --port 22 \
  --backup_dir "/opt/cisco_backup/backups" \
  --days 45 \
  --name "core-sw1"
```

## Parameters

- --ip : Cisco device IP address
- --user : SSH username
- --password : SSH login password
- --enable : Enable (privileged) password
- --port : SSH port (default: 22)
- --backup_dir : Local directory to store backups
- --days : Days to keep backups (default: 30)
- --name : Device name (used for filename prefix)

The backup filename format is: <device_name>_<DDMMYY>.conf