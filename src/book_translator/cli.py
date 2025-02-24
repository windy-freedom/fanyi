import argparse
import sys
from pathlib import Path
from typing import List
from book_translator.translator import BookTranslator
from book_translator.utils.text_extractor import TextExtractor

def display_text_preview(chunks: List[str], max_chunks: int = 3):
    """显示文本预览"""
    print("\n提取的文本预览:")
    print("-" * 50)
    for i, chunk in enumerate(chunks[:max_chunks]):
        preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
        print(f"块 {i + 1}: {preview}")
    if len(chunks) > max_chunks:
        print(f"... 还有 {len(chunks) - max_chunks} 个文本块")
    print("-" * 50 + "\n")

def confirm_continue(prompt: str = "是否继续？[y/N] ") -> bool:
    """请求用户确认"""
    response = input(prompt).lower()
    return response in ['y', 'yes']

def main():
    parser = argparse.ArgumentParser(description='电子书翻译工具')
    parser.add_argument('input_file', help='输入文件路径 (支持 .epub, .pdf, .txt)')
    parser.add_argument('output_file', help='输出文件路径')
    parser.add_argument('--target-lang', default='zh-CN', help='目标语言 (默认: zh-CN)')
    parser.add_argument('--api-key', help='OpenAI API密钥 (可选，也可通过环境变量OPENAI_API_KEY设置)')
    parser.add_argument('--start-page', type=int, help='起始页码 (仅PDF格式适用)')
    parser.add_argument('--end-page', type=int, help='结束页码 (仅PDF格式适用)')
    parser.add_argument('--max-retries', type=int, default=3, help='翻译失败时的最大重试次数 (默认: 3)')
    parser.add_argument('--retry-delay', type=int, default=5, help='重试之间的等待时间(秒) (默认: 5)')
    parser.add_argument('--no-preview', action='store_true', help='跳过文本预览')
    parser.add_argument('--no-confirm', action='store_true', help='跳过确认步骤')
    parser.add_argument('--batch-size', type=int, default=1000, help='翻译批次大小(字符数) (默认: 1000)')
    
    args = parser.parse_args()
    
    try:
        # 检查输入文件
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"错误: 输入文件不存在: {args.input_file}")
            return 1
            
        # 检查输出目录
        output_path = Path(args.output_file)
        if output_path.exists() and not args.no_confirm:
            if not confirm_continue(f"输出文件 {args.output_file} 已存在，是否覆盖？[y/N] "):
                print("操作已取消")
                return 0
        
        # 提取文本
        print(f"正在从 {args.input_file} 提取文本...")
        if args.start_page or args.end_page:
            print(f"处理页面范围: {args.start_page or 1} - {args.end_page or '末页'}")
            
        chunks = TextExtractor.extract_text(
            args.input_file,
            start_page=args.start_page,
            end_page=args.end_page
        )
        
        if not chunks:
            print("错误: 未能提取到任何文本")
            return 1
            
        print(f"成功提取 {len(chunks)} 个文本块")
        
        # 显示文本预览
        if not args.no_preview:
            display_text_preview(chunks)
            if not args.no_confirm and not confirm_continue():
                print("操作已取消")
                return 0
        
        # 初始化翻译器
        translator = BookTranslator(
            api_key=args.api_key,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay
        )
        
        # 翻译文本
        print(f"正在翻译到 {args.target_lang}...")
        translated_chunks = translator.translate_chunks(chunks, args.target_lang)
        
        # 保存翻译结果
        print(f"正在保存翻译结果到 {args.output_file}...")
        translator.save_translation(translated_chunks, args.output_file)
        
        print("\n翻译完成！")
        print(f"输出文件: {args.output_file}")
        
        # 显示翻译结果预览
        if not args.no_preview:
            print("\n翻译结果预览:")
            print("-" * 50)
            with open(args.output_file, 'r', encoding='utf-8') as f:
                preview = f.read(500)
                print(preview + ("..." if len(preview) == 500 else ""))
            print("-" * 50)
        
    except KeyboardInterrupt:
        print("\n操作已被用户中断")
        return 130
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1
        
    return 0

if __name__ == '__main__':
    exit(main())