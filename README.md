# 音頻降噪處理系統

這個專案提供多種音頻降噪算法和評估工具，用於優化音頻質量並分析處理效果。

## 功能特點

- 支持多種降噪方法，包括標準頻譜減法、小波降噪和增強型多階段降噪
- 自動評估音頻質量，包括SNR、RMS、峰值和變異係數等指標
- 提供完整的實驗比較功能，幫助選擇最佳降噪方法
- 生成豐富的可視化圖表，直觀展示處理效果

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
│       └── visualization.py # 可視化工具
├── data/                    # 數據目錄
│   └── audio_paired/        # 配對音頻目錄
├── results/                 # 結果輸出目錄
├── temp/                    # 臨時文件目錄
├── main.py                  # 主程式
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

## 使用方法

### 基本用法

```bash
# 使用預設方法處理音頻
python main.py

# 指定輸入和輸出目錄
python main.py --input_dir data/my_audio --output_dir my_results
```

### 選擇特定方法

```bash
# 使用小波降噪方法
python main.py --method wavelet

# 使用增強型多階段降噪
python main.py --method enhanced_multi_stage
```

### 比較不同方法

```bash
# 對同一組音頻比較所有降噪方法
python main.py --compare

# 比較並生成可視化結果
python main.py --compare --visualize
```

### 使用配置文件

```bash
# 使用JSON配置文件
python main.py --config my_config.json
```

配置文件示例:
```json
{
  "input_dir": "data/audio_paired",
  "output_dir": "results",
  "temp_dir": "temp",
  "selected_method": "enhanced_multi_stage",
  "create_plots": true,
  "methods": ["standard", "wavelet", "multi_stage", "enhanced_multi_stage"]
}
```

## 評估指標

- **信噪比 (SNR)**: 衡量信號與噪聲的比例
- **均方根 (RMS)**: 測量音頻的能量水平
- **峰值**: 測量音頻的最大振幅
- **變異係數 (CV)**: 衡量音量的穩定性
- **非語音比例**: 音頻中非語音部分的佔比
- **最大靜音段**: 最長連續靜音段的長度 (秒)