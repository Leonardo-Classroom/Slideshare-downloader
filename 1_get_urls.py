#!/usr/bin/env python3
"""
SlideShare URL 爬取工具 - 步驟1：收集簡報 URL

這是 SlideShare 下載工具的第一步，負責從 SlideShare 網站爬取簡報的 URL 連結和標題，
並儲存為 CSV 檔案供步驟2使用。

功能特點：
- 支援 40+ 個類別和 3 種區塊類型
- 並行爬取模式（最多 10 個視窗）
- 智慧重試機制和錯誤處理
- 詳細的進度追蹤和日誌記錄
- 自動生成時間戳目錄和元資料

基本使用範例：
    # 使用預設設定（business, featured, 100筆）
    python 1_get_urls.py

    # 爬取特定類別和區塊
    python 1_get_urls.py -c technology -s popular -n 50

    # 使用無頭模式（推薦用於大規模爬取）
    python 1_get_urls.py -c business -s featured -n 100 --headless

並行爬取範例：
    # 並行爬取所有類別的 featured 區塊
    python 1_get_urls.py -c all -s featured -n 50 -p 10 --headless

    # 並行爬取單一類別的所有區塊
    python 1_get_urls.py -c business -s all -n 30 -p 3

    # 大規模並行爬取
    python 1_get_urls.py -c all -s all -n 20 -p 5 --headless

查看支援選項：
    # 列出所有支援的類別
    python 1_get_urls.py --list-categories

    # 列出所有支援的區塊類型
    python 1_get_urls.py --list-sections

    # 查看完整說明
    python 1_get_urls.py --help

輸出結果：
    爬取完成後會在 output_url/ 目錄下生成時間戳目錄，包含：
    - CSV 檔案：簡報標題和 URL 清單
    - JSON 檔案：爬取元資料和統計資訊

下一步：
    爬取完成後，使用 2_download_slide.py 下載簡報圖片：
    python 2_download_slide.py --from-latest

更多詳細說明請參考：
- README.md - 完整使用說明
- WORKFLOW_GUIDE.md - 詳細工作流程指南
"""

from slideshare_scraper.cli import main

if __name__ == "__main__":
    main()
