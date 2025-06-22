#!/usr/bin/env python3
"""
SlideShare 爬蟲模組

這個模組提供了完整的 SlideShare 爬取功能，包括：
- 單一和並行爬取模式
- 多類別和多區塊類型支援
- 智慧重試機制
- 詳細的輸出路徑管理

主要組件：
- scraper: 核心爬蟲類別
- parallel: 並行處理功能
- utils: 工具函數
- constants: 常數定義
- cli: 命令列介面
"""

from .scraper import SlideShareScraper
from .downloader import SlideShareDownloader
from .constants import SUPPORTED_CATEGORIES, SUPPORTED_SECTIONS
from .utils import get_category_url, generate_output_path, save_scrape_info
from .parallel import execute_parallel_tasks, execute_single_task, warmup_webdriver, retry_failed_tasks
from .cli import parse_arguments, main

__version__ = "2.0.0"
__author__ = "SlideShare Scraper Team"
__email__ = "support@slideshare-scraper.com"

__all__ = [
    # 核心類別
    "SlideShareScraper",
    "SlideShareDownloader",

    # 常數
    "SUPPORTED_CATEGORIES",
    "SUPPORTED_SECTIONS",

    # 工具函數
    "get_category_url",
    "generate_output_path",
    "save_scrape_info",

    # 並行處理
    "execute_parallel_tasks",
    "execute_single_task",
    "warmup_webdriver",
    "retry_failed_tasks",

    # 命令列介面
    "parse_arguments",
    "main",
]
