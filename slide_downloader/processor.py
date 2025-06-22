"""
SlideShare 簡報下載工具 - 結果處理模組

負責處理下載結果和顯示摘要資訊。
"""

import sys


class ResultProcessor:
    """下載結果處理器"""
    
    def __init__(self, slideshare_downloader):
        """初始化結果處理器
        
        Args:
            slideshare_downloader: SlideShareDownloader 實例
        """
        self.downloader = slideshare_downloader
    
    def process_results(self, results):
        """處理下載結果
        
        Args:
            results: 下載結果字典
        """
        # 檢查結果有效性
        if not self._validate_results(results):
            return
            
        # 檢查錯誤
        if self._check_errors(results):
            return
            
        # 顯示摘要
        self._display_summary(results)
        
        # 檢查失敗的下載
        self._check_failed_downloads(results)
        
        print("\n🎉 下載完成！")
    
    def _validate_results(self, results):
        """驗證結果有效性
        
        Args:
            results: 下載結果字典
            
        Returns:
            bool: 結果是否有效
        """
        if results is None:
            print("❌ 錯誤：下載操作未執行")
            sys.exit(1)
            
        return True
    
    def _check_errors(self, results):
        """檢查錯誤
        
        Args:
            results: 下載結果字典
            
        Returns:
            bool: 是否有錯誤
        """
        if "error" in results:
            print(f"❌ 錯誤：{results['error']}")
            sys.exit(1)
            
        return False
    
    def _display_summary(self, results):
        """顯示摘要
        
        Args:
            results: 下載結果字典
        """
        self.downloader.print_summary(results)
    
    def _check_failed_downloads(self, results):
        """檢查失敗的下載
        
        Args:
            results: 下載結果字典
        """
        # 檢查是否有失敗的下載
        if "total_summary" in results:
            failed = results["total_summary"].get("failed_downloads", 0)
        else:
            failed = results.get("summary", {}).get("failed_downloads", 0)

        if failed > 0:
            print(f"\n⚠️  有 {failed} 個簡報下載失敗，請檢查日誌檔案 slideshare_downloader.log")
