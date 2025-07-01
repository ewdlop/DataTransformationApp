from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import tempfile
from encryption.text_encryption import TextEncryption
from encryption.data_encryption import DataEncryption
from encryption.image_encryption import ImageEncryption

app = FastAPI(
    title="加密 API 服務",
    description="提供文本、數據和圖像加密/解密服務的 FastAPI 應用程式",
    version="1.0.0"
)

# 請求模型
class TextEncryptRequest(BaseModel):
    text: str
    password: str

class TextDecryptRequest(BaseModel):
    encrypted_text: str
    password: str

class DataEncryptRequest(BaseModel):
    data: str
    password: str
    algorithm: Optional[str] = "AES"

class DataDecryptRequest(BaseModel):
    encrypted_data: str
    password: str
    algorithm: Optional[str] = "AES"

# 初始化加密類
text_crypto = TextEncryption()
data_crypto = DataEncryption()
image_crypto = ImageEncryption()

@app.get("/")
async def root():
    return {
        "message": "歡迎使用加密 API 服務",
        "endpoints": {
            "text_encrypt": "/encrypt/text",
            "text_decrypt": "/decrypt/text",
            "data_encrypt": "/encrypt/data",
            "data_decrypt": "/decrypt/data",
            "image_encrypt": "/encrypt/image",
            "image_decrypt": "/decrypt/image"
        }
    }

# 文本加密端點
@app.post("/encrypt/text")
async def encrypt_text(request: TextEncryptRequest):
    try:
        encrypted_text = text_crypto.encrypt(request.text, request.password)
        return {
            "status": "success",
            "encrypted_text": encrypted_text,
            "message": "文本加密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"加密失敗: {str(e)}")

@app.post("/decrypt/text")
async def decrypt_text(request: TextDecryptRequest):
    try:
        decrypted_text = text_crypto.decrypt(request.encrypted_text, request.password)
        return {
            "status": "success",
            "decrypted_text": decrypted_text,
            "message": "文本解密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解密失敗: {str(e)}")

# 數據加密端點
@app.post("/encrypt/data")
async def encrypt_data(request: DataEncryptRequest):
    try:
        encrypted_data = data_crypto.encrypt(request.data, request.password, request.algorithm)
        return {
            "status": "success",
            "encrypted_data": encrypted_data,
            "algorithm": request.algorithm,
            "message": "數據加密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"數據加密失敗: {str(e)}")

@app.post("/decrypt/data")
async def decrypt_data(request: DataDecryptRequest):
    try:
        decrypted_data = data_crypto.decrypt(request.encrypted_data, request.password, request.algorithm)
        return {
            "status": "success",
            "decrypted_data": decrypted_data,
            "algorithm": request.algorithm,
            "message": "數據解密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"數據解密失敗: {str(e)}")

# 圖像加密端點
@app.post("/encrypt/image")
async def encrypt_image(password: str, file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        # 讀取上傳的圖像
        image_data = await file.read()
        
        # 加密圖像
        encrypted_data = image_crypto.encrypt(image_data, password)
        
        # 保存加密文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as temp_file:
            temp_file.write(encrypted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='application/octet-stream',
            filename=f"encrypted_{file.filename}.enc"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像加密失敗: {str(e)}")

@app.post("/decrypt/image")
async def decrypt_image(password: str, file: UploadFile = File(...)):
    try:
        # 讀取加密文件
        encrypted_data = await file.read()
        
        # 解密圖像
        decrypted_data = image_crypto.decrypt(encrypted_data, password)
        
        # 保存解密文件
        original_filename = file.filename.replace('.enc', '') if file.filename.endswith('.enc') else file.filename
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(decrypted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/jpeg',
            filename=f"decrypted_{original_filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像解密失敗: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 