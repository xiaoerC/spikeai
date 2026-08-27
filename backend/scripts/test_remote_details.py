"""详细探测远程 Redis 密码与 PostgreSQL 数据库及扩展。"""

import paramiko

HOST = "140.143.87.234"
USER = "root"
PASSWORD = r"N3.Xw,6?)nY`4"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, port=22, username=USER, password=PASSWORD, timeout=10)

    commands = [
        # 查看 redis 启动命令及密码配置
        "docker inspect coze-redis --format '{{.Path}} {{range .Args}}{{.}} {{end}}'",
        "docker exec coze-redis redis-cli ping",
        "docker exec coze-redis redis-cli CONFIG GET requirepass",
        # 检查 postgres databases
        "docker exec postgres psql -U postgres -d aichat -c '\\l'",
        # 检查 postgres 扩展是否支持 vector 和 uuid-ossp
        "docker exec postgres psql -U postgres -d aichat -c 'SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name IN (\"vector\", \"uuid-ossp\");'",
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
