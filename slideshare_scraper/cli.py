#!/usr/bin/env python3
"""
SlideShare 爬蟲命令列介面

包含命令列參數解析和主要執行邏輯。
"""

import os
import time
import argparse

from .constants import SUPPORTED_CATEGORIES, SUPPORTED_SECTIONS
from .utils import (
    validate_category, validate_section, generate_output_path, 
    save_scrape_info, move_files_to_output_path, count_csv_data,
    find_latest_files_by_pattern, get_category_url
)
from .scraper import SlideShareScraper
from .parallel import execute_parallel_tasks, warmup_webdriver, retry_failed_tasks


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="SlideShare 爬蟲程式 - 爬取不同區塊的投影片資料",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支援的類別：
{', '.join(SUPPORTED_CATEGORIES)}

支援的區塊類型：
  featured  - Featured in XXX 區塊 (預設)
  popular   - Most popular in XXX 區塊
  new       - New in XXX 區塊
  all       - 所有區塊類型

使用範例：
  python 1_get_urls.py                             # 使用預設設定 (business, featured, 100筆)
  python 1_get_urls.py -c technology -s popular -n 50    # 爬取 technology 類別的 popular 區塊 50筆
  python 1_get_urls.py -c all -s all -n 20               # 並行爬取所有類別的所有區塊各 20筆
  python 1_get_urls.py -c all -s featured -p 5           # 使用 5 個並行視窗爬取所有類別的 featured 區塊
  python 1_get_urls.py -s new --headless                 # 爬取 new 區塊，使用無頭模式
        """
    )

    parser.add_argument(
        "-c", "--category",
        default="business",
        help="要爬取的類別 (預設: business)，使用 'all' 爬取所有類別"
    )

    parser.add_argument(
        "-s", "--section",
        default="featured",
        help="要爬取的區塊類型 (預設: featured)，可選: featured, popular, new, all"
    )

    parser.add_argument(
        "-n", "--num",
        type=int,
        default=100,
        help="要爬取的數量 (預設: 100)"
    )

    parser.add_argument(
        "-o", "--output-dir",
        default="output_url",
        help="指定輸出目錄 (預設: output_url)"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="使用無頭模式運行 (不顯示瀏覽器視窗)"
    )

    parser.add_argument(
        "-p", "--parallel",
        type=int,
        default=10,
        help="使用 'all' 選項時的並行數量 (預設: 10)"
    )

    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="列出所有支援的類別"
    )

    parser.add_argument(
        "--list-sections",
        action="store_true",
        help="列出所有支援的區塊類型"
    )

    return parser.parse_args()


def handle_list_commands(args):
    """處理列表命令"""
    if args.list_categories:
        print("支援的類別：")
        for category in SUPPORTED_CATEGORIES:
            print(f"  - {category}")
        return True

    if args.list_sections:
        print("支援的區塊類型：")
        for section in SUPPORTED_SECTIONS:
            print(f"  - {section}")
        return True

    return False


def validate_arguments(args):
    """驗證命令列參數"""
    # 驗證類別參數
    if not validate_category(args.category, SUPPORTED_CATEGORIES):
        print(f"錯誤：不支援的類別 '{args.category}'")
        print(f"支援的類別：{', '.join(SUPPORTED_CATEGORIES)}")
        print("或使用 'all' 爬取所有類別")
        return False

    # 驗證區塊類型參數
    if not validate_section(args.section, SUPPORTED_SECTIONS):
        print(f"錯誤：不支援的區塊類型 '{args.section}'")
        print(f"支援的區塊類型：{', '.join(SUPPORTED_SECTIONS)}")
        print("或使用 'all' 爬取所有區塊類型")
        return False

    return True


def execute_parallel_mode(args, categories, sections, total_tasks):
    """執行並行模式"""
    print(f"🚀 並行爬取模式：{len(categories)} 個類別 × {len(sections)} 個區塊類型 = {total_tasks} 個任務")
    print(f"📊 每個任務爬取 {args.num} 筆資料")
    print(f"🔧 使用 {args.parallel} 個並行視窗")
    print(f"💡 模式：{'無頭' if args.headless else '顯示瀏覽器'}")

    # 生成輸出路徑
    output_path = generate_output_path(
        category=args.category,
        section=args.section,
        num=args.num,
        window_num=args.parallel,
        headless=args.headless
    )
    print(f"📁 輸出路徑：{output_path}")

    # WebDriver 預熱，避免並行下載衝突
    if not warmup_webdriver():
        print("⚠️  WebDriver 預熱失敗，但仍會繼續執行...")

    # 準備任務列表
    tasks = []
    task_id = 0
    for category in categories:
        for section in sections:
            task_id += 1
            tasks.append({
                "task_id": task_id,
                "category": category,
                "section": section,
                "download_num": args.num,
                "headless": args.headless,
                "output_path": output_path
            })

    # 執行並行任務
    start_time = time.time()
    results = execute_parallel_tasks(tasks, args.parallel)
    end_time = time.time()

    return process_parallel_results(results, output_path, args, start_time, end_time, total_tasks)


def process_parallel_results(results, output_path, args, start_time, end_time, total_tasks):
    """處理並行結果"""
    # 顯示結果摘要
    print("\n" + "="*70)
    print("📋 任務執行結果摘要")
    print("="*70)

    successful_tasks = [r for r in results if r["success"]]
    failed_tasks = [r for r in results if not r["success"]]
    total_data = sum(r["data_count"] for r in successful_tasks)
    execution_time = end_time - start_time

    print(f"✅ 成功任務：{len(successful_tasks)}/{total_tasks}")
    print(f"❌ 失敗任務：{len(failed_tasks)}/{total_tasks}")
    print(f"📊 總共爬取：{total_data} 筆資料")
    print(f"⏱️  執行時間：{execution_time:.1f} 秒")

    # 移動檔案到新的輸出路徑
    if successful_tasks:
        print(f"\n📁 移動檔案到：{output_path}")
        moved_files = move_files_to_output_path("output_url", output_path, ".csv")
        
        for result in successful_tasks:
            if result['filename'] in moved_files:
                print(f"   ✅ {result['filename']} ({result['data_count']} 筆)")

        # 儲存爬取資訊
        parameters = {
            "category": args.category,
            "section": args.section,
            "num": args.num,
            "window_num": args.parallel,
            "headless": args.headless
        }

        results_info = {
            "total_tasks": total_tasks,
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "total_data": total_data,
            "execution_time": execution_time,
            "files": moved_files
        }

        save_scrape_info(output_path, parameters, results_info)

    return failed_tasks


def execute_single_mode(args, categories, sections):
    """執行單一任務模式"""
    print(f"📝 單一任務模式：爬取 {args.category} 類別的 {args.section} 區塊")
    print(f"📊 目標數量：{args.num} 筆資料")

    category = categories[0]
    section = sections[0]
    url = get_category_url(category)

    # 生成輸出路徑
    output_path = generate_output_path(
        category=args.category,
        section=args.section,
        num=args.num,
        headless=args.headless
    )
    print(f"📁 輸出路徑：{output_path}")

    # 建立爬蟲實例
    scraper = SlideShareScraper(
        download_num=args.num,
        headless=args.headless,
        section_type=section
    )

    # 開始爬取
    start_time = time.time()
    scraper.scrape_slideshare(url)
    end_time = time.time()

    # 處理單一任務的結果
    execution_time = end_time - start_time

    # 檢查生成的檔案
    section_name = section.capitalize()
    output_dir = "output_url"
    generated_files = find_latest_files_by_pattern(output_dir, f"_{section_name}.csv")

    if generated_files:
        # 移動檔案到新輸出路徑
        moved_files = move_files_to_output_path(output_dir, output_path, f"_{section_name}.csv")

        print(f"\n📁 移動檔案到：{output_path}")
        total_data = 0

        for filename in moved_files:
            filepath = os.path.join(output_path, filename)
            data_count = count_csv_data(filepath)
            total_data += data_count
            print(f"   ✅ {filename} ({data_count} 筆)")

        # 儲存爬取資訊
        parameters = {
            "category": args.category,
            "section": args.section,
            "num": args.num,
            "headless": args.headless
        }

        results_info = {
            "total_tasks": 1,
            "successful_tasks": 1,
            "failed_tasks": 0,
            "total_data": total_data,
            "execution_time": execution_time,
            "files": moved_files
        }

        save_scrape_info(output_path, parameters, results_info)
    else:
        print("⚠️  未找到生成的檔案")


def main():
    """主函數"""
    args = parse_arguments()

    # 處理列表命令
    if handle_list_commands(args):
        return

    # 驗證參數
    if not validate_arguments(args):
        return

    # 決定要爬取的類別和區塊類型
    categories = SUPPORTED_CATEGORIES if args.category == "all" else [args.category]
    sections = SUPPORTED_SECTIONS if args.section == "all" else [args.section]

    total_tasks = len(categories) * len(sections)

    # 檢查是否需要使用並行處理
    use_parallel = (args.category == "all" or args.section == "all") and total_tasks > 1

    if use_parallel:
        # 並行處理模式
        failed_tasks = execute_parallel_mode(args, categories, sections, total_tasks)

        # 處理失敗任務
        if failed_tasks:
            print(f"\n⚠️  失敗的任務：")
            for result in failed_tasks:
                print(f"   - {result['category']}_{result['section']}: {result['error']}")

            # 詢問是否要重試失敗的任務
            if len(failed_tasks) > 0:
                print(f"\n🔄 發現 {len(failed_tasks)} 個失敗任務，是否要進行額外重試？")
                print("建議：使用較少的並行視窗數量重試失敗任務")
                retry_choice = input("是否重試失敗任務？(y/n): ").lower().strip()

                if retry_choice == 'y':
                    retry_failed_tasks(failed_tasks, args)

    else:
        # 單一任務模式
        execute_single_mode(args, categories, sections)

    print(f"\n{'='*70}")
    print("🎉 所有任務完成！")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
