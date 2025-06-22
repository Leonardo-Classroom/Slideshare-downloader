#!/usr/bin/env python3
"""
SlideShare 爬蟲工具函數

包含路徑處理、檔案操作、URL 生成等工具函數。
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

from .constants import (
    SLIDESHARE_CATEGORY_URL_TEMPLATE,
    OUTPUT_BASE_DIR,
    SCRAPE_INFO_FILENAME,
    PATH_FORMAT_TEMPLATE,
    PATH_OPTIONAL_COMPONENTS,
    DATE_FORMAT,
    TIME_FORMAT,
    TIMESTAMP_FORMAT
)


def get_category_url(category: str) -> str:
    """
    根據類別名稱生成 SlideShare URL
    
    Args:
        category: 類別名稱
        
    Returns:
        完整的 SlideShare 類別 URL
    """
    return SLIDESHARE_CATEGORY_URL_TEMPLATE.format(category=category)


def generate_output_path(category: str, section: str, num: int, 
                        window_num: Optional[int] = None, 
                        headless: bool = False) -> str:
    """
    生成詳細的輸出路徑
    
    格式：output/{YYYY-MM-DD}_{HH-MM-SS}_category={category}_section={section}_num={num}[_window={window_num}][_headless]/
    
    Args:
        category: 類別名稱
        section: 區塊類型
        num: 爬取數量
        window_num: 並行視窗數（可選）
        headless: 是否無頭模式
        
    Returns:
        完整的輸出路徑
    """
    # 生成時間戳
    now = datetime.now()
    date_str = now.strftime(DATE_FORMAT)
    time_str = now.strftime(TIME_FORMAT)
    
    # 基本路徑組件
    path_components = [
        PATH_FORMAT_TEMPLATE.format(
            date=date_str,
            time=time_str,
            category=category,
            section=section,
            num=num
        )
    ]
    
    # 添加可選組件
    if window_num is not None and window_num > 1:
        path_components.append(PATH_OPTIONAL_COMPONENTS["window"].format(window_num=window_num))
    
    if headless:
        path_components.append(PATH_OPTIONAL_COMPONENTS["headless"])
    
    # 組合路徑
    folder_name = "_".join(path_components)
    return os.path.join(OUTPUT_BASE_DIR, folder_name)


def save_scrape_info(output_dir: str, parameters: Dict, results: Dict) -> None:
    """
    儲存爬取資訊到 JSON 檔案
    
    Args:
        output_dir: 輸出目錄
        parameters: 爬取參數
        results: 爬取結果
    """
    try:
        # 確保目錄存在
        ensure_directory_exists(output_dir)
        
        # 準備資訊
        scrape_info = {
            "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
            "parameters": parameters,
            "results": results,
            "system_info": get_system_info()
        }
        
        # 儲存到檔案
        info_file = os.path.join(output_dir, SCRAPE_INFO_FILENAME)
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(scrape_info, f, indent=2, ensure_ascii=False)
        
        print(f"📄 爬取資訊已儲存至：{info_file}")
        
    except Exception as e:
        print(f"⚠️  儲存爬取資訊時發生錯誤：{e}")


def get_system_info() -> Dict[str, str]:
    """
    獲取系統資訊
    
    Returns:
        包含系統資訊的字典
    """
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": os.name,
        "browser": "Edge/Chrome"
    }


def ensure_directory_exists(directory: str) -> None:
    """
    確保目錄存在，如果不存在則創建
    
    Args:
        directory: 目錄路徑
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def move_files_to_output_path(source_dir: str, target_dir: str, 
                             file_pattern: str = None) -> List[str]:
    """
    將檔案從來源目錄移動到目標目錄
    
    Args:
        source_dir: 來源目錄
        target_dir: 目標目錄
        file_pattern: 檔案模式（可選）
        
    Returns:
        成功移動的檔案列表
    """
    moved_files = []
    
    if not os.path.exists(source_dir):
        return moved_files
    
    # 確保目標目錄存在
    ensure_directory_exists(target_dir)
    
    # 移動檔案
    for filename in os.listdir(source_dir):
        if file_pattern and not filename.endswith(file_pattern):
            continue
            
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, filename)
        
        try:
            os.rename(source_path, target_path)
            moved_files.append(filename)
        except Exception as e:
            print(f"⚠️  移動檔案 {filename} 時發生錯誤：{e}")
    
    return moved_files


def count_csv_data(filepath: str) -> int:
    """
    計算 CSV 檔案的資料筆數（扣除標題行）
    
    Args:
        filepath: CSV 檔案路徑
        
    Returns:
        資料筆數
    """
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            return sum(1 for _ in f) - 1  # 扣除標題行
    except Exception:
        return 0


def find_latest_files_by_pattern(directory: str, pattern: str) -> List[str]:
    """
    根據模式找到最新的檔案
    
    Args:
        directory: 搜尋目錄
        pattern: 檔案模式
        
    Returns:
        符合模式的檔案列表（按修改時間排序）
    """
    if not os.path.exists(directory):
        return []
    
    matching_files = []
    for filename in os.listdir(directory):
        if filename.endswith(pattern):
            filepath = os.path.join(directory, filename)
            mtime = os.path.getmtime(filepath)
            matching_files.append((filename, mtime))
    
    # 按修改時間排序（最新的在前）
    matching_files.sort(key=lambda x: x[1], reverse=True)
    
    return [filename for filename, _ in matching_files]


def format_execution_time(seconds: float) -> str:
    """
    格式化執行時間
    
    Args:
        seconds: 秒數
        
    Returns:
        格式化的時間字串
    """
    if seconds < 60:
        return f"{seconds:.1f} 秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)} 分 {remaining_seconds:.1f} 秒"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{int(hours)} 小時 {int(remaining_minutes)} 分"


def validate_category(category: str, supported_categories: List[str]) -> bool:
    """
    驗證類別是否支援
    
    Args:
        category: 類別名稱
        supported_categories: 支援的類別列表
        
    Returns:
        是否支援
    """
    return category == "all" or category in supported_categories


def validate_section(section: str, supported_sections: List[str]) -> bool:
    """
    驗證區塊類型是否支援
    
    Args:
        section: 區塊類型
        supported_sections: 支援的區塊類型列表
        
    Returns:
        是否支援
    """
    return section == "all" or section in supported_sections
