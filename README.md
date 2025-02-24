# Book Translator

一个使用LLM（如GPT-3.5）翻译电子书的Python工具，支持epub、pdf和txt格式。

## 安装

```bash
# 克隆仓库
git clone [repository-url]
cd book-translator

# 安装依赖
pip install -e .
```

## 使用方法

### 1. 设置OpenAI API密钥

你可以通过以下两种方式之一设置API密钥：

1. 环境变量：
```bash
export OPENAI_API_KEY='你的API密钥'
```

2. 创建.env文件：
```
OPENAI_API_KEY=你的API密钥
```

### 2. 使用命令行工具

```bash
# 基本用法
translate-book input.epub output.txt

# 指定目标语言（默认为中文）
translate-book input.pdf output.txt --target-lang zh-CN

# 直接提供API密钥
translate-book input.txt output.txt --api-key 你的API密钥
```

### 3. 在Python代码中使用

```python
from book_translator import BookTranslator, TextExtractor

# 提取文本
chunks = TextExtractor.extract_text("input.epub")

# 初始化翻译器
translator = BookTranslator(api_key="你的API密钥")  # 或从环境变量读取

# 翻译文本
translated_chunks = translator.translate_chunks(chunks, target_lang="zh-CN")

# 保存结果
translator.save_translation("\n\n".join(translated_chunks), "output.txt")
```

## 支持的文件格式

- EPUB (.epub)
- PDF (.pdf)
- 文本文件 (.txt)

## 注意事项

1. 确保你有足够的OpenAI API额度
2. 大型文件的翻译可能需要较长时间
3. 翻译结果的质量取决于LLM模型的性能

## License

MIT