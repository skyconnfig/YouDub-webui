#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 HuggingFace Token 是否有效"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')

def test_hf():
    """测试 HuggingFace API"""
    if not HF_TOKEN or HF_TOKEN == 'hf_xxx':
        print("错误: 未找到 HF_TOKEN")
        return False
    
    try:
        import requests
        
        print("正在测试 HuggingFace Token...")
        
        # 测试 API
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.get(
            "https://huggingface.co/api/whoami",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Token 有效！")
            print(f"用户名: {data.get('name', 'Unknown')}")
            print(f"类型: {data.get('type', 'Unknown')}")
            return True
        else:
            print(f"错误: HTTP {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = test_hf()
    sys.exit(0 if success else 1)
