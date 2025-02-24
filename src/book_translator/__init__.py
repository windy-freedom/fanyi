"""
Book Translator
==============

一个使用LLM（如GPT-3.5）翻译电子书的工具，支持epub、pdf和txt格式。
"""

__version__ = "0.1.0"

from .translator import BookTranslator
from .utils.text_extractor import TextExtractor

__all__ = ["BookTranslator", "TextExtractor"]