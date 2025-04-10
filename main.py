#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音頻降噪系統主程式
提供命令行界面，執行降噪實驗
"""

import os
import argparse
import json
from pathlib import Path

from src.experiment.experiment_runner import NoiseReductionExperiment

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description="音頻降噪實驗系統")
    
    # 基本參數
    parser.add_argument("--input_dir", type=str, default="data/audio_paired",
                        help="輸入音頻目錄")
    parser.add_argument("--output_dir", type=str, default="results",
                        help="輸出結果目錄")
    parser.add_argument("--temp_dir", type=str, default="temp",
                        help="臨時文件目錄")
    
    # 降噪方法參數
    parser.add_argument("--method", type=str, default="enhanced_multi_stage",
                        choices=["standard", "wavelet", "multi_stage", "enhanced_multi_stage"],
                        help="降噪方法")
    
    # 實驗參數
    parser.add_argument("--compare", action="store_true",
                        help="比較所有降噪方法")
    parser.add_argument("--visualize", action="store_true",
                        help="生成可視化結果")
    parser.add_argument("--config", type=str, default=None,
                        help="配置文件路徑 (JSON 格式)")
    
    args = parser.parse_args()
    
    # 讀取配置文件
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            config = json.load(f)
    else:
        # 使用命令行參數構建配置
        config = {
            "input_dir": args.input_dir,
            "output_dir": args.output_dir,
            "temp_dir": args.temp_dir,
            "selected_method": args.method,
            "create_plots": args.visualize
        }
    
    # 初始化實驗
    experiment = NoiseReductionExperiment(config)
    
    # 執行實驗
    if args.compare:
        print("=== 比較不同降噪方法 ===")
        # 查找所有音頻文件
        input_files = []
        for ext in [".wav", ".mp3"]:
            input_files.extend(list(Path(args.input_dir).glob(f"*{ext}")))
        
        if input_files:
            comparison_df = experiment.compare_methods(input_files)
            
            # 顯示比較結果
            print("\n=== 方法比較結果 ===")
            print(comparison_df[["method", "avg_snr_improvement", "compliance_rate"]].round(2))
            
            # 找出最佳方法
            best_method = comparison_df.sort_values("avg_snr_improvement", ascending=False).iloc[0]["method"]
            print(f"\n推薦方法: {best_method}")
        else:
            print(f"錯誤: 未在 {args.input_dir} 中找到音頻文件")
    else:
        print(f"=== 使用 {args.method} 方法執行降噪 ===")
        results_df = experiment.run_experiment()
        
        if results_df is not None:
            # 顯示簡要結果
            improved_files = results_df[results_df["snr_improvement"] > 0].shape[0]
            total_files = results_df.shape[0]
            
            print(f"\n處理了 {total_files} 個文件，其中 {improved_files} 個 ({improved_files/total_files*100:.1f}%) 有SNR改善")
            print(f"平均SNR改善: {results_df['snr_improvement'].mean():.2f} dB")
            
            # 顯示符合標準的文件數量
            compliant_before = results_df[results_df["original_compliant"]].shape[0]
            compliant_after = results_df[results_df["processed_compliant"]].shape[0]
            
            print(f"符合標準的文件: {compliant_before} -> {compliant_after} ({(compliant_after-compliant_before)/total_files*100:.1f}% 改善)")

if __name__ == "__main__":
    main()