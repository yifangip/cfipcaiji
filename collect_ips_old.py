import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

# ============ 配置区域 ============
# Telegram 推送配置（从 GitHub Secrets 环境变量中读取）
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 目标URL列表
urls = [
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://ip.164746.xyz'
]

# 匹配 IPv4 地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
# 输出文件
output_file = 'ip.txt'
# =================================


def send_tg_message(text):
    """推送消息到 Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 未设置 BOT_TOKEN 或 CHAT_ID，跳过TG推送。")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, data=data, timeout=15)
        if response.status_code == 200:
            print("✅ Telegram 推送成功。")
        else:
            print(f"❌ Telegram 推送失败: {response.text}")
    except Exception as e:
        print(f"❌ Telegram 推送异常: {e}")


def fetch_ips():
    """抓取网页中的 IP 地址"""
    all_ips = set()
    for url in urls:
        print(f"正在抓取: {url}")
        try:
            response = requests.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            elements = soup.find_all(['li', 'tr'])
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)
                for ip in ip_matches:
                    all_ips.add(ip)
        except Exception as e:
            print(f"❌ 抓取 {url} 失败: {e}")
    return sorted(all_ips)


def main():
    # 删除旧文件
    if os.path.exists(output_file):
        os.remove(output_file)

    # 抓取新IP
    ips = fetch_ips()

    # 写入文件
    with open(output_file, 'w') as f:
        for ip in ips:
            f.write(ip + '\n')

    # 生成时间戳
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构造推送文本
    if ips:
        ip_list_text = "\n".join(ips)
        message = (
            f"📡 <b>Cloudflare IP 更新通知</b>\n"
            f"🕒 <b>更新时间：</b>{now_time}\n"
            f"📦 <b>共收集：</b>{len(ips)} 个 IP\n\n"
            f"<b>全部IP如下：</b>\n"
            f"<code>{ip_list_text}</code>"
        )
    else:
        message = (
            f"⚠️ <b>未获取到任何IP地址</b>\n"
            f"🕒 <b>检测时间：</b>{now_time}"
        )

    print(message)
    send_tg_message(message)


if __name__ == "__main__":
    main()
