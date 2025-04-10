#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音頻評估模組
提供音頻質量評估功能
"""

import numpy as np
import librosa

class AudioEvaluator:
    """音頻評估器基類"""
    
    def __init__(self):
        """初始化音頻評估器"""
        # 預設評估標準
        self.standards = {
            'rms_db': -30,             # RMS最小值 (dBFS)
            'peak_db': 0,              # 峰值最大值 (dBFS)
            'cv': 0.5,                 # 音量穩定性變異係數
            'snr': 20,                 # 信噪比 (dB)
            'non_speech_ratio': 0.3,   # 無語音部分佔比
            'max_silence': 1.0,        # 最大靜音段 (秒)
        }
    
    def calculate_rms(self, audio_data):
        """
        計算均方根(RMS)值
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            rms: RMS值
            rms_db: RMS值(dB)
        """
        rms = np.sqrt(np.mean(audio_data**2))
        rms_db = 20 * np.log10(rms) if rms > 0 else -100
        return rms, rms_db
    
    def calculate_peak(self, audio_data):
        """
        計算峰值
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            peak: 峰值
            peak_db: 峰值(dB)
        """
        peak = np.max(np.abs(audio_data))
        peak_db = 20 * np.log10(peak) if peak > 0 else -100
        return peak, peak_db
    
    def calculate_cv(self, audio_data):
        """
        計算變異係數，衡量音量的穩定性
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            cv: 變異係數
        """
        abs_data = np.abs(audio_data)
        if np.mean(abs_data) > 0:
            cv = np.std(abs_data) / np.mean(abs_data)
        else:
            cv = 1.0
        return cv
    
    def estimate_snr(self, audio_data):
        """
        估計信噪比
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            snr: 信噪比(dB)
        """
        signal_power = np.mean(audio_data**2)
        noise = audio_data - np.mean(audio_data)
        noise_power = np.mean(noise**2)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 100
        return snr
    
    def detect_silence(self, audio_data, sr, threshold_db=-45):
        """
        檢測靜音比例和最大靜音段
        
        參數:
            audio_data: 音頻數據
            sr: 採樣率
            threshold_db: 靜音閾值(dB)
            
        返回值:
            non_speech_ratio: 靜音比例
            max_silence: 最大靜音段(秒)
        """
        # 計算短時能量
        frame_length = int(0.02 * sr)  # 20ms
        hop_length = int(0.01 * sr)    # 10ms
        
        frames = librosa.util.frame(audio_data, frame_length=frame_length, hop_length=hop_length)
        energy = np.sum(frames**2, axis=0)
        energy_db = librosa.amplitude_to_db(energy, ref=np.max)
        
        # 檢測靜音
        silence_mask = energy_db < threshold_db
        
        # 計算靜音比例
        non_speech_ratio = np.sum(silence_mask) / len(silence_mask)
        
        # 找出最長的靜音段
        max_silence_frames = 0
        current_silence = 0
        
        for is_silence in silence_mask:
            if is_silence:
                current_silence += 1
            else:
                max_silence_frames = max(max_silence_frames, current_silence)
                current_silence = 0
                
        # 處理最後可能的靜音段
        max_silence_frames = max(max_silence_frames, current_silence)
        
        # 轉換為秒
        max_silence = max_silence_frames * hop_length / sr
        
        return non_speech_ratio, max_silence
    
    def evaluate_audio(self, audio_data, sr):
        """
        全面評估音頻質量
        
        參數:
            audio_data: 音頻數據
            sr: 採樣率
            
        返回值:
            metrics: 評估指標字典
            compliant: 是否符合標準
        """
        # 計算指標
        rms, rms_db = self.calculate_rms(audio_data)
        peak, peak_db = self.calculate_peak(audio_data)
        cv = self.calculate_cv(audio_data)
        snr = self.estimate_snr(audio_data)
        non_speech_ratio, max_silence = self.detect_silence(audio_data, sr)
        
        # 收集指標
        metrics = {
            'rms': rms,
            'rms_db': rms_db,
            'peak': peak,
            'peak_db': peak_db,
            'cv': cv,
            'snr': snr,
            'non_speech_ratio': non_speech_ratio,
            'max_silence': max_silence
        }
        
        # 檢查是否符合標準
        compliant = (
            rms_db >= self.standards['rms_db'] and
            peak_db <= self.standards['peak_db'] and
            cv <= self.standards['cv'] and
            snr >= self.standards['snr'] and
            non_speech_ratio <= self.standards['non_speech_ratio'] and
            max_silence <= self.standards['max_silence']
        )
        
        return metrics, compliant