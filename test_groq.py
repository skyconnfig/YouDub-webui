#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Groq API Key 是否有效

使用方法:
1. 在 .env 文件中配置 GROQ_API_KEY=你的key
2. 运行: python test_groq.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 从环境变量读取 API Key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def test_groq():
    """测试 Groq API 连接"""
    if not GROQ_API_KEY:
        print("错误: 未找到 GROQ_API_KEY")
        print("请在 .env 文件中添加: GROQ_API_KEY=gsk_你的key")
        return False
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY
        )
        
        print("正在测试 Groq API 连接...")
        
        # 测试模型列表
        models = client.models.list()
        print("API Key 有效！")
        print("可用模型数量: {}".format(len(models.data)))
        print("\n推荐模型:")
        
        recommended = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768']
        for model in models.data:
            if model.id in recommended:
                print("  - {}".format(model.id))
        
        # 测试简单翻译
        print("\n测试简单翻译...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a translator. Translate to Chinese."},
                {"role": "user", "content": 'Translate: "Hello, how are you?"'}
            ],
            max_tokens=100
        )
        
        translation = response.choices[0].message.content
        print("翻译测试成功！")
        print("原文: Hello, how are you?")
        print("译文: {}".format(translation))
        
        return True
        
    except Exception as e:
        print("错误: {}".format(e))
        return False

if __name__ == "__main__":
    success = test_groq()
    sys.exit(0 if success else 1)
