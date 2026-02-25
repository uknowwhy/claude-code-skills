#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 项目自动发布工具
自动化项目初始化、Git 配置、推送到 GitHub
"""

import os
import sys
import subprocess
from pathlib import Path

class GitHubPublisher:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path).resolve()

    def check_git_installed(self):
        """检查 Git 是否已安装"""
        try:
            subprocess.run(["git", "--version"],
                          capture_output=True,
                          check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def init_git_repo(self):
        """初始化 Git 仓库"""
        if (self.project_path / ".git").exists():
            print("✓ Git 仓库已存在")
            return True

        try:
            subprocess.run(["git", "init"],
                          cwd=self.project_path,
                          check=True,
                          capture_output=True)
            print("✓ Git 仓库已初始化")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Git 初始化失败: {e}")
            return False

    def create_gitignore(self, project_type="general"):
        """创建 .gitignore 文件"""

        gitignore_templates = {
            "python": """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
""",
            "general": """
# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
build/
dist/

# Logs
*.log
"""
        }

        template = gitignore_templates.get(project_type,
                                          gitignore_templates["general"])

        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            print("✓ .gitignore 已存在")
            return True

        try:
            gitignore_path.write_text(template.strip() + "\n")
            print("✓ .gitignore 已创建")
            return True
        except IOError as e:
            print(f"✗ .gitignore 创建失败: {e}")
            return False

    def create_license(self, license_type="MIT"):
        """创建 LICENSE 文件"""

        license_templates = {
            "MIT": """MIT License

Copyright (c) {year} {username}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        }

        template = license_templates.get(license_type, license_templates["MIT"])

        license_path = self.project_path / "LICENSE"
        if license_path.exists():
            print("✓ LICENSE 已存在")
            return True

        try:
            import datetime
            year = datetime.datetime.now().year
            # username 会从外部传入
            content = template.format(year=year, username="{username}")
            license_path.write_text(content.strip() + "\n")
            print("✓ LICENSE 已创建")
            return True
        except IOError as e:
            print(f"✗ LICENSE 创建失败: {e}")
            return False

    def commit_files(self, message="Initial commit"):
        """提交所有文件到 Git"""
        try:
            # 添加所有文件
            subprocess.run(["git", "add", "."],
                          cwd=self.project_path,
                          check=True,
                          capture_output=True)
            print("✓ 文件已添加到 Git")

            # 提交
            subprocess.run(["git", "commit", "-m", message],
                          cwd=self.project_path,
                          check=True,
                          capture_output=True)
            print(f"✓ 已提交: {message}")
            return True
        except subprocess.CalledProcessError as e:
            # 可能没有改动
            if "nothing to commit" in str(e.stderr):
                print("✓ 没有需要提交的改动")
                return True
            print(f"✗ 提交失败: {e}")
            return False

    def add_remote(self, username, repo_name):
        """添加远程仓库"""
        remote_url = f"https://github.com/{username}/{repo_name}.git"

        try:
            # 检查是否已存在
            result = subprocess.run(["git", "remote", "-v"],
                                    cwd=self.project_path,
                                    capture_output=True,
                                    text=True)

            if "origin" in result.stdout:
                print("✓ 远程仓库已配置")
                return True

            subprocess.run(["git", "remote", "add", "origin", remote_url],
                          cwd=self.project_path,
                          check=True,
                          capture_output=True)
            print(f"✓ 远程仓库已添加: {remote_url}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 添加远程仓库失败: {e}")
            return False

    def push_to_github(self, branch="main"):
        """推送代码到 GitHub"""
        try:
            # 设置分支名
            subprocess.run(["git", "branch", "-M", branch],
                          cwd=self.project_path,
                          check=True,
                          capture_output=True)

            # 推送
            subprocess.run(["git", "push", "-u", "origin", branch],
                          cwd=self.project_path,
                          check=True)
            print(f"✓ 代码已推送到 GitHub (分支: {branch})")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 推送失败: {e}")
            print("\n请检查:")
            print("1. GitHub 用户名和仓库名是否正确")
            print("2. Personal Access Token 是否有效")
            print("3. 网络连接是否正常")
            return False

    def check_gh_cli(self):
        """检查是否安装了 gh CLI"""
        try:
            subprocess.run(["gh", "--version"],
                          capture_output=True,
                          check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def create_repo_with_gh(self, repo_name, description="", visibility="public"):
        """使用 gh CLI 创建仓库"""
        try:
            cmd = ["gh", "repo", "create", repo_name,
                   f"--{visibility}",
                   "--source=.",
                   "--remote=origin",
                   "--push"]

            if description:
                cmd.extend(["--description", description])

            subprocess.run(cmd,
                          cwd=self.project_path,
                          check=True)
            print(f"✓ GitHub 仓库已创建并推送: {repo_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 创建仓库失败: {e}")
            return False

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python3 github_publisher.py <项目路径>")
        sys.exit(1)

    project_path = sys.argv[1]
    publisher = GitHubPublisher(project_path)

    print("\n=== GitHub 项目自动发布工具 ===\n")

    # 检查 Git
    if not publisher.check_git_installed():
        print("✗ Git 未安装，请先安装 Git")
        sys.exit(1)

    print("✓ Git 已安装\n")

    # 初始化 Git
    publisher.init_git_repo()

    # 创建 .gitignore
    publisher.create_gitignore()

    # 创建 LICENSE
    publisher.create_license()

    # 提交
    publisher.commit_files()

    print("\n✓ 项目已准备就绪！")
    print("\n下一步:")
    print("1. 在 GitHub 创建仓库")
    print("2. 运行推送命令")

if __name__ == "__main__":
    main()
