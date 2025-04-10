#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
專案整理工具
建立標準化的專案目錄結構，並將現有文件分類存放
"""

import os
import shutil
import argparse
import glob
import re
from pathlib import Path
import sys
from tqdm import tqdm

def create_directory_structure(base_dir="."):
    """
    創建標準化的專案目錄結構
    
    參數:
        base_dir: 專案根目錄
    """
    directories = [
        "data/audio_paired",
        "data/audio_samples",
        "results/standard_evaluation",
        "results/method_comparison",
        "results/analysis_results",
        "results/raw_data",
        "reports/html",
        "reports/excel",
        "reports/visualizations",
        "temp",
    ]
    
    print("創建目錄結構...")
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"  創建: {dir_path}")

def organize_csv_files(base_dir=".", dry_run=False):
    """
    整理CSV文件到適當的目錄
    
    參數:
        base_dir: 專案根目錄
        dry_run: 如果為True，只顯示將執行的操作而不實際移動文件
    """
    # 查找根目錄下的所有CSV文件
    csv_files = glob.glob(os.path.join(base_dir, "*.csv"))
    
    if not csv_files:
        print("未找到CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 個CSV文件，開始分類...")
    
    for file_path in tqdm(csv_files, desc="整理CSV文件"):
        file_name = os.path.basename(file_path)
        
        # 根據文件名分類
        if "standard" in file_name.lower() and "noise_reduction" in file_name.lower():
            # 標準評估結果
            target_dir = os.path.join(base_dir, "results/standard_evaluation")
        elif "comparison" in file_name.lower() or "compare" in file_name.lower():
            # 方法比較結果
            target_dir = os.path.join(base_dir, "results/method_comparison")
        elif "analysis" in file_name.lower():
            # 分析結果
            target_dir = os.path.join(base_dir, "results/analysis_results")
        else:
            # 其他原始數據
            target_dir = os.path.join(base_dir, "results/raw_data")
        
        target_path = os.path.join(target_dir, file_name)
        
        if dry_run:
            print(f"將移動: {file_path} -> {target_path}")
        else:
            shutil.copy2(file_path, target_path)

def organize_audio_files(base_dir=".", dry_run=False):
    """
    整理音頻文件到適當的目錄
    
    參數:
        base_dir: 專案根目錄
        dry_run: 如果為True，只顯示將執行的操作而不實際移動文件
    """
    # 查找所有音頻文件
    audio_extensions = ["*.wav", "*.mp3", "*.flac", "*.ogg"]
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(base_dir, ext)))
    
    if not audio_files:
        print("未找到音頻文件")
        return
    
    print(f"找到 {len(audio_files)} 個音頻文件，開始分類...")
    
    # 音頻目標目錄
    paired_dir = os.path.join(base_dir, "data/audio_paired")
    samples_dir = os.path.join(base_dir, "data/audio_samples")
    
    for file_path in tqdm(audio_files, desc="整理音頻文件"):
        file_name = os.path.basename(file_path)
        
        # 判斷是否為成對音頻
        if "teacher" in file_name.lower() or "student" in file_name.lower():
            target_dir = paired_dir
        else:
            target_dir = samples_dir
        
        target_path = os.path.join(target_dir, file_name)
        
        if dry_run:
            print(f"將移動: {file_path} -> {target_path}")
        else:
            shutil.copy2(file_path, target_path)

def organize_python_files(base_dir=".", dry_run=False):
    """
    整理分散的Python文件
    
    參數:
        base_dir: 專案根目錄
        dry_run: 如果為True，只顯示將執行的操作而不實際移動文件
    """
    # 獲取根目錄中的主要Python文件 (跳過我們剛建立的文件)
    skip_files = ["main.py", "data_organizer.py", "file_organizer.py", "organize_project.py"]
    python_files = []
    
    for py_file in glob.glob(os.path.join(base_dir, "*.py")):
        if os.path.basename(py_file) not in skip_files:
            python_files.append(py_file)
    
    # 創建備份目錄
    if not dry_run:
        os.makedirs(os.path.join(base_dir, "python_backup"), exist_ok=True)
    
    print(f"找到 {len(python_files)} 個需要備份的Python文件...")
    
    # 備份這些文件
    for file_path in python_files:
        file_name = os.path.basename(file_path)
        backup_path = os.path.join(base_dir, "python_backup", file_name)
        
        if dry_run:
            print(f"將備份: {file_path} -> {backup_path}")
        else:
            shutil.copy2(file_path, backup_path)
            print(f"已備份: {file_path} -> {backup_path}")

def check_files_exist(base_dir="."):
    """
    檢查專案中重要的文件是否存在
    
    參數:
        base_dir: 專案根目錄
        
    返回值:
        布爾值，指示是否所有重要文件都存在
    """
    important_files = [
        "main.py",
        "src/core/noise_reducer.py",
        "src/core/evaluator.py",
        "src/experiment/experiment_runner.py",
        "src/utils/visualization.py",
        "src/utils/data_manager.py",
        "README.md",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in important_files:
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("警告: 以下重要文件缺失:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    return True

def clean_up_original_files(base_dir=".", dry_run=False):
    """
    清理已移動的原始文件
    
    參數:
        base_dir: 專案根目錄
        dry_run: 如果為True，只顯示將執行的操作而不實際刪除文件
    """
    # 詢問用戶確認
    if not dry_run:
        confirm = input("確認刪除已移動的原始文件? (y/n): ")
        if confirm.lower() != 'y':
            print("取消刪除操作")
            return
    
    # 刪除已移動的CSV文件
    csv_files = glob.glob(os.path.join(base_dir, "*.csv"))
    for file_path in csv_files:
        if dry_run:
            print(f"將刪除: {file_path}")
        else:
            os.remove(file_path)
            print(f"已刪除: {file_path}")
    
    # 刪除已移動的音頻文件
    audio_extensions = ["*.wav", "*.mp3", "*.flac", "*.ogg"]
    for ext in audio_extensions:
        for file_path in glob.glob(os.path.join(base_dir, ext)):
            if dry_run:
                print(f"將刪除: {file_path}")
            else:
                os.remove(file_path)
                print(f"已刪除: {file_path}")

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="專案整理工具")
    
    parser.add_argument("--dir", type=str, default=".",
                        help="專案根目錄")
    parser.add_argument("--dry-run", action="store_true",
                        help="只顯示將執行的操作而不實際修改文件系統")
    parser.add_argument("--clean", action="store_true",
                        help="清理已移動的原始文件")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("=== 試運行模式，不會執行實際操作 ===")
    
    # 檢查目錄是否存在
    if not os.path.exists(args.dir):
        print(f"錯誤: 目錄 {args.dir} 不存在")
        sys.exit(1)
    
    # 建立目錄結構
    create_directory_structure(args.dir)
    
    # 整理CSV文件
    organize_csv_files(args.dir, args.dry_run)
    
    # 整理音頻文件
    organize_audio_files(args.dir, args.dry_run)
    
    # 備份Python文件
    organize_python_files(args.dir, args.dry_run)
    
    # 檢查重要文件
    check_files_exist(args.dir)
    
    print("\n=== 專案整理完成 ===")
    
    # 清理原始文件
    if args.clean and not args.dry_run:
        clean_up_original_files(args.dir, args.dry_run)

if __name__ == "__main__":
    main()