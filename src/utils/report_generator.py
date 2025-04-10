#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
報告生成模組
提供整理實驗數據並生成各種報告的功能
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import jinja2
import webbrowser

from src.utils.data_manager import ExperimentDataManager

class ReportGenerator:
    """實驗報告生成器"""
    
    def __init__(self, results_dir="results", output_dir="reports"):
        """初始化報告生成器"""
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化數據管理器
        self.data_manager = ExperimentDataManager(results_dir)
    
    def set_output_dir(self, output_dir):
        """設置輸出目錄"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_method_summary_plots(self, comparison_df=None):
        """
        生成方法比較的可視化圖表
        
        參數:
            comparison_df: 方法比較DataFrame (可選)
            
        返回值:
            圖表文件路徑列表
        """
        if comparison_df is None:
            comparison_df = self.data_manager.create_method_comparison_report()
        
        if comparison_df is None or comparison_df.empty:
            print("無法生成方法比較圖表: 沒有可用的數據")
            return []
        
        plot_files = []
        
        # 生成SNR改善柱狀圖
        plt.figure(figsize=(10, 6))
        sns.barplot(x='method', y='avg_snr_improvement', data=comparison_df)
        plt.title('不同方法的平均信噪比改善')
        plt.ylabel('信噪比改善 (dB)')
        plt.xlabel('降噪方法')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        snr_plot_file = self.output_dir / 'methods_snr_comparison.png'
        plt.savefig(snr_plot_file, dpi=300)
        plt.close()
        plot_files.append(snr_plot_file)
        
        # 生成合規率柱狀圖
        plt.figure(figsize=(10, 6))
        sns.barplot(x='method', y='compliance_rate', data=comparison_df)
        plt.title('不同方法的符合標準率')
        plt.ylabel('符合標準率')
        plt.xlabel('降噪方法')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        compliance_plot_file = self.output_dir / 'methods_compliance_comparison.png'
        plt.savefig(compliance_plot_file, dpi=300)
        plt.close()
        plot_files.append(compliance_plot_file)
        
        # 生成多指標比較雷達圖
        methods = comparison_df['method'].tolist()
        metrics = ['avg_snr_improvement', 'avg_cv_improvement', 
                  'avg_rms_improvement', 'compliance_rate']
        
        # 正規化數據用於雷達圖
        radar_data = comparison_df[metrics].copy()
        for col in radar_data.columns:
            if radar_data[col].min() < 0:
                # 對於可能有負值的列，使用不同的正規化方法
                radar_data[col] = (radar_data[col] - radar_data[col].min()) / (radar_data[col].max() - radar_data[col].min())
            else:
                # 對於正值列，簡單除以最大值
                radar_data[col] = radar_data[col] / radar_data[col].max()
        
        # 設置雷達圖參數
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # 閉合雷達圖
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        
        for i, method in enumerate(methods):
            values = radar_data.iloc[i].tolist()
            values += values[:1]  # 閉合雷達圖
            ax.plot(angles, values, linewidth=2, label=method)
            ax.fill(angles, values, alpha=0.1)
        
        # 設置標籤
        ax.set_thetagrids(np.degrees(angles[:-1]), metrics)
        ax.set_title('方法性能比較 (正規化數值)')
        ax.grid(True)
        plt.legend(loc='upper right')
        plt.tight_layout()
        
        radar_plot_file = self.output_dir / 'methods_radar_comparison.png'
        plt.savefig(radar_plot_file, dpi=300)
        plt.close()
        plot_files.append(radar_plot_file)
        
        return plot_files
    
    def generate_experiment_summary_excel(self, filename="experiment_summary.xlsx"):
        """
        生成實驗數據的Excel摘要文件
        
        參數:
            filename: 輸出Excel文件名
            
        返回值:
            輸出文件路徑
        """
        # 獲取數據
        method_comparison = self.data_manager.create_method_comparison_report()
        stats_summary = self.data_manager.generate_summary_stats()
        
        if method_comparison is None or stats_summary is None:
            print("無法生成Excel摘要: 沒有足夠的數據")
            return None
        
        # 重置列索引為單層
        stats_df = stats_summary.copy()
        stats_df.columns = [f"{col[0]}_{col[1]}" for col in stats_df.columns]
        stats_df = stats_df.reset_index()
        
        # 創建Excel writer
        output_path = self.output_dir / filename
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 寫入方法比較摘要
            method_comparison.to_excel(writer, sheet_name='方法比較', index=False)
            
            # 寫入詳細統計數據
            stats_df.to_excel(writer, sheet_name='詳細統計', index=False)
            
            # 如果有時間線數據，也寫入
            try:
                timeline_df = self.data_manager.create_experiment_timeline()
                if timeline_df is not None and not timeline_df.empty:
                    timeline_df.to_excel(writer, sheet_name='實驗時間線', index=False)
            except:
                pass
        
        print(f"Excel摘要已保存至 {output_path}")
        return output_path
    
    def generate_html_report(self, filename="experiment_report.html"):
        """
        生成HTML格式的實驗報告
        
        參數:
            filename: 輸出HTML文件名
            
        返回值:
            輸出文件路徑
        """
        # 生成所需的數據和圖表
        method_comparison = self.data_manager.create_method_comparison_report()
        plot_files = self.generate_method_summary_plots(method_comparison)
        
        # 確保有數據可用
        if method_comparison is None or not plot_files:
            print("無法生成HTML報告: 沒有足夠的數據")
            return None
        
        # 獲取最佳方法
        best_method = method_comparison.iloc[0]['method']
        
        # 創建HTML報告模板
        template_str = """
        <!DOCTYPE html>
        <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>音頻降噪實驗報告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }
                .container { max-width: 1200px; margin: 0 auto; }
                header { text-align: center; margin-bottom: 30px; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                .summary { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
                .recommendation { background: #e8f4f8; padding: 15px; border-left: 5px solid #3498db; margin: 20px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                tr:hover { background-color: #f5f5f5; }
                .plot-container { text-align: center; margin: 30px 0; }
                .plot-container img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }
                footer { margin-top: 50px; text-align: center; font-size: 0.9em; color: #7f8c8d; }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>音頻降噪實驗報告</h1>
                    <p>生成時間: {{ current_time }}</p>
                </header>
                
                <section class="summary">
                    <h2>實驗摘要</h2>
                    <p>本報告匯總了多種音頻降噪方法的實驗結果。共測試了 {{ method_count }} 種降噪方法。</p>
                    
                    <div class="recommendation">
                        <h3>推薦方法</h3>
                        <p>根據實驗結果，<strong>{{ best_method }}</strong> 是效果最佳的降噪方法，平均SNR改善達 {{ best_snr_improvement }} dB。</p>
                    </div>
                </section>
                
                <section>
                    <h2>方法比較</h2>
                    <table>
                        <tr>
                            <th>方法</th>
                            <th>SNR改善 (dB)</th>
                            <th>CV改善 (%)</th>
                            <th>RMS改善 (%)</th>
                            <th>合規率</th>
                        </tr>
                        {% for _, row in method_comparison.iterrows() %}
                        <tr>
                            <td>{{ row.method }}</td>
                            <td>{{ "%.2f"|format(row.avg_snr_improvement) }}</td>
                            <td>{{ "%.2f"|format(row.avg_cv_improvement) }}</td>
                            <td>{{ "%.2f"|format(row.avg_rms_improvement) }}</td>
                            <td>{{ "%.1f%%"|format(row.compliance_rate*100) }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </section>
                
                <section>
                    <h2>視覺化結果</h2>
                    
                    <div class="plot-container">
                        <h3>SNR改善比較</h3>
                        <img src="{{ plot_files[0].name }}" alt="SNR改善比較">
                    </div>
                    
                    <div class="plot-container">
                        <h3>合規率比較</h3>
                        <img src="{{ plot_files[1].name }}" alt="合規率比較">
                    </div>
                    
                    <div class="plot-container">
                        <h3>多指標性能比較</h3>
                        <img src="{{ plot_files[2].name }}" alt="多指標性能比較">
                    </div>
                </section>
                
                <footer>
                    <p>© {{ current_year }} 音頻降噪實驗系統 | 報告自動生成</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # 準備模板數據
        template_data = {
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'current_year': datetime.now().year,
            'method_count': len(method_comparison),
            'best_method': best_method,
            'best_snr_improvement': f"{method_comparison.iloc[0]['avg_snr_improvement']:.2f}",
            'method_comparison': method_comparison,
            'plot_files': [Path(f) for f in plot_files]
        }
        
        # 渲染模板
        template = jinja2.Template(template_str)
        html_content = template.render(**template_data)
        
        # 寫入HTML文件
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML報告已保存至 {output_path}")
        return output_path
    
    def open_html_report(self, report_path=None):
        """
        在瀏覽器中打開HTML報告
        
        參數:
            report_path: 報告文件路徑
        """
        if report_path is None:
            report_path = self.output_dir / "experiment_report.html"
        
        if not report_path.exists():
            print(f"報告文件 {report_path} 不存在")
            return False
        
        # 嘗試在瀏覽器中打開
        try:
            webbrowser.open(f"file://{report_path.absolute()}")
            return True
        except Exception as e:
            print(f"無法在瀏覽器中打開報告: {str(e)}")
            return False