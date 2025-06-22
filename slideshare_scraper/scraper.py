#!/usr/bin/env python3
"""
SlideShare 核心爬蟲類別

包含 SlideShareScraper 類別和相關的爬取邏輯。
"""

import csv
import time
import re
import os
import logging
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config import get_environment_config
from .constants import SECTION_PATTERNS


class SlideShareScraper:
    """SlideShare 爬蟲類別"""

    def __init__(self, download_num: int = None, headless: bool = None, 
                 section_type: str = "featured", config: dict = None, 
                 environment: str = "development"):
        """
        初始化爬蟲

        Args:
            download_num: 要爬取的數量，預設從配置檔讀取
            headless: 是否使用無頭模式，預設從配置檔讀取
            section_type: 要爬取的區塊類型 (featured, popular, new)
            config: 自訂配置字典
            environment: 環境設定 (development, production, testing)
        """
        # 載入配置
        self.config = config or get_environment_config(environment)

        # 設定參數
        self.download_num = download_num or self.config["download"]["default_num"]
        self.headless = headless if headless is not None else self.config["download"]["default_headless"]
        self.delay = self.config["download"]["default_delay"]
        self.section_type = section_type

        # WebDriver 相關
        self.driver = None
        self.wait = None

        # 統計資訊
        self.stats = {
            "total_scraped": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }

        # 設定日誌
        self._setup_logging()

    def _setup_logging(self):
        """設定日誌系統"""
        log_config = self.config["logging"]

        # 設定日誌格式
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_config["file"], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        """設定 WebDriver"""
        try:
            chrome_options = Options()

            # 基本選項
            if self.headless:
                chrome_options.add_argument("--headless")

            # 從配置檔載入 Chrome 選項
            for option in self.config["chrome_options"]:
                chrome_options.add_argument(option)

            # 設定視窗大小和 User-Agent
            chrome_options.add_argument(f"--window-size={self.config['browser']['window_size']}")
            chrome_options.add_argument(f"--user-agent={self.config['browser']['user_agent']}")

            # 嘗試自動偵測 Chrome 路徑
            chrome_options.add_experimental_option("detach", True)

            # 建立 WebDriver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except WebDriverException as e:
                if "cannot find Chrome binary" in str(e):
                    self.logger.error("找不到 Chrome 瀏覽器，請確認已安裝 Chrome")
                    self.logger.info("嘗試使用 Edge 瀏覽器...")
                    # 嘗試使用 Edge 作為替代
                    edge_options = EdgeOptions()
                    if self.headless:
                        edge_options.add_argument("--headless")
                    for option in self.config["chrome_options"]:
                        edge_options.add_argument(option)

                    edge_service = EdgeService(EdgeChromiumDriverManager().install())
                    self.driver = webdriver.Edge(service=edge_service, options=edge_options)
                else:
                    raise e

            # 設定超時時間
            self.driver.set_page_load_timeout(self.config["browser"]["page_load_timeout"])
            self.wait = WebDriverWait(self.driver, self.config["browser"]["timeout"])

            self.logger.info("WebDriver 設定完成")

        except Exception as e:
            self.logger.error("設定 WebDriver 時發生錯誤: %s", e)
            raise

    def extract_category_from_title(self, title_text: str, pattern: str = "Featured in") -> Optional[str]:
        """
        從標題中提取類別名稱

        Args:
            title_text: 標題文字，例如 "Featured in Business" 或 "Most popular in Technology"
            pattern: 要匹配的模式，例如 "Featured in" 或 "Most popular in"

        Returns:
            類別名稱，例如 "Business"
        """
        # 轉義特殊字符並建立正則表達式
        escaped_pattern = re.escape(pattern)
        match = re.search(f'{escaped_pattern} (.+)', title_text)
        return match.group(1) if match else None

    def find_target_section(self) -> Optional[tuple]:
        """
        根據 section_type 尋找對應的區塊

        Returns:
            (section_element, category_name) 或 None
        """
        try:
            pattern = SECTION_PATTERNS.get(self.section_type, "Featured in")
            self.logger.info("開始尋找 %s 區塊...", pattern)

            # 使用配置檔中的選擇器
            sections = self.driver.find_elements(By.CSS_SELECTOR, self.config["selectors"]["section"])
            self.logger.info("找到 %d 個 section 元素", len(sections))

            for i, section in enumerate(sections, 1):
                try:
                    h2_element = section.find_element(By.CSS_SELECTOR, self.config["selectors"]["section_title"])
                    title_text = h2_element.text.strip()

                    self.logger.debug("檢查第 %d 個 section 標題: %s", i, title_text)

                    if pattern in title_text:
                        category = self.extract_category_from_title(title_text, pattern)
                        if category:
                            self.logger.info("找到 %s 區塊: %s", pattern, title_text)
                            return section, category

                except NoSuchElementException:
                    self.logger.debug("第 %d 個 section 沒有 h2 標題", i)
                    continue

        except Exception as e:
            self.logger.error("尋找 %s 區塊時發生錯誤: %s", pattern, e)
            self.stats["errors"] += 1

        self.logger.warning("未找到 %s 區塊", pattern)
        return None

    def extract_slideshow_data(self, section) -> List[Dict[str, str]]:
        """
        從區塊中提取投影片資料

        Args:
            section: 區塊元素

        Returns:
            投影片資料列表
        """
        slideshow_data = []

        try:
            # 使用配置檔中的選擇器
            selectors = self.config["selectors"]
            cards = section.find_elements(By.CSS_SELECTOR, selectors["slideshow_card"])

            self.logger.info("找到 %d 個投影片卡片", len(cards))

            for i, card in enumerate(cards, 1):
                try:
                    # 提取連結
                    link_element = card.find_element(By.CSS_SELECTOR, selectors["slideshow_link"])
                    link = link_element.get_attribute("href")

                    # 提取標題
                    title_element = card.find_element(By.CSS_SELECTOR, selectors["slideshow_title"])
                    title = title_element.text.strip()

                    # 資料驗證
                    if self._validate_data(title, link):
                        slideshow_data.append({
                            "編號": str(len(slideshow_data) + 1),
                            "標題": title,
                            "連結": link
                        })
                        self.logger.debug("提取第 %d 筆: %s...", len(slideshow_data), title[:50])

                except NoSuchElementException as e:
                    self.logger.warning("提取第 %d 個卡片時發生錯誤: %s", i, e)
                    self.stats["errors"] += 1
                    continue

        except Exception as e:
            self.logger.error("提取投影片資料時發生錯誤: %s", e)
            self.stats["errors"] += 1

        self.logger.info("成功提取 %d 筆投影片資料", len(slideshow_data))
        return slideshow_data

    def _validate_data(self, title: str, link: str) -> bool:
        """
        驗證資料有效性

        Args:
            title: 投影片標題
            link: 投影片連結

        Returns:
            是否有效
        """
        validation = self.config["validation"]

        # 檢查標題長度
        if not (validation["min_title_length"] <= len(title) <= validation["max_title_length"]):
            self.logger.warning("標題長度不符合要求: %s", title)
            return False

        # 檢查 URL 格式
        if not link or not any(part in link for part in validation["required_url_parts"]):
            self.logger.warning("URL 格式不正確: %s", link)
            return False

        return True

    def click_show_more_button(self, section) -> bool:
        """
        點擊 "Show More" 按鈕

        Args:
            section: 區塊元素

        Returns:
            是否成功點擊
        """
        try:
            # 使用配置檔中的選擇器
            show_more_button = section.find_element(
                By.CSS_SELECTOR,
                self.config["selectors"]["show_more_button"]
            )

            if show_more_button.is_displayed() and show_more_button.is_enabled():
                self.logger.info("點擊 Show More 按鈕...")
                self.driver.execute_script("arguments[0].click();", show_more_button)

                # 使用配置檔中的延遲時間
                time.sleep(self.delay)
                return True
            else:
                self.logger.info("Show More 按鈕不可用")
                return False

        except NoSuchElementException:
            self.logger.info("找不到 Show More 按鈕")
            return False
        except Exception as e:
            self.logger.error("點擊 Show More 按鈕時發生錯誤: %s", e)
            self.stats["errors"] += 1
            return False

    def save_to_csv(self, data: List[Dict[str, str]], filename: str):
        """
        將資料儲存至 CSV 檔案

        Args:
            data: 要儲存的資料
            filename: 檔案名稱
        """
        try:
            # 確保輸出目錄存在
            output_dir = self.config["files"]["output_directory"]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 完整檔案路徑
            filepath = os.path.join(output_dir, filename)

            # 使用配置檔中的設定
            file_config = self.config["files"]

            with open(filepath, 'w', newline='', encoding=file_config["csv_encoding"]) as csvfile:
                if data:
                    fieldnames = self.config["output"]["csv"]["fields"]
                    writer = csv.DictWriter(
                        csvfile,
                        fieldnames=fieldnames,
                        delimiter=file_config["csv_delimiter"]
                    )

                    writer.writeheader()
                    writer.writerows(data)

                    self.logger.info("成功儲存 %d 筆資料至 %s", len(data), filepath)
                else:
                    self.logger.warning("沒有資料可儲存")

        except Exception as e:
            self.logger.error("儲存 CSV 檔案時發生錯誤: %s", e)
            self.stats["errors"] += 1

    def _is_duplicate(self, item: Dict[str, str], existing_data: List[Dict[str, str]]) -> bool:
        """
        檢查是否為重複資料

        Args:
            item: 要檢查的項目
            existing_data: 現有資料列表

        Returns:
            是否重複
        """
        if not self.config["cleaning"]["remove_duplicates"]:
            return False

        for existing_item in existing_data:
            if (item.get("標題") == existing_item.get("標題") and
                item.get("連結") == existing_item.get("連結")):
                return True
        return False

    def _finalize_data(self, data: List[Dict[str, str]]):
        """
        最終化資料處理

        Args:
            data: 要處理的資料列表
        """
        cleaning_config = self.config["cleaning"]

        for i, item in enumerate(data, 1):
            # 重新編號
            item["編號"] = str(i)

            # 清理空白字符
            if cleaning_config["trim_whitespace"]:
                for key, value in item.items():
                    if isinstance(value, str):
                        item[key] = value.strip()

            # 標準化 URL
            if cleaning_config["normalize_urls"] and "連結" in item:
                url = item["連結"]
                if url and not url.startswith(("http://", "https://")):
                    item["連結"] = "https://" + url

    def _print_summary(self):
        """列印爬取摘要"""
        duration = self.stats["end_time"] - self.stats["start_time"]

        self.logger.info("=" * 50)
        self.logger.info("爬取完成摘要")
        self.logger.info("=" * 50)
        self.logger.info("總共爬取: %d 筆資料", self.stats['total_scraped'])
        self.logger.info("錯誤次數: %d", self.stats['errors'])
        self.logger.info("執行時間: %.2f 秒", duration)
        self.logger.info("平均速度: %.2f 筆/秒", self.stats['total_scraped']/duration)
        self.logger.info("=" * 50)

    def scrape_slideshare(self, url: str):
        """
        主要爬取函數

        Args:
            url: SlideShare 頁面 URL
        """
        self.stats["start_time"] = time.time()

        try:
            self.logger.info("開始爬取: %s", url)
            self.setup_driver()

            # 載入頁面
            self.driver.get(url)
            time.sleep(5)

            # 尋找目標區塊
            result = self.find_target_section()
            if not result:
                section_patterns = {
                    "featured": "Featured",
                    "popular": "Most popular",
                    "new": "New"
                }
                pattern_name = section_patterns.get(self.section_type, "Featured")
                self.logger.warning("找不到 %s 區塊", pattern_name)
                return

            section, category = result
            all_data = []
            consecutive_errors = 0
            max_errors = self.config["error"]["max_consecutive_errors"]

            self.logger.info("開始爬取 %s 類別的投影片...", category)

            # 持續爬取直到達到指定數量
            while len(all_data) < self.download_num:
                try:
                    # 提取當前頁面的資料
                    current_data = self.extract_slideshow_data(section)

                    # 過濾重複資料
                    new_items = 0
                    for item in current_data:
                        if self._is_duplicate(item, all_data):
                            continue
                        if len(all_data) < self.download_num:
                            all_data.append(item)
                            new_items += 1

                    self.logger.info("目前已爬取 %d 筆資料（新增 %d 筆）", len(all_data), new_items)

                    # 如果已達到目標數量，停止爬取
                    if len(all_data) >= self.download_num:
                        break

                    # 如果沒有新資料且無法點擊 Show More，停止爬取
                    if new_items == 0:
                        if not self.click_show_more_button(section):
                            self.logger.info("無法載入更多內容，停止爬取")
                            break
                    else:
                        # 有新資料時也嘗試載入更多
                        self.click_show_more_button(section)

                    consecutive_errors = 0  # 重置錯誤計數

                except Exception as e:
                    consecutive_errors += 1
                    self.logger.error("爬取過程中發生錯誤 (%d/%d): %s", consecutive_errors, max_errors, e)

                    if consecutive_errors >= max_errors:
                        self.logger.error("連續錯誤次數過多，停止爬取")
                        break

                    time.sleep(2)  # 錯誤後稍作休息

            # 重新編號和清理資料
            self._finalize_data(all_data)

            # 儲存至 CSV，檔名包含區塊類型
            section_name = self.section_type.capitalize()
            filename = f"{category}_{section_name}.csv"
            self.save_to_csv(all_data, filename)

            self.stats["total_scraped"] = len(all_data)
            self.stats["end_time"] = time.time()

            self._print_summary()

        except Exception as e:
            self.logger.error("爬取過程中發生錯誤: %s", e)
            self.stats["errors"] += 1
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver 已關閉")
