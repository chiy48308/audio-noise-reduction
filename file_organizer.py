#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件組織工具
整理和分類現有的CSV文件，將它們移動到適當的文件夾中
"""

import os
import shutil
import argparse
import glob
import re
from pathlib import Path
import pandas as pd

def organize_csv_files(source_dir=".", target_dir="organized_data", dry_run=False):
    """
    整理CSV文件，將它們分類並移動到指定的目錄結構中
    
    參數:
        source_dir: 源目錄，包含要整理的CSV文件
        target_dir: 目標目錄，用於存放整理後的文件
        dry_run: 如果為True，只顯示將執行的操作而不實際移動文件
    """
    # 創建目標目錄結構
    if not dry_run:
        os.makedirs(os.path.join(target_dir, "standard_evaluation"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "method_comparison"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "analysis_results"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "raw_data"), exist_ok=True)
    
    # 查找所有CSV文件
    csv_files = glob.glob(os.path.join(source_dir, "*.csv"))
    print(f"找到 {len(csv_files)} 個CSV文件")
    
    # 分類和移動文件
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        
        # 確定目標子目錄
        if "standard" in file_name.lower() and "noise_reduction" in file_name.lower():
            # 標準評估結果
            target_subdir = "standard_evaluation"
        elif "comparison" in file_name.lower() or "compare" in file_name.lower():
            # 方法比較結果
            target_subdir = "method_comparison"
        elif "analysis" in file_name.lower():
            # 分析結果
            target_subdir = "analysis_results"
        else:
            # 其他原始數據
            target_subdir = "raw_data"
        
        # 目標路徑
        target_path = os.path.join(target_dir, target_subdir, file_name)
        
        # 執行或模擬移動操作
        if dry_run:
            print(f"將移動: {file_path} -> {target_path}")
        else:
            print(f"移動: {file_path} -> {target_path}")
            shutil.copy2(file_path, target_path)  # 使用copy2保留元數據

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="CSV文件組織工具")
    
    parser.add_argument("--source", type=str, default=".",
                        help="源目錄，包含要整理的CSV文件")
    parser.add_argument("--target", type=str, default="organized_data",
                        help="目標目錄，用於存放整理後的文件")
    parser.add_argument("--move", action="store_true",
                        help="移動文件而不是複製")
    parser.add_argument("--dry-run", action="store_true",
                        help="只顯示將執行的操作而不實際移動文件")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("=== 試運行模式，不會執行實際操作 ===")
    
    organize_csv_files(args.source, args.target, args.dry_run)
    
    # 如果選擇移動文件而不是複製
    if args.move and not args.dry_run:
        print("\n=== 刪除原始文件 ===")
        csv_files = glob.glob(os.path.join(args.source, "*.csv"))
        for file_path in csv_files:
            target_exists = False
            file_name = os.path.basename(file_path)
            
            # 檢查文件是否已成功複製
            for subdir in ["standard_evaluation", "method_comparison", "analysis_results", "raw_data"]:
                check_path = os.path.join(args.target, subdir, file_name)
                if os.path.exists(check_path):
                    target_exists = True
                    break
            
            if target_exists:
                print(f"刪除: {file_path}")
                os.remove(file_path)
            else:
                print(f"警告: 文件可能未成功複製，不刪除: {file_path}")
    
    print("\n=== 文件整理完成 ===")
    if not args.dry_run:
        print(f"整理後的文件位於: {args.target}")

if __name__ == "__main__":
    main()