#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據整理工具
整理實驗數據並生成報告
"""

import os
import argparse
from pathlib import Path

from src.utils.data_manager import ExperimentDataManager
from src.utils.report_generator import ReportGenerator

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description="音頻降噪實驗數據整理工具")
    
    # 基本參數
    parser.add_argument("--results_dir", type=str, default="results",
                       help="實驗結果目錄")
    parser.add_argument("--output_dir", type=str, default="reports",
                       help="報告輸出目錄")
    
    # 操作選項
    parser.add_argument("--aggregate", action="store_true",
                       help="匯總所有實驗數據")
    parser.add_argument("--excel", action="store_true",
                       help="生成Excel摘要報告")
    parser.add_argument("--html", action="store_true",
                       help="生成HTML報告")
    parser.add_argument("--timeline", action="store_true",
                       help="生成實驗時間線")
    parser.add_argument("--compare", action="store_true",
                       help="生成方法比較報告")
    parser.add_argument("--all", action="store_true",
                       help="執行所有整理和報告任務")
    
    args = parser.parse_args()
    
    # 創建數據管理器和報告生成器
    data_manager = ExperimentDataManager(args.results_dir)
    report_generator = ReportGenerator(args.results_dir, args.output_dir)
    
    # 檢查目錄是否存在
    results_dir = Path(args.results_dir)
    if not results_dir.exists() or not results_dir.is_dir():
        print(f"錯誤: 結果目錄 {args.results_dir} 不存在")
        return
    
    # 根據參數執行相應任務
    if args.aggregate or args.all:
        print("匯總實驗數據...")
        combined_data = data_manager.aggregate_method_results()
        if combined_data is not None:
            data_manager.export_combined_data()
    
    if args.compare or args.all:
        print("生成方法比較報告...")
        comparison_report = data_manager.create_method_comparison_report()
        if comparison_report is not None:
            print("\n=== 方法比較結果 ===")
            print(comparison_report[["method", "avg_snr_improvement", "compliance_rate"]].round(2))
    
    if args.timeline or args.all:
        print("生成實驗時間線...")
        timeline_df = data_manager.create_experiment_timeline()
        if timeline_df is not None:
            print(f"實驗時間線已保存")
    
    if args.excel or args.all:
        print("生成Excel摘要報告...")
        excel_path = report_generator.generate_experiment_summary_excel()
        if excel_path:
            print(f"Excel報告已保存至: {excel_path}")
    
    if args.html or args.all:
        print("生成HTML報告...")
        html_path = report_generator.generate_html_report()
        if html_path:
            print(f"HTML報告已保存至: {html_path}")
            # 嘗試在瀏覽器中打開
            report_generator.open_html_report(html_path)
    
    # 如果沒有指定任何操作
    if not (args.aggregate or args.excel or args.html or args.timeline or args.compare or args.all):
        # 默認生成Excel和HTML報告
        print("生成標準報告...")
        data_manager.aggregate_method_results()
        excel_path = report_generator.generate_experiment_summary_excel()
        html_path = report_generator.generate_html_report()
        if html_path:
            report_generator.open_html_report(html_path)

if __name__ == "__main__":
    main()