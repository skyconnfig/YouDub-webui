# -*- coding: utf-8 -*-
import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
import time
from loguru import logger
from .terminology import TerminologyManager

load_dotenv()

# 初始化术语管理器
_terminology_manager = None

def get_terminology_manager():
    """获取术语管理器（延迟初始化）"""
    global _terminology_manager
    if _terminology_manager is None:
        _terminology_manager = TerminologyManager()
    return _terminology_manager

# 配置翻译后端: "ollama", "groq", 或 "openai"
# 默认使用 groq（免费且不需要本地服务）
TRANSLATION_BACKEND = os.getenv('TRANSLATION_BACKEND', 'groq').lower()

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

# 兼容旧函数名
def get_openai_client():
    """获取 OpenAI 客户端，支持 Groq/Ollama 配置"""
    return get_translation_client()

def summarize(info, transcript, target_language='简体中文'):
    client = get_openai_client()
    transcript = ' '.join(line['text'] for line in transcript)
    transcript = ensure_transcript_length(transcript, max_length=2000)
    info_message = f'Title: "{info["title"]}" Author: "{info["uploader"]}". ' 
    # info_message = ''
    
    full_description = f'The following is the full content of the video:\n{info_message}\n{transcript}\n{info_message}\nAccording to the above content, detailedly Summarize the video in JSON format:\n```json\n{{"title": "", "summary": ""}}\n```'
    
    messages = [
        {'role': 'system',
            'content': f'你是一位专业的视频内容分析师。请结合标题和文案，对视频内容进行深入总结。输出格式必须为严格的 JSON。\n```json\n{{"title": "中文标题", "summary": "详细的中内容摘要"}}\n```'},
        {'role': 'user', 'content': full_description},
    ]
    retry_message=''
    success = False
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
                extra_body=extra_body
            )
            summary = response.choices[0].message.content.replace('\n', '')
            if '视频标题' in summary:
                raise Exception("包含“视频标题”")
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
            retry_message += '\nSummarize the video in JSON format:\n```json\n{"title": "", "summary": ""}\n```'
            logger.warning(f'总结失败\n{e}')
            time.sleep(1)
    if not success:
        raise Exception(f'总结失败')
        
    title = summary['title']
    summary = summary['summary']
    tags = info['tags']
    messages = [
        {'role': 'system',
            'content': f'你是一位母语为{target_language}的资深本地化专家。请将视频的标题、摘要和标签翻译成地道的{target_language}，确保符合中国用户的阅读习惯和搜索偏好。输出格式为 JSON。\n```json\n{{"title": "{target_language}标题", "summary": "{target_language}摘要", "tags": [针对B站优化的标签列表]}}\n```.'},
        {'role': 'user',
            'content': f'原标题: "{title}"\n原摘要: "{summary}"\n原标签: {tags}.\n请翻译成{target_language}，特别注意标题要吸引人。'},
    ]
    while True:
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=messages,
                timeout=240,
                extra_body=extra_body
            )
            summary = response.choices[0].message.content.replace('\n', '')
            logger.info(summary)
            summary = re.findall(r'\{.*?\}', summary)[0]
            summary = json.loads(summary)
            if target_language in summary['title'] or target_language in summary['summary']:
                raise Exception('Invalid translation')
            title = summary['title'].strip()
            if (title.startswith('"') and title.endswith('"')) or (title.startswith('“') and title.endswith('”')) or (title.startswith('‘') and title.endswith('’')) or (title.startswith("'") and title.endswith("'")) or (title.startswith('《') and title.endswith('》')):
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
            logger.warning(f'总结翻译失败\n{e}')
            time.sleep(1)


def translation_postprocess(result):
    result = re.sub(r'\（[^)]*\）', '', result)
    result = result.replace('...', '，')
    result = re.sub(r'(?<=\d),(?=\d)', '', result)
    result = result.replace('²', '的平方').replace(
        '————', '：').replace('——', '：').replace('°', '度')
    result = result.replace("AI", '人工智能')
    result = result.replace('变压器', "Transformer")
    return result


def _is_repetitive(text: str, threshold: int = 3) -> bool:
    """检测文本是否包含重复短语（LLM复读识别）"""
    # 按标点分割后统计重复
    sentences = [s.strip() for s in re.split(r'[。，！？；\n]', text) if s.strip()]
    if not sentences:
        return False
    from collections import Counter
    counts = Counter(sentences)
    # 如果任何一个片段出现超过阈值次数，认为是复读
    return any(v >= threshold for v in counts.values())


def valid_translation(text, translation):
    
    if (translation.startswith('```') and translation.endswith('```')):
        translation = translation[3:-3]
        return True, translation_postprocess(translation)
    
    if (translation.startswith('"') and translation.endswith('"')):
        translation = translation[1:-1]
        return True, translation_postprocess(translation)
    
    # Handle Ollama format: 翻译："..." or 翻译："..."
    if translation.startswith('翻译：') or translation.startswith('翻译:'):
        # Extract content after 翻译： or 翻译:
        translation = translation[3:].strip()
        # Remove surrounding quotes if present
        if (translation.startswith('"') and translation.endswith('"')) or \
           (translation.startswith('"') and translation.endswith('"')) or \
           (translation.startswith('"') and translation.endswith('"')):
            translation = translation[1:-1]
        return True, translation_postprocess(translation)
    
    if '翻译' in translation and '："' in translation and '"' in translation:
        translation = translation.split('："')[-1].split('"')[0]
        return True, translation_postprocess(translation)
    
    if (translation.startswith('“') and translation.endswith('”')) or (translation.startswith('"') and translation.endswith('"')):
        translation = translation[1:-1]
        return True, translation_postprocess(translation)
    
    if '翻译' in translation and '：“' in translation and '”' in translation:
        translation = translation.split('：“')[-1].split('”')[0]
        return True, translation_postprocess(translation)
    
    if '翻译' in translation and '："' in translation and '"' in translation:
        translation = translation.split('："')[-1].split('"')[0]
        return True, translation_postprocess(translation)

    if '翻译' in translation and ':"' in translation and '"' in translation:
        translation = translation.split('："')[-1].split('"')[0]
        return True, translation_postprocess(translation)
    
    # 中文翻译通常比英文原文短，不需要严格限制长度
    # 只拦截明显过长(超过原文3倍)的情况，避免误杀正常翻译
    if len(text) <= 10:
        if len(translation) > 30:
            return False, f'Translation is too long. Just give me the short Chinese translation directly, no explanation.'
    elif len(translation) > len(text) * 3:
        return False, f'Translation is too long ({len(translation)} chars vs original {len(text)} chars). Just translate directly.'
    
    forbidden = ['这句', '\n', '简体中文', '中文', 'translate', 'Translate', 'translation', 'Translation']
    translation = translation.strip()
    for word in forbidden:
        if word in translation:
            return False, f"Don't include `{word}` in the translation. Only translate the following sentence and give me the result."
    
    # 最后一关：复读检测
    if _is_repetitive(translation, threshold=3):
        return False, '翻译内容出现大量重复，请重新翻译，只输出正常的一句话翻译结果。'
    
    return True, translation_postprocess(translation)
# def split_sentences(translation, punctuations=['。', '？', '！', '\n', '”', '"']):
#     def is_punctuation(char):
#         return char in punctuations
    
#     output_data = []
#     for item in translation:
#         start = item['start'] 
#         text = item['text']
#         speaker = item['speaker']
#         translation = item['translation']
#         sentence_start = 0
#         duration_per_char = (item['end'] - item['start']) / len(translation)
#         for i, char in enumerate(translation):
#             # If the character is a punctuation, split the sentence
#             if not is_punctuation(char) and i != len(translation) - 1:
#                 continue
#             if i - sentence_start < 5 and i != len(translation) - 1:
#                 continue
#             if i < len(translation) - 1 and is_punctuation(translation[i+1]):
#                 continue
#             sentence = translation[sentence_start:i+1]
#             sentence_end = start + duration_per_char * len(sentence)

#             # Append the new item
#             output_data.append({
#                 "start": round(start, 3),
#                 "end": round(sentence_end, 3),
#                 "text": text,
#                 "speaker": speaker,
#                 "translation": sentence
#             })

#             # Update the start for the next sentence
#             start = sentence_end
#             sentence_start = i + 1
#     return output_data


def split_text_into_sentences(para):
    para = re.sub('([。！？\?])([^，。！？\?”’》])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^，。！？\?”’》])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^，。！？\?”’》])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?”’》])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return para.split("\n")

def split_sentences(translation):
    output_data = []
    for item in translation:
        start = item['start']
        text = item['text']
        speaker = item['speaker']
        translation_text = item['translation']
        sentences = split_text_into_sentences(translation_text)
        duration_per_char = (item['end'] - item['start']
                             ) / len(translation_text)
        sentence_start = 0
        for sentence in sentences:
            sentence_end = start + duration_per_char * len(sentence)

            # Append the new item
            output_data.append({
                "start": round(start, 3),
                "end": round(sentence_end, 3),
                "text": text,
                "speaker": speaker,
                "translation": sentence
            })

            # Update the start for the next sentence
            start = sentence_end
            sentence_start += len(sentence)
    return output_data
    
def _translate(summary, transcript, target_language='简体中文'):
    client = get_translation_client()
    info = f'This is a video called "{summary["title"]}". {summary["summary"]}.'
    full_translation = []
    # 选择正确的模型
    current_model = OLLAMA_MODEL if TRANSLATION_BACKEND == 'ollama' else model_name
    
    # 初始化术语管理器
    terminology = get_terminology_manager()
    logger.info(f"术语词典已加载，共 {len(terminology.get_terms())} 个术语")
    
    fixed_message = [
        {'role': 'system', 'content': f'你是一位天才翻译家和资深配音导演。正在处理视频《{summary["title"]}》。摘要：{summary["summary"]}\n\n你的任务是将以下字幕片段翻译成地道的{target_language}，用于后期配音。\n\n**金律：**\n1. **绝对不要“翻译腔”**：不要直译，要像中国人在说话。使用口语化表达。\n2. **信达雅**：保持原意，但要转换成目标语言中对应的惯用语、成语或流行梗。\n3. **配音适配**：控制语速和字数，确保配音时自然顺滑。\n4. **术语统一**：专业名词要准确，不要画蛇添足（如：agent -> 智能体）。\n5. **简洁有力**：只返回翻译后的文本，严禁带任何多余说明或转义符号。'},
    ]
    
    history = []
    for i, line in enumerate(transcript):
        text = line['text']
        # history = ''.join(full_translation[:-10])
        
        retry_message = 'Only translate the quoted sentence and give me the final translation.'
        for retry in range(30):
            messages = fixed_message + \
                history[-30:] + [{'role': 'user',
                                  'content': f'使用地道的中文Translate:"{text}"'}]
            
            try:
                response = client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    timeout=240,
                    extra_body=extra_body
                )
                translation = response.choices[0].message.content.replace('\n', '')
                
                # 应用术语一致性替换
                translation_before = translation
                translation = terminology.apply_to_translation(translation)
                if translation != translation_before:
                    logger.debug(f"术语替换: '{translation_before}' -> '{translation}'")
                
                logger.info(f'原文：{text}')
                logger.info(f'译文：{translation}')
                success, translation = valid_translation(text, translation)
                if not success:
                    retry_message += translation
                    raise Exception('Invalid translation')
                break
            except Exception as e:
                logger.error(e)
                if e == 'Internal Server Error':
                    client = get_openai_client()
                # logger.warning('翻译失败')
                time.sleep(1)
        full_translation.append(translation)
        
        # 每10句显示一次进度
        if (i + 1) % 10 == 0:
            logger.info(f"翻译进度: {i + 1}/{len(transcript)}")
        history.append({'role': 'user', 'content': f'Translate:"{text}"'})
        history.append({'role': 'assistant', 'content': f'翻译：“{translation}”'})
        time.sleep(0.1)

    return full_translation

def translate(folder, target_language='简体中文'):
    if os.path.exists(os.path.join(folder, 'translation.json')):
        logger.info(f'Translation already exists in {folder}')
        return True
    
    info_path = os.path.join(folder, 'download.info.json')
    if not os.path.exists(info_path):
        return False
    # info_path = r'videos\Lex Clips\20231222 Jeff Bezos on fear of death ｜ Lex Fridman Podcast Clips\download.info.json'
    with open(info_path, 'r', encoding='utf-8') as f:
        info = json.load(f)
    info = get_necessary_info(info)
    
    transcript_path = os.path.join(folder, 'transcript.json')
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = json.load(f)
    
    summary_path = os.path.join(folder, 'summary.json')
    if os.path.exists(summary_path):
        summary = json.load(open(summary_path, 'r', encoding='utf-8'))
    else:
        summary = summarize(info, transcript, target_language)
        if summary is None:
            logger.error(f'Failed to summarize {folder}')
            return False
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    translation_path = os.path.join(folder, 'translation.json')
    translation = _translate(summary, transcript, target_language)
    for i, line in enumerate(transcript):
        line['translation'] = translation[i]
    transcript = split_sentences(transcript)
    with open(translation_path, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)
    return True

def translate_all_transcript_under_folder(folder, target_language):
    for root, dirs, files in os.walk(folder):
        if 'transcript.json' in files and 'translation.json' not in files:
            translate(root, target_language)
    return f'Translated all videos under {folder}'

if __name__ == '__main__':
    translate_all_transcript_under_folder(
        r'videos\TED-Ed\20240227 Can you solve the magical maze riddle - Alex Rosenthal', '简体中文')
