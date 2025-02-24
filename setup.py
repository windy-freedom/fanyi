from setuptools import setup, find_packages

setup(
    name="book_translator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ebooklib>=0.18.0",
        "PyPDF2>=3.0.0",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
        "tqdm>=4.65.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "translate-book=book_translator.cli:main",
        ],
    },
    python_requires=">=3.8",
)