import os
import requests
import datetime
import git
from pathlib import Path
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置项
REPO_PATH = "ad"
REWRITE_DIR = "rewrite"
RULES_DIR = "rules"  # 新增：存放从网站抓取的规则
OUTPUT_FILE = "ad_rewrite.conf"
README_PATH = "README-rewrite.md"

# 网站规则源
WEBSITE_RULES = {
    "adultraplus": "https://whatshub.top/rewrite/adultraplus.conf",
    "wechatad": "https://whatshub.top/rewrite/wechatad.conf",
    "youtube": "https://whatshub.top/rewrite/youtube.conf"
}

# GitHub 规则源
GITHUB_SOURCES = {
    "surge去广告": "https://raw.githubusercontent.com/QingRex/LoonKissSurge/refs/heads/main/Surge/Official/%E6%96%B0%E6%89%8B%E5%8F%8B%E5%A5%BD%E3%81%AE%E5%8E%BB%E5%B9%BF%E5%91%8A%E9%9B%86%E5%90%88.official.sgmodule",
    # ... 其他 GitHub 源
}

def setup_directory():
    """创建必要的目录"""
    Path(os.path.join(REPO_PATH, REWRITE_DIR)).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(REPO_PATH, RULES_DIR)).mkdir(parents=True, exist_ok=True)

def download_website_rules():
    """下载网站规则并保存到文件"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    for name, url in WEBSITE_RULES.items():
        try:
            print(f"Downloading rule from website: {name}")
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            
            # 保存规则到文件
            rule_path = os.path.join(REPO_PATH, RULES_DIR, f"{name}.conf")
            with open(rule_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"Successfully saved {name} rule")
            
        except Exception as e:
            print(f"Error downloading {name}: {str(e)}")

def merge_all_rules():
    """合并所有规则"""
    merged_content = f"""# 广告拦截重写规则合集
# 更新时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 合并自以下源：
"""

    # 添加网站规则源信息
    for name, url in WEBSITE_RULES.items():
        merged_content += f"# {name}: {url}\n"
    
    # 添加 GitHub 规则源信息
    for name, url in GITHUB_SOURCES.items():
        merged_content += f"# {name}: {url}\n"

    # 首先合并本地保存的网站规则
    for name in WEBSITE_RULES.keys():
        rule_path = os.path.join(REPO_PATH, RULES_DIR, f"{name}.conf")
        if os.path.exists(rule_path):
            with open(rule_path, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content += f"\n# ======== {name} ========\n"
                merged_content += content + "\n"

    # 然后下载并合并 GitHub 规则
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for name, url in GITHUB_SOURCES.items():
        try:
            print(f"Downloading rules from {name}...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            merged_content += f"\n# ======== {name} ========\n"
            merged_content += response.text + "\n"
            
        except Exception as e:
            print(f"Error downloading {name}: {str(e)}")

    # 保存合并后的文件
    output_path = os.path.join(REPO_PATH, REWRITE_DIR, OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    print(f"Successfully merged all rules to {OUTPUT_FILE}")

def update_readme():
    """更新 README.md"""
    content = f"""# 广告拦截重写规则合集

## 更新时间
{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 规则说明
本重写规则集合并自各个开源规则，保持原始格式不变。

## 规则来源
### 网站规则
{chr(10).join([f'- {name}: {url}' for name, url in WEBSITE_RULES.items()])}

### GitHub规则
{chr(10).join([f'- {name}: {url}' for name, url in GITHUB_SOURCES.items()])}
"""
    
    with open(os.path.join(REPO_PATH, README_PATH), 'w', encoding='utf-8') as f:
        f.write(content)

def git_push():
    """提交更改到 Git"""
    try:
        repo = git.Repo(REPO_PATH)
        repo.git.add(all=True)
        repo.index.commit(f"Update rewrite rules: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        origin = repo.remote(name='origin')
        origin.push()
        print("Successfully pushed to repository")
    except Exception as e:
        print(f"Error pushing to repository: {str(e)}")

def main():
    setup_directory()
    download_website_rules()  # 先下载网站规则
    merge_all_rules()        # 然后合并所有规则
    update_readme()
    git_push()

if __name__ == "__main__":
    main()
