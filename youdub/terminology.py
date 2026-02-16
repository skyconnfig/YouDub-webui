# -*- coding: utf-8 -*-
"""
术语一致性管理模块
确保专业术语在翻译中保持一致
"""
import json
import os
import re
from pathlib import Path
from loguru import logger

# 默认术语词典 - AI/科技领域常用术语
DEFAULT_TERMINOLOGY = {
    # AI/Machine Learning
    "AI": "AI",
    "Artificial Intelligence": "人工智能",
    "Machine Learning": "机器学习",
    "Deep Learning": "深度学习",
    "Neural Network": "神经网络",
    "Transformer": "Transformer",  # 保持英文
    "LLM": "大语言模型",
    "Large Language Model": "大语言模型",
    "GPT": "GPT",
    "ChatGPT": "ChatGPT",
    "API": "API",
    "GPU": "GPU",
    "CPU": "CPU",
    "RAM": "内存",
    "SSD": "固态硬盘",
    "Machine": "机器",
    "Algorithm": "算法",
    "Model": "模型",
    "Dataset": "数据集",
    "Training": "训练",
    "Inference": "推理",
    "Fine-tuning": "微调",
    "Prompt": "提示词",
    "Token": "Token",
    "Embedding": "嵌入",
    "Vector": "向量",
    "Clustering": "聚类",
    "Classification": "分类",
    "Regression": "回归",
    "Overfitting": "过拟合",
    "Underfitting": "欠拟合",
    "Gradient": "梯度",
    "Backpropagation": "反向传播",
    "Activation Function": "激活函数",
    "Loss Function": "损失函数",
    "Optimizer": "优化器",
    "Learning Rate": "学习率",
    "Batch": "批次",
    "Epoch": "轮次",
    "Dropout": "随机失活",
    "Regularization": "正则化",
    "CNN": "CNN",
    "RNN": "RNN",
    "LSTM": "LSTM",
    "GAN": "生成对抗网络",
    "NLP": "自然语言处理",
    "Computer Vision": "计算机视觉",
    "Reinforcement Learning": "强化学习",
    "Supervised Learning": "监督学习",
    "Unsupervised Learning": "无监督学习",
    "Python": "Python",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "Code": "代码",
    "Programming": "编程",
    "Framework": "框架",
    "Library": "库",
    "Function": "函数",
    "Variable": "变量",
    "Class": "类",
    "Object": "对象",
    "Method": "方法",
    "Interface": "接口",
    "Database": "数据库",
    "Server": "服务器",
    "Client": "客户端",
    "Frontend": "前端",
    "Backend": "后端",
    "Full-stack": "全栈",
    "DevOps": "DevOps",
    "CI/CD": "CI/CD",
    "Docker": "Docker",
    "Kubernetes": "Kubernetes",
    "Cloud": "云",
    "AWS": "AWS",
    "Azure": "Azure",
    "GCP": "谷歌云",
    "Linux": "Linux",
    "Windows": "Windows",
    "macOS": "macOS",
    "Git": "Git",
    "GitHub": "GitHub",
    "Open Source": "开源",
    "Repository": "仓库",
    "Branch": "分支",
    "Commit": "提交",
    "Pull Request": "拉取请求",
    "Merge": "合并",
    "Bug": "Bug",
    "Debug": "调试",
    "Test": "测试",
    "Deploy": "部署",
    "Production": "生产环境",
    "Development": "开发环境",
    "Staging": "预发布环境",
    "Version": "版本",
    "Release": "发布",
    "Update": "更新",
    "Install": "安装",
    "Configure": "配置",
    "Setup": "设置",
    "Documentation": "文档",
    "Tutorial": "教程",
    "Demo": "演示",
    "Example": "示例",
    "Best Practice": "最佳实践",
    "Pattern": "模式",
    "Architecture": "架构",
    "Design": "设计",
    "Implementation": "实现",
    "Refactoring": "重构",
    "Optimization": "优化",
    "Performance": "性能",
    "Security": "安全",
    "Scalability": "可扩展性",
    "Reliability": "可靠性",
    "Maintainability": "可维护性",
    "Usability": "可用性",
    "Accessibility": "无障碍",
    "Responsive": "响应式",
    "Mobile": "移动端",
    "Desktop": "桌面端",
    "Web": "Web",
    "App": "应用",
    "Application": "应用",
    "Software": "软件",
    "Hardware": "硬件",
    "Device": "设备",
    "User": "用户",
    "Admin": "管理员",
    "Authentication": "认证",
    "Authorization": "授权",
    "Encryption": "加密",
    "Decryption": "解密",
    "Hash": "哈希",
    "Cookie": "Cookie",
    "Session": "会话",
    "Token": "令牌",
    "JWT": "JWT",
    "OAuth": "OAuth",
    "SSO": "单点登录",
    "SQL": "SQL",
    "NoSQL": "NoSQL",
    "JSON": "JSON",
    "XML": "XML",
    "HTML": "HTML",
    "CSS": "CSS",
    "HTTP": "HTTP",
    "HTTPS": "HTTPS",
    "TCP": "TCP",
    "IP": "IP",
    "DNS": "DNS",
    "URL": "URL",
    "URI": "URI",
    "REST": "REST",
    "GraphQL": "GraphQL",
    "gRPC": "gRPC",
    "WebSocket": "WebSocket",
    "AJAX": "AJAX",
    "SDK": "SDK",
    "IDE": "IDE",
    "CLI": "命令行",
    "GUI": "图形界面",
    "UI": "UI",
    "UX": "UX",
    "SaaS": "SaaS",
    "PaaS": "PaaS",
    "IaaS": "IaaS",
    "FaaS": "FaaS",
    "Microservices": "微服务",
    "Monolith": "单体架构",
    "Container": "容器",
    "Virtual Machine": "虚拟机",
    "Hypervisor": "虚拟化平台",
    "Kernel": "内核",
    "Process": "进程",
    "Thread": "线程",
    "Memory": "内存",
    "Cache": "缓存",
    "Buffer": "缓冲区",
    "Stack": "栈",
    "Heap": "堆",
    "Pointer": "指针",
    "Reference": "引用",
    "Value": "值",
    "Type": "类型",
    "String": "字符串",
    "Integer": "整数",
    "Float": "浮点数",
    "Boolean": "布尔值",
    "Array": "数组",
    "List": "列表",
    "Dictionary": "字典",
    "Map": "映射",
    "Set": "集合",
    "Tuple": "元组",
    "Queue": "队列",
    "Stack": "栈",
    "Tree": "树",
    "Graph": "图",
    "Node": "节点",
    "Edge": "边",
    "Vertex": "顶点",
    "Path": "路径",
    "Cycle": "循环",
    "Loop": "循环",
    "Recursion": "递归",
    "Iteration": "迭代",
    "Callback": "回调",
    "Promise": "Promise",
    "Async": "异步",
    "Await": "等待",
    "Sync": "同步",
    "Concurrent": "并发",
    "Parallel": "并行",
    "Race Condition": "竞态条件",
    "Deadlock": "死锁",
    "Starvation": "饥饿",
    "Mutex": "互斥锁",
    "Semaphore": "信号量",
    "Lock": "锁",
    "Monitor": "监视器",
    "Condition Variable": "条件变量",
    "Barrier": "屏障",
    "Latch": "门闩",
    "Future": "Future",
    "CompletableFuture": "CompletableFuture",
    "Observable": "Observable",
    "Observer": "Observer",
    "Subject": "Subject",
    "Stream": "流",
    "Pipeline": "管道",
    "Filter": "过滤器",
    "Map": "映射",
    "Reduce": "归约",
    "Fold": "折叠",
    "FlatMap": "展平映射",
    "Zip": "压缩",
    "Merge": "合并",
    "Split": "分割",
    "Join": "连接",
    "Concat": "连接",
    "Slice": "切片",
    "Chunk": "分块",
    "Buffer": "缓冲",
    "Debounce": "防抖",
    "Throttle": "节流",
    "Sample": "采样",
    "Distinct": "去重",
    "GroupBy": "分组",
    "Partition": "分区",
    "Sort": "排序",
    "Reverse": "反转",
    "Shuffle": "随机排序",
    "Random": "随机",
    "Seed": "种子",
    "Entropy": "熵",
    "Probability": "概率",
    "Statistics": "统计",
    "Mean": "平均值",
    "Median": "中位数",
    "Mode": "众数",
    "Standard Deviation": "标准差",
    "Variance": "方差",
    "Covariance": "协方差",
    "Correlation": "相关性",
    "Regression": "回归",
    "Distribution": "分布",
    "Normal Distribution": "正态分布",
    "Uniform Distribution": "均匀分布",
    "Binomial Distribution": "二项分布",
    "Poisson Distribution": "泊松分布",
    "Exponential Distribution": "指数分布",
    "Beta Distribution": "贝塔分布",
    "Gamma Distribution": "伽马分布",
    "Chi-Square Distribution": "卡方分布",
    "T-Distribution": "t分布",
    "F-Distribution": "F分布",
    "Hypothesis Testing": "假设检验",
    "Null Hypothesis": "零假设",
    "Alternative Hypothesis": "备择假设",
    "P-Value": "P值",
    "Significance Level": "显著性水平",
    "Confidence Interval": "置信区间",
    "Type I Error": "第一类错误",
    "Type II Error": "第二类错误",
    "Power": "功效",
    "Effect Size": "效应量",
    "Sample Size": "样本量",
    "Population": "总体",
    "Sample": "样本",
    "Parameter": "参数",
    "Statistic": "统计量",
    "Estimator": "估计量",
    "Bias": "偏差",
    "Variance": "方差",
    "MSE": "均方误差",
    "RMSE": "均方根误差",
    "MAE": "平均绝对误差",
    "R-Squared": "R方",
    "Adjusted R-Squared": "调整R方",
    "AIC": "赤池信息准则",
    "BIC": "贝叶斯信息准则",
    "Cross-Validation": "交叉验证",
    "Train-Test Split": "训练测试划分",
    "Validation Set": "验证集",
    "Test Set": "测试集",
    "Training Set": "训练集",
    "Feature": "特征",
    "Label": "标签",
    "Target": "目标",
    "Input": "输入",
    "Output": "输出",
    "Variable": "变量",
    "Constant": "常量",
    "Coefficient": "系数",
    "Weight": "权重",
    "Bias": "偏置",
    "Intercept": "截距",
    "Slope": "斜率",
    "Residual": "残差",
    "Error": "误差",
    "Noise": "噪声",
    "Signal": "信号",
    "Feature Engineering": "特征工程",
    "Feature Selection": "特征选择",
    "Feature Extraction": "特征提取",
    "Dimensionality Reduction": "降维",
    "PCA": "主成分分析",
    "LDA": "线性判别分析",
    "t-SNE": "t-SNE",
    "UMAP": "UMAP",
    "Clustering": "聚类",
    "K-Means": "K均值",
    "Hierarchical Clustering": "层次聚类",
    "DBSCAN": "DBSCAN",
    "Gaussian Mixture Model": "高斯混合模型",
    "Anomaly Detection": "异常检测",
    "Outlier": "异常值",
    "Novelty Detection": "新颖性检测",
    "One-Class SVM": "单类SVM",
    "Isolation Forest": "孤立森林",
    "Local Outlier Factor": "局部异常因子",
    "Time Series": "时间序列",
    "Forecasting": "预测",
    "Trend": "趋势",
    "Seasonality": "季节性",
    "Cyclical": "周期性",
    "Stationary": "平稳性",
    "Autocorrelation": "自相关",
    "Partial Autocorrelation": "偏自相关",
    "AR": "自回归",
    "MA": "移动平均",
    "ARMA": "自回归移动平均",
    "ARIMA": "差分自回归移动平均",
    "SARIMA": "季节性差分自回归移动平均",
    "VAR": "向量自回归",
    "GARCH": "广义自回归条件异方差",
    "Exponential Smoothing": "指数平滑",
    "Holt-Winters": "霍尔特-温特斯",
    "Prophet": "Prophet",
    "Recommendation System": "推荐系统",
    "Collaborative Filtering": "协同过滤",
    "Content-Based Filtering": "基于内容的过滤",
    "Matrix Factorization": "矩阵分解",
    "Singular Value Decomposition": "奇异值分解",
    "Alternating Least Squares": "交替最小二乘",
    "Implicit Feedback": "隐式反馈",
    "Explicit Feedback": "显式反馈",
    "Cold Start": "冷启动",
    "Serendipity": "意外发现",
    "Diversity": "多样性",
    "Coverage": "覆盖率",
    "Novelty": "新颖性",
    "Personalization": "个性化",
    "Context-Aware": "上下文感知",
    "Sequence-Aware": "序列感知",
    "Session-Based": "基于会话的",
    "Real-Time": "实时",
    "Batch": "批处理",
    "Online Learning": "在线学习",
    "Incremental Learning": "增量学习",
    "Transfer Learning": "迁移学习",
    "Domain Adaptation": "域适应",
    "Few-Shot Learning": "小样本学习",
    "Zero-Shot Learning": "零样本学习",
    "Meta-Learning": "元学习",
    "Multi-Task Learning": "多任务学习",
    "Multi-Modal Learning": "多模态学习",
    "Self-Supervised Learning": "自监督学习",
    "Contrastive Learning": "对比学习",
    "Generative Model": "生成模型",
    "Discriminative Model": "判别模型",
    "Variational Autoencoder": "变分自编码器",
    "VAE": "VAE",
    "Diffusion Model": "扩散模型",
    "Stable Diffusion": "Stable Diffusion",
    "DALL-E": "DALL-E",
    "Midjourney": "Midjourney",
    "GPT-3": "GPT-3",
    "GPT-4": "GPT-4",
    "Claude": "Claude",
    "Llama": "Llama",
    "BERT": "BERT",
    "RoBERTa": "RoBERTa",
    "T5": "T5",
    "BART": "BART",
    "Electra": "Electra",
    "DeBERTa": "DeBERTa",
    "Vision Transformer": "Vision Transformer",
    "ViT": "ViT",
    "Swin Transformer": "Swin Transformer",
    "ConvNeXt": "ConvNeXt",
    "EfficientNet": "EfficientNet",
    "ResNet": "ResNet",
    "DenseNet": "DenseNet",
    "MobileNet": "MobileNet",
    "YOLO": "YOLO",
    "Faster R-CNN": "Faster R-CNN",
    "Mask R-CNN": "Mask R-CNN",
    "U-Net": "U-Net",
    "SegNet": "SegNet",
    "DeepLab": "DeepLab",
    "PSPNet": "PSPNet",
    "HRNet": "HRNet",
    "OCR": "光学字符识别",
    "Object Detection": "目标检测",
    "Image Segmentation": "图像分割",
    "Instance Segmentation": "实例分割",
    "Semantic Segmentation": "语义分割",
    "Panoptic Segmentation": "全景分割",
    "Keypoint Detection": "关键点检测",
    "Pose Estimation": "姿态估计",
    "Face Recognition": "人脸识别",
    "Face Detection": "人脸检测",
    "Image Classification": "图像分类",
    "Action Recognition": "动作识别",
    "Video Classification": "视频分类",
    "Video Captioning": "视频描述",
    "Visual Question Answering": "视觉问答",
    "Image Captioning": "图像描述",
    "Speech Recognition": "语音识别",
    "Speech Synthesis": "语音合成",
    "Text-to-Speech": "文本转语音",
    "TTS": "TTS",
    "ASR": "自动语音识别",
    "Speaker Recognition": "说话人识别",
    "Voice Conversion": "语音转换",
    "Audio Classification": "音频分类",
    "Music Generation": "音乐生成",
    "Sound Event Detection": "声音事件检测",
    "Natural Language Understanding": "自然语言理解",
    "Natural Language Generation": "自然语言生成",
    "Text Classification": "文本分类",
    "Sentiment Analysis": "情感分析",
    "Named Entity Recognition": "命名实体识别",
    "NER": "NER",
    "Part-of-Speech Tagging": "词性标注",
    "Dependency Parsing": "依存句法分析",
    "Constituency Parsing": "成分句法分析",
    "Semantic Role Labeling": "语义角色标注",
    "Coreference Resolution": "指代消解",
    "Relation Extraction": "关系抽取",
    "Event Extraction": "事件抽取",
    "Question Answering": "问答",
    "Reading Comprehension": "阅读理解",
    "Text Summarization": "文本摘要",
    "Machine Translation": "机器翻译",
    "Dialogue System": "对话系统",
    "Chatbot": "聊天机器人",
    "Intent Recognition": "意图识别",
    "Slot Filling": "槽位填充",
    "Knowledge Graph": "知识图谱",
    "Ontology": "本体",
    "Entity Linking": "实体链接",
    "Word Sense Disambiguation": "词义消歧",
    "Semantic Similarity": "语义相似度",
    "Paraphrase Detection": "复述检测",
    "Textual Entailment": "文本蕴含",
    "Natural Language Inference": "自然语言推理",
    "NLI": "NLI",
    "RAG": "检索增强生成",
    "Retrieval-Augmented Generation": "检索增强生成",
}

class TerminologyManager:
    """术语管理器"""
    
    def __init__(self, custom_dict_path=None):
        """
        初始化术语管理器
        
        Args:
            custom_dict_path: 自定义术语词典文件路径（JSON格式）
        """
        self.terms = DEFAULT_TERMINOLOGY.copy()
        
        # 加载自定义术语
        if custom_dict_path and os.path.exists(custom_dict_path):
            try:
                with open(custom_dict_path, 'r', encoding='utf-8') as f:
                    custom_terms = json.load(f)
                    self.terms.update(custom_terms)
                    logger.info(f"加载了 {len(custom_terms)} 个自定义术语")
            except Exception as e:
                logger.warning(f"加载自定义术语失败: {e}")
        
        # 尝试从项目根目录加载术语文件
        project_root = Path(__file__).parent.parent
        terms_file = project_root / 'config' / 'terminology.json'
        if terms_file.exists():
            try:
                with open(terms_file, 'r', encoding='utf-8') as f:
                    custom_terms = json.load(f)
                    self.terms.update(custom_terms)
                    logger.info(f"从配置文件加载了 {len(custom_terms)} 个术语")
            except Exception as e:
                logger.warning(f"加载配置文件术语失败: {e}")
    
    def apply_to_translation(self, text):
        """
        对翻译文本应用术语替换
        
        策略：
        1. 先替换最长的术语（避免部分匹配）
        2. 使用单词边界确保完整匹配
        3. 保持大小写不敏感
        """
        # 按长度降序排序，优先替换长术语
        sorted_terms = sorted(self.terms.items(), key=lambda x: len(x[0]), reverse=True)
        
        for en_term, cn_term in sorted_terms:
            # 使用单词边界正则，确保完整匹配
            # 处理带空格的术语（如 "Machine Learning"）
            if ' ' in en_term:
                pattern = r'\b' + re.escape(en_term) + r'\b'
            else:
                pattern = r'\b' + re.escape(en_term) + r'\b'
            
            # 替换（保持大小写不敏感）
            text = re.sub(pattern, cn_term, text, flags=re.IGNORECASE)
        
        return text
    
    def extract_terms_from_text(self, text, min_length=3):
        """
        从文本中提取候选术语
        用于发现新的专业术语
        """
        # 提取大写字母开头的连续单词（可能是专有名词）
        candidates = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', text)
        
        # 过滤掉太短的和已经在词典中的
        candidates = [
            c for c in candidates 
            if len(c) >= min_length and c not in self.terms
        ]
        
        return list(set(candidates))  # 去重
    
    def add_term(self, en_term, cn_term):
        """添加新术语"""
        self.terms[en_term] = cn_term
        logger.info(f"添加术语: {en_term} -> {cn_term}")
    
    def get_terms(self):
        """获取所有术语"""
        return self.terms.copy()
    
    def save_to_file(self, filepath):
        """保存术语词典到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.terms, f, indent=2, ensure_ascii=False)
        logger.info(f"术语词典已保存: {filepath}")


# 便捷函数
def apply_terminology(text, custom_dict_path=None):
    """
    快速应用术语替换
    
    使用示例：
        text = "Transformer is a type of Neural Network used in Deep Learning."
        translated = apply_terminology(text)
    """
    manager = TerminologyManager(custom_dict_path)
    return manager.apply_to_translation(text)


if __name__ == '__main__':
    # 测试
    manager = TerminologyManager()
    
    test_text = """
    Machine Learning and Deep Learning are subsets of Artificial Intelligence.
    Transformer models like GPT and BERT have revolutionized NLP.
    We use GPU to train Neural Networks.
    """
    
    result = manager.apply_to_translation(test_text)
    print("原文:")
    print(test_text)
    print("\n应用术语后:")
    print(result)
    
    # 提取候选术语
    candidates = manager.extract_terms_from_text(test_text)
    print("\n候选术语:")
    print(candidates)
