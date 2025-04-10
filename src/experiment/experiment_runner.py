#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
實驗運行器
用於執行降噪實驗並分析結果
"""

import os
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# 導入自定義模塊
from src.core.noise_reducer import NoiseReducer
from src.core.evaluator import AudioEvaluator

# 忽略警告
warnings.filterwarnings("ignore")

class NoiseReductionExperiment:
    """降噪實驗運行器"""
    
    def __init__(self, config=None):
        """初始化實驗運行器"""
        # 預設配置
        self.config = {
            'input_dir': 'data/audio_paired',
            'output_dir': 'results',
            'temp_dir': 'temp',
            'methods': ['standard', 'wavelet', 'multi_stage', 'enhanced_multi_stage'],
            'selected_method': 'enhanced_multi_stage',
            'create_plots': True
        }
        
        # 更新配置
        if config:
            self.config.update(config)
        
        # 確保目錄存在
        os.makedirs(self.config['output_dir'], exist_ok=True)
        os.makedirs(self.config['temp_dir'], exist_ok=True)
        
        # 初始化評估器和降噪器
        self.evaluator = AudioEvaluator()
        self.noise_reducer = NoiseReducer()
        
        # 儲存結果
        self.results = []
        self.comparison_results = {}
    
    def process_file(self, audio_file, method='enhanced_multi_stage'):
        """
        處理單個音頻文件
        
        參數:
            audio_file: 音頻文件路徑
            method: 降噪方法
            
        返回值:
            processed_audio: 處理後的音頻
            sr: 採樣率
        """
        # 讀取音頻
        audio_data, sr = librosa.load(audio_file, sr=None)
        
        # 設置降噪器採樣率
        self.noise_reducer.sample_rate = sr
        
        # 應用選擇的降噪方法
        if method == 'standard':
            processed_audio = self.noise_reducer.reduce_noise_standard(audio_data)
        elif method == 'wavelet':
            processed_audio = self.noise_reducer.reduce_noise_wavelet(audio_data)
        elif method == 'multi_stage':
            processed_audio = self.noise_reducer.multi_stage_denoising(audio_data)
        elif method == 'enhanced_multi_stage':
            processed_audio = self.noise_reducer.enhanced_multi_stage_denoising(audio_data)
        else:
            print(f"未知方法: {method}, 使用預設方法 enhanced_multi_stage")
            processed_audio = self.noise_reducer.enhanced_multi_stage_denoising(audio_data)
        
        return processed_audio, sr
    
    def analyze_audio_pair(self, original_file, processed_file):
        """
        分析原始音頻和處理後音頻
        
        參數:
            original_file: 原始音頻文件路徑
            processed_file: 處理後音頻文件路徑
            
        返回值:
            result: 分析結果字典
        """
        # 讀取音頻
        original_audio, sr = librosa.load(original_file, sr=None)
        processed_audio, _ = librosa.load(processed_file, sr=sr)
        
        # 確保長度相同
        min_len = min(len(original_audio), len(processed_audio))
        original_audio = original_audio[:min_len]
        processed_audio = processed_audio[:min_len]
        
        # 獲取文件名
        filename = os.path.basename(original_file)
        
        # 評估原始音頻
        original_metrics, original_compliant = self.evaluator.evaluate_audio(original_audio, sr)
        
        # 評估處理後音頻
        processed_metrics, processed_compliant = self.evaluator.evaluate_audio(processed_audio, sr)
        
        # 計算改善程度
        improvements = {
            'rms_improvement': ((processed_metrics['rms'] - original_metrics['rms']) / original_metrics['rms']) * 100 if original_metrics['rms'] > 0 else 0,
            'peak_improvement': ((processed_metrics['peak'] - original_metrics['peak']) / original_metrics['peak']) * 100 if original_metrics['peak'] > 0 else 0,
            'snr_improvement': processed_metrics['snr'] - original_metrics['snr'],
            'cv_improvement': ((processed_metrics['cv'] - original_metrics['cv']) / original_metrics['cv']) * 100 if original_metrics['cv'] > 0 else 0
        }
        
        # 合併結果
        result = {
            'filename': filename,
            'original_compliant': original_compliant,
            'processed_compliant': processed_compliant,
            **{f'original_{k}': v for k, v in original_metrics.items()},
            **{f'processed_{k}': v for k, v in processed_metrics.items()},
            **improvements
        }
        
        return result
    
    def run_experiment(self, input_dir=None, output_dir=None, method=None):
        """
        運行實驗
        
        參數:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            method: 降噪方法
            
        返回值:
            results_df: 實驗結果DataFrame
        """
        # 如果提供參數，則更新配置
        if input_dir:
            self.config['input_dir'] = input_dir
        if output_dir:
            self.config['output_dir'] = output_dir
        if method:
            self.config['selected_method'] = method
        
        # 獲取輸入文件
        input_dir = Path(self.config['input_dir'])
        output_dir = Path(self.config['output_dir'])
        method = self.config['selected_method']
        
        # 找到所有音頻文件
        audio_files = []
        for ext in ['.wav', '.mp3']:
            audio_files.extend(list(input_dir.glob(f'*{ext}')))
        
        if not audio_files:
            print(f"在 {input_dir} 中未找到音頻文件")
            return None
        
        print(f"開始處理 {len(audio_files)} 個音頻文件，使用方法: {method}")
        
        # 清空結果
        self.results = []
        
        # 處理每個文件
        for audio_file in tqdm(audio_files):
            try:
                # 處理音頻
                processed_audio, sr = self.process_file(audio_file, method)
                
                # 設置輸出文件路徑
                output_file = output_dir / f"processed_{audio_file.name}"
                
                # 保存處理後的音頻
                sf.write(output_file, processed_audio, sr)
                
                # 分析結果
                result = self.analyze_audio_pair(audio_file, output_file)
                self.results.append(result)
                
            except Exception as e:
                print(f"處理文件 {audio_file} 時出錯: {str(e)}")
        
        # 創建結果DataFrame
        if self.results:
            results_df = pd.DataFrame(self.results)
            
            # 保存結果
            csv_file = output_dir / f"noise_reduction_{method}_results.csv"
            results_df.to_csv(csv_file, index=False)
            
            # 生成可視化
            if self.config['create_plots']:
                self.create_visualizations(results_df, output_dir, method)
            
            return results_df
        else:
            print("沒有得到任何結果")
            return None
    
    def compare_methods(self, input_files, output_dir=None):
        """
        比較不同降噪方法
        
        參數:
            input_files: 要處理的音頻文件
            output_dir: 輸出目錄
            
        返回值:
            comparison_df: 比較結果DataFrame
        """
        if output_dir:
            self.config['output_dir'] = output_dir
        
        output_dir = Path(self.config['output_dir'])
        
        # 準備結果收集
        comparison_results = {
            'method': [],
            'avg_snr_improvement': [],
            'avg_cv_improvement': [],
            'avg_rms_improvement': [],
            'avg_peak_improvement': [],
            'compliance_rate': []
        }
        
        # 對每種方法運行實驗
        for method in self.config['methods']:
            print(f"\n=== 方法: {method} ===")
            
            method_results = []
            compliance_count = 0
            
            # 對每個文件運行降噪
            for audio_file in tqdm(input_files):
                try:
                    # 處理音頻
                    processed_audio, sr = self.process_file(audio_file, method)
                    
                    # 設置臨時輸出文件
                    temp_file = Path(self.config['temp_dir']) / f"{method}_{Path(audio_file).name}"
                    
                    # 保存處理後的音頻
                    sf.write(temp_file, processed_audio, sr)
                    
                    # 分析結果
                    result = self.analyze_audio_pair(audio_file, temp_file)
                    method_results.append(result)
                    
                    # 計算符合標準的數量
                    if result['processed_compliant']:
                        compliance_count += 1
                        
                except Exception as e:
                    print(f"處理文件 {audio_file} 時出錯: {str(e)}")
            
            # 如果有結果
            if method_results:
                # 計算平均改善
                avg_snr_improvement = np.mean([r['snr_improvement'] for r in method_results])
                avg_cv_improvement = np.mean([r['cv_improvement'] for r in method_results])
                avg_rms_improvement = np.mean([r['rms_improvement'] for r in method_results])
                avg_peak_improvement = np.mean([r['peak_improvement'] for r in method_results])
                compliance_rate = compliance_count / len(method_results)
                
                # 添加到比較結果
                comparison_results['method'].append(method)
                comparison_results['avg_snr_improvement'].append(avg_snr_improvement)
                comparison_results['avg_cv_improvement'].append(avg_cv_improvement)
                comparison_results['avg_rms_improvement'].append(avg_rms_improvement)
                comparison_results['avg_peak_improvement'].append(avg_peak_improvement)
                comparison_results['compliance_rate'].append(compliance_rate)
        
        # 創建比較DataFrame
        comparison_df = pd.DataFrame(comparison_results)
        
        # 保存結果
        csv_file = output_dir / "method_comparison_results.csv"
        comparison_df.to_csv(csv_file, index=False)
        
        # 創建比較可視化
        self.create_comparison_visualizations(comparison_df, output_dir)
        
        return comparison_df
    
    def create_comparison_visualizations(self, comparison_df, output_dir):
        """
        創建方法比較可視化
        
        參數:
            comparison_df: 比較結果DataFrame
            output_dir: 輸出目錄
        """
        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='method', y='avg_snr_improvement', data=comparison_df)
        plt.title('不同方法的平均信噪比改善')
        plt.ylabel('信噪比改善 (dB)')
        plt.xlabel('降噪方法')
        plt.tight_layout()
        plt.savefig(output_dir / 'methods_snr_comparison.png', dpi=300)
        plt.close()
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='method', y='compliance_rate', data=comparison_df)
        plt.title('不同方法的符合標準率')
        plt.ylabel('符合標準率')
        plt.xlabel('降噪方法')
        plt.tight_layout()
        plt.savefig(output_dir / 'methods_compliance_comparison.png', dpi=300)
        plt.close()
    
    def create_visualizations(self, results_df, output_dir, method):
        """
        創建實驗結果可視化
        
        參數:
            results_df: 實驗結果DataFrame
            output_dir: 輸出目錄
            method: 降噪方法
        """
        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # 繪製SNR改善
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(results_df)), results_df['snr_improvement'])
        plt.axhline(y=0, color='r', linestyle='-')
        plt.title(f'{method} 方法的信噪比改善')
        plt.ylabel('信噪比改善 (dB)')
        plt.xlabel('音頻文件')
        plt.tight_layout()
        plt.savefig(output_dir / f'{method}_snr_improvement.png', dpi=300)
        plt.close()
        
        # 繪製SNR對比圖
        plt.figure(figsize=(10, 6))
        plt.scatter(results_df['original_snr'], results_df['processed_snr'])
        plt.plot([0, 40], [0, 40], 'r--')  # 對角線
        plt.title(f'{method} 方法前後信噪比對比')
        plt.xlabel('原始SNR (dB)')
        plt.ylabel('處理後SNR (dB)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_dir / f'{method}_snr_comparison.png', dpi=300)
        plt.close()