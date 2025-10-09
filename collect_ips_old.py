import requests
from bs4 import BeautifulSoup
import re
import os

# ============ 配置区域 ============
# Telegram 推送配置
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Telegram Bot Token
CHAT_ID = os.environ.get("CHAT_ID")      # 你的Telegram聊天ID

# 目标URL列表
urls = [
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://ip.164746.xyz'
]

# 匹配 IPv4 地址的正则
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
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram 推送成功。")
        else:
            print(f"❌ Telegram 推送失败: {response.text}")
    except Exception as e:
        print(f"❌ Telegram 推送异常: {e}")


def fetch_ips():
    """抓取网页中的 IP 地址"""
    all_ips = set()  # 去重
    for url in urls:
        print(f"正在抓取: {url}")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 根据网站结构提取
            if '164746' in url:
                elements = soup.find_all('tr')
            else:
                elements = soup.find_all(['li', 'tr'])

            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)
                for ip in ip_matches:
                    all_ips.add(ip)

        except Exception as e:
            print(f"❌ 抓取 {url} 失败: {e}")

    return sorted(list(all_ips))


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

    # 输出与推送
    msg = f"✅ 共获取到 <b>{len(ips)}</b> 个 IP 地址。\n"
    if ips:
        preview = "\n".join(ips[:5])
        msg += f"<b>前5个示例：</b>\n<code>{preview}</code>"
    else:
        msg += "未抓取到任何IP。"

    print(msg)
    send_tg_message(msg)


if __name__ == "__main__":
    main()
