"""远程服务器 Docker 环境探测脚本。

通过 SSH 远程连接 140.143.87.234 查看正在运行的 Docker 容器、配置与环境变量。
"""

import paramiko

HOST = "140.143.87.234"
USER = "root"
PASSWORD = r"N3.Xw,6?)nY`4"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"Connecting to {HOST} as {USER}...")
    client.connect(hostname=HOST, port=22, username=USER, password=PASSWORD, timeout=10)

    commands = [
        "docker ps -a",
        "docker inspect $(docker ps -q) --format '{{.Name}}: Image={{.Config.Image}} Env={{.Config.Env}} Ports={{.NetworkSettings.Ports}}' 2>/dev/null || true",
    ]

    for cmd in commands:
        print(f"\n=== Executing: {cmd} ===")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        if out:
            print(out)
        if err:
            print("[STDERR]", err)

    client.close()


if __name__ == "__main__":
    main()
