#!/usr/bin/env python3
"""
SlideShare 簡報下載工具 - 步驟2：下載簡報圖片

這是 SlideShare 下載工具的第二步，負責讀取步驟1產生的 CSV 檔案，
並下載每個簡報的所有投影片圖片。

功能特點：
- 自動圖片格式轉換（WebP → JPEG）
- 智慧檔案命名和目錄整理
- 並行下載模式（多執行緒）
- 斷點續傳和錯誤重試
- 靈活的輸入來源選擇

使用前提：
需要先執行 1_get_urls.py 爬取 SlideShare URL 清單

基本使用範例：
    # 從最新的爬取結果下載
    python 2_download_slide.py --from-latest

    # 從指定時間戳目錄下載
    python 2_download_slide.py --folder "2025-06-23_12-30-45_category=business_section=featured_num=50_headless"

    # 從單一 CSV 檔案下載
    python 2_download_slide.py --csv-file "output_url/folder_name/Business_Featured.csv"

進階使用範例：
    # 並行下載（3個工作執行緒）
    python 2_download_slide.py --from-latest -p 3

    # 顯示瀏覽器模式（用於監控和除錯）
    python 2_download_slide.py --from-latest

    # 自訂下載延遲和重試次數
    python 2_download_slide.py --from-latest -d 2.0 -r 5

    # 過濾特定類別和區塊
    python 2_download_slide.py --from-latest -c business -s featured

完整工作流程範例：
    # 步驟1：爬取 URL
    python 1_get_urls.py -c technology -s popular -n 30 --headless

    # 步驟2：下載簡報圖片
    python 2_download_slide.py --from-latest -p 2

更多詳細說明請參考：
- README.md - 完整使用說明
- WORKFLOW_GUIDE.md - 詳細工作流程指南
"""

from slide_downloader import main

if __name__ == "__main__":
    main()
