import os
import time
from pathlib import Path
from typing import List, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

class BookTranslator:
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, retry_delay: int = 5):
        """初始化翻译器"""
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.context_window = []  # 用于存储翻译上下文
        
    def _get_translation_prompt(self, text: str, target_lang: str, context: Optional[List[Tuple[str, str]]] = None) -> List[dict]:
        """生成带有上下文的翻译提示"""
        messages = [
            {
                "role": "system",
                "content": f"""你是一个专业的文学翻译专家。请将文本翻译成{target_lang}，注意：
1. 保持原文的文学风格和语气
2. 确保译文的流畅性和可读性
3. 准确传达原文的意思和情感
4. 保持段落格式和标点符号的合理使用
5. 对于书籍特有的标记（如页码标记）保持原样
6. 注意上下文的连贯性"""
            }
        ]
        
        # 添加上下文（如果有）
        if context:
            context_str = "\n上下文参考：\n"
            for orig, trans in context:
                context_str += f"原文：{orig}\n译文：{trans}\n"
            messages.append({"role": "user", "content": context_str})
        
        messages.append({"role": "user", "content": text})
        return messages

    def translate_text(self, text: str, target_lang: str = "zh-CN") -> str:
        """使用OpenAI API翻译文本，带有重试机制"""
        if not text.strip():
            return ""
            
        for attempt in range(self.max_retries):
            try:
                # 获取最近的翻译上下文
                context = self.context_window[-2:] if self.context_window else None
                
                # 创建带有上下文的提示
                messages = self._get_translation_prompt(text, target_lang, context)
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.3,
                )
                
                translated_text = response.choices[0].message.content.strip()
                
                # 更新上下文窗口
                self.context_window.append((text, translated_text))
                if len(self.context_window) > 5:  # 保持上下文窗口大小
                    self.context_window.pop(0)
                    
                return translated_text
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"翻译出错 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"翻译失败: {e}")
                    return text
            
    def translate_chunks(self, chunks: List[str], target_lang: str = "zh-CN") -> List[str]:
        """翻译文本块列表，保持页面标记和段落格式"""
        translated_chunks = []
        self.context_window = []  # 重置上下文窗口
        
        for chunk in tqdm(chunks, desc="翻译进度"):
            # 检查是否是页面标记
            if chunk.startswith("="):
                translated_chunks.append(chunk)  # 保持页面标记不变
                continue
                
            translated_text = self.translate_text(chunk, target_lang)
            translated_chunks.append(translated_text)
            
        return translated_chunks

    def save_translation(self, translated_chunks: List[str], output_path: str):
        """保存翻译结果，优化格式"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(translated_chunks):
                # 写入当前块
                f.write(chunk)
                
                # 根据内容类型添加适当的分隔符
                if i < len(translated_chunks) - 1:  # 不是最后一个块
                    if chunk.startswith("="):  # 页面标记后添加一个空行
                        f.write("\n\n")
                    elif not translated_chunks[i + 1].startswith("="):  # 普通段落之间添加一个空行
                        f.write("\n\n")
                    else:  # 段落后面是页面标记，只需要一个换行
                        f.write("\n")