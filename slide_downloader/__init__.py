"""
SlideShare 簡報下載工具套件

這個套件提供了從 SlideShare URL 下載簡報圖片的功能。
"""

__version__ = "1.0.0"
__author__ = "SlideShare Downloader Team"

from .cli import main
from .downloader import SlideDownloader
from .validator import ArgumentValidator
from .processor import ResultProcessor

__all__ = [
    "main",
    "SlideDownloader", 
    "ArgumentValidator",
    "ResultProcessor"
]
