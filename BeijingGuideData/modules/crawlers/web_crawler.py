"""
网页爬虫模块

本模块负责从网页 URL 中提取文本内容。

支持两种模式：
1. 静态爬取（默认）：适用于传统HTML网站
2. 动态爬取（可选）：适用于JavaScript渲染的网站（如React、Vue、Next.js等）

Usage:
    from modules.crawlers.web_crawler import crawl_url
    
    # 静态爬取
    text = crawl_url("https://example.com/article")
    
    # 动态爬取（需要安装playwright）
    text = crawl_url("https://example.com", use_browser=True)
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional

from utils.logger import logger


def crawl_url(
    url: str,
    timeout: int = 10,
    encoding: Optional[str] = None,
    use_browser: Optional[bool] = None
) -> str:
    """
    从网页 URL 提取文本内容
    
    流程：
    1. 使用 requests 获取网页 HTML（或使用浏览器渲染）
    2. 使用 BeautifulSoup 解析 HTML
    3. 提取所有可见文本
    4. 清洗文本（去除多余空行、制表符等）
    
    Args:
        url: 网页 URL 地址
        timeout: 请求超时时间（秒），默认 10
        encoding: 强制指定编码，默认自动检测
        use_browser: 是否使用浏览器渲染
            - None (默认): 自动检测，先尝试静态，如果内容为空则自动切换到动态模式
            - False: 强制使用静态模式
            - True: 强制使用动态模式
        
    Returns:
        提取的文本内容，失败返回空字符串
        
    Note:
        - 静态模式适用于传统HTML网站，速度快
        - 动态模式适用于React/Vue/Next.js等JavaScript框架网站
        - 自动模式会智能选择最佳方式
        - 动态模式需要安装: pip install playwright && playwright install chromium
    """
    # 验证 URL 格式
    if not url or not url.strip():
        logger.error("URL 不能为空")
        return ""
    
    url = url.strip()
    
    if not url.startswith(('http://', 'https://')):
        logger.error(f"URL 格式无效，必须以 http:// 或 https:// 开头: {url}")
        return ""
    
    # 自动模式：use_browser=None
    if use_browser is None:
        logger.info(f"开始爬取网页 (自动模式): {url}")
        
        # 先尝试静态模式
        logger.info("尝试静态模式...")
        html_content = _fetch_html_static(url, timeout, encoding)
        
        if html_content:
            # 解析并提取文本
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(['script', 'style', 'meta', 'noscript', 'header', 'footer', 'nav']):
                script.decompose()
            text = soup.get_text()
            cleaned_text = _clean_text(text)
            
            # 如果文本内容足够（>100字符），使用静态结果
            if len(cleaned_text) > 100:
                logger.info(f"✓ 静态模式成功，提取 {len(cleaned_text)} 字符")
                return cleaned_text
            else:
                logger.warning(f"静态模式提取内容较少 ({len(cleaned_text)} 字符)，切换到动态模式...")
                use_browser = True  # 切换到动态模式
        else:
            logger.warning("静态模式失败，切换到动态模式...")
            use_browser = True
    
    # 显式指定模式
    logger.info(f"开始爬取网页: {url} (模式: {'动态' if use_browser else '静态'})")
    
    try:
        # 根据模式选择不同的HTML获取方式
        if use_browser:
            html_content = _fetch_html_with_browser(url, timeout)
        else:
            html_content = _fetch_html_static(url, timeout, encoding)
        
        if not html_content:
            logger.error("未能获取HTML内容")
            return ""
        
        logger.info(f"成功获取网页内容，大小: {len(html_content)} 字符")
        
        # 2. 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除脚本和样式元素
        for script in soup(['script', 'style', 'meta', 'noscript', 'header', 'footer', 'nav']):
            script.decompose()
        
        # 3. 提取所有文本
        text = soup.get_text()
        logger.debug(f"BeautifulSoup 提取的原始文本长度: {len(text)} 字符")
        logger.debug(f"原始文本前500字符: {text[:500]}")
        
        # 4. 清洗文本
        cleaned_text = _clean_text(text)
        
        logger.info(f"文本提取成功，清洗后字符数: {len(cleaned_text)}")
        
        return cleaned_text
        
    except Exception as e:
        logger.error(f"爬取网页失败: {url}, 错误: {str(e)}")
        return ""


def _fetch_html_static(
    url: str,
    timeout: int = 10,
    encoding: Optional[str] = None
) -> str:
    """
    使用 requests 静态获取 HTML（适用于传统网站）
    
    Args:
        url: 网页 URL
        timeout: 超时时间
        encoding: 编码
        
    Returns:
        HTML 内容，失败返回空字符串
    """
    try:
        # 发送 HTTP GET 请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()  # 检查 HTTP 状态码
        
        # 设置编码
        if encoding:
            response.encoding = encoding
        elif response.encoding == 'ISO-8859-1':
            # 如果检测到是 ISO-8859-1，尝试使用 apparent_encoding
            response.encoding = response.apparent_encoding
        
        return response.text
        
    except requests.exceptions.Timeout:
        logger.error(f"请求超时 ({timeout}秒): {url}")
        return ""
    
    except requests.exceptions.ConnectionError:
        logger.error(f"网络连接失败: {url}")
        return ""
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP 错误 {e.response.status_code}: {url}")
        return ""
    
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {url}, 错误: {str(e)}")
        return ""


def _fetch_html_with_browser(url: str, timeout: int = 60) -> str:
    """
    使用浏览器渲染获取 HTML（适用于JavaScript渲染的网站）
    
    需要安装：
        pip install playwright
        playwright install chromium
    
    Args:
        url: 网页 URL
        timeout: 超时时间（秒），默认60秒
        
    Returns:
        渲染后的 HTML 内容，失败返回空字符串
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error(
            "使用浏览器模式需要安装 Playwright。\n"
            "请运行: pip install playwright && playwright install chromium"
        )
        return ""
    
    try:
        with sync_playwright() as p:
            logger.debug("启动浏览器...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            logger.debug(f"访问页面: {url}")
            page.goto(url, timeout=timeout * 1000, wait_until='networkidle')
            
            # 等待页面完全加载
            logger.debug("等待页面渲染...")
            page.wait_for_load_state('domcontentloaded')
            
            # 获取渲染后的HTML
            html_content = page.content()
            
            browser.close()
            logger.debug(f"浏览器渲染完成，获取 {len(html_content)} 字符")
            
            return html_content
            
    except Exception as e:
        logger.error(f"浏览器渲染失败: {url}, 错误: {str(e)}")
        return ""


def _clean_text(text: str) -> str:
    """
    清洗提取的文本
    
    Args:
        text: 原始文本
        
    Returns:
        清洗后的文本
    """
    if not text or not text.strip():
        logger.debug("文本为空或全为空白字符")
        return ""
    
    logger.debug(f"原始文本长度: {len(text)} 字符")
    
    # 1. 替换多个空白字符（空格、制表符）为单个空格
    text = re.sub(r'[ \t]+', ' ', text)
    logger.debug(f"空白字符规范化后: {len(text)} 字符")
    
    # 2. 规范化换行符（统一为 \n）
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 3. 去除每行首尾空格
    lines = [line.strip() for line in text.split('\n')]
    logger.debug(f"分割为 {len(lines)} 行")
    
    # 4. 过滤空行
    lines = [line for line in lines if line]
    logger.debug(f"过滤空行后剩余 {len(lines)} 行")
    
    # 5. 用单个换行符重新组合（保持段落结构）
    cleaned = '\n'.join(lines)
    
    # 6. 压缩连续的换行符为最多两个（保留段落分隔）
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    result = cleaned.strip()
    logger.debug(f"最终清洗后: {len(result)} 字符")
    
    return result


# ============================================================================
# 使用示例和测试
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("网页爬虫测试")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        
        # 解析命令行参数
        use_browser = None  # 默认自动模式
        if '--browser' in sys.argv or '-b' in sys.argv:
            use_browser = True  # 强制动态模式
        elif '--static' in sys.argv or '-s' in sys.argv:
            use_browser = False  # 强制静态模式
        
        mode_name = "自动" if use_browser is None else ("动态（浏览器）" if use_browser else "静态（requests）")
        print(f"\n测试 URL: {test_url}")
        print(f"模式: {mode_name}\n")
        
        # 爬取网页
        text = crawl_url(test_url, use_browser=use_browser)
        
        if text:
            print("\n" + "=" * 60)
            print(f"爬取成功，提取 {len(text)} 字符")
            print("=" * 60)
            
            # 显示前 500 字符
            preview = text[:500] + "..." if len(text) > 500 else text
            print(f"\n内容预览:\n{preview}\n")
        else:
            print("\n❌ 爬取失败")
            if use_browser is False:
                print("\n提示：如果网站使用JavaScript渲染内容，请尝试使用动态模式：")
                print(f"  python -m modules.crawlers.web_crawler {test_url} --browser")
    else:
        print("\n使用方法:")
        print("  python -m modules.crawlers.web_crawler <url> [选项]")
        print("\n选项:")
        print("  (无)            自动模式（推荐）- 智能选择最佳方式")
        print("  --browser, -b   强制动态模式（用于JavaScript渲染的网站）")
        print("  --static, -s    强制静态模式（用于传统HTML网站）")
        print("\n示例:")
        print("  # 自动模式（推荐）")
        print("  python -m modules.crawlers.web_crawler https://example.com")
        print("\n  # 强制静态模式")
        print("  python -m modules.crawlers.web_crawler https://example.com --static")
        print("\n  # 强制动态模式")
        print("  python -m modules.crawlers.web_crawler https://example.com --browser")
