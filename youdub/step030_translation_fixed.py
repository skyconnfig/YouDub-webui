# -*- coding: utf-8 -*-
import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import time
from loguru import logger

load_dotenv()

# 配置翻译后端: "ollama", "groq", 或 "openai"
TRANSLATION_BACKEND = os.getenv('TRANSLATION_BACKEND', 'ollama').lower()

# Ollama 配置
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Groq 配置
if os.getenv('GROQ_API_KEY'):
    model_name = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    print(f'using Groq model {model_name}')
else:
    model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    print(f'using model {model_name}')

print(f'Using translation backend: {TRANSLATION_BACKEND}')
if TRANSLATION_BACKEND == 'ollama':
    print(f'Using Ollama model: {OLLAMA_MODEL}')

# NOTE: repetition_penalty is not supported by all API providers
# Only include it for specific models that support it
if model_name == "01ai/Yi-34B-Chat-4bits":
    extra_body = {
        'stop_token_ids': [7]
    }
else:
    extra_body = {}

# Ollama 客户端 (延迟初始化)
_ollama_client = None

def get_ollama_client():
    """获取 Ollama 客户端"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OpenAI(
            base_url=f'{OLLAMA_BASE_URL}/v1',
            api_key='ollama'  # Ollama 不需要真实 key
        )
    return _ollama_client

def get_necessary_info(info: dict):
    return {
        'title': info['title'],
        'uploader': info['uploader'],
        'description': info['description'],
        'upload_date': info['upload_date'],
        'categories': info['categories'],
        'tags': info['tags'],
    }


def ensure_transcript_length(transcript, max_length=4000):
    mid = len(transcript)//2
    before, after = transcript[:mid], transcript[mid:]
    length = max_length//2
    return before[:length] + after[-length:]
def get_openai_client():
    """获取 OpenAI 客户端，支持 Groq/Ollama 配置"""
    if TRANSLATION_BACKEND == 'ollama':
        return get_ollama_client()
    if os.getenv('GROQ_API_KEY'):
        return OpenAI(
            base_url='https://api.groq.com/openai/v1',
            api_key=os.getenv('GROQ_API_KEY')
        )
    return OpenAI(
        base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
        api_key=os.getenv('OPENAI_API_KEY')
    )

def get_translation_client():
    """获取翻译用的客户端"""
    if TRANSLATION_BACKEND == 'ollama':
        return get_ollama_client()
    elif os.getenv('GROQ_API_KEY'):
        return OpenAI(
            base_url='https://api.groq.com/openai/v1',
            api_key=os.getenv('GROQ_API_KEY')
        )
    else:
        return OpenAI(
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            api_key=os.getenv('OPENAI_API_KEY')
        )

def summarize(info, transcript, target_language='简体中文'):
    client = get_translation_client()
    transcript = ' '.join(line['text'] for line in transcript)
    transcript = ensure_transcript_length(transcript, max_length=2000)
    info_message = f'Title: "{info["title"]}" Author: "{info["uploader"]}". ' 
    # info_message = ''
    
    full_description = f'The following is the full content of the video:\n{info_message}\n{transcript}\n{info_message}\nAccording to the above content, detailedly Summarize the video in JSON format:\n```json\n{{"title": "", "summary": ""}}\n```'
    
    messages = [
        {'role': 'system',
            'content': f'You are a expert in the field of this video. Please detailedly summarize the video in JSON format.\n```json\n{{"title": "the title of the video", "summary", "the summary of the video"}}\n```'},
        {'role': 'user', 'content': full_description},
    ]
    retry_message=''
    success = False
    # 选择正确的模型
    current_model = OLLAMA_MODEL if TRANSLATION_BACKEND == 'ollama' else model_name

    # 选择正确的模型
    current_model = OLLAMA_MODEL if TRANSLATION_BACKEND == 'ollama' else model_name
    for retry in range(5):
        try:
            messages = [
                {'role': 'system', 'content': 'You are a expert in the field of this video. Please summarize the video in JSON format. ```json {"title": "the title of the video", "summary": "the summary of the video"} ```'},
                {'role': 'user', 'content': full_description+retry_message},
            ]
            response = client.chat.completions.create(
                model=current_model,
                messages=messages,
                timeout=240,
                extra_body={} if TRANSLATION_BACKEND == 'ollama' else extra_body
            )
            summary = response.choices[0].message.content.replace('
', '')
            if '视频标题' in summary:
                raise Exception("包含"视频标题"")
            logger.info(summary)
            summary = re.findall(r'\{.*?\}', summary)[0]
            summary = json.loads(summary)
            summary = {
                'title': summary['title'].replace('title:', '').strip(),
                'summary': summary['summary'].replace('summary:', '').strip()
            }
            if 'title' in summary['title']:
                raise Exception('Invalid summary')
            success = True
            break
        except Exception as e:
            retry_message += '
Summarize the video in JSON format:
```json
{"title": "", "summary": ""}
```'
            logger.warning(f'总结失败
{e}')
            time.sleep(1)
    if not success:
        raise Exception(f'总结失败')

    title = summary['title']
    summary = summary['summary']
    tags = info['tags']
    messages = [
        {'role': 'system',
            'content': f'You are a native speaker of {target_language}. Please translate the title and summary into {target_language} in JSON format. ```json
{{"title": "the {target_language} title of the video", "summary": "the {target_language} summary of the video", "tags": [list of tags in {target_language}]}}
```.'},
        {'role': 'user',
            'content': f'The title of the video is "{title}". The summary of the video is "{summary}". Tags: {tags}.
Please translate the above title and summary and tags into {target_language} in JSON format. ```json
{{"title": "", "summary": ""， "tags": []}}
```. Remember to tranlate the title and the summary and tags into {target_language} in JSON.'},
    ]
    while True:
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=messages,
                timeout=240,
                extra_body={} if TRANSLATION_BACKEND == 'ollama' else extra_body
            )
            summary = response.choices[0].message.content.replace('
', '')
            logger.info(summary)
            summary = re.findall(r'\{.*?\}', summary)[0]
            summary = json.loads(summary)
            if target_language in summary['title'] or target_language in summary['summary']:
                raise Exception('Invalid translation')
            title = summary['title'].strip()
            if (title.startswith('"') and title.endswith('"')) or (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")) or (title.startswith('《') and title.endswith('》')):
                title = title[1:-1]
            result = {
                'title': title,
                'author': info['uploader'],
                'summary': summary['summary'],
                'tags': summary['tags'],
                'language': target_language
            }
            return result
        except Exception as e:
            logger.warning(f'总结翻译失败
{e}')
            time.sleep(1)
