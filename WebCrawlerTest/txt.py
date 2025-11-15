import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time

def clean_text(text):
    """清理文本，去除多余空格和特殊字符"""
    # 替换多个空格为单个空格
    text = re.sub(r' +', ' ', text)
    # 去除首尾空格
    text = text.strip()
    # 处理中英文标点混排问题
    text = re.sub(r'，', ',', text)
    text = re.sub(r'。', '.', text)
    text = re.sub(r'；', ';', text)
    text = re.sub(r'：', ':', text)
    return text

def get_formatted_text_from_page(url, base_url=None, timeout=10):
    """从单页提取并格式化文本内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 自动识别编码
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除所有非文本元素
        for tag in soup(['script', 'style', 'iframe', 'noscript', 'svg', 'img', 
                        'form', 'nav', 'footer', 'aside', 'ad', 'header']):
            tag.decompose()
        
        # 提取标题
        title = soup.title.get_text(strip=True) if soup.title else "无标题"
        title = clean_text(title)
        
        # 提取正文内容
        content = []
        content.append(f"【页面标题】: {title}\n")
        content.append("-" * (len(title) + 6) + "\n\n")  # 标题下划线
        
        # 主要内容区域识别（优先尝试常见的内容容器）
        main_containers = ['main', 'article', 'div[class*="content"]', 
                          'div[class*="article"]', 'div[class*="post"]']
        main_content = None
        
        for container in main_containers:
            main_content = soup.select_one(container)
            if main_content:
                break
        
        # 如果找不到特定容器，使用body
        if not main_content:
            main_content = soup.body
        
        if not main_content:
            return "无法提取页面内容", None
        
        # 提取并格式化文本元素
        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']):
            # 跳过空元素
            if not element.get_text(strip=True):
                continue
                
            text = clean_text(element.get_text())
            if not text:
                continue
                
            # 根据标签类型应用一致的格式
            if element.name.startswith('h'):
                level = int(element.name[1:])
                # 标题格式：级别越高，前缀越少
                prefix = '#' * min(level, 3)  # 限制最大级别为3
                content.append(f"\n{prefix} {text}\n")
            elif element.name == 'p':
                # 段落格式：空行分隔
                content.append(f"{text}\n\n")
            elif element.name == 'li':
                # 列表项格式
                if element.parent.name == 'ul':
                    content.append(f"  • {text}\n")
                else:  # ol
                    # 计算有序列表索引
                    siblings = list(element.parent.find_all('li'))
                    index = siblings.index(element) + 1
                    content.append(f"  {index}. {text}\n")
        
        # 合并内容并清理格式
        full_text = ''.join(content)
        # 规范空行：确保段落间是两个空行，列表项后是一个空行
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)
        # 确保列表项后只有一个空行
        full_text = re.sub(r'(\n  [•0-9])\n+', r'\1\n', full_text)
        # 确保标题后有两个空行
        full_text = re.sub(r'(\n#+.+)\n+', r'\1\n\n', full_text)
        
        # 查找下一页链接
        next_page_link = None
        next_page_patterns = [
            re.compile(r'下一页', re.IGNORECASE),
            re.compile(r'next', re.IGNORECASE),
            re.compile(r'更多', re.IGNORECASE),
            re.compile(r'»', re.IGNORECASE),
            re.compile(r'›', re.IGNORECASE)
        ]
        
        # 检查链接
        for link in soup.find_all('a'):
            link_text = link.get_text(strip=True)
            link_href = link.get('href')
            
            if link_href and any(pattern.search(link_text) for pattern in next_page_patterns):
                next_page_link = urljoin(base_url or url, link_href)
                # 避免循环链接
                if next_page_link == current_url:
                    continue
                break
        
        # 检查rel="next"属性
        if not next_page_link:
            rel_next = soup.find('link', rel='next')
            if rel_next and rel_next.get('href'):
                next_page_link = urljoin(base_url or url, rel_next.get('href'))
        
        return full_text, next_page_link
        
    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}", None
    except Exception as e:
        return f"处理错误: {str(e)}", None

def extract_paginated_text(start_url, max_pages=10):
    """提取多页内容，处理分页"""
    all_text = []
    current_url = start_url
    base_url = f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}"
    page_count = 0
    visited_urls = set()  # 记录已访问URL，防止循环
    
    print(f"开始从 {start_url} 提取内容...")
    
    while current_url and page_count < max_pages and current_url not in visited_urls:
        visited_urls.add(current_url)
        page_count += 1
        print(f"正在提取第 {page_count} 页: {current_url}")
        
        text, next_url = get_formatted_text_from_page(current_url, base_url)
        
        if text:
            all_text.append(f"===== 第 {page_count} 页 =====")
            all_text.append(text)
            all_text.append("\n" + "=" * 40 + "\n")  # 页面分隔线
        
        # 避免请求过于频繁
        if next_url:
            time.sleep(1.5)  # 增加延迟，更友好
        
        current_url = next_url
    
    print(f"提取完成，共提取 {page_count} 页内容")
    return '\n'.join(all_text)

if __name__ == "__main__":
    # 示例使用
    url = input("请输入要提取内容的起始URL: ").strip()
    if not url:
        url = "https://example.com"
    
    try:
        max_pages = int(input("请输入最大提取页数(默认10): ") or "10")
    except ValueError:
        max_pages = 10
    
    print("\n开始提取内容...\n")
    full_content = extract_paginated_text(url, max_pages)
    
    # 显示部分内容预览
    preview_length = 800
    print("\n内容预览:")
    print("-" * 70)
    print(full_content[:preview_length] + ("..." if len(full_content) > preview_length else ""))
    print("-" * 70)
    
    # 保存到文件
    filename = input("\n请输入保存的文件名(默认: formatted_content.txt): ").strip()
    if not filename:
        filename = "formatted_content.txt"
    if not filename.endswith('.txt'):
        filename += '.txt'
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print(f"全部内容已保存到 {filename}")
    
