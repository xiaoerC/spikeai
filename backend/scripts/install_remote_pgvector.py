"""在远程 postgres 容器中安装 pgvector 扩展。"""

import paramiko

HOST = "140.143.87.234"
USER = "root"
PASSWORD = r"N3.Xw,6?)nY`4"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, port=22, username=USER, password=PASSWORD, timeout=10)

    commands = [
        "docker exec -u 0 postgres apt-get update -y && docker exec -u 0 postgres apt-get install -y postgresql-16-pgvector",
        "docker exec postgres psql -U postgres -d spikeai_db -c 'CREATE EXTENSION IF NOT EXISTS vector;'",
        "docker exec postgres psql -U postgres -d spikeai_db -c '\\dx'",
    ]

    for cmd in commands:
        print(f"\n=== {cmd} ===")
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
