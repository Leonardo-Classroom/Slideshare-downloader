#!/usr/bin/env python3
"""
SlideShare 爬蟲配置檔案
包含所有可調整的設定參數
"""

# 爬取設定
DEFAULT_DOWNLOAD_NUM = 100  # 預設爬取數量
DEFAULT_HEADLESS = False    # 預設是否使用無頭模式
DEFAULT_DELAY = 3          # 點擊 Show More 後的等待時間（秒）

# 瀏覽器設定
BROWSER_SETTINGS = {
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "timeout": 10,  # WebDriverWait 超時時間
    "page_load_timeout": 30,  # 頁面載入超時時間
}

# Chrome 選項
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",  # 不載入圖片以提高速度
    "--disable-javascript",  # 如果不需要 JS 可以禁用
]

# CSS 選擇器
SELECTORS = {
    "section": "section",
    "section_title": "h2",
    "slideshow_card": ".SlideshowCard_root__pD8t4",
    "slideshow_link": "a.SlideshowCardLink_root__p8KI7",
    "slideshow_title": ".slideshow-title",
    "show_more_button": "button.ShowMoreButton_root__oAN_0",
    "slideshow_author": ".slideshow-author",
    "slideshow_stats": ".slideshow-stats",
}

# 檔案設定
FILE_SETTINGS = {
    "csv_encoding": "utf-8-sig",  # CSV 檔案編碼
    "csv_delimiter": ",",         # CSV 分隔符
    "output_directory": "./output_url",  # URL 輸出目錄
}

# 重試設定
RETRY_SETTINGS = {
    "max_retries": 3,           # 最大重試次數
    "retry_delay": 5,           # 重試間隔（秒）
    "element_wait_time": 10,    # 等待元素出現的時間
}

# 日誌設定
LOGGING_SETTINGS = {
    "level": "INFO",            # 日誌級別
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "slideshare_scraper.log",
}

# 網站相關設定
SITE_SETTINGS = {
    "base_url": "https://www.slideshare.net/",
    "featured_pattern": r"Featured in (.+)",  # 用於提取類別名稱的正規表達式
    "max_scroll_attempts": 5,   # 最大滾動嘗試次數
}

# 資料驗證設定
VALIDATION_SETTINGS = {
    "min_title_length": 5,      # 標題最小長度
    "max_title_length": 200,    # 標題最大長度
    "required_url_parts": ["slideshare.net"],  # URL 必須包含的部分
}

# 效能設定
PERFORMANCE_SETTINGS = {
    "batch_size": 20,           # 批次處理大小
    "memory_limit_mb": 512,     # 記憶體限制（MB）
    "max_concurrent_requests": 1,  # 最大並發請求數
}

# 開發/除錯設定
DEBUG_SETTINGS = {
    "save_screenshots": False,   # 是否儲存截圖
    "screenshot_dir": "./screenshots",
    "verbose_logging": False,    # 詳細日誌
    "save_page_source": False,   # 是否儲存頁面原始碼
}

# 預設 URL 列表
DEFAULT_URLS = [
    "https://www.slideshare.net/",
    # 可以添加其他預設的 SlideShare URL
]

# 輸出格式設定
OUTPUT_FORMATS = {
    "csv": {
        "enabled": True,
        "fields": ["編號", "標題", "連結"],
    },
    "json": {
        "enabled": False,
        "indent": 2,
    },
    "excel": {
        "enabled": False,
        "sheet_name": "SlideShare_Data",
    }
}

# 代理設定（如果需要）
PROXY_SETTINGS = {
    "enabled": False,
    "http_proxy": None,
    "https_proxy": None,
    "proxy_auth": None,
}

# 錯誤處理設定
ERROR_HANDLING = {
    "continue_on_error": True,   # 遇到錯誤時是否繼續
    "save_error_log": True,      # 是否儲存錯誤日誌
    "error_log_file": "errors.log",
    "max_consecutive_errors": 5,  # 最大連續錯誤數
}

# 資料清理設定
DATA_CLEANING = {
    "remove_duplicates": True,   # 移除重複資料
    "trim_whitespace": True,     # 移除前後空白
    "normalize_urls": True,      # 標準化 URL
    "validate_urls": True,       # 驗證 URL 有效性
}


def get_config():
    """
    取得完整的配置字典
    
    Returns:
        dict: 包含所有配置的字典
    """
    return {
        "download": {
            "default_num": DEFAULT_DOWNLOAD_NUM,
            "default_headless": DEFAULT_HEADLESS,
            "default_delay": DEFAULT_DELAY,
        },
        "browser": BROWSER_SETTINGS,
        "chrome_options": CHROME_OPTIONS,
        "selectors": SELECTORS,
        "files": FILE_SETTINGS,
        "retry": RETRY_SETTINGS,
        "logging": LOGGING_SETTINGS,
        "site": SITE_SETTINGS,
        "validation": VALIDATION_SETTINGS,
        "performance": PERFORMANCE_SETTINGS,
        "debug": DEBUG_SETTINGS,
        "urls": DEFAULT_URLS,
        "output": OUTPUT_FORMATS,
        "proxy": PROXY_SETTINGS,
        "error": ERROR_HANDLING,
        "cleaning": DATA_CLEANING,
    }


def update_config(**kwargs):
    """
    更新配置設定
    
    Args:
        **kwargs: 要更新的配置項目
    """
    config = get_config()
    
    for key, value in kwargs.items():
        if key in config:
            if isinstance(config[key], dict) and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
    
    return config


# 環境特定配置
ENVIRONMENT_CONFIGS = {
    "development": {
        "debug": {"verbose_logging": True, "save_screenshots": True},
        "browser": {"timeout": 30},
        "download": {"default_num": 10},
    },
    "production": {
        "debug": {"verbose_logging": False, "save_screenshots": False},
        "browser": {"timeout": 10},
        "download": {"default_headless": True},
    },
    "testing": {
        "debug": {"verbose_logging": True},
        "download": {"default_num": 5},
        "browser": {"timeout": 5},
    }
}


def get_environment_config(env="development"):
    """
    取得特定環境的配置
    
    Args:
        env: 環境名稱 (development, production, testing)
        
    Returns:
        dict: 環境特定的配置
    """
    base_config = get_config()
    env_config = ENVIRONMENT_CONFIGS.get(env, {})
    
    # 合併配置
    for section, settings in env_config.items():
        if section in base_config:
            base_config[section].update(settings)
    
    return base_config
