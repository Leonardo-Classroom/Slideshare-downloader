# SlideShare 下載工具 v2.0

這是一個功能完整、模組化的 SlideShare 網站簡報下載工具，採用兩步驟工作流程，確保高效率、可靠性和可追蹤性。

## 🎯 專案概覽

### 核心工作流程
```
步驟 1: URL 爬取          步驟 2: 簡報下載
┌─────────────────┐      ┌─────────────────┐
│  1_get_urls.py  │ ───► │ 2_download_slide│
│                 │ CSV  │      .py        │
│ 爬取 SlideShare │ 檔案 │ 下載投影片圖片  │
│ 簡報 URL 清單   │      │                 │
└─────────────────┘      └─────────────────┘
```

### 主要特色
- **🔍 智慧爬取**：支援 40+ 個類別和 3 種區塊類型
- **📥 高效下載**：自動圖片格式轉換和智慧檔案命名
- **⚡ 並行處理**：多視窗並行爬取和多執行緒下載
- **📁 完美組織**：時間戳目錄結構和 CSV 編號前綴
- **🔄 統一參數**：兩個步驟使用完全一致的參數體系
- **🛡️ 可靠性**：智慧重試機制和完善的錯誤處理

### 新功能亮點 (v2.0)
- **✨ 參數統一**：兩個步驟的參數名稱和邏輯完全統一
- **📊 CSV 編號前綴**：下載的簡報資料夾有對應的編號前綴
- **📂 時間戳目錄**：下載結果自動放入對應的時間戳資料夾
- **🎯 智慧路徑**：自動從 CSV 路徑推斷輸出目錄結構

## 📁 專案結構

```
slideshare_downloader/
├── 1_get_urls.py              # 步驟1：爬取 SlideShare URL
├── 2_download_slide.py        # 步驟2：下載簡報圖片
├── quick_start.py             # 🚀 快速開始腳本（推薦新手使用）
├── examples.py                # 📚 詳細使用範例腳本
├── slideshare_scraper/        # URL 爬取核心套件
│   ├── __init__.py           # 模組初始化
│   ├── constants.py          # 常數定義
│   ├── scraper.py            # 核心爬蟲類別
│   ├── downloader.py         # 簡報下載器
│   ├── parallel.py           # 並行處理模組
│   ├── utils.py              # 工具函數
│   └── cli.py                # 命令列介面
├── slide_downloader/          # 簡報下載核心套件
│   ├── __init__.py           # 套件初始化
│   ├── __main__.py           # 模組入口點
│   ├── cli.py                # 命令列介面
│   ├── validator.py          # 參數驗證模組
│   ├── downloader.py         # 下載邏輯模組
│   ├── processor.py          # 結果處理模組
│   └── README.md             # 套件說明
├── config.py                 # 爬蟲配置檔案
├── requirements.txt          # 依賴清單
└── README.md                 # 使用說明
```

## 🛠️ 安裝需求

### 系統需求
- Python 3.8+
- Chrome 或 Edge 瀏覽器

### 安裝依賴
```bash
pip install -r requirements.txt
```

## 🚀 快速開始

### 方式 1：使用快速開始腳本（推薦新手）
```bash
python quick_start.py
```
這個互動式腳本會引導您完成整個設定和執行過程，包括：
- ✅ 系統需求檢查
- ✅ 依賴自動安裝
- ✅ 參數互動式設定
- ✅ 完整工作流程執行
- ✅ 結果展示

### 方式 2：查看詳細範例
```bash
python examples.py
```
這個腳本包含各種使用場景的完整範例：
- ✅ 基本工作流程
- ✅ 並行工作流程
- ✅ 特定類別深度爬取
- ✅ CSV 檔案下載
- ✅ 說明和支援選項查看

### 方式 3：手動執行（進階用戶）
繼續閱讀下面的詳細說明。

## 🔄 詳細工作流程

SlideShare 下載工具採用清晰的兩步驟工作流程，確保高效率、可靠性和可追蹤性：

### 📋 工作流程圖
```
步驟 1: URL 爬取                    步驟 2: 簡報下載
┌─────────────────┐                ┌─────────────────┐
│  1_get_urls.py  │                │ 2_download_slide│
│                 │                │      .py        │
│ ┌─────────────┐ │   CSV 檔案     │ ┌─────────────┐ │
│ │ SlideShare  │ │ ────────────► │ │ 讀取 CSV    │ │
│ │ 網站爬取    │ │                │ │ 檔案        │ │
│ │             │ │                │ │             │ │
│ │ 收集 URL    │ │                │ │ 下載圖片    │ │
│ │ 和標題      │ │                │ │             │ │
│ └─────────────┘ │                │ └─────────────┘ │
└─────────────────┘                └─────────────────┘
        │                                   │
        ▼                                   ▼
   output_url/                         output_files/
   時間戳目錄/                         時間戳目錄/
   ├── *.csv                          ├── CSV檔案名稱/
   └── scrape_info.json               │   ├── 001_簡報1/
                                      │   │   ├── 圖片1.jpg
                                      │   │   └── 圖片2.jpg
                                      │   └── 002_簡報2/
                                      │       ├── 圖片1.jpg
                                      │       └── 圖片2.jpg
                                      └── ...
```

### 🔍 步驟 1：URL 爬取 (`1_get_urls.py`)
**主要目的**：從 SlideShare 網站爬取簡報的 URL 連結和標題
**輸入**：類別、區塊類型、數量等參數
**輸出**：包含簡報資訊的 CSV 檔案和元資料 JSON 檔案
**核心套件**：`slideshare_scraper`

**執行流程**：
1. **初始化瀏覽器**：根據參數設定 Chrome/Edge 瀏覽器
2. **訪問目標頁面**：導航到指定類別的 SlideShare 頁面
3. **定位區塊**：找到指定的區塊（Featured、Popular、New）
4. **滾動載入**：自動滾動頁面載入更多內容
5. **提取資料**：解析 HTML 提取簡報標題和 URL
6. **儲存結果**：將資料儲存為 CSV 檔案，元資料儲存為 JSON

### 📥 步驟 2：簡報下載 (`2_download_slide.py`)
**主要目的**：讀取步驟1產生的 CSV 檔案，下載每個簡報的所有投影片圖片
**輸入**：CSV 檔案路徑或時間戳目錄
**輸出**：按簡報分類整理的圖片檔案
**核心套件**：`slide_downloader`

**執行流程**：
1. **讀取 CSV 檔案**：解析步驟1產生的簡報清單
2. **初始化下載器**：設定瀏覽器和下載參數
3. **逐一訪問 URL**：開啟每個簡報的詳細頁面
4. **提取圖片連結**：分析頁面結構找到所有投影片圖片
5. **下載圖片**：批量下載並轉換格式（WebP → JPEG）
6. **整理檔案**：按簡報標題建立目錄並命名檔案

---

## 📖 使用方法

### 🔍 步驟 1：爬取 URL

```bash
# 使用預設設定（business, featured, 100筆）
python 1_get_urls.py

# 爬取特定類別和區塊
python 1_get_urls.py -c technology -s popular -n 50

# 使用無頭模式
python 1_get_urls.py -c business -s featured -n 100 --headless
```

#### 並行爬取 URL

```bash
# 並行爬取所有類別的 featured 區塊
python 1_get_urls.py -c all -s featured -n 50 -p 10 --headless

# 並行爬取單一類別的所有區塊
python 1_get_urls.py -c business -s all -n 30 -p 3

# 大規模並行爬取
python 1_get_urls.py -c all -s all -n 20 -p 5 --headless
```

#### 查看支援選項

```bash
# 列出所有支援的類別
python 1_get_urls.py --list-categories

# 列出所有支援的區塊類型
python 1_get_urls.py --list-sections

# 查看完整說明
python 1_get_urls.py --help
```

### 📥 步驟 2：下載簡報圖片

```bash
# 從指定時間戳目錄下載（推薦方式）
python 2_download_slide.py --folder "2025-06-23_02-34-27_category=business_section=featured_num=3_headless"

# 從指定目錄下載特定類別和區塊
python 2_download_slide.py --folder "2025-06-23_01-13-35_category=all_section=all_num=100_window=30" --category technology --section featured

# 從單一 CSV 檔案下載簡報圖片
python 2_download_slide.py --csv-file output_url/2025-06-23_01-13-35_category=all_section=all_num=100_window=30/Business_Featured.csv

# 從最新的 output_url 目錄下載
python 2_download_slide.py --from-latest

# 下載特定類別的簡報
python 2_download_slide.py --from-latest -c business

# 下載特定區塊類型的簡報
python 2_download_slide.py --from-latest -s featured

# 使用無頭模式下載
python 2_download_slide.py --folder "folder_name" --headless -d 2

# 使用多執行緒並行下載（3個工作執行緒）
python 2_download_slide.py --folder "folder_name" -p 3

# 組合使用：多執行緒 + 無頭模式 + 自訂延遲
python 2_download_slide.py --folder "folder_name" -p 2 --headless -d 0.5
```

### 🔄 完整工作流程範例

```bash
# 範例 1：基本工作流程
# 步驟 1：爬取 business 類別的 featured 區塊 URL（50筆）
python 1_get_urls.py -c business -s featured -n 50 --headless

# 步驟 2：下載剛才爬取的簡報圖片
python 2_download_slide.py --from-latest --category business --section featured

# 範例 2：大規模並行工作流程
# 步驟 1：並行爬取所有類別的所有區塊 URL（每個20筆，使用5個視窗）
python 1_get_urls.py -c all -s all -n 20 -p 5 --headless

# 步驟 2：並行下載所有爬取的簡報圖片（使用3個工作執行緒）
python 2_download_slide.py --from-latest -p 3

# 範例 3：特定類別工作流程
# 步驟 1：爬取 technology 類別的 popular 區塊 URL
python 1_get_urls.py -c technology -s popular -n 30

# 步驟 2：下載特定類別的簡報，使用預設顯示瀏覽器模式監控
python 2_download_slide.py --from-latest -c technology -s popular
```

## ⚙️ 參數說明

| 參數 | 簡寫 | 預設值 | 說明 |
|------|------|--------|------|
| `--category` | `-c` | `business` | 要爬取的類別，使用 `all` 爬取所有類別 |
| `--section` | `-s` | `featured` | 區塊類型：`featured`、`popular`、`new`、`all` |
| `--num` | `-n` | `100` | 每個任務要爬取的數量 |
| `--headless` | - | `False` | 使用無頭模式運行（不顯示瀏覽器視窗） |
| `--parallel` | `-p` | `10` | 並行數量（僅並行模式） |
| `--list-categories` | - | - | 列出所有支援的類別 |
| `--list-sections` | - | - | 列出所有支援的區塊類型 |

### 簡報下載參數

| 參數 | 簡寫 | 預設值 | 說明 |
|------|------|--------|------|
| `--folder` | - | - | 指定時間戳目錄名稱（推薦方式） |
| `--csv-file` | - | - | 指定單一 CSV 檔案路徑 |
| `--from-latest` | - | - | 從最新的 output_url 目錄下載 |
| `--category` | `-c` | - | 類別過濾器（與 --folder 或 --from-latest 一起使用） |
| `--section` | `-s` | - | 區塊過濾器（與 --folder 或 --from-latest 一起使用） |
| `--output-dir` | `-o` | `output_files` | 指定輸出目錄 |
| `--headless` | - | `False` | 使用無頭模式 |
| `--delay` | `-d` | `1.0` | 下載間隔時間（秒） |
| `--max-retries` | `-r` | `3` | 最大重試次數 |
| `--parallel` | `-p` | `1` | 並行工作執行緒數量 |

## 📂 輸出格式

### 檔案結構
```
output_url/                    # URL 收集結果
└── 2025-06-23_12-30-45_category=business_section=featured_num=100_headless/
    ├── Business_Featured.csv
    └── scrape_info.json

output_files/                  # 下載的簡報圖片
└── 2025-06-23_12-30-45_category=business_section=featured_num=100_headless/
    └── Business_Featured/
        ├── 001_The AI Rush/
        │   ├── The AI Rush_001.jpg
        │   ├── The AI Rush_002.jpg
        │   └── ... (32張投影片)
        ├── 002_APIdays Paris 2019 - Innovation @ scale/
        │   ├── APIdays Paris 2019 - Innovation @ scale_001.jpg
        │   ├── APIdays Paris 2019 - Innovation @ scale_002.jpg
        │   └── ... (28張投影片)
        └── 003_2017 holiday survey_ An annual analysis/
            ├── 2017 holiday survey_ An annual analysis_001.jpg
            ├── 2017 holiday survey_ An annual analysis_002.jpg
            └── ... (40張投影片)
```

### 目錄結構特點
- **時間戳目錄**：對應 URL 爬取的時間戳和參數
- **CSV 子目錄**：對應具體的 CSV 檔案（如 Business_Featured）
- **編號前綴**：簡報資料夾有三位數編號前綴（001_, 002_, 003_）
- **圖片檔案**：按順序編號的簡報圖片

### CSV 檔案格式
| 欄位 | 說明 |
|------|------|
| 編號 | 資料序號 |
| 標題 | 投影片標題 |
| 連結 | 投影片連結 |

### JSON 資訊檔案
```json
{
  "timestamp": "2025-06-23T12:30:45",
  "parameters": {
    "category": "business",
    "section": "featured",
    "num": 100,
    "headless": true
  },
  "results": {
    "total_tasks": 1,
    "successful_tasks": 1,
    "failed_tasks": 0,
    "total_data": 100,
    "execution_time": 45.2,
    "files": ["Business_Featured.csv"]
  },
  "system_info": {
    "python_version": "3.10.15",
    "platform": "nt",
    "browser": "Edge/Chrome"
  }
}
```

## 🎯 支援的類別

### 商業類別
- `business` - 商業
- `marketing` - 行銷
- `leadership-management` - 領導管理
- `recruiting-hr` - 招聘人力資源
- `retail` - 零售
- `sales` - 銷售
- `services` - 服務
- `small-business-entrepreneurship` - 小企業創業
- `economy-finance` - 經濟金融
- `data-analytics` - 資料分析
- `investor-relations` - 投資者關係

### 技術類別
- `technology` - 技術
- `mobile` - 行動裝置
- `software` - 軟體
- `engineering` - 工程
- `internet` - 網際網路
- `devices-hardware` - 設備硬體

### 創意類別
- `design` - 設計
- `art-photos` - 藝術攝影
- `presentations-public-speaking` - 簡報公開演講
- `entertainment-humor` - 娛樂幽默

### 社會類別
- `social-media` - 社群媒體
- `education` - 教育
- `career` - 職業
- `healthcare` - 醫療保健
- `health-medicine` - 健康醫學
- `government-nonprofit` - 政府非營利
- `law` - 法律
- `news-politics` - 新聞政治

### 生活類別
- `lifestyle` - 生活方式
- `food` - 食物
- `travel` - 旅遊
- `sports` - 運動
- `automotive` - 汽車
- `environment` - 環境
- `science` - 科學
- `spiritual` - 精神
- `self-improvement` - 自我提升
- `real-estate` - 房地產

## 🔧 進階配置

### 配置檔案 (config.py)
程式使用 `config.py` 進行詳細配置，包括：
- 瀏覽器設定
- 選擇器配置
- 超時時間
- 檔案格式
- 日誌設定

### 環境設定
支援三種環境模式：
- `development` - 開發模式（預設）
- `production` - 生產模式
- `testing` - 測試模式

## 🚨 注意事項

### 使用限制
- 請遵守 SlideShare 的使用條款
- 建議在非高峰時段進行大規模爬取
- 使用適當的延遲時間，避免對伺服器造成過大負載

### 效能建議
- 並行視窗數量建議不超過 10 個
- 大規模爬取時建議使用無頭模式
- 定期清理輸出目錄，避免佔用過多磁碟空間

### 故障排除
- 如果遇到 WebDriver 問題，請確認瀏覽器版本
- 網路連線問題可能導致爬取失敗，建議重試
- 檔案權限問題請檢查輸出目錄的寫入權限

## 🎯 使用場景和最佳實踐

### 場景 1：小規模測試
```bash
# 步驟 1：爬取少量資料進行測試
python 1_get_urls.py -c business -s featured -n 10

# 步驟 2：下載測試資料，使用預設顯示瀏覽器模式監控
python 2_download_slide.py --from-latest
```

### 場景 2：中等規模收集
```bash
# 步驟 1：爬取特定類別的資料
python 1_get_urls.py -c technology -s popular -n 50 --headless

# 步驟 2：並行下載，提高效率
python 2_download_slide.py --from-latest -p 2
```

### 場景 3：大規模資料收集
```bash
# 步驟 1：並行爬取多個類別
python 1_get_urls.py -c all -s all -n 20 -p 5 --headless

# 步驟 2：高並行下載
python 2_download_slide.py --from-latest -p 3 -d 0.5
```

## ⚡ 效能優化建議

### URL 爬取階段
- **並行數量**：使用 `-p` 參數，建議不超過 10 個
- **無頭模式**：大規模爬取時使用 `--headless` 提高效率
- **適當數量**：每個任務建議不超過 100 筆，避免單次執行時間過長

### 簡報下載階段
- **並行工作**：使用 `-p` 參數，建議 2-3 個
- **下載延遲**：使用 `-d` 參數控制請求頻率，避免被限制
- **分批處理**：大量簡報建議分批下載，避免記憶體不足

## 📊 監控和追蹤

### 進度監控
- 兩個步驟都提供即時進度顯示
- 詳細的日誌記錄所有操作
- 錯誤和重試資訊完整記錄

### 結果驗證
- 檢查 `scrape_info.json` 確認爬取結果
- 統計下載的圖片數量和檔案大小
- 驗證檔案完整性和格式正確性

### 除錯技巧
```bash
# 使用顯示瀏覽器模式觀察執行過程
python 1_get_urls.py -c business -s featured -n 5
python 2_download_slide.py --from-latest

# 檢查日誌檔案
tail -f slideshare_scraper.log
tail -f slideshare_downloader.log
```

## 📝 更新日誌

### v2.0.0 (2025-06-23) - 重大更新
- 🎉 **完全重構**：模組化架構，清晰的職責分離
- ✨ **參數統一**：兩個步驟使用完全一致的參數體系
- 📊 **CSV 編號前綴**：下載的簡報資料夾有對應的編號前綴
- 📂 **時間戳目錄**：下載結果自動放入對應的時間戳資料夾
- 🎯 **智慧路徑**：自動從 CSV 路徑推斷輸出目錄結構
- ⚡ **效能提升**：優化並行處理機制和 WebDriver 管理
- 🔧 **錯誤處理**：完善的重試機制和錯誤恢復
- 📚 **完整文檔**：整合所有說明到單一 README.md

#### 新功能詳細說明
- **統一參數系統**：
  - 共同參數：`-c`, `-s`, `-o`, `--headless`, `-p`
  - 簡寫支援：所有常用參數都有簡寫
  - 邏輯一致：瀏覽器模式統一使用 `--headless`

- **智慧目錄管理**：
  - 三層目錄結構：`output_files/時間戳目錄/CSV檔案名稱/編號_簡報標題/`
  - 自動編號前綴：`001_`, `002_`, `003_` 對應 CSV 順序
  - 路徑自動推斷：從 CSV 路徑自動創建對應輸出目錄

- **增強的用戶體驗**：
  - 互動式快速開始腳本
  - 豐富的使用範例
  - 詳細的進度監控和日誌

### v1.x.x
- 基礎爬取功能
- 簡單並行處理
- 基本錯誤處理

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 📄 授權

本專案採用 MIT 授權條款。

## 📞 支援和幫助

### 獲取幫助
- **查看說明**：`python 1_get_urls.py --help` 或 `python 2_download_slide.py --help`
- **快速開始**：`python quick_start.py`（推薦新手）
- **查看範例**：`python examples.py`
- **測試功能**：`python test_csv_numbering.py`

### 常見問題
- **依賴安裝**：`pip install -r requirements.txt`
- **瀏覽器版本**：確保 Chrome/Edge 是最新版本
- **網路連線**：確保可以訪問 SlideShare 網站
- **檔案權限**：確保有寫入輸出目錄的權限

### 聯繫方式
如有問題或建議，請透過以下方式聯繫：
- 提交 GitHub Issue
- 查看專案文檔和範例

## 🎉 總結

這個兩步驟工作流程設計確保了：
- **可靠性**：每個步驟獨立執行，失敗時可單獨重試
- **可追蹤性**：完整的日誌和元資料記錄
- **可擴展性**：支援從小規模測試到大規模生產
- **可維護性**：清晰的職責分離和模組化設計
- **易用性**：統一的參數體系和豐富的範例

---

**SlideShare 下載工具 v2.0** - 讓簡報收集變得簡單高效！ 🚀