"""
SlideShare 簡報下載工具 - 下載邏輯模組

負責執行實際的下載操作。
"""

import os
import sys


class SlideDownloader:
    """簡報下載器"""
    
    def __init__(self, slideshare_downloader):
        """初始化下載器
        
        Args:
            slideshare_downloader: SlideShareDownloader 實例
        """
        self.downloader = slideshare_downloader
    
    def execute_download(self, args):
        """執行下載操作
        
        Args:
            args: 解析後的命令列參數
            
        Returns:
            dict: 下載結果
        """
        # 根據參數選擇下載方式
        if args.csv_file:
            return self._download_from_csv_file(args)
        elif args.folder:
            return self._download_from_folder(args)
        elif args.from_latest:
            return self._download_from_latest(args)
        else:
            # 這種情況理論上不應該發生，因為參數驗證應該確保至少有一個選項被選中
            print("❌ 錯誤：未指定有效的下載來源")
            sys.exit(1)
    
    def _download_from_csv_file(self, args):
        """從 CSV 檔案下載

        Args:
            args: 解析後的命令列參數

        Returns:
            dict: 下載結果
        """
        print(f"📄 從 CSV 檔案下載：{args.csv_file}")

        # 如果沒有指定輸出目錄，根據 CSV 檔案路徑自動創建對應的時間戳目錄
        output_dir = args.output_dir
        if not output_dir:
            # 從 CSV 檔案路徑中提取時間戳目錄名稱和 CSV 檔案名稱
            csv_path = os.path.normpath(args.csv_file)
            path_parts = csv_path.split(os.sep)

            # 查找 output_url 後面的時間戳目錄
            timestamp_dir = None
            csv_filename = None
            for i, part in enumerate(path_parts):
                if part == "output_url" and i + 1 < len(path_parts):
                    timestamp_dir = path_parts[i + 1]
                    # 獲取 CSV 檔案名稱（去掉 .csv 副檔名）
                    if i + 2 < len(path_parts):
                        csv_filename = os.path.splitext(path_parts[i + 2])[0]
                    break

            if timestamp_dir:
                if csv_filename:
                    # 創建：output_files/時間戳目錄/CSV檔案名稱/
                    output_dir = os.path.join("output_files", timestamp_dir, csv_filename)
                    print(f"📁 自動設置輸出目錄：{output_dir}")
                else:
                    # 只有時間戳目錄
                    output_dir = os.path.join("output_files", timestamp_dir)
                    print(f"📁 自動設置輸出目錄：{output_dir}")
            else:
                output_dir = "output_files"
                print(f"📁 使用預設輸出目錄：{output_dir}")

        return self.downloader.download_from_csv_file(args.csv_file, output_dir)
    
    def _download_from_folder(self, args):
        """從時間戳目錄下載
        
        Args:
            args: 解析後的命令列參數
            
        Returns:
            dict: 下載結果
        """
        folder_path = os.path.join("output_url", args.folder)
        print(f"📁 從時間戳目錄下載：{args.folder}")
        
        if args.category:
            print(f"🏷️  類別過濾：{args.category}")
        if args.section:
            print(f"📋 區塊過濾：{args.section}")

        # 創建對應的輸出目錄
        output_dir = args.output_dir or os.path.join("output_files", args.folder)
        
        return self.downloader.download_from_directory(
            folder_path,
            output_dir,
            file_pattern="*.csv",
            category_filter=args.category,
            section_filter=args.section
        )
    
    def _download_from_latest(self, args):
        """從最新的 output_url 目錄下載
        
        Args:
            args: 解析後的命令列參數
            
        Returns:
            dict: 下載結果
        """
        print("📅 從最新的 output_url 目錄下載")
        
        if args.category:
            print(f"🏷️  類別過濾：{args.category}")
        if args.section:
            print(f"📋 區塊過濾：{args.section}")

        return self.downloader.download_from_url_directory(
            "output_url",
            category_filter=args.category,
            section_filter=args.section
        )
