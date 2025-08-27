#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import time
import datetime
import os
import argparse
import socket


def parse_args():
    parser = argparse.ArgumentParser(description="Cisco backup script")
    parser.add_argument("--ip", required=True, help="Cisco device IP address")
    parser.add_argument("--user", required=True, help="SSH username")
    parser.add_argument("--password", required=True, help="SSH login password")
    parser.add_argument("--enable", required=True, help="Enable (privileged) password")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--backup_dir", required=True, help="Local directory to store backups")
    parser.add_argument("--days", type=int, default=30, help="Days to keep backups (default: 30)")
    parser.add_argument("--name", required=True, help="Device name (used for filename prefix)")

    args = parser.parse_args()
    return args


def connect(IP, User, Password, Password_en, PORT=22):
    """
    Connect to Cisco device via SSH, enter enable mode, and grab running config.
    """
    router_output = ""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(IP, port=PORT, username=User, password=Password, look_for_keys=False)
        print(f"[+] Connected successfully to {IP}")

        connection = ssh.invoke_shell()
        connection.send("enable\n")
        time.sleep(0.5)
        connection.send(Password_en + "\n")
        time.sleep(0.5)
        connection.recv(99999)

        connection.send("term len 0\n")
        time.sleep(0.5)
        connection.recv(99999)

        connection.send("show running-config\n")
        time.sleep(2)
        router_output = connection.recv(999999).decode(errors="ignore")

        connection.send("end\n")

    except paramiko.AuthenticationException:
        print(f"[-] Authentication failed for {IP}")
    except socket.error:
        print(f"[-] Socket error while connecting to {IP}")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
    finally:
        ssh.close()

    return router_output


def convert(conf_bak):
    """ Convert Cisco running config string for readability. """
    return conf_bak.replace("\r\n", "\n")


def write_conf(conf_bak, dev_name, Date, bak_dir):
    """ Save configuration to file. """
    os.makedirs(bak_dir, exist_ok=True)
    bak_file = os.path.join(bak_dir, f"{dev_name}_{Date}.conf")
    with open(bak_file, "w") as f:
        f.write(conf_bak)
    print(f"[✓] Saved backup: {bak_file}")


def del_old(bak_dir, day_to_del, dev_name):
    """ Delete backups older than given number of days. """
    cmd = f'find {bak_dir} -name "{dev_name}_*" -mtime +{day_to_del} -exec rm -f {{}} \;'
    os.system(cmd)
    print(f"[✓] Deleted old backups for {dev_name} older than {day_to_del} days.")


def main():
    args = parse_args()
    now = datetime.datetime.now()
    Date = now.strftime("%d%m%y")

    print(f"[+] Starting backup for {args.name} ({args.ip})...")

    conf_bak = connect(args.ip, args.user, args.password, args.enable, args.port)
    if conf_bak:
        conf_bak = convert(conf_bak)
        write_conf(conf_bak, args.name, Date, args.backup_dir)
        del_old(args.backup_dir, args.days, args.name)
        print(f"[✓] Backup job for {args.name} succeeded.")
    else:
        print(f"[!] Backup job for {args.name} failed.")


if __name__ == "__main__":
    main()

