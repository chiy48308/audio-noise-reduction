#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據管理模組
用於整理、整合和分析實驗數據
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import glob
from datetime import datetime

class ExperimentDataManager:
    """實驗數據管理器類"""
    
    def __init__(self, results_dir="results"):
        """初始化數據管理器"""
        self.results_dir = Path(results_dir)
        self.data_cache = {}  # 用於緩存已加載的數據
        self.summary_data = None  # 用於存儲匯總數據
    
    def set_results_dir(self, results_dir):
        """設置結果目錄"""
        self.results_dir = Path(results_dir)
        # 清空緩存
        self.data_cache = {}
        self.summary_data = None
    
    def load_result_file(self, file_path):
        """
        加載單個結果文件
        
        參數:
            file_path: 結果文件路徑
            
        返回值:
            數據 DataFrame
        """
        file_path = Path(file_path)
        
        # 檢查文件是否存在
        if not file_path.exists():
            print(f"錯誤: 文件 {file_path} 不存在")
            return None
        
        # 檢查文件類型並加載
        if file_path.suffix.lower() == '.csv':
            try:
                df = pd.read_csv(file_path)
                # 保存到緩存
                self.data_cache[str(file_path)] = df
                return df
            except Exception as e:
                print(f"無法加載CSV文件 {file_path}: {str(e)}")
                return None
        elif file_path.suffix.lower() == '.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 轉換為DataFrame
                df = pd.DataFrame(data)
                # 保存到緩存
                self.data_cache[str(file_path)] = df
                return df
            except Exception as e:
                print(f"無法加載JSON文件 {file_path}: {str(e)}")
                return None
        else:
            print(f"不支持的文件格式: {file_path.suffix}")
            return None
    
    def load_all_results(self, pattern="*.csv"):
        """
        加載所有符合模式的結果文件
        
        參數:
            pattern: 文件匹配模式
            
        返回值:
            字典 {文件名: 數據DataFrame}
        """
        # 查找所有匹配的文件
        files = list(self.results_dir.glob(pattern))
        
        if not files:
            print(f"在 {self.results_dir} 中未找到匹配 {pattern} 的文件")
            return {}
        
        results = {}
        for file in files:
            df = self.load_result_file(file)
            if df is not None:
                results[file.name] = df
        
        return results
    
    def aggregate_method_results(self, method_pattern="noise_reduction_*_results.csv"):
        """
        匯總所有方法的結果文件
        
        參數:
            method_pattern: 方法結果文件匹配模式
            
        返回值:
            匯總後的 DataFrame
        """
        # 加載所有方法結果
        method_results = self.load_all_results(method_pattern)
        
        if not method_results:
            return None
        
        # 提取方法名稱並合併數據
        all_data = []
        for filename, df in method_results.items():
            # 從文件名提取方法名
            method = filename.replace("noise_reduction_", "").replace("_results.csv", "")
            df['method'] = method
            all_data.append(df)
        
        # 合併所有數據
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            self.summary_data = combined_df
            return combined_df
        else:
            return None
    
    def generate_summary_stats(self):
        """
        生成匯總統計信息
        
        返回值:
            統計摘要 DataFrame
        """
        if self.summary_data is None:
            self.aggregate_method_results()
        
        if self.summary_data is None:
            print("無法生成統計摘要: 沒有可用的數據")
            return None
        
        # 按方法分組計算統計量
        stats = self.summary_data.groupby('method').agg({
            'snr_improvement': ['mean', 'std', 'min', 'max'],
            'cv_improvement': ['mean', 'std', 'min', 'max'],
            'processed_compliant': ['mean', 'sum', 'count']
        })
        
        # 添加合規率
        stats[('processed_compliant', 'rate')] = (
            stats[('processed_compliant', 'sum')] / stats[('processed_compliant', 'count')]
        )
        
        return stats
    
    def export_summary(self, output_file="experiment_summary.csv"):
        """
        導出數據摘要
        
        參數:
            output_file: 輸出文件名
        """
        stats = self.generate_summary_stats()
        
        if stats is None:
            return
        
        # 重置列索引為單層
        stats.columns = [f"{col[0]}_{col[1]}" for col in stats.columns]
        stats = stats.reset_index()
        
        # 保存到文件
        output_path = self.results_dir / output_file
        stats.to_csv(output_path, index=False)
        print(f"摘要統計已保存至 {output_path}")
        
        return output_path
    
    def export_combined_data(self, output_file="all_experiment_data.csv"):
        """
        導出合併後的所有數據
        
        參數:
            output_file: 輸出文件名
        """
        if self.summary_data is None:
            self.aggregate_method_results()
        
        if self.summary_data is None:
            print("無法導出合併數據: 沒有可用的數據")
            return
        
        # 保存到文件
        output_path = self.results_dir / output_file
        self.summary_data.to_csv(output_path, index=False)
        print(f"合併數據已保存至 {output_path}")
        
        return output_path
    
    def create_method_comparison_report(self, output_file="method_comparison_report.csv"):
        """
        創建方法比較報告
        
        參數:
            output_file: 輸出文件名
            
        返回值:
            比較報告 DataFrame
        """
        if self.summary_data is None:
            self.aggregate_method_results()
        
        if self.summary_data is None:
            print("無法創建方法比較報告: 沒有可用的數據")
            return None
        
        # 按方法分組計算關鍵指標
        report = self.summary_data.groupby('method').agg({
            'snr_improvement': 'mean',
            'cv_improvement': 'mean',
            'rms_improvement': 'mean',
            'peak_improvement': 'mean',
            'processed_compliant': 'mean'
        }).reset_index()
        
        # 重命名列
        report = report.rename(columns={
            'snr_improvement': 'avg_snr_improvement',
            'cv_improvement': 'avg_cv_improvement',
            'rms_improvement': 'avg_rms_improvement',
            'peak_improvement': 'avg_peak_improvement',
            'processed_compliant': 'compliance_rate'
        })
        
        # 排序 (按SNR改善)
        report = report.sort_values('avg_snr_improvement', ascending=False)
        
        # 保存到文件
        output_path = self.results_dir / output_file
        report.to_csv(output_path, index=False)
        print(f"方法比較報告已保存至 {output_path}")
        
        return report
    
    def create_experiment_timeline(self, output_file="experiment_timeline.csv"):
        """
        創建實驗時間線 (基於文件修改時間)
        
        參數:
            output_file: 輸出文件名
        """
        # 獲取所有結果文件
        all_files = list(self.results_dir.glob("*.csv"))
        
        timeline_data = []
        for file in all_files:
            # 獲取文件修改時間
            mod_time = datetime.fromtimestamp(file.stat().st_mtime)
            
            # 提取方法名 (如果適用)
            method = "unknown"
            if "noise_reduction_" in file.name and "_results.csv" in file.name:
                method = file.name.replace("noise_reduction_", "").replace("_results.csv", "")
            
            # 添加到數據
            timeline_data.append({
                'file': file.name,
                'method': method,
                'timestamp': mod_time,
                'size_kb': file.stat().st_size / 1024
            })
        
        # 創建DataFrame並排序
        timeline_df = pd.DataFrame(timeline_data)
        timeline_df = timeline_df.sort_values('timestamp')
        
        # 保存到文件
        output_path = self.results_dir / output_file
        timeline_df.to_csv(output_path, index=False)
        print(f"實驗時間線已保存至 {output_path}")
        
        return timeline_df