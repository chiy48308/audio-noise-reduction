#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
視覺化工具
提供音頻數據和實驗結果的可視化功能
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import seaborn as sns
from pathlib import Path

class AudioVisualizer:
    """音頻可視化器"""
    
    def __init__(self, output_dir="visualizations"):
        """初始化可視化器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def set_output_dir(self, output_dir):
        """設置輸出目錄"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_waveform(self, audio_data, sr, title="音頻波形", filename=None):
        """
        繪製音頻波形圖
        
        參數:
            audio_data: 音頻數據
            sr: 採樣率
            title: 標題
            filename: 輸出文件名
        """
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(audio_data, sr=sr)
        plt.title(title)
        plt.xlabel("時間 (秒)")
        plt.ylabel("振幅")
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        
        plt.close()
    
    def plot_spectrogram(self, audio_data, sr, title="頻譜圖", filename=None):
        """
        繪製頻譜圖
        
        參數:
            audio_data: 音頻數據
            sr: 採樣率
            title: 標題
            filename: 輸出文件名
        """
        plt.figure(figsize=(10, 6))
        
        # 計算短時傅立葉變換
        D = librosa.amplitude_to_db(abs(librosa.stft(audio_data)), ref=np.max)
        
        # 繪製頻譜圖
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title(title)
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        
        plt.close()
    
    def plot_audio_comparison(self, original_audio, processed_audio, sr, title="音頻對比", filename=None):
        """
        繪製原始音頻和處理後音頻的對比圖
        
        參數:
            original_audio: 原始音頻數據
            processed_audio: 處理後音頻數據
            sr: 採樣率
            title: 標題
            filename: 輸出文件名
        """
        plt.figure(figsize=(10, 8))
        
        # 繪製原始波形
        plt.subplot(2, 1, 1)
        librosa.display.waveshow(original_audio, sr=sr)
        plt.title("原始音頻")
        plt.xlabel("時間 (秒)")
        plt.ylabel("振幅")
        
        # 繪製處理後波形
        plt.subplot(2, 1, 2)
        librosa.display.waveshow(processed_audio, sr=sr)
        plt.title("處理後音頻")
        plt.xlabel("時間 (秒)")
        plt.ylabel("振幅")
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        
        plt.close()
    
    def plot_spectrum_comparison(self, original_audio, processed_audio, sr, title="頻譜對比", filename=None):
        """
        繪製原始音頻和處理後音頻的頻譜對比圖
        
        參數:
            original_audio: 原始音頻數據
            processed_audio: 處理後音頻數據
            sr: 採樣率
            title: 標題
            filename: 輸出文件名
        """
        plt.figure(figsize=(10, 8))
        
        # 計算原始音頻的短時傅立葉變換
        D_original = librosa.amplitude_to_db(abs(librosa.stft(original_audio)), ref=np.max)
        
        # 計算處理後音頻的短時傅立葉變換
        D_processed = librosa.amplitude_to_db(abs(librosa.stft(processed_audio)), ref=np.max)
        
        # 繪製原始頻譜圖
        plt.subplot(2, 1, 1)
        librosa.display.specshow(D_original, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title("原始音頻頻譜")
        
        # 繪製處理後頻譜圖
        plt.subplot(2, 1, 2)
        librosa.display.specshow(D_processed, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title("處理後音頻頻譜")
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        
        plt.close()

class ExperimentVisualizer:
    """實驗可視化器"""
    
    def __init__(self, output_dir="experiment_results"):
        """初始化可視化器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def set_output_dir(self, output_dir):
        """設置輸出目錄"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_metrics_improvement(self, results_df, metric, title=None, filename=None):
        """
        繪製指標改善圖
        
        參數:
            results_df: 實驗結果DataFrame
            metric: 要繪製的指標
            title: 標題
            filename: 輸出文件名
        """
        if not title:
            title = f"{metric} 改善圖"
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(results_df)), results_df[f'{metric}_improvement'])
        plt.axhline(y=0, color='r', linestyle='-')
        plt.title(title)
        plt.ylabel(f"{metric} 改善")
        plt.xlabel("音頻文件")
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        else:
            plt.savefig(self.output_dir / f"{metric}_improvement.png", dpi=300)
        
        plt.close()
    
    def plot_method_comparison(self, comparison_df, metric, title=None, filename=None):
        """
        繪製方法比較圖
        
        參數:
            comparison_df: 方法比較DataFrame
            metric: 要比較的指標
            title: 標題
            filename: 輸出文件名
        """
        if not title:
            title = f"不同方法的 {metric} 比較"
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='method', y=f'avg_{metric}_improvement', data=comparison_df)
        plt.title(title)
        plt.ylabel(f"{metric} 改善")
        plt.xlabel("降噪方法")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        else:
            plt.savefig(self.output_dir / f"methods_{metric}_comparison.png", dpi=300)
        
        plt.close()
    
    def plot_compliance_comparison(self, comparison_df, title=None, filename=None):
        """
        繪製符合標準率比較圖
        
        參數:
            comparison_df: 方法比較DataFrame
            title: 標題
            filename: 輸出文件名
        """
        if not title:
            title = "不同方法的符合標準率"
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='method', y='compliance_rate', data=comparison_df)
        plt.title(title)
        plt.ylabel("符合標準率")
        plt.xlabel("降噪方法")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        else:
            plt.savefig(self.output_dir / "methods_compliance_comparison.png", dpi=300)
        
        plt.close()
    
    def create_summary_report(self, results_df, method, title=None, filename=None):
        """
        創建摘要報告圖
        
        參數:
            results_df: 實驗結果DataFrame
            method: 降噪方法
            title: 標題
            filename: 輸出文件名
        """
        if not title:
            title = f"{method} 方法降噪效果摘要"
        
        plt.figure(figsize=(12, 10))
        
        # 信噪比改善
        plt.subplot(2, 2, 1)
        plt.bar(range(len(results_df)), results_df['snr_improvement'])
        plt.axhline(y=0, color='r', linestyle='-')
        plt.title("信噪比改善")
        plt.ylabel("SNR 改善 (dB)")
        
        # 變異係數改善
        plt.subplot(2, 2, 2)
        plt.bar(range(len(results_df)), results_df['cv_improvement'])
        plt.axhline(y=0, color='r', linestyle='-')
        plt.title("變異係數改善")
        plt.ylabel("CV 改善 (%)")
        
        # 原始vs處理後 SNR
        plt.subplot(2, 2, 3)
        plt.scatter(results_df['original_snr'], results_df['processed_snr'])
        plt.plot([0, 40], [0, 40], 'r--')  # 對角線
        plt.title("原始 vs. 處理後 SNR")
        plt.xlabel("原始 SNR (dB)")
        plt.ylabel("處理後 SNR (dB)")
        plt.grid(True)
        
        # 符合標準率
        plt.subplot(2, 2, 4)
        labels = ['原始音頻', '處理後音頻']
        values = [
            results_df['original_compliant'].mean() * 100,
            results_df['processed_compliant'].mean() * 100
        ]
        plt.bar(labels, values)
        plt.title("符合標準率")
        plt.ylabel("符合標準率 (%)")
        plt.ylim(0, 100)
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if filename:
            plt.savefig(self.output_dir / filename, dpi=300)
        else:
            plt.savefig(self.output_dir / f"{method}_summary_report.png", dpi=300)
        
        plt.close()