# collect_ips_old.py
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import sys

# ============ 配置区域 ============
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

urls = [
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://ip.164746.xyz'
]

ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
output_file = 'ip.txt'

def is_valid_ip(ip):
    """验证IP地址格式是否正确"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if not 0 <= int(part) <= 255:
            return False
    # 排除私有地址
    if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
        return False
    return True

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
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有文本内容
            text_content = soup.get_text()
            ip_matches = re.findall(ip_pattern, text_content)
            
            # 过滤有效IP
            for ip in ip_matches:
                if is_valid_ip(ip):
                    all_ips.add(ip)
                    print(f"找到有效IP: {ip}")
                else:
                    print(f"跳过无效IP: {ip}")
                    
        except Exception as e:
            print(f"❌ 抓取 {url} 失败: {e}")
    
    print(f"最终收集到的IP数量: {len(all_ips)}")
    return sorted(all_ips)

def main():
    print("🚀 开始执行 Cloudflare IP 抓取任务...")
    
    # 删除旧文件
    if os.path.exists(output_file):
        os.remove(output_file)
        print("🗑️ 已删除旧文件")
    
    # 抓取新IP
    ips = fetch_ips()
    print(f"📊 抓取到的IP列表: {ips}")
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for ip in ips:
            f.write(ip + '\n')
    print("💾 IP已写入文件")
    
    # 重新读取验证
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            file_content = f.read().strip()
            file_ips = file_content.split('\n') if file_content else []
        
        print(f"📄 文件实际内容: {file_content}")
        print(f"📋 从文件读取的IP列表: {file_ips}")
        
        # 对比两个列表
        if set(ips) != set(file_ips):
            print("⚠️ 警告: 内存中的IP与文件中的IP不一致!")
            print(f"内存IP: {sorted(ips)}")
            print(f"文件IP: {sorted(file_ips)}")
        else:
            print("✅ 文件内容验证通过")
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
    
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
    
    print("📤 发送TG消息...")
    send_tg_message(message)
    print("🎉 任务完成")

if __name__ == "__main__":
    main()
