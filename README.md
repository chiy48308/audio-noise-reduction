# 音頻降噪處理系統

這個專案提供多種音頻降噪算法和評估工具，用於優化音頻質量並分析處理效果。

## 功能特點

- 支持多種降噪方法，包括標準頻譜減法、小波降噪和增強型多階段降噪
- 自動評估音頻質量，包括SNR、RMS、峰值和變異係數等指標
- 提供完整的實驗比較功能，幫助選擇最佳降噪方法
- 生成豐富的可視化圖表，直觀展示處理效果
- **新增**: 實驗數據整理和報告生成功能，支持Excel和HTML格式

## 系統架構

```
audio-noise-reduction/
├── src/                     # 源代碼目錄
│   ├── core/                # 核心模組
│   │   ├── noise_reducer.py # 降噪處理器
│   │   └── evaluator.py     # 音頻評估器
│   ├── experiment/          # 實驗模組
│   │   └── experiment_runner.py # 實驗運行器
│   └── utils/               # 工具模組
│       ├── visualization.py # 可視化工具
│       ├── data_manager.py  # 數據管理工具
│       └── report_generator.py # 報告生成工具
├── data/                    # 數據目錄
│   └── audio_paired/        # 配對音頻目錄
├── results/                 # 結果輸出目錄
├── reports/                 # 報告輸出目錄
├── main.py                  # 主程式
├── data_organizer.py        # 數據整理工具
└── README.md                # 說明文檔
```

## 支持的降噪方法

1. **標準降噪 (standard)** - 基於頻譜減法的基礎降噪方法
2. **小波降噪 (wavelet)** - 使用小波變換進行降噪
3. **多階段降噪 (multi_stage)** - 結合頻譜減法和小波處理的多階段方法
4. **增強型多階段降噪 (enhanced_multi_stage)** - 包含增益控制和語音保護功能的進階方法

## 安裝和依賴

```bash
# 安裝依賴
pip install -r requirements.txt
```

主要依賴項:
- numpy
- pandas
- librosa
- scipy
- matplotlib
- seaborn
- soundfile
- jinja2
- openpyxl

## 使用方法

### 音頻處理

```bash
# 使用預設方法處理音頻
python main.py

# 指定輸入和輸出目錄
python main.py --input_dir data/my_audio --output_dir my_results

# 使用小波降噪方法
python main.py --method wavelet

# 比較並生成可視化結果
python main.py --compare --visualize
```

### 數據整理與報告生成

```bash
# 生成標準報告 (Excel + HTML)
python data_organizer.py

# 指定結果目錄和報告輸出目錄
python data_organizer.py --results_dir my_results --output_dir my_reports

# 僅生成HTML報告
python data_organizer.py --html

# 僅生成Excel摘要
python data_organizer.py --excel

# 生成實驗時間線
python data_organizer.py --timeline

# 執行所有數據整理和報告生成任務
python data_organizer.py --all
```

## 報告示例

HTML報告包含:
- 實驗摘要和最佳方法推薦
- 降噪方法比較表格
- SNR改善比較圖
- 合規率比較圖
- 多指標性能雷達圖

Excel報告包含:
- 方法比較摘要表
- 詳細統計數據
- 實驗時間線

## 評估指標

- **信噪比 (SNR)**: 衡量信號與噪聲的比例
- **均方根 (RMS)**: 測量音頻的能量水平
- **峰值**: 測量音頻的最大振幅
- **變異係數 (CV)**: 衡量音量的穩定性
- **非語音比例**: 音頻中非語音部分的佔比
- **最大靜音段**: 最長連續靜音段的長度 (秒)