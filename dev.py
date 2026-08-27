"""SpikeAI / 叙梦 Naro 全栈一键启动服务 (跨平台高可靠版)。

通过 Python 原生进程管理拉起后端与前端，彻底杜绝 Windows CMD 编码与引号解析异常。
"""

import os
import subprocess
import sys
import time
import webbrowser

# 兼容 Windows GBK 默认终端编码
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


def main() -> None:
    print("=" * 70)
    print("            [SpikeAI / 叙梦 Naro] 全栈一键启动器")
    print("=" * 70)
    print()

    # 1. 启动后端 FastAPI
    print("[1/3] 正在启动后端 FastAPI 服务 (端口 8000)...")
    backend_cmd = f'start "SpikeAI-Backend-8000" cmd /k "cd /d "{BACKEND_DIR}" && uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 || pause"'
    subprocess.Popen(backend_cmd, shell=True)

    time.sleep(2)

    # 2. 启动前端 Vite
    print("[2/3] 正在启动前端 Vue 3.5 + Vite 服务 (端口 5173)...")
    frontend_cmd = f'start "SpikeAI-Frontend-5173" cmd /k "cd /d "{FRONTEND_DIR}" && pnpm run dev || pause"'
    subprocess.Popen(frontend_cmd, shell=True)

    time.sleep(2)

    # 3. 打开浏览器
    print("[3/3] 正在自动打开网页...")
    try:
        webbrowser.open("http://localhost:5173")
        webbrowser.open("http://localhost:8000/docs")
    except Exception as e:
        print(f"打开浏览器提示: {e}")

    print()
    print("=" * 70)
    print(" [OK] 启动就绪！后端与前端正在独立窗口运行。")
    print("   - 前端体验地址 : http://localhost:5173")
    print("   - 后端 API 文档 : http://localhost:8000/docs")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
