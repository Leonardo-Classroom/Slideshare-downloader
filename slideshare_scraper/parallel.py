#!/usr/bin/env python3
"""
SlideShare 並行處理模組

包含並行爬取、任務執行、重試機制等功能。
"""

import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from .scraper import SlideShareScraper
from .utils import get_category_url, count_csv_data, find_latest_files_by_pattern
from .constants import DEFAULT_SETTINGS


def warmup_webdriver():
    """
    預熱 WebDriver，確保驅動程式已下載
    
    Returns:
        是否成功預熱
    """
    try:
        print("🔧 正在預熱 WebDriver...")
        scraper = SlideShareScraper(download_num=1, headless=True, section_type="featured")
        scraper.setup_driver()
        if scraper.driver:
            scraper.driver.quit()
        print("✅ WebDriver 預熱完成")
        return True
    except Exception as e:
        print(f"⚠️  WebDriver 預熱失敗：{e}")
        return False


def execute_single_task(task_info: Dict) -> Dict:
    """
    執行單一爬取任務（帶重試機制）

    Args:
        task_info: 包含任務資訊的字典

    Returns:
        任務執行結果
    """
    category = task_info["category"]
    section = task_info["section"]
    download_num = task_info["download_num"]
    headless = task_info["headless"]
    task_id = task_info["task_id"]
    max_retries = task_info.get("max_retries", DEFAULT_SETTINGS["max_retries"])

    result = {
        "task_id": task_id,
        "category": category,
        "section": section,
        "success": False,
        "error": None,
        "data_count": 0,
        "filename": None,
        "retry_count": 0
    }

    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                # 重試前等待隨機時間，避免同時重試
                wait_time = random.uniform(*DEFAULT_SETTINGS["retry_delay_range"])
                print(f"[任務 {task_id}] 第 {attempt + 1} 次嘗試，等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)

            print(f"[任務 {task_id}] 開始爬取 {category} 類別的 {section} 區塊")

            url = get_category_url(category)

            # 添加啟動延遲，避免同時啟動太多瀏覽器
            startup_delay = random.uniform(*DEFAULT_SETTINGS["startup_delay_range"])
            time.sleep(startup_delay)

            scraper = SlideShareScraper(
                download_num=download_num,
                headless=headless,
                section_type=section
            )

            # 執行爬取
            scraper.scrape_slideshare(url)

            # 檢查是否成功生成檔案
            section_name = section.capitalize()
            output_dir = "output_url"

            # 搜尋所有可能的檔案名稱格式
            possible_files = find_latest_files_by_pattern(output_dir, f"_{section_name}.csv")

            # 找到最新的檔案（假設是剛剛生成的）
            if possible_files:
                latest_file = possible_files[0]  # 已經按時間排序
                filepath = os.path.join(output_dir, latest_file)

                # 計算資料筆數
                data_count = count_csv_data(filepath)

                result.update({
                    "success": True,
                    "data_count": data_count,
                    "filename": latest_file,
                    "retry_count": attempt
                })
                print(f"[任務 {task_id}] ✅ 完成！爬取 {data_count} 筆資料 → {latest_file}")
                return result

            raise FileNotFoundError("檔案未生成")

        except Exception as e:
            result["error"] = str(e)
            result["retry_count"] = attempt

            if attempt < max_retries:
                print(f"[任務 {task_id}] ⚠️  第 {attempt + 1} 次嘗試失敗：{e}，準備重試...")
            else:
                print(f"[任務 {task_id}] ❌ 最終失敗：{e}")

    return result


def execute_parallel_tasks(tasks: List[Dict], window_num: int) -> List[Dict]:
    """
    並行執行多個爬取任務（優化版）

    Args:
        tasks: 任務列表
        window_num: 並行視窗數量

    Returns:
        任務執行結果列表
    """
    print(f"開始並行執行 {len(tasks)} 個任務，使用 {window_num} 個並行視窗")
    print("=" * 70)

    # 為每個任務添加重試設定
    for task in tasks:
        task["max_retries"] = DEFAULT_SETTINGS["max_retries"]

    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=window_num) as executor:
        # 提交所有任務
        future_to_task = {
            executor.submit(execute_single_task, task): task
            for task in tasks
        }

        # 收集結果
        for future in as_completed(future_to_task):
            try:
                result = future.result()
                results.append(result)

                # 顯示進度
                completed = len(results)
                total = len(tasks)
                success_count = sum(1 for r in results if r["success"])
                elapsed_time = time.time() - start_time

                print(f"進度：{completed}/{total} 個任務完成 | 成功：{success_count} | 耗時：{elapsed_time:.1f}s")

            except Exception as e:
                # 處理執行緒異常
                task = future_to_task[future]
                error_result = {
                    "task_id": task["task_id"],
                    "category": task["category"],
                    "section": task["section"],
                    "success": False,
                    "error": f"執行緒異常：{e}",
                    "data_count": 0,
                    "filename": None,
                    "retry_count": 0
                }
                results.append(error_result)
                print(f"[任務 {task['task_id']}] ❌ 執行緒異常：{e}")

    return results


def retry_failed_tasks(failed_tasks: List[Dict], args) -> None:
    """
    重試失敗的任務

    Args:
        failed_tasks: 失敗任務列表
        args: 命令列參數
    """
    print(f"\n🔄 開始重試 {len(failed_tasks)} 個失敗任務...")
    print("使用較保守的設定：2 個並行視窗，增加延遲時間")

    # 準備重試任務列表
    retry_tasks = []
    for i, failed_task in enumerate(failed_tasks, 1):
        retry_tasks.append({
            "task_id": f"重試-{i}",
            "category": failed_task["category"],
            "section": failed_task["section"],
            "download_num": args.num,
            "headless": args.headless,
            "max_retries": 3  # 增加重試次數
        })

    # 使用較少的並行視窗重試
    retry_window_num = min(2, len(retry_tasks))
    retry_results = execute_parallel_tasks(retry_tasks, retry_window_num)

    # 顯示重試結果
    retry_successful = [r for r in retry_results if r["success"]]
    retry_failed = [r for r in retry_results if not r["success"]]

    print("\n🔄 重試結果摘要：")
    print(f"✅ 重試成功：{len(retry_successful)}/{len(failed_tasks)}")
    print(f"❌ 仍然失敗：{len(retry_failed)}/{len(failed_tasks)}")

    if retry_successful:
        print("\n📁 重試成功的檔案：")
        for result in retry_successful:
            print(f"   - {result['filename']} ({result['data_count']} 筆)")

    if retry_failed:
        print("\n⚠️  仍然失敗的任務：")
        for result in retry_failed:
            print(f"   - {result['category']}_{result['section']}: {result['error']}")
