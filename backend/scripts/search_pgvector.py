"""在远程 postgres 容器中搜索 pgvector 包名。"""

import paramiko

HOST = "140.143.87.234"
USER = "root"
PASSWORD = r"N3.Xw,6?)nY`4"


def main() -> None:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOST, port=22, username=USER, password=PASSWORD, timeout=30)

    cmd = (
        "docker exec -u 0 postgres apt-cache search pgvector && "
        "docker exec -u 0 postgres apt-cache search postgresql | grep -i vector"
    )

    stdin, stdout, stderr = client.exec_command(cmd)
    print("STDOUT:\n", stdout.read().decode("utf-8", errors="ignore"))
    print("STDERR:\n", stderr.read().decode("utf-8", errors="ignore"))
    client.close()


if __name__ == "__main__":
    main()
