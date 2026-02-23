#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Bilibili cookie 文件提取凭据并配置 .env
"""
import os
import re
import sys

# 解决 Windows 控制台中文输出问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def parse_cookies(cookie_file):
    """解析 Netscape 格式的 cookie 文件"""
    sessdata = None
    bili_jct = None
    
    with open(cookie_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                
                if name == 'SESSDATA':
                    sessdata = value
                elif name == 'bili_jct':
                    bili_jct = value
    
    return sessdata, bili_jct

def update_env_file(sessdata, bili_jct, env_file='.env'):
    """更新 .env 文件"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), env_file)
    
    # 读取现有内容
    existing_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    
    # 检查是否已有配置
    has_sessdata = False
    has_bili_jct = False
    
    new_lines = []
    for line in existing_lines:
        if line.startswith('BILI_SESSDATA'):
            has_sessdata = True
            new_lines.append(f'BILI_SESSDATA={sessdata}\n')
        elif line.startswith('BILI_BILI_JCT'):
            has_bili_jct = True
            new_lines.append(f'BILI_BILI_JCT={bili_jct}\n')
        else:
            new_lines.append(line)
    
    # 如果没有则添加
    if not has_sessdata:
        new_lines.append(f'BILI_SESSDATA={sessdata}\n')
    if not has_bili_jct:
        new_lines.append(f'BILI_BILI_JCT={bili_jct}\n')
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return env_path

def main():
    # Try project root config/bilibili.txt
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookie_file = os.path.join(project_root, 'config', 'bilibili.txt')
    env_file = os.path.join(project_root, '.env')
    
    if not os.path.exists(cookie_file):
        # Fallback to local
        cookie_file = 'bilibili.txt'
    
    if not os.path.exists(cookie_file):
        print(f"错误: 找不到 cookie 文件 {cookie_file}")
        print("请确保 bilibili.txt 文件在 config/ 目录下")
        return
    
    print("正在解析 cookie 文件...")
    sessdata, bili_jct = parse_cookies(cookie_file)
    
    if not sessdata:
        print("错误: 无法从 cookie 文件中提取 SESSDATA")
        return
    
    if not bili_jct:
        print("错误: 无法从 cookie 文件中提取 bili_jct")
        return
    
    print(f"SESSDATA: {sessdata[:20]}...")
    print(f"bili_jct: {bili_jct}")
    
    env_path = update_env_file(sessdata, bili_jct, env_file)
    print(f"\n[OK] Updated {env_path}")
    print("\nNow you can run the program!")

if __name__ == '__main__':
    main()
