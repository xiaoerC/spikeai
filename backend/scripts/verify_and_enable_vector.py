"""验证并在 spikeai_db 中启用 vector 扩展。"""

import paramiko

HOST = "140.143.87.234"
USER = "root"
PASSWORD = r"N3.Xw,6?)nY`4"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, port=22, username=USER, password=PASSWORD, timeout=30)

    # 先安装再创建扩展
    cmd = (
        "docker exec -u 0 postgres apt-get install -y postgresql-16-pgvector && "
        "docker exec postgres psql -U postgres -d spikeai_db -c 'CREATE EXTENSION IF NOT EXISTS vector;' && "
        "docker exec postgres psql -U postgres -d spikeai_db -c '\\dx'"
    )

    print(f"Executing: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    print("STDOUT:\n", stdout.read().decode("utf-8", errors="ignore"))
    print("STDERR:\n", stderr.read().decode("utf-8", errors="ignore"))
    client.close()


if __name__ == "__main__":
    main()
