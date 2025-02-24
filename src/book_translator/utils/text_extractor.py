import os
import re
from typing import List
from pathlib import Path
import ebooklib
from ebooklib import epub
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

class TextExtractor:
    @staticmethod
    def clean_text(text: str) -> str:
        """清理和规范化文本"""
        # 替换多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        # 清理特殊字符
        text = re.sub(r'[^\S\n]+', ' ', text)
        # 规范化换行符
        text = re.sub(r'\r\n|\r', '\n', text)
        # 清理行首行尾空白
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()

    @staticmethod
    def split_into_paragraphs(text: str) -> List[str]:
        """智能分割段落"""
        # 首先按换行符分割
        lines = text.split('\n')
        paragraphs = []
        current_paragraph = []

        for line in lines:
            line = line.strip()
            if not line:  # 空行表示段落分隔
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            # 检查行是否以句号、问号或感叹号结尾，或者长度过短（可能是标题）
            elif line[-1] in '.!?。！？' or len(line) < 20:
                if current_paragraph:
                    current_paragraph.append(line)
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                else:
                    paragraphs.append(line)
            else:
                current_paragraph.append(line)

        # 处理最后一个段落
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))

        return [p for p in paragraphs if p.strip()]

    @staticmethod
    def extract_from_epub(file_path: str) -> List[str]:
        """从EPUB文件中提取文本"""
        book = epub.read_epub(file_path)
        chunks = []
        
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = TextExtractor.clean_text(soup.get_text())
            if text.strip():
                paragraphs = TextExtractor.split_into_paragraphs(text)
                chunks.extend(paragraphs)
                
        return chunks

    @staticmethod
    def extract_from_pdf(file_path: str, start_page: int = None, end_page: int = None) -> List[str]:
        """从PDF文件中提取文本，可以指定页面范围"""
        reader = PdfReader(file_path)
        chunks = []
        
        # 确定页面范围
        start = start_page - 1 if start_page else 0
        end = min(end_page or len(reader.pages), len(reader.pages))
        
        current_text_block = []
        
        for page_num in range(start, end):
            text = reader.pages[page_num].extract_text()
            text = TextExtractor.clean_text(text)
            
            if text.strip():
                # 添加页码标记（使用更明显的分隔符）
                if chunks:  # 只在不是第一页时添加分隔符
                    chunks.append("\n" + "=" * 30 + f" 第 {page_num + 1} 页 " + "=" * 30 + "\n")
                
                # 智能分割段落
                paragraphs = TextExtractor.split_into_paragraphs(text)
                
                # 处理段落
                for paragraph in paragraphs:
                    # 检查是否是新的完整句子的开始
                    if not current_text_block or paragraph[0].isupper() or paragraph[0].isdigit():
                        if current_text_block:
                            chunks.append(' '.join(current_text_block))
                            current_text_block = []
                        current_text_block.append(paragraph)
                    else:
                        # 如果不是新句子的开始，可能是被错误分割的句子部分
                        current_text_block.append(paragraph)
                
                # 在页面结束时处理剩余的文本块
                if current_text_block:
                    chunks.append(' '.join(current_text_block))
                    current_text_block = []
                
        return chunks

    @staticmethod
    def extract_from_txt(file_path: str) -> List[str]:
        """从TXT文件中提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        text = TextExtractor.clean_text(text)
        return TextExtractor.split_into_paragraphs(text)

    @staticmethod
    def extract_text(file_path: str, start_page: int = None, end_page: int = None) -> List[str]:
        """根据文件类型提取文本"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        ext = file_path.suffix.lower()
        
        if ext == '.epub':
            return TextExtractor.extract_from_epub(str(file_path))
        elif ext == '.pdf':
            return TextExtractor.extract_from_pdf(str(file_path), start_page, end_page)
        elif ext == '.txt':
            return TextExtractor.extract_from_txt(str(file_path))
        else:
            raise ValueError(f"不支持的文件格式: {ext}")