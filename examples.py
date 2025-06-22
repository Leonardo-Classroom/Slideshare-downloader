#!/usr/bin/env python3
"""
SlideShare 下載工具使用範例

這個檔案包含了各種使用場景的完整範例，展示如何使用兩步驟工作流程
來爬取 SlideShare URL 並下載簡報圖片。

執行前請確保：
1. 已安裝所有依賴：pip install -r requirements.txt
2. 已安裝 Chrome 或 Edge 瀏覽器
3. 網路連線正常
"""

import os
import subprocess
import time
from datetime import datetime


def run_command(command, description):
    """執行命令並顯示結果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"執行命令：{command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 執行成功！")
            if result.stdout:
                print("輸出：")
                print(result.stdout)
        else:
            print("❌ 執行失敗！")
            if result.stderr:
                print("錯誤：")
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 執行異常：{e}")
        return False


def example_basic_workflow():
    """範例1：基本工作流程"""
    print("\n" + "="*80)
    print("📚 範例1：基本工作流程 - 爬取 business 類別的 featured 區塊")
    print("="*80)
    
    # 步驟1：爬取 URL
    success1 = run_command(
        "python 1_get_urls.py -c business -s featured -n 10 --headless",
        "步驟1：爬取 business 類別的 featured 區塊 URL（10筆）"
    )
    
    if success1:
        time.sleep(2)  # 等待檔案寫入完成
        
        # 步驟2：下載簡報
        success2 = run_command(
            "python 2_download_slide.py --from-latest -c business -s featured",
            "步驟2：下載剛才爬取的簡報圖片"
        )
        
        if success2:
            print("\n🎉 基本工作流程完成！")
            print("📁 請檢查 output_files/ 目錄查看下載的簡報圖片")
        else:
            print("\n⚠️ 簡報下載失敗，請檢查日誌檔案")
    else:
        print("\n⚠️ URL 爬取失敗，請檢查網路連線和瀏覽器設定")


def example_parallel_workflow():
    """範例2：並行工作流程"""
    print("\n" + "="*80)
    print("⚡ 範例2：並行工作流程 - 高效率爬取和下載")
    print("="*80)
    
    # 步驟1：並行爬取多個類別
    success1 = run_command(
        "python 1_get_urls.py -c technology,design -s popular -n 5 -p 2 --headless",
        "步驟1：並行爬取 technology 和 design 類別的 popular 區塊（各5筆）"
    )

    if success1:
        time.sleep(2)

        # 步驟2：並行下載
        success2 = run_command(
            "python 2_download_slide.py --from-latest -p 2",
            "步驟2：使用2個工作執行緒並行下載簡報圖片"
        )
        
        if success2:
            print("\n🎉 並行工作流程完成！")
            print("📁 請檢查 output_files/ 目錄查看下載的簡報圖片")


def example_specific_category():
    """範例3：特定類別深度爬取"""
    print("\n" + "="*80)
    print("🎯 範例3：特定類別深度爬取 - technology 類別所有區塊")
    print("="*80)
    
    # 步驟1：爬取 technology 類別的所有區塊
    success1 = run_command(
        "python 1_get_urls.py -c technology -s all -n 8 -p 3 --headless",
        "步驟1：爬取 technology 類別的所有區塊（featured, popular, new 各8筆）"
    )

    if success1:
        time.sleep(2)

        # 步驟2：下載特定類別，使用顯示瀏覽器模式監控
        success2 = run_command(
            "python 2_download_slide.py --from-latest -c technology -d 1.5",
            "步驟2：下載 technology 類別簡報，使用預設顯示瀏覽器模式監控"
        )
        
        if success2:
            print("\n🎉 特定類別深度爬取完成！")


def example_csv_file_download():
    """範例4：從 CSV 檔案下載"""
    print("\n" + "="*80)
    print("📄 範例4：從指定 CSV 檔案下載簡報")
    print("="*80)
    
    # 首先檢查是否有現有的 CSV 檔案
    output_dir = "output_url"
    if os.path.exists(output_dir):
        csv_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        
        if csv_files:
            # 使用第一個找到的 CSV 檔案
            csv_file = csv_files[0]
            print(f"📁 找到 CSV 檔案：{csv_file}")
            
            success = run_command(
                f'python 2_download_slide.py --csv-file "{csv_file}" -p 2',
                f"從指定 CSV 檔案下載簡報：{os.path.basename(csv_file)}"
            )
            
            if success:
                print("\n🎉 CSV 檔案下載完成！")
        else:
            print("⚠️ 未找到 CSV 檔案，請先執行步驟1爬取 URL")
    else:
        print("⚠️ output_url 目錄不存在，請先執行步驟1爬取 URL")


def example_help_and_info():
    """範例5：查看說明和支援選項"""
    print("\n" + "="*80)
    print("ℹ️ 範例5：查看說明和支援選項")
    print("="*80)
    
    # 查看步驟1的說明
    run_command(
        "python 1_get_urls.py --help",
        "查看步驟1（URL爬取）的完整說明"
    )
    
    # 查看支援的類別
    run_command(
        "python 1_get_urls.py --list-categories",
        "列出所有支援的類別"
    )
    
    # 查看支援的區塊類型
    run_command(
        "python 1_get_urls.py --list-sections",
        "列出所有支援的區塊類型"
    )
    
    # 查看步驟2的說明
    run_command(
        "python 2_download_slide.py --help",
        "查看步驟2（簡報下載）的完整說明"
    )


def main():
    """主函數 - 執行所有範例"""
    print("🎯 SlideShare 下載工具使用範例")
    print("=" * 80)
    print("這個腳本將展示各種使用場景的完整範例")
    print("請確保您已經安裝了所有依賴並且網路連線正常")
    print("\n⚠️ 注意：這些範例會實際執行爬取和下載操作")
    print("如果您只想查看命令，請直接閱讀這個檔案的原始碼")
    
    choice = input("\n是否要執行範例？(y/n): ").lower().strip()
    
    if choice != 'y':
        print("👋 已取消執行，您可以直接查看檔案中的範例命令")
        return
    
    print(f"\n🕐 開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 執行各種範例
        example_help_and_info()      # 先查看說明
        example_basic_workflow()     # 基本工作流程
        example_parallel_workflow()  # 並行工作流程
        example_specific_category()  # 特定類別爬取
        example_csv_file_download()  # CSV 檔案下載
        
        print(f"\n🕐 結束時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎉 所有範例執行完成！")
        print("📁 請檢查以下目錄：")
        print("   - output_url/: 爬取的 URL 清單")
        print("   - output_files/: 下載的簡報圖片")
        print("📝 日誌檔案：")
        print("   - slideshare_scraper.log: URL 爬取日誌")
        print("   - slideshare_downloader.log: 簡報下載日誌")
        
    except KeyboardInterrupt:
        print("\n⏹️ 用戶中斷執行")
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤：{e}")


if __name__ == "__main__":
    main()
