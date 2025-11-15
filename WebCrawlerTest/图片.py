import requests
from bs4 import BeautifulSoup
import re
import os
import time
import random
import socket
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import NewConnectionError, MaxRetryError

# 随机User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/111.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/112.0.1722.58'
]

def check_network_connection(host="8.8.8.8", port=53, timeout=3):
    """检查网络连接是否正常"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as e:
        print(f"网络连接检查失败: {str(e)}")
        return False

def check_domain_resolution(domain):
    """检查域名解析是否正常"""
    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        print(f"域名解析成功: {domain} -> {ip_addresses}")
        return True
    except socket.gaierror:
        print(f"域名解析失败: 无法解析 {domain}")
        return False
    except Exception as e:
        print(f"域名解析出错: {str(e)}")
        return False

def create_save_dir(base_dir):
    """创建保存目录"""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.abspath(base_dir)

def get_next_page_url(soup, base_url):
    """获取下一页链接"""
    next_patterns = [re.compile(r'下一页|next|更多|»|›', re.IGNORECASE)]
    for link in soup.find_all('a'):
        link_text = link.get_text(strip=True)
        link_href = link.get('href')
        if link_href and any(pattern.search(link_text) for pattern in next_patterns):
            return urljoin(base_url, link_href)
    rel_next = soup.find('link', rel='next')
    if rel_next and rel_next.get('href'):
        return urljoin(base_url, rel_next.get('href'))
    return None

def create_session_with_retries():
    """创建带有增强重试机制的会话"""
    session = requests.Session()
    
    # 配置详细的重试策略
    retry_strategy = Retry(
        total=5,
        backoff_factor=3,  # 指数退避：1, 2, 4, 8, 16秒
        status_forcelist=[429, 500, 502, 503, 504, 403, 408],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # 连接超时设置
    session.timeout = 15
    
    return session

def random_headers(base_url):
    """生成随机请求头"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': base_url,
        'Upgrade-Insecure-Requests': '1'
    }

def is_valid_image(url):
    """验证图片URL有效性"""
    valid_suffix = (".jpg", ".jpeg", ".png", ".gif", ".webp")
    return urlparse(url).scheme in ("http", "https") and url.lower().endswith(valid_suffix)

def download_image(img_url, save_dir, page_num, img_idx, session, base_url):
    """下载单张图片"""
    try:
        time.sleep(random.uniform(1, 2))
        session.headers.update(random_headers(base_url))
        
        response = session.get(img_url, stream=True)
        response.raise_for_status()
        
        # 确定图片后缀
        suffix = os.path.splitext(urlparse(img_url).path)[1].lower()
        suffix = suffix if suffix in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"
        img_name = f"page_{page_num}_img_{img_idx}{suffix}"
        save_path = os.path.join(save_dir, img_name)
        
        # 保存图片
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)
        print(f"✅ 成功：{img_name}")
        return True
    except Exception as e:
        print(f"❌ 失败（{img_url[:50]}）：{str(e)[:30]}")
        return False

def crawl_paginated_images(start_url, max_pages, save_dir):
    """分页爬取图片，增强连接错误处理"""
    # 预处理URL
    parsed_url = urlparse(start_url)
    if not parsed_url.scheme:
        start_url = f"https://{start_url}"
        parsed_url = urlparse(start_url)
    
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    domain = parsed_url.netloc
    
    # 检查网络和域名
    print("正在检查网络连接...")
    if not check_network_connection():
        print("无法连接到网络，请检查网络设置")
        return
    
    print(f"正在检查域名解析: {domain}")
    if not check_domain_resolution(domain):
        print("域名解析失败，无法继续")
        return
    
    current_url = start_url
    page_count = 0
    visited = set()
    session = create_session_with_retries()
    
    print(f"\n开始下载图片（最大{max_pages}页），保存路径：{save_dir}")
    
    while current_url and page_count < max_pages and current_url not in visited:
        visited.add(current_url)
        page_count += 1
        print(f"\n--- 处理第{page_count}页：{current_url} ---")
        
        try:
            # 随机延迟
            delay = random.uniform(2, 4)
            print(f"等待{delay:.2f}秒后请求...")
            time.sleep(delay)
            
            # 更新请求头
            session.headers.update(random_headers(base_url))
            
            # 尝试连接
            response = session.get(current_url)
            
            # 检查状态码
            if response.status_code == 403:
                print("遇到403错误，尝试使用浏览器Cookie...")
                cookie = input("请输入浏览器中的Cookie（留空跳过）：")
                if cookie:
                    session.headers['Cookie'] = cookie
                    response = session.get(current_url)
                    if response.status_code == 403:
                        print("Cookie无效，无法访问")
                        current_url = None
                        continue
            
            response.raise_for_status()
            
            # 解析内容
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            valid_urls = []
            
            # 提取图片URL
            for img in img_tags:
                srcset = img.get('srcset')
                if srcset:
                    high_res = srcset.split(',')[-1].strip().split()[0]
                    if is_valid_image(high_res):
                        valid_urls.append(urljoin(base_url, high_res))
                        continue
                src = img.get('src')
                if src and is_valid_image(src):
                    valid_urls.append(urljoin(base_url, src))
            
            # 去重并下载
            unique_urls = list(set(valid_urls))
            print(f"找到{len(unique_urls)}张有效图片")
            for idx, url in enumerate(unique_urls, 1):
                download_image(url, save_dir, page_count, idx, session, base_url)
            
            current_url = get_next_page_url(soup, base_url)
            
        except (NewConnectionError, MaxRetryError, requests.exceptions.ConnectionError) as e:
            print(f"连接错误: {str(e)[:100]}")
            print("尝试更换网络或稍后再试")
            # 尝试直接获取下一页（如果可能）
            current_url = None
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {str(e)[:50]}")
            current_url = None
        except Exception as e:
            print(f"处理错误: {str(e)[:50]}")
            current_url = None
    
    print(f"\n图片下载完成！保存路径：{save_dir}")

if __name__ == "__main__":
    start_url = input("请输入起始网页URL：").strip()
    if not start_url:
        start_url = "https://example.com"
    
    try:
        max_pages = int(input("请输入最大处理页数（默认10页）：") or "10")
    except ValueError:
        max_pages = 10
    
    img_dir = create_save_dir("web_images")
    crawl_paginated_images(start_url, max_pages, img_dir)
    
