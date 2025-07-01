#!/usr/bin/env python3
"""
簡單的 API 測試腳本
用於驗證加密與處理 API 服務的功能
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_text_encryption():
    """測試文本加密功能"""
    print("🔐 測試文本加密...")
    
    # 加密
    encrypt_data = {
        "text": "這是一個測試訊息",
        "password": "test_password"
    }
    response = requests.post(f"{BASE_URL}/encrypt/text", json=encrypt_data)
    if response.status_code == 200:
        encrypted_result = response.json()
        print(f"✅ 加密成功: {encrypted_result['encrypted_text'][:50]}...")
        
        # 解密
        decrypt_data = {
            "encrypted_text": encrypted_result['encrypted_text'],
            "password": "test_password"
        }
        response = requests.post(f"{BASE_URL}/decrypt/text", json=decrypt_data)
        if response.status_code == 200:
            decrypted_result = response.json()
            print(f"✅ 解密成功: {decrypted_result['decrypted_text']}")
        else:
            print(f"❌ 解密失敗: {response.text}")
    else:
        print(f"❌ 加密失敗: {response.text}")

def test_text_compression():
    """測試文本壓縮功能"""
    print("\n🗜️ 測試文本壓縮...")
    
    test_text = "這是一個很長的測試文本，用來測試壓縮功能。" * 20
    
    # 壓縮
    compress_data = {
        "text": test_text,
        "algorithm": "gzip",
        "level": 6
    }
    response = requests.post(f"{BASE_URL}/compress/text", json=compress_data)
    if response.status_code == 200:
        compressed_result = response.json()
        print(f"✅ 壓縮成功: {compressed_result['compressed_text'][:50]}...")
        
        # 解壓
        decompress_data = {
            "compressed_text": compressed_result['compressed_text'],
            "algorithm": "gzip"
        }
        response = requests.post(f"{BASE_URL}/decompress/text", json=decompress_data)
        if response.status_code == 200:
            decompressed_result = response.json()
            print(f"✅ 解壓成功，長度: {len(decompressed_result['decompressed_text'])}")
        else:
            print(f"❌ 解壓失敗: {response.text}")
            
        # 壓縮統計
        response = requests.post(f"{BASE_URL}/compress/stats", json=compress_data)
        if response.status_code == 200:
            stats = response.json()['stats']
            print(f"✅ 壓縮統計 - 原始大小: {stats['original_size_bytes']}, 壓縮後: {stats['compressed_size_bytes']}, 節省: {stats['space_saved_percent']:.2f}%")
        else:
            print(f"❌ 壓縮統計失敗: {response.text}")
    else:
        print(f"❌ 壓縮失敗: {response.text}")

def test_hash_functions():
    """測試哈希功能"""
    print("\n#️⃣ 測試哈希功能...")
    
    # 普通哈希
    hash_data = {
        "text": "Hello World",
        "algorithm": "sha256"
    }
    response = requests.post(f"{BASE_URL}/hash/text", json=hash_data)
    if response.status_code == 200:
        hash_result = response.json()
        print(f"✅ SHA256 哈希: {hash_result['hash']}")
    else:
        print(f"❌ 哈希計算失敗: {response.text}")
    
    # Crunch Hash
    crunch_data = {
        "data": "sensitive data",
        "iterations": 1000,  # 測試時使用較少迭代
        "algorithm": "sha256"
    }
    response = requests.post(f"{BASE_URL}/hash/crunch", json=crunch_data)
    if response.status_code == 200:
        crunch_result = response.json()['crunch_hash']
        print(f"✅ Crunch Hash: {crunch_result['hash'][:32]}...")
        print(f"   鹽值: {crunch_result['salt'][:16]}...")
        print(f"   迭代次數: {crunch_result['iterations']}")
    else:
        print(f"❌ Crunch Hash 失敗: {response.text}")

def test_api_info():
    """測試 API 基本信息"""
    print("\n📋 測試 API 基本信息...")
    
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        info = response.json()
        print(f"✅ API 服務: {info['message']}")
        print(f"✅ 版本: {info['version']}")
        print(f"✅ 功能類別數量: {len(info['categories'])}")
        for category, endpoints in info['categories'].items():
            print(f"   {category}: {len(endpoints)} 個端點")
    else:
        print(f"❌ API 信息獲取失敗: {response.text}")

def main():
    """主測試函數"""
    print("🚀 開始測試加密與處理 API 服務")
    print("=" * 50)
    
    try:
        # 檢查服務是否運行
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ API 服務無法連接")
            return
    except requests.exceptions.RequestException:
        print("❌ API 服務無法連接，請確保服務正在運行 (python main.py)")
        return
    
    # 運行測試
    test_api_info()
    test_text_encryption()
    test_text_compression()
    test_hash_functions()
    
    print("\n" + "=" * 50)
    print("✨ 測試完成！")
    print("\n💡 提示:")
    print("- 訪問 http://localhost:8000/docs 查看完整的 API 文檔")
    print("- 使用 Swagger UI 進行交互式測試")

if __name__ == "__main__":
    main() 