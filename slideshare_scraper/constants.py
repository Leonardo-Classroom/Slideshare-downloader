#!/usr/bin/env python3
"""
SlideShare 爬蟲常數定義

包含所有支援的類別、區塊類型和其他常數定義。
"""

# 支援的類別清單
SUPPORTED_CATEGORIES = [
    "business",
    "mobile", 
    "social-media",
    "marketing",
    "technology",
    "art-photos",
    "career",
    "design",
    "education",
    "presentations-public-speaking",
    "government-nonprofit",
    "healthcare",
    "internet",
    "law",
    "leadership-management",
    "automotive",
    "engineering",
    "software",
    "recruiting-hr",
    "retail",
    "sales",
    "services",
    "science",
    "small-business-entrepreneurship",
    "food",
    "environment",
    "economy-finance",
    "data-analytics",
    "investor-relations",
    "sports",
    "spiritual",
    "news-politics",
    "travel",
    "self-improvement",
    "real-estate",
    "entertainment-humor",
    "health-medicine",
    "devices-hardware",
    "lifestyle"
]

# 支援的區塊類型
SUPPORTED_SECTIONS = [
    "featured",
    "popular", 
    "new"
]

# 區塊類型對應的模式字串
SECTION_PATTERNS = {
    "featured": "Featured in",
    "popular": "Most popular in", 
    "new": "New in"
}

# 預設設定
DEFAULT_SETTINGS = {
    "download_num": 100,
    "window_num": 10,
    "headless": False,
    "max_retries": 2,
    "startup_delay_range": (0, 3),
    "retry_delay_range": (5, 15)
}

# SlideShare 基礎 URL
SLIDESHARE_BASE_URL = "https://www.slideshare.net"
SLIDESHARE_CATEGORY_URL_TEMPLATE = f"{SLIDESHARE_BASE_URL}/category/{{category}}"

# 輸出相關常數
OUTPUT_BASE_DIR = "output_url"
SCRAPE_INFO_FILENAME = "scrape_info.json"

# 檔案路徑格式
PATH_FORMAT_TEMPLATE = "{date}_{time}_category={category}_section={section}_num={num}"
PATH_OPTIONAL_COMPONENTS = {
    "window": "window={window_num}",
    "headless": "headless"
}

# 日期時間格式
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H-%M-%S"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

# CSV 相關常數
CSV_FIELDS = ["編號", "標題", "連結"]
CSV_ENCODING = "utf-8-sig"
CSV_DELIMITER = ","

# 日誌相關常數
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_FILENAME = "slideshare_scraper.log"

# 瀏覽器相關常數
BROWSER_TYPES = ["chrome", "edge"]
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
DEFAULT_WINDOW_SIZE = "1920,1080"

# 錯誤處理常數
MAX_CONSECUTIVE_ERRORS = 3
CONNECTION_TIMEOUT = 30
PAGE_LOAD_TIMEOUT = 60

# 驗證常數
MIN_TITLE_LENGTH = 5
MAX_TITLE_LENGTH = 500
REQUIRED_URL_PARTS = ["slideshare.net"]
