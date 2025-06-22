#!/usr/bin/env python3
"""
SlideShare 簡報下載器

根據 CSV 檔案中的 URL 連結，下載每個簡報的所有投影片圖片。
"""

import os
import re
import csv
import time
import requests
import random
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Optional
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import io

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
from .constants import OUTPUT_BASE_DIR


class SlideShareDownloader:
    """SlideShare 簡報圖片下載器"""

    def __init__(self, headless: bool = True, download_delay: float = 1.0,
                 max_retries: int = 3, parallel_workers: int = 1,
                 environment: str = "development"):
        """
        初始化下載器

        Args:
            headless: 是否使用無頭模式
            download_delay: 下載間隔時間（秒）
            max_retries: 最大重試次數
            parallel_workers: 並行工作執行緒數量（預設：1）
            environment: 環境設定
        """
        self.config = get_environment_config(environment)
        self.headless = headless
        self.download_delay = download_delay
        self.max_retries = max_retries
        self.parallel_workers = parallel_workers
        
        # WebDriver 相關
        self.driver = None
        self.wait = None
        
        # 統計資訊
        self.stats = {
            "total_presentations": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_slides": 0,
            "start_time": None,
            "end_time": None
        }
        
        # 設定日誌
        self._setup_logging()
        
        # 創建輸出目錄
        self.output_base = "output_files"
        self._ensure_directory_exists(self.output_base)

    def _setup_logging(self):
        """設定日誌系統"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('slideshare_downloader.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _ensure_directory_exists(self, directory: str):
        """確保目錄存在"""
        Path(directory).mkdir(parents=True, exist_ok=True)

    def setup_driver(self):
        """設定 WebDriver"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # 基本選項
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # 建立 WebDriver
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except WebDriverException as e:
                if "cannot find Chrome binary" in str(e):
                    self.logger.info("Chrome 不可用，嘗試使用 Edge...")
                    edge_options = EdgeOptions()
                    if self.headless:
                        edge_options.add_argument("--headless")
                    edge_options.add_argument("--no-sandbox")
                    edge_options.add_argument("--disable-dev-shm-usage")
                    
                    edge_service = EdgeService(EdgeChromiumDriverManager().install())
                    self.driver = webdriver.Edge(service=edge_service, options=edge_options)
                else:
                    raise e
            
            # 設定超時時間
            self.driver.set_page_load_timeout(60)
            self.wait = WebDriverWait(self.driver, 30)
            
            self.logger.info("WebDriver 設定完成")
            
        except Exception as e:
            self.logger.error(f"設定 WebDriver 時發生錯誤: {e}")
            raise

    def _sanitize_filename(self, filename: str) -> str:
        """清理檔案名稱，移除不合法字符"""
        if not filename:
            return "unknown"

        # 移除或替換不合法字符（包括單引號和其他特殊字符）
        filename = re.sub(r'[<>:"/\\|?*\'`]', '_', filename)

        # 移除多餘空白和特殊字符
        filename = re.sub(r'\s+', ' ', filename).strip()
        filename = re.sub(r'[._\-\s]+$', '', filename)  # 移除結尾的點、底線、破折號、空白
        filename = re.sub(r'^[._\-\s]+', '', filename)  # 移除開頭的點、底線、破折號、空白

        # 限制長度（考慮 Windows 路徑限制，更保守的長度）
        max_length = 40  # 減少到40字符，為完整路徑留出更多空間
        if len(filename) > max_length:
            # 智慧截斷：嘗試在單詞邊界截斷
            words = filename.split()
            truncated = ""
            for word in words:
                if len(truncated + " " + word) <= max_length:
                    truncated = (truncated + " " + word).strip()
                else:
                    break

            if truncated:
                filename = truncated
            else:
                # 如果單個單詞就超長，直接截斷
                filename = filename[:max_length]

        # 確保不是空字符串
        if not filename:
            filename = "unknown"

        return filename

    def _extract_title_from_url(self, url: str) -> str:
        """從 URL 中提取標題"""
        try:
            # SlideShare URL 格式通常是 /username/title-slug
            path = urlparse(url).path
            parts = path.strip('/').split('/')
            if len(parts) >= 2:
                title_slug = parts[-1]
                # 將 slug 轉換為可讀標題
                title = title_slug.replace('-', ' ').title()
                return self._sanitize_filename(title)
        except Exception as e:
            self.logger.warning(f"無法從 URL 提取標題: {e}")
        
        # 備用方案：使用 URL 的最後部分
        return self._sanitize_filename(url.split('/')[-1] or "unknown_presentation")

    def _get_presentation_title(self, url: str) -> str:
        """獲取簡報標題"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # 嘗試多種標題選擇器
            title_selectors = [
                'h1[data-cy="presentation-title"]',
                'h1.slideshow-title',
                'h1',
                '.presentation-title',
                '[data-testid="presentation-title"]'
            ]
            
            for selector in title_selectors:
                try:
                    title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    if title:
                        return self._sanitize_filename(title)
                except NoSuchElementException:
                    continue
            
            # 如果都找不到，從 URL 提取
            return self._extract_title_from_url(url)
            
        except Exception as e:
            self.logger.warning(f"獲取標題失敗，使用 URL 提取: {e}")
            return self._extract_title_from_url(url)

    def _extract_slide_images(self, url: str) -> List[Dict[str, str]]:
        """提取簡報中的所有投影片圖片"""
        try:
            self.driver.get(url)
            time.sleep(5)  # 等待頁面載入
            
            # 等待投影片容器載入
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.vertical-slide-image')))
            except TimeoutException:
                self.logger.warning("投影片容器載入超時")
                return []
            
            # 提取所有投影片圖片
            slide_images = []
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, '.vertical-slide-image')
            
            self.logger.info(f"找到 {len(img_elements)} 張投影片")
            
            for i, img_element in enumerate(img_elements, 1):
                try:
                    # 獲取最高解析度的圖片 URL
                    img_url = self._get_best_quality_image_url(img_element)
                    if img_url:
                        slide_images.append({
                            "slide_number": i,
                            "image_url": img_url,
                            "alt_text": img_element.get_attribute("alt") or f"Slide {i}"
                        })
                except Exception as e:
                    self.logger.warning(f"提取第 {i} 張投影片時發生錯誤: {e}")
                    continue
            
            return slide_images
            
        except Exception as e:
            self.logger.error(f"提取投影片圖片時發生錯誤: {e}")
            return []

    def _get_best_quality_image_url(self, img_element) -> Optional[str]:
        """獲取最佳品質的圖片 URL"""
        try:
            # 嘗試從 srcset 獲取最高解析度圖片
            srcset = img_element.get_attribute("srcset")
            if srcset:
                # 解析 srcset，選擇最大尺寸
                sources = []
                for source in srcset.split(','):
                    parts = source.strip().split()
                    if len(parts) >= 2:
                        url = parts[0]
                        width_str = parts[1]
                        if width_str.endswith('w'):
                            try:
                                width = int(width_str[:-1])
                                sources.append((url, width))
                            except ValueError:
                                continue
                
                if sources:
                    # 選擇最大寬度的圖片
                    best_source = max(sources, key=lambda x: x[1])
                    return best_source[0]
            
            # 備用方案：使用 src 屬性
            return img_element.get_attribute("src")
            
        except Exception as e:
            self.logger.warning(f"獲取圖片 URL 時發生錯誤: {e}")
            return None

    def _download_image(self, image_url: str, save_path: str) -> bool:
        """下載單張圖片並轉換為 JPEG 格式"""
        # 確保目錄存在
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        except Exception as e:
            self.logger.error(f"創建目錄失敗: {e}")
            return False

        # 檢查路徑長度
        if len(save_path) > 250:
            self.logger.warning(f"檔案路徑過長，可能導致下載失敗: {save_path}")

        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.slideshare.net/'
                }

                response = requests.get(image_url, headers=headers, timeout=30)
                response.raise_for_status()

                # 檢測圖片格式並轉換為 JPEG
                try:
                    # 使用 PIL 開啟圖片
                    image = Image.open(io.BytesIO(response.content))

                    # 如果是 RGBA 模式（有透明度），轉換為 RGB
                    if image.mode in ('RGBA', 'LA', 'P'):
                        # 創建白色背景
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')

                    # 確保檔案副檔名是 .jpg
                    if not save_path.lower().endswith('.jpg'):
                        save_path = save_path.rsplit('.', 1)[0] + '.jpg'

                    # 儲存為高品質 JPEG
                    image.save(save_path, 'JPEG', quality=95, optimize=True)

                    self.logger.debug(f"成功下載並轉換圖片: {save_path}")
                    return True

                except Exception as img_error:
                    # 如果 PIL 處理失敗，嘗試直接儲存原始檔案
                    self.logger.warning(f"圖片轉換失敗，嘗試直接儲存: {img_error}")

                    # 根據內容類型決定副檔名
                    content_type = response.headers.get('content-type', '').lower()
                    if 'webp' in content_type:
                        save_path = save_path.rsplit('.', 1)[0] + '.webp'
                    elif 'png' in content_type:
                        save_path = save_path.rsplit('.', 1)[0] + '.png'

                    with open(save_path, 'wb') as f:
                        f.write(response.content)

                    self.logger.debug(f"成功下載原始格式圖片: {save_path}")
                    return True

            except (OSError, IOError) as e:
                # 檔案系統錯誤，通常是路徑問題
                if "No such file or directory" in str(e) or "cannot find the path" in str(e):
                    self.logger.error(f"檔案路徑錯誤: {save_path}")
                    self.logger.error(f"錯誤詳情: {e}")
                    return False
                else:
                    self.logger.warning(f"檔案系統錯誤 (嘗試 {attempt + 1}/{self.max_retries}): {e}")
            except Exception as e:
                self.logger.warning(f"下載圖片失敗 (嘗試 {attempt + 1}/{self.max_retries}): {e}")

            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # 指數退避

        return False

    def _download_presentation(self, url: str, title: str, output_dir: str, csv_index: Optional[int] = None) -> Dict:
        """下載單個簡報的所有投影片"""
        result = {
            "url": url,
            "title": title,
            "success": False,
            "slides_downloaded": 0,
            "total_slides": 0,
            "error": None,
            "output_path": None
        }

        try:
            self.logger.info(f"開始下載簡報: {title}")

            # 獲取簡報標題（如果沒有提供）
            if not title or title == "unknown":
                title = self._get_presentation_title(url)

            # 創建簡報專用目錄，確保路徑不會過長
            sanitized_title = self._sanitize_filename(title)

            # 如果有 CSV 編號，添加編號前綴
            if csv_index is not None:
                dir_name = f"{csv_index:03d}_{sanitized_title}"
            else:
                dir_name = sanitized_title

            presentation_dir = os.path.join(output_dir, dir_name)

            # 檢查完整路徑長度（Windows 限制約 260 字符）
            if len(presentation_dir) > 200:  # 保守估計，留出空間給檔案名
                # 進一步縮短目錄名
                short_title = sanitized_title[:20] + "_" + str(hash(title) % 10000)
                if csv_index is not None:
                    short_dir_name = f"{csv_index:03d}_{short_title}"
                else:
                    short_dir_name = short_title
                presentation_dir = os.path.join(output_dir, short_dir_name)
                self.logger.warning(f"路徑過長，縮短目錄名：{dir_name} -> {short_dir_name}")

            self._ensure_directory_exists(presentation_dir)
            result["output_path"] = presentation_dir

            # 提取所有投影片圖片
            slide_images = self._extract_slide_images(url)
            result["total_slides"] = len(slide_images)

            if not slide_images:
                result["error"] = "未找到投影片圖片"
                return result

            # 下載每張投影片
            successful_downloads = 0
            for slide_info in slide_images:
                slide_num = slide_info["slide_number"]
                image_url = slide_info["image_url"]

                # 生成檔案名稱：標題_編號.jpg，確保檔案名不會過長
                base_filename = self._sanitize_filename(title)
                # 進一步限制檔案名長度，為編號和副檔名留出空間
                if len(base_filename) > 30:
                    base_filename = base_filename[:30]
                filename = f"{base_filename}_{slide_num:03d}.jpg"
                save_path = os.path.join(presentation_dir, filename)

                # 最終檢查完整路徑長度
                if len(save_path) > 250:  # Windows 路徑限制
                    # 使用更短的檔案名
                    short_filename = f"slide_{slide_num:03d}.jpg"
                    save_path = os.path.join(presentation_dir, short_filename)
                    self.logger.debug(f"路徑過長，使用簡化檔案名：{short_filename}")

                # 如果檔案已存在，跳過
                if os.path.exists(save_path):
                    self.logger.debug(f"檔案已存在，跳過: {filename}")
                    successful_downloads += 1
                    continue

                # 下載圖片
                if self._download_image(image_url, save_path):
                    successful_downloads += 1
                    self.stats["total_slides"] += 1

                # 下載間隔
                time.sleep(self.download_delay)

            result["slides_downloaded"] = successful_downloads
            result["success"] = successful_downloads > 0

            if result["success"]:
                self.logger.info(f"簡報下載完成: {title} ({successful_downloads}/{len(slide_images)} 張)")
            else:
                result["error"] = "所有投影片下載失敗"

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"下載簡報時發生錯誤: {e}")

        return result

    def download_from_csv_file(self, csv_file_path: str, output_dir: Optional[str] = None) -> Dict:
        """從 CSV 檔案下載簡報（支援並行處理）"""
        if output_dir is None:
            output_dir = self.output_base

        self._ensure_directory_exists(output_dir)

        results = {
            "csv_file": csv_file_path,
            "output_directory": output_dir,
            "presentations": [],
            "summary": {
                "total_presentations": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "total_slides": 0
            }
        }

        try:
            # 讀取 CSV 檔案
            with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                presentations = list(reader)

            if not presentations:
                self.logger.warning(f"CSV 檔案為空: {csv_file_path}")
                return results

            self.logger.info(f"從 {csv_file_path} 讀取到 {len(presentations)} 個簡報")
            self.logger.info(f"使用 {self.parallel_workers} 個並行工作執行緒")
            results["summary"]["total_presentations"] = len(presentations)

            if self.parallel_workers == 1:
                # 單執行緒模式（原有邏輯）
                self.setup_driver()

                for i, presentation in enumerate(presentations, 1):
                    url = presentation.get("連結", "").strip()
                    title = presentation.get("標題", "").strip()

                    if not url:
                        self.logger.warning(f"第 {i} 筆資料缺少 URL，跳過")
                        continue

                    self.logger.info(f"處理第 {i}/{len(presentations)} 個簡報: {title}")

                    download_result = self._download_presentation(url, title, output_dir, csv_index=i)
                    results["presentations"].append(download_result)

                    if download_result["success"]:
                        results["summary"]["successful_downloads"] += 1
                        results["summary"]["total_slides"] += download_result["slides_downloaded"]
                    else:
                        results["summary"]["failed_downloads"] += 1

                    self.logger.info(f"進度: {i}/{len(presentations)} 完成")

                if self.driver:
                    self.driver.quit()
                    self.logger.info("WebDriver 已關閉")

            else:
                # 多執行緒並行模式
                tasks = []
                for i, presentation in enumerate(presentations, 1):
                    url = presentation.get("連結", "").strip()
                    title = presentation.get("標題", "").strip()

                    if not url:
                        self.logger.warning(f"第 {i} 筆資料缺少 URL，跳過")
                        continue

                    tasks.append({
                        "task_id": i,
                        "url": url,
                        "title": title,
                        "output_dir": output_dir,
                        "worker_id": None  # 將在執行時分配
                    })

                # 執行並行下載
                start_time = time.time()
                with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
                    # 為每個任務分配工作執行緒 ID
                    for i, task in enumerate(tasks):
                        task["worker_id"] = (i % self.parallel_workers) + 1

                    # 提交所有任務
                    future_to_task = {
                        executor.submit(self._download_presentation_worker, task): task
                        for task in tasks
                    }

                    # 收集結果
                    completed = 0
                    for future in as_completed(future_to_task):
                        try:
                            download_result = future.result()
                            results["presentations"].append(download_result)

                            if download_result["success"]:
                                results["summary"]["successful_downloads"] += 1
                                results["summary"]["total_slides"] += download_result["slides_downloaded"]
                            else:
                                results["summary"]["failed_downloads"] += 1

                            completed += 1
                            elapsed_time = time.time() - start_time
                            self.logger.info(f"進度: {completed}/{len(tasks)} 完成 | 耗時: {elapsed_time:.1f}s")

                        except Exception as e:
                            task = future_to_task[future]
                            self.logger.error(f"任務 {task['task_id']} 執行失敗: {e}")
                            results["presentations"].append({
                                "task_id": task["task_id"],
                                "url": task["url"],
                                "title": task["title"],
                                "success": False,
                                "error": f"執行緒異常: {e}",
                                "slides_downloaded": 0,
                                "total_slides": 0
                            })
                            results["summary"]["failed_downloads"] += 1

        except Exception as e:
            self.logger.error(f"處理 CSV 檔案時發生錯誤: {e}")
            results["error"] = str(e)

        return results

    def _download_presentation_worker(self, task_info: Dict) -> Dict:
        """
        並行工作執行緒：下載單個簡報

        Args:
            task_info: 包含任務資訊的字典

        Returns:
            下載結果字典
        """
        url = task_info["url"]
        title = task_info["title"]
        output_dir = task_info["output_dir"]
        worker_id = task_info["worker_id"]
        task_id = task_info["task_id"]

        result = {
            "worker_id": worker_id,
            "task_id": task_id,
            "url": url,
            "title": title,
            "success": False,
            "slides_downloaded": 0,
            "total_slides": 0,
            "error": None,
            "output_path": None
        }

        # 為每個工作執行緒創建獨立的 WebDriver
        driver = None
        try:
            # 添加啟動延遲，避免同時啟動太多瀏覽器
            startup_delay = random.uniform(0, 3)
            time.sleep(startup_delay)

            self.logger.info(f"[工作執行緒 {worker_id}] 開始下載簡報: {title}")

            # 設定獨立的 WebDriver
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")

            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except WebDriverException as e:
                if "cannot find Chrome binary" in str(e):
                    edge_options = EdgeOptions()
                    if self.headless:
                        edge_options.add_argument("--headless")
                    edge_options.add_argument("--no-sandbox")
                    edge_options.add_argument("--disable-dev-shm-usage")

                    edge_service = EdgeService(EdgeChromiumDriverManager().install())
                    driver = webdriver.Edge(service=edge_service, options=edge_options)
                else:
                    raise e

            driver.set_page_load_timeout(60)
            wait = WebDriverWait(driver, 30)

            # 獲取簡報標題（如果沒有提供）
            if not title or title == "unknown":
                driver.get(url)
                time.sleep(3)

                title_selectors = [
                    'h1[data-cy="presentation-title"]',
                    'h1.slideshow-title',
                    'h1',
                    '.presentation-title',
                    '[data-testid="presentation-title"]'
                ]

                for selector in title_selectors:
                    try:
                        title_element = driver.find_element(By.CSS_SELECTOR, selector)
                        title = title_element.text.strip()
                        if title:
                            title = self._sanitize_filename(title)
                            break
                    except NoSuchElementException:
                        continue

                if not title:
                    title = self._extract_title_from_url(url)

            # 創建簡報專用目錄，確保路徑不會過長
            sanitized_title = self._sanitize_filename(title)

            # 添加 CSV 編號前綴
            dir_name = f"{task_id:03d}_{sanitized_title}"
            presentation_dir = os.path.join(output_dir, dir_name)

            # 檢查完整路徑長度
            if len(presentation_dir) > 200:
                short_title = sanitized_title[:20] + "_" + str(hash(title) % 10000)
                short_dir_name = f"{task_id:03d}_{short_title}"
                presentation_dir = os.path.join(output_dir, short_dir_name)
                self.logger.warning(f"[工作執行緒 {worker_id}] 路徑過長，縮短目錄名：{dir_name} -> {short_dir_name}")

            self._ensure_directory_exists(presentation_dir)
            result["output_path"] = presentation_dir

            # 提取所有投影片圖片
            driver.get(url)
            time.sleep(5)

            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.vertical-slide-image')))
            except TimeoutException:
                result["error"] = "投影片容器載入超時"
                return result

            img_elements = driver.find_elements(By.CSS_SELECTOR, '.vertical-slide-image')
            result["total_slides"] = len(img_elements)

            if not img_elements:
                result["error"] = "未找到投影片圖片"
                return result

            self.logger.info(f"[工作執行緒 {worker_id}] 找到 {len(img_elements)} 張投影片")

            # 下載每張投影片
            successful_downloads = 0
            for i, img_element in enumerate(img_elements, 1):
                try:
                    img_url = self._get_best_quality_image_url(img_element)
                    if img_url:
                        # 生成檔案名稱，確保不會過長
                        base_filename = self._sanitize_filename(title)
                        if len(base_filename) > 30:
                            base_filename = base_filename[:30]
                        filename = f"{base_filename}_{i:03d}.jpg"
                        save_path = os.path.join(presentation_dir, filename)

                        # 檢查完整路徑長度
                        if len(save_path) > 250:
                            short_filename = f"slide_{i:03d}.jpg"
                            save_path = os.path.join(presentation_dir, short_filename)

                        if os.path.exists(save_path):
                            successful_downloads += 1
                            continue

                        if self._download_image(img_url, save_path):
                            successful_downloads += 1

                        time.sleep(self.download_delay)

                except Exception as e:
                    self.logger.warning(f"[工作執行緒 {worker_id}] 提取第 {i} 張投影片時發生錯誤: {e}")
                    continue

            result["slides_downloaded"] = successful_downloads
            result["success"] = successful_downloads > 0

            if result["success"]:
                self.logger.info(f"[工作執行緒 {worker_id}] 簡報下載完成: {title} ({successful_downloads}/{len(img_elements)} 張)")
            else:
                result["error"] = "所有投影片下載失敗"

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"[工作執行緒 {worker_id}] 下載簡報時發生錯誤: {e}")

        finally:
            if driver:
                driver.quit()

        return result

    def download_from_directory(self, input_directory: str, output_dir: Optional[str] = None,
                               file_pattern: str = "*.csv", category_filter: Optional[str] = None,
                               section_filter: Optional[str] = None) -> Dict:
        """從目錄中的所有 CSV 檔案下載簡報"""
        if output_dir is None:
            output_dir = self.output_base

        self._ensure_directory_exists(output_dir)

        # 找到所有 CSV 檔案
        input_path = Path(input_directory)
        all_csv_files = list(input_path.glob(file_pattern))

        # 應用過濾器
        csv_files = []
        for csv_file in all_csv_files:
            filename = csv_file.stem

            # 應用類別過濾器
            if category_filter and category_filter.lower() not in filename.lower():
                continue
            # 應用區塊過濾器
            if section_filter and section_filter.lower() not in filename.lower():
                continue

            csv_files.append(csv_file)

        if not csv_files:
            if category_filter or section_filter:
                self.logger.warning(f"在目錄 {input_directory} 中未找到符合過濾條件的 CSV 檔案")
                return {"error": f"未找到符合過濾條件的 CSV 檔案（類別：{category_filter}，區塊：{section_filter}）"}
            else:
                self.logger.warning(f"在目錄 {input_directory} 中未找到 CSV 檔案")
                return {"error": "未找到 CSV 檔案"}

        self.logger.info(f"找到 {len(csv_files)} 個 CSV 檔案")

        all_results = {
            "input_directory": input_directory,
            "output_directory": output_dir,
            "csv_files": [],
            "total_summary": {
                "total_csv_files": len(csv_files),
                "total_presentations": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "total_slides": 0
            }
        }

        # 處理每個 CSV 檔案
        for csv_file in csv_files:
            self.logger.info(f"處理 CSV 檔案: {csv_file.name}")

            # 為每個 CSV 檔案創建子目錄
            csv_output_dir = os.path.join(output_dir, csv_file.stem)

            # 下載該 CSV 檔案中的所有簡報
            file_results = self.download_from_csv_file(str(csv_file), csv_output_dir)
            all_results["csv_files"].append(file_results)

            # 累計統計
            summary = file_results.get("summary", {})
            all_results["total_summary"]["total_presentations"] += summary.get("total_presentations", 0)
            all_results["total_summary"]["successful_downloads"] += summary.get("successful_downloads", 0)
            all_results["total_summary"]["failed_downloads"] += summary.get("failed_downloads", 0)
            all_results["total_summary"]["total_slides"] += summary.get("total_slides", 0)

        return all_results

    def download_from_url_directory(self, url_directory: str,
                                   category_filter: Optional[str] = None,
                                   section_filter: Optional[str] = None) -> Dict:
        """
        從 output_url 目錄下載簡報

        Args:
            url_directory: output_url 目錄路徑
            category_filter: 類別過濾器（可選）
            section_filter: 區塊過濾器（可選）
        """
        url_path = Path(url_directory)
        if not url_path.exists():
            return {"error": f"目錄不存在: {url_directory}"}

        # 找到所有時間戳目錄
        timestamp_dirs = [d for d in url_path.iterdir() if d.is_dir()]

        if not timestamp_dirs:
            return {"error": f"在 {url_directory} 中未找到時間戳目錄"}

        # 選擇最新的目錄
        latest_dir = max(timestamp_dirs, key=lambda x: x.stat().st_mtime)
        self.logger.info(f"使用最新的 URL 目錄: {latest_dir.name}")

        # 找到符合條件的 CSV 檔案
        csv_files = []
        for csv_file in latest_dir.glob("*.csv"):
            filename = csv_file.stem

            # 應用過濾器
            if category_filter and category_filter.lower() not in filename.lower():
                continue
            if section_filter and section_filter.lower() not in filename.lower():
                continue

            csv_files.append(csv_file)

        if not csv_files:
            return {"error": "未找到符合條件的 CSV 檔案"}

        self.logger.info(f"找到 {len(csv_files)} 個符合條件的 CSV 檔案")

        # 創建對應的輸出目錄
        output_dir = os.path.join(self.output_base, latest_dir.name)

        # 下載所有符合條件的簡報
        return self.download_from_directory(str(latest_dir), output_dir, "*.csv")

    def print_summary(self, results: Dict):
        """列印下載摘要"""
        print("\n" + "="*70)
        print("📥 SlideShare 簡報下載摘要")
        print("="*70)

        if "total_summary" in results:
            summary = results["total_summary"]
            print(f"📁 處理的 CSV 檔案: {summary.get('total_csv_files', 0)} 個")
            print(f"📊 總簡報數量: {summary.get('total_presentations', 0)} 個")
            print(f"✅ 成功下載: {summary.get('successful_downloads', 0)} 個")
            print(f"❌ 下載失敗: {summary.get('failed_downloads', 0)} 個")
            print(f"🖼️  總投影片數: {summary.get('total_slides', 0)} 張")

            if summary.get('total_presentations', 0) > 0:
                success_rate = (summary.get('successful_downloads', 0) /
                              summary.get('total_presentations', 1)) * 100
                print(f"📈 成功率: {success_rate:.1f}%")

        elif "summary" in results:
            summary = results["summary"]
            print(f"📊 總簡報數量: {summary.get('total_presentations', 0)} 個")
            print(f"✅ 成功下載: {summary.get('successful_downloads', 0)} 個")
            print(f"❌ 下載失敗: {summary.get('failed_downloads', 0)} 個")
            print(f"🖼️  總投影片數: {summary.get('total_slides', 0)} 張")

        if "output_directory" in results:
            print(f"📁 輸出目錄: {results['output_directory']}")

        print("="*70)
