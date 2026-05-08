#!/usr/bin/env python3
"""
简单的 HTTP 隧道工具，使用 tunnelto.dev
免费、无需注册、自动生成公网URL
"""

import subprocess
import json
import time
import signal
import sys
import os

def install_tunnelto():
    """安装 tunnelto-go CLI"""
    print("正在安装 tunnelto-go...")
    try:
        # tunnelto-go 是 Go 编写的，这里我们直接下载二进制
        arch = "darwin-arm64"
        url = f"https://github.com/agrinman/tunnelto/releases/latest/download/tunnelto-{arch}"
        target = os.path.expanduser("~/Downloads/cloud_coupon_manager/tunnel/tunnelto")

        subprocess.run([
            "curl", "-L", url, "-o", target
        ], check=True)

        subprocess.run(["chmod", "+x", target], check=True)
        print(f"✅ tunnelto 安装成功: {target}")
        return target
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return None

def start_tunnel(tunnelto_path, port):
    """启动隧道"""
    print(f"正在启动隧道，转发本地 {port} 端口...")

    # tunnelto 不需要注册，但首次运行会生成一个随机URL
    cmd = [tunnelto_path, "--port", str(port)]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # 等待输出，解析公网URL
        time.sleep(2)

        for _ in range(30):  # 最多等待30秒
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                time.sleep(0.5)
                continue

            print(line.strip())

            if "https://" in line and ".tunnelto.dev" in line:
                # 提取URL
                url = line.strip()
                print(f"\n{'='*60}")
                print(f"✅ 公网访问地址:")
                print(f"   {url}")
                print(f"{'='*60}\n")
                print("按 Ctrl+C 停止隧道")

        # 保持运行
        process.wait()
    except KeyboardInterrupt:
        print("\n正在停止隧道...")
        process.terminate()
        process.wait()
        print("隧道已停止")
    except Exception as e:
        print(f"❌ 隧道启动失败: {e}")
        if process:
            process.terminate()

if __name__ == "__main__":
    port = 5001

    tunnelto_path = os.path.expanduser("~/Downloads/cloud_coupon_manager/tunnel/tunnelto")

    # 检查是否已安装
    if not os.path.exists(tunnelto_path):
        tunnelto_path = install_tunnelto()
        if not tunnelto_path:
            sys.exit(1)

    start_tunnel(tunnelto_path, port)
