"""在远程 PostgreSQL 上检查/创建 spikeai_db 数据库与扩展。"""

import paramiko

HOST = "140.143.87.234"
USER = "root"
PASSWORD = r"N3.Xw,6?)nY`4"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, port=22, username=USER, password=PASSWORD, timeout=10)

    commands = [
        # 1. 检查是否存在 spikeai_db，没有则创建
        "docker exec postgres psql -U postgres -tc \"SELECT 1 FROM pg_database WHERE datname = 'spikeai_db'\" | grep -q 1 || docker exec postgres psql -U postgres -c 'CREATE DATABASE spikeai_db;'",
        # 2. 列出 databases
        "docker exec postgres psql -U postgres -c '\\l'",
        # 3. 检查 spikeai_db 扩展可用性
        "docker exec postgres psql -U postgres -d spikeai_db -c \"SELECT name, default_version FROM pg_available_extensions WHERE name IN ('vector', 'uuid-ossp');\"",
        # 4. 启用 uuid-ossp 扩展
        "docker exec postgres psql -U postgres -d spikeai_db -c 'CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";'",
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
