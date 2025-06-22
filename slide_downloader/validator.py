"""
SlideShare 簡報下載工具 - 參數驗證模組

負責驗證命令列參數的有效性。
"""

import os


class ArgumentValidator:
    """命令列參數驗證器"""
    
    def validate(self, args):
        """驗證命令列參數
        
        Args:
            args: 解析後的命令列參數
            
        Returns:
            bool: 驗證是否通過
        """
        # 檢查檔案/目錄是否存在
        if not self._validate_file_existence(args):
            return False
            
        # 檢查過濾器選項
        if not self._validate_filter_options(args):
            return False
            
        return True
    
    def _validate_file_existence(self, args):
        """驗證檔案和目錄是否存在
        
        Args:
            args: 解析後的命令列參數
            
        Returns:
            bool: 驗證是否通過
        """
        # 檢查 CSV 檔案
        if args.csv_file and not os.path.exists(args.csv_file):
            print(f"錯誤：CSV 檔案不存在：{args.csv_file}")
            return False

        # 檢查時間戳目錄
        if args.folder:
            folder_path = os.path.join("output_url", args.folder)
            if not os.path.exists(folder_path):
                print(f"錯誤：時間戳目錄不存在：{folder_path}")
                self._list_available_directories()
                return False

        # 檢查 output_url 目錄
        if args.from_latest and not os.path.exists("output_url"):
            print("錯誤：output_url 目錄不存在，請先執行爬蟲收集 URL")
            return False
            
        return True
    
    def _validate_filter_options(self, args):
        """驗證過濾器選項
        
        Args:
            args: 解析後的命令列參數
            
        Returns:
            bool: 驗證是否通過
        """
        # 檢查過濾器選項是否與正確的來源選項一起使用
        if (args.category or args.section) and not (args.from_latest or args.folder):
            print("錯誤：--category 和 --section 選項只能與 --from-latest 或 --folder 一起使用")
            return False
            
        return True
    
    def _list_available_directories(self):
        """列出可用的目錄"""
        print("可用的目錄：")
        if os.path.exists("output_url"):
            for item in os.listdir("output_url"):
                if os.path.isdir(os.path.join("output_url", item)):
                    print(f"  - {item}")
        else:
            print("  無可用目錄")
