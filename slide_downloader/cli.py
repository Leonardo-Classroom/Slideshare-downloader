#!/usr/bin/env python3
"""
SlideShare 簡報下載工具 - 命令列介面

根據 CSV 檔案中的 URL 連結，下載每個簡報的所有投影片圖片。
"""

import argparse
import sys

from slideshare_scraper.downloader import SlideShareDownloader
from .validator import ArgumentValidator
from .processor import ResultProcessor


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="SlideShare 簡報圖片下載工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  # 從指定時間戳目錄下載（推薦方式）
  python 2_download_slide.py --folder "2025-06-23_02-34-27_category=business_section=featured_num=3_headless"

  # 從單一 CSV 檔案下載
  python 2_download_slide.py --csv-file output_url/2025-06-23_01-13-35_category=all_section=all_num=100_window=30/Business_Featured.csv

  # 從最新的 output_url 目錄下載
  python 2_download_slide.py --from-latest

  # 下載特定類別
  python 2_download_slide.py --from-latest -c business

  # 下載特定區塊類型
  python 2_download_slide.py --from-latest -s featured

  # 使用無頭模式
  python 2_download_slide.py --folder "folder_name" --headless

  # 使用多執行緒並行下載（3個工作執行緒）
  python 2_download_slide.py --folder "folder_name" -p 3
        """
    )

    # 輸入來源選項（互斥）
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--csv-file",
        help="指定單一 CSV 檔案路徑"
    )
    source_group.add_argument(
        "--folder",
        help="指定時間戳目錄名稱（例如：2025-06-23_02-34-27_category=business_section=featured_num=3_headless）"
    )
    source_group.add_argument(
        "--from-latest",
        action="store_true",
        help="從最新的 output_url 目錄下載"
    )

    # 過濾選項
    parser.add_argument(
        "-c", "--category",
        help="類別過濾器（與 --from-latest 或 --folder 一起使用）"
    )
    parser.add_argument(
        "-s", "--section",
        help="區塊過濾器（與 --from-latest 或 --folder 一起使用）"
    )

    # 輸出選項
    parser.add_argument(
        "-o", "--output-dir",
        help="指定輸出目錄（預設：output_files）"
    )

    # 下載選項
    parser.add_argument(
        "--headless",
        action="store_true",
        help="使用無頭模式運行（不顯示瀏覽器視窗）"
    )
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=1.0,
        help="下載間隔時間（秒，預設：1.0）"
    )
    parser.add_argument(
        "-r", "--max-retries",
        type=int,
        default=3,
        help="最大重試次數（預設：3）"
    )
    parser.add_argument(
        "-p", "--parallel",
        type=int,
        default=1,
        help="並行工作執行緒數量（預設：1）"
    )

    return parser.parse_args()


def main():
    """主函數"""
    args = parse_arguments()
    
    # 驗證參數
    validator = ArgumentValidator()
    if not validator.validate(args):
        sys.exit(1)
    
    # 創建下載器
    downloader = SlideShareDownloader(
        headless=args.headless,
        download_delay=args.delay,
        max_retries=args.max_retries,
        parallel_workers=args.parallel
    )

    print("🚀 開始下載 SlideShare 簡報...")
    print(f"💡 模式：{'無頭模式' if args.headless else '顯示瀏覽器'}")
    print(f"⏱️  下載間隔：{args.delay} 秒")
    print(f"🔄 最大重試：{args.max_retries} 次")
    print(f"🔀 並行執行緒：{args.parallel} 個")
    
    try:
        # 執行下載
        from .downloader import SlideDownloader
        slide_downloader = SlideDownloader(downloader)
        results = slide_downloader.execute_download(args)
        
        # 處理結果
        processor = ResultProcessor(downloader)
        processor.process_results(results)
        
    except KeyboardInterrupt:
        print("\n⏹️  用戶中斷下載")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 下載過程中發生錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
