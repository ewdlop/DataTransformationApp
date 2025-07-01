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

def test_image_steganography():
    """測試圖像隱寫術功能"""
    print("\n🎭 測試圖像隱寫術...")
    
    try:
        from PIL import Image
        import io
        
        # 創建一個測試圖像
        test_image = Image.new('RGB', (200, 200), color='blue')
        image_buffer = io.BytesIO()
        test_image.save(image_buffer, format='PNG')
        image_data = image_buffer.getvalue()
        
        secret_text = "這是隱藏在圖像中的秘密訊息！🔐"
        
        # 測試隱藏文本
        files = {"image": ("test_image.png", image_data, "image/png")}
        data = {
            "secret_text": secret_text,
            "method": "lsb",
            "encrypt_text": "false"
        }
        
        response = requests.post(f"{BASE_URL}/stego/hide", files=files, data=data)
        if response.status_code == 200:
            hidden_image_data = response.content
            print(f"✅ 隱藏文本成功，圖像大小: {len(hidden_image_data)} bytes")
            
            # 測試提取文本
            files = {"image": ("hidden_image.png", hidden_image_data, "image/png")}
            data = {"method": "lsb", "is_encrypted": "false"}
            
            response = requests.post(f"{BASE_URL}/stego/extract", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                extracted_text = result.get('extracted_text', '')
                print(f"✅ 提取文本成功: {extracted_text}")
                print(f"✅ 文本匹配: {'是' if extracted_text == secret_text else '否'}")
            else:
                print(f"❌ 提取文本失敗: {response.text}")
                
            # 測試檢查容量
            files = {"image": ("test_image.png", image_data, "image/png")}
            data = {"method": "lsb"}
            
            response = requests.post(f"{BASE_URL}/stego/capacity", files=files, data=data)
            if response.status_code == 200:
                capacity = response.json()['capacity']
                print(f"✅ 圖像容量: 最大 {capacity['max_characters']} 字符")
            else:
                print(f"❌ 容量檢查失敗: {response.text}")
                
            # 測試 DCT 方法
            print("\n--- 測試 DCT 方法 ---")
            files = {"image": ("test_image.png", image_data, "image/png")}
            data = {
                "secret_text": "DCT測試文本123",
                "method": "dct",
                "encrypt_text": "false"
            }
            
            response = requests.post(f"{BASE_URL}/stego/hide", files=files, data=data)
            if response.status_code == 200:
                dct_hidden_image_data = response.content
                print(f"✅ DCT 隱藏成功，圖像大小: {len(dct_hidden_image_data)} bytes")
                
                # 提取 DCT 隱藏的文本
                files = {"image": ("dct_hidden_image.png", dct_hidden_image_data, "image/png")}
                data = {"method": "dct", "is_encrypted": "false"}
                
                response = requests.post(f"{BASE_URL}/stego/extract", files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    extracted_text = result.get('extracted_text', '')
                    print(f"✅ DCT 提取成功: {extracted_text}")
                    print(f"✅ DCT 文本匹配: {'是' if extracted_text == 'DCT測試文本123' else '否'}")
                else:
                    print(f"❌ DCT 提取失敗: {response.text}")
            else:
                print(f"❌ DCT 隱藏失敗: {response.text}")
                
        else:
            print(f"❌ 隱藏文本失敗: {response.text}")
            
    except ImportError:
        print("⚠️ 跳過圖像隱寫術測試 (需要 Pillow 庫)")
    except Exception as e:
        print(f"❌ 圖像隱寫術測試出錯: {str(e)}")

def test_file_encryption():
    """測試文件加密功能"""
    print("\n📁 測試文件加密...")
    
    try:
        import io
        
        # 創建測試文件內容
        test_content = "這是一個測試文件的內容，包含中文字符。\nThis is a test file content.".encode('utf-8')
        
        # 測試文件加密
        files = {'file': ('test.txt', io.BytesIO(test_content), 'text/plain')}
        data = {'password': 'test123', 'preserve_metadata': True}
        response = requests.post(f"{BASE_URL}/encrypt/file", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文件加密成功：{result['message']}")
            encrypted_data = result['encrypted_data']
            
            # 測試文件解密
            import base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            files = {'encrypted_file': ('encrypted.bin', io.BytesIO(encrypted_bytes), 'application/octet-stream')}
            data = {'password': 'test123'}
            response = requests.post(f"{BASE_URL}/decrypt/file", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                decrypted_content = base64.b64decode(result['decrypted_data'])
                if decrypted_content == test_content:
                    print("✅ 文件解密成功，內容匹配")
                else:
                    print("❌ 文件解密後內容不匹配")
            else:
                print(f"❌ 文件解密失敗：{response.text}")
        else:
            print(f"❌ 文件加密失敗：{response.text}")
            
    except Exception as e:
        print(f"❌ 文件加密測試出錯：{e}")

def test_digital_signatures():
    """測試數字簽名功能"""
    print("\n✍️ 測試數字簽名...")
    
    try:
        # 生成密鑰對
        data = {'key_size': 2048}
        response = requests.post(f"{BASE_URL}/signature/generate-keypair", json=data)
        
        if response.status_code == 200:
            keypair = response.json()
            print(f"✅ 密鑰對生成成功，指紋：{keypair.get('fingerprint', '未知')[:16]}...")
            
            # 測試數據簽名
            sign_data = {
                'data': '這是要簽名的測試數據',
                'private_key': keypair['private_key'],
                'hash_algorithm': 'sha256'
            }
            response = requests.post(f"{BASE_URL}/signature/sign", json=sign_data)
            
            if response.status_code == 200:
                sign_result = response.json()
                print("✅ 數字簽名成功")
                
                # 測試簽名驗證
                verify_data = {
                    'data': '這是要簽名的測試數據',
                    'signature': sign_result['signature'],
                    'public_key': sign_result['public_key'],
                    'hash_algorithm': 'sha256'
                }
                response = requests.post(f"{BASE_URL}/signature/verify", json=verify_data)
                
                if response.status_code == 200:
                    verify_result = response.json()
                    if verify_result['is_valid']:
                        print("✅ 簽名驗證成功")
                    else:
                        print("❌ 簽名驗證失敗")
                else:
                    print(f"❌ 簽名驗證請求失敗：{response.text}")
            else:
                print(f"❌ 數字簽名失敗：{response.text}")
        else:
            print(f"❌ 密鑰對生成失敗：{response.text}")
            
    except Exception as e:
        print(f"❌ 數字簽名測試出錯：{e}")

def test_password_utilities():
    """測試密碼工具功能"""
    print("\n🔐 測試密碼工具...")
    
    try:
        # 測試密碼生成
        data = {
            'length': 16,
            'include_uppercase': True,
            'include_lowercase': True,
            'include_numbers': True,
            'include_symbols': True
        }
        response = requests.post(f"{BASE_URL}/password/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            password = result['password']
            print(f"✅ 密碼生成成功：{password}")
            print(f"   強度等級：{result['strength_level']}")
            
            # 測試密碼強度分析
            analyze_data = {'password': password}
            response = requests.post(f"{BASE_URL}/password/analyze", json=analyze_data)
            
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ 密碼強度分析完成，分數：{analysis['strength_score']}/100")
                print(f"   破解時間：{analysis['time_to_crack']['time']}")
            else:
                print(f"❌ 密碼強度分析失敗：{response.text}")
        else:
            print(f"❌ 密碼生成失敗：{response.text}")
        
        # 測試 PIN 生成
        pin_data = {'length': 6, 'exclude_patterns': True}
        response = requests.post(f"{BASE_URL}/password/pin", json=pin_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PIN 生成成功：{result['pin']}")
        else:
            print(f"❌ PIN 生成失敗：{response.text}")
            
    except Exception as e:
        print(f"❌ 密碼工具測試出錯：{e}")

def test_qr_codes():
    """測試 QR 碼功能"""
    print("\n📱 測試 QR 碼功能...")
    
    try:
        # 測試文本 QR 碼生成
        data = {
            'data': '這是一個測試 QR 碼內容',
            'error_correction': 'M',
            'box_size': 10,
            'border': 4
        }
        response = requests.post(f"{BASE_URL}/qr/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ QR 碼生成成功，大小：{result['size']} 字節")
            
            # 測試 WiFi QR 碼
            wifi_data = {
                'ssid': 'TestWiFi',
                'password': 'testpass123',
                'security': 'WPA',
                'hidden': False
            }
            response = requests.post(f"{BASE_URL}/qr/wifi", json=wifi_data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ WiFi QR 碼生成成功")
            else:
                print(f"❌ WiFi QR 碼生成失敗：{response.text}")
        else:
            print(f"❌ QR 碼生成失敗：{response.text}")
            
    except Exception as e:
        print(f"❌ QR 碼測試出錯：{e}")

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
    test_image_steganography()
    test_file_encryption()
    test_digital_signatures()
    test_password_utilities()
    test_qr_codes()
    
    print("\n" + "=" * 50)
    print("✨ 測試完成！")
    print("\n💡 提示:")
    print("- 訪問 http://localhost:8000/docs 查看完整的 API 文檔")
    print("- 使用 Swagger UI 進行交互式測試")

if __name__ == "__main__":
    main() 