#!/usr/bin/env python3
"""
SlideShare 下載工具快速開始腳本

這個腳本提供了一個簡單的互動式介面，讓新用戶可以快速開始使用 SlideShare 下載工具。
"""

import os
import subprocess
import sys
from datetime import datetime


def print_header():
    """顯示標題"""
    print("=" * 70)
    print("🚀 SlideShare 下載工具 - 快速開始")
    print("=" * 70)
    print("這個工具可以幫您從 SlideShare 下載簡報圖片")
    print("工作流程：1️⃣ 爬取 URL → 2️⃣ 下載圖片")
    print("=" * 70)


def check_requirements():
    """檢查基本需求"""
    print("\n🔍 檢查系統需求...")
    
    # 檢查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ Python 版本過低，需要 Python 3.8+")
        return False
    else:
        print(f"✅ Python 版本：{sys.version.split()[0]}")
    
    # 檢查依賴檔案
    if not os.path.exists("requirements.txt"):
        print("❌ 找不到 requirements.txt 檔案")
        return False
    else:
        print("✅ 找到 requirements.txt 檔案")
    
    # 檢查核心檔案
    if not os.path.exists("1_get_urls.py"):
        print("❌ 找不到 1_get_urls.py 檔案")
        return False
    else:
        print("✅ 找到 1_get_urls.py 檔案")
    
    if not os.path.exists("2_download_slide.py"):
        print("❌ 找不到 2_download_slide.py 檔案")
        return False
    else:
        print("✅ 找到 2_download_slide.py 檔案")
    
    return True


def install_dependencies():
    """安裝依賴"""
    print("\n📦 安裝依賴套件...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 依賴套件安裝成功")
            return True
        else:
            print(f"❌ 依賴套件安裝失敗：{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安裝過程中發生錯誤：{e}")
        return False


def get_user_preferences():
    """獲取用戶偏好設定"""
    print("\n⚙️ 設定爬取參數")
    print("-" * 30)
    
    # 選擇類別
    print("📂 選擇要爬取的類別：")
    print("1. business (商業)")
    print("2. technology (技術)")
    print("3. design (設計)")
    print("4. education (教育)")
    print("5. marketing (行銷)")
    
    while True:
        choice = input("請選擇 (1-5，預設為1): ").strip()
        if choice == "" or choice == "1":
            category = "business"
            break
        elif choice == "2":
            category = "technology"
            break
        elif choice == "3":
            category = "design"
            break
        elif choice == "4":
            category = "education"
            break
        elif choice == "5":
            category = "marketing"
            break
        else:
            print("❌ 無效選擇，請重新輸入")
    
    # 選擇區塊類型
    print(f"\n📋 選擇 {category} 類別的區塊類型：")
    print("1. featured (精選)")
    print("2. popular (熱門)")
    print("3. new (最新)")
    
    while True:
        choice = input("請選擇 (1-3，預設為1): ").strip()
        if choice == "" or choice == "1":
            section = "featured"
            break
        elif choice == "2":
            section = "popular"
            break
        elif choice == "3":
            section = "new"
            break
        else:
            print("❌ 無效選擇，請重新輸入")
    
    # 選擇數量
    while True:
        num_input = input("\n📊 要爬取多少筆資料？(預設為10): ").strip()
        if num_input == "":
            num = 10
            break
        try:
            num = int(num_input)
            if 1 <= num <= 100:
                break
            else:
                print("❌ 數量必須在 1-100 之間")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    # 選擇是否顯示瀏覽器
    show_browser = input("\n🖥️ 是否顯示瀏覽器視窗？(y/n，預設為n): ").strip().lower()
    headless = show_browser != "y"
    
    return {
        "category": category,
        "section": section,
        "num": num,
        "headless": headless
    }


def run_step1(params):
    """執行步驟1：爬取 URL"""
    print("\n" + "="*50)
    print("🔍 步驟1：爬取 SlideShare URL")
    print("="*50)
    
    headless_flag = "--headless" if params["headless"] else ""
    command = f'python 1_get_urls.py -c {params["category"]} -s {params["section"]} -n {params["num"]} {headless_flag}'
    
    print(f"執行命令：{command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            print("✅ 步驟1完成：URL 爬取成功")
            return True
        else:
            print("❌ 步驟1失敗：URL 爬取失敗")
            return False
    except Exception as e:
        print(f"❌ 步驟1執行異常：{e}")
        return False


def run_step2(params):
    """執行步驟2：下載簡報"""
    print("\n" + "="*50)
    print("📥 步驟2：下載簡報圖片")
    print("="*50)

    headless_flag = "--headless" if params["headless"] else ""
    command = f'python 2_download_slide.py --from-latest -c {params["category"]} -s {params["section"]} {headless_flag}'
    
    print(f"執行命令：{command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            print("✅ 步驟2完成：簡報下載成功")
            return True
        else:
            print("❌ 步驟2失敗：簡報下載失敗")
            return False
    except Exception as e:
        print(f"❌ 步驟2執行異常：{e}")
        return False


def show_results():
    """顯示結果"""
    print("\n" + "="*50)
    print("📁 查看結果")
    print("="*50)
    
    # 檢查 output_url 目錄
    if os.path.exists("output_url"):
        print("✅ URL 爬取結果：")
        for item in os.listdir("output_url"):
            if os.path.isdir(os.path.join("output_url", item)):
                print(f"   📂 {item}")
    
    # 檢查 output_files 目錄
    if os.path.exists("output_files"):
        print("✅ 簡報下載結果：")
        for item in os.listdir("output_files"):
            if os.path.isdir(os.path.join("output_files", item)):
                print(f"   📂 {item}")
    
    print("\n📝 日誌檔案：")
    if os.path.exists("slideshare_scraper.log"):
        print("   📄 slideshare_scraper.log - URL 爬取日誌")
    if os.path.exists("slideshare_downloader.log"):
        print("   📄 slideshare_downloader.log - 簡報下載日誌")


def main():
    """主函數"""
    print_header()
    
    # 檢查系統需求
    if not check_requirements():
        print("\n❌ 系統需求檢查失敗，請解決上述問題後重試")
        return
    
    # 詢問是否安裝依賴
    install_deps = input("\n📦 是否要安裝/更新依賴套件？(y/n，預設為y): ").strip().lower()
    if install_deps != "n":
        if not install_dependencies():
            print("\n❌ 依賴安裝失敗，請手動執行：pip install -r requirements.txt")
            return
    
    # 獲取用戶設定
    params = get_user_preferences()
    
    # 確認設定
    print(f"\n📋 您的設定：")
    print(f"   類別：{params['category']}")
    print(f"   區塊：{params['section']}")
    print(f"   數量：{params['num']}")
    print(f"   模式：{'顯示瀏覽器' if not params['headless'] else '無頭模式'}")
    
    confirm = input("\n確認開始執行？(y/n): ").strip().lower()
    if confirm != "y":
        print("👋 已取消執行")
        return
    
    print(f"\n🕐 開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 執行步驟1
        if run_step1(params):
            # 執行步驟2
            if run_step2(params):
                print(f"\n🎉 完整工作流程執行成功！")
                show_results()
            else:
                print(f"\n⚠️ 步驟2失敗，但步驟1的結果已保存")
                print("您可以稍後手動執行：python 2_download_slide.py --from-latest")
        else:
            print(f"\n⚠️ 步驟1失敗，請檢查網路連線和瀏覽器設定")
    
    except KeyboardInterrupt:
        print("\n⏹️ 用戶中斷執行")
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤：{e}")
    
    print(f"\n🕐 結束時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📚 更多使用方法請參考：")
    print("   - README.md - 完整使用說明")
    print("   - examples.py - 詳細使用範例")
    print("   - WORKFLOW_GUIDE.md - 工作流程指南")


if __name__ == "__main__":
    main()
