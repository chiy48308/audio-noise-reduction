#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心降噪處理器
實現多種音頻降噪算法
"""

import numpy as np
import librosa
from scipy import signal
import warnings

# 忽略警告
warnings.filterwarnings("ignore")

class NoiseReducer:
    """核心降噪處理器"""
    
    def __init__(self, sample_rate=44100):
        """初始化降噪處理器"""
        self.sample_rate = sample_rate
        self.silence_threshold_db = -45
        self.wavelet_threshold_mult = 2.5
        self.target_snr = 20
    
    def detect_silence(self, audio_data, threshold_db=None):
        """
        檢測音頻中的靜音部分
        
        參數:
            audio_data: 音頻數據
            threshold_db: 靜音閾值 (dB)
            
        返回值:
            silence_mask: 靜音掩碼 (布爾數組)
        """
        if threshold_db is None:
            threshold_db = self.silence_threshold_db
            
        # 計算短時能量
        frame_length = int(0.02 * self.sample_rate)  # 20ms
        hop_length = int(0.01 * self.sample_rate)    # 10ms
        
        frames = librosa.util.frame(audio_data, frame_length=frame_length, hop_length=hop_length)
        energy = np.sum(frames**2, axis=0)
        energy_db = librosa.amplitude_to_db(energy, ref=np.max)
        
        # 檢測靜音
        silence_mask = energy_db < threshold_db
        
        # 擴展掩碼到原始音頻長度
        full_mask = np.zeros(len(audio_data), dtype=bool)
        for i, is_silence in enumerate(silence_mask):
            start = i * hop_length
            end = min(start + frame_length, len(audio_data))
            if is_silence:
                full_mask[start:end] = True
        
        return full_mask
    
    def reduce_noise_standard(self, audio_data):
        """
        標準降噪 - 簡單的頻譜減法
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            denoised_audio: 降噪後的音頻
        """
        # 檢測靜音段落
        silence_mask = self.detect_silence(audio_data)
        
        if np.sum(silence_mask) > 0:
            # 從靜音段估計噪聲特徵
            noise_sample = audio_data[silence_mask]
            
            # 計算短時傅立葉變換
            n_fft = 2048
            hop_length = 512
            
            # 處理原始音頻
            stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
            stft_mag, stft_phase = librosa.magphase(stft)
            
            # 處理噪聲樣本
            noise_stft = librosa.stft(noise_sample, n_fft=n_fft, hop_length=hop_length)
            noise_mag = np.abs(noise_stft)
            noise_spec = np.mean(noise_mag, axis=1)
            noise_spec = np.expand_dims(noise_spec, 1)
            
            # 應用頻譜減法
            masked_stft_mag = np.maximum(stft_mag - noise_spec, 0.01 * stft_mag)
            
            # 重建音頻
            masked_stft = masked_stft_mag * np.exp(1j * np.angle(stft))
            denoised_audio = librosa.istft(masked_stft, hop_length=hop_length, length=len(audio_data))
        else:
            # 沒有檢測到靜音段，使用一般的低通濾波器
            cutoff = 0.1  # 截止頻率為0.1*fs/2
            b, a = signal.butter(8, cutoff, 'lowpass')
            denoised_audio = signal.filtfilt(b, a, audio_data)
        
        return denoised_audio

    def reduce_noise_wavelet(self, audio_data):
        """
        使用小波降噪方法
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            denoised_audio: 降噪後的音頻
        """
        # 使用小波分解
        coeffs = signal.cwt(audio_data, signal.ricker, np.arange(1, 31))
        
        # 計算閾值
        threshold = self.wavelet_threshold_mult * np.median(np.abs(coeffs)) / 0.6745
        
        # 應用閾值
        coeffs_thresholded = coeffs * (np.abs(coeffs) > threshold)
        
        # 重建信號
        denoised_audio = np.mean(coeffs_thresholded, axis=0)
        
        # 正規化
        if np.max(np.abs(denoised_audio)) > 0:
            denoised_audio = denoised_audio / np.max(np.abs(denoised_audio))
        
        # 保持原始能量
        orig_energy = np.sqrt(np.mean(audio_data**2))
        denoised_energy = np.sqrt(np.mean(denoised_audio**2))
        
        if denoised_energy > 0:
            denoised_audio = denoised_audio * (orig_energy / denoised_energy)
        
        return denoised_audio

    def multi_stage_denoising(self, audio_data):
        """
        多階段降噪法，結合頻譜減法和小波處理
        
        參數:
            audio_data: 音頻數據
            
        返回值:
            denoised_audio: 降噪後的音頻
        """
        # 第一階段：標準頻譜降噪
        stage1_audio = self.reduce_noise_standard(audio_data)
        
        # 第二階段：小波降噪
        stage2_audio = self.reduce_noise_wavelet(stage1_audio)
        
        # 適應性混合
        silence_mask = self.detect_silence(audio_data)
        non_silence_mask = ~silence_mask
        
        # 對非靜音部分，更傾向於保留原始信號特徵
        mixed_audio = np.zeros_like(audio_data)
        mixed_audio[silence_mask] = stage2_audio[silence_mask] * 0.9  # 靜音部分強降噪
        mixed_audio[non_silence_mask] = stage2_audio[non_silence_mask] * 0.6 + audio_data[non_silence_mask] * 0.4  # 混合，保留語音特徵
        
        return mixed_audio

    def enhanced_multi_stage_denoising(self, audio_data, voice_preserve=True):
        """
        增強型多階段降噪法，包含增益控制和保護主要語音
        
        參數:
            audio_data: 音頻數據
            voice_preserve: 是否保護語音特徵
            
        返回值:
            denoised_audio: 降噪後的音頻
        """
        # 基礎降噪
        denoised_audio = self.multi_stage_denoising(audio_data)
        
        if voice_preserve:
            # 識別語音段
            silence_mask = self.detect_silence(audio_data)
            voice_mask = ~silence_mask
            
            # 應用不同強度的處理
            result = np.zeros_like(audio_data)
            result[silence_mask] = denoised_audio[silence_mask] * 0.9  # 靜音部分強降噪
            
            # 保護語音段，混合原始音頻和降噪結果
            result[voice_mask] = denoised_audio[voice_mask] * 0.7 + audio_data[voice_mask] * 0.3
            
            # 平滑過渡
            window_size = int(0.01 * self.sample_rate)  # 10ms
            result = np.convolve(result, np.ones(window_size)/window_size, mode='same')
            
            return result
        else:
            return denoised_audio