from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import tempfile
from encryption.text_encryption import TextEncryption
from encryption.data_encryption import DataEncryption
from encryption.image_encryption import ImageEncryption
from encryption.image_transformation import ImageTransformation
from encryption.text_compression import TextCompression
from encryption.hash_functions import HashFunctions

app = FastAPI(
    title="加密與處理 API 服務",
    description="提供文本、數據和圖像加密/解密、圖像變換、文本壓縮和哈希服務的 FastAPI 應用程式",
    version="2.0.0"
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

# 文本壓縮請求模型
class TextCompressRequest(BaseModel):
    text: str
    algorithm: Optional[str] = "gzip"
    level: Optional[int] = 6

class TextDecompressRequest(BaseModel):
    compressed_text: str
    algorithm: Optional[str] = "gzip"

# 哈希請求模型
class HashRequest(BaseModel):
    text: str
    algorithm: Optional[str] = "sha256"

class HashVerifyRequest(BaseModel):
    text: str
    expected_hash: str
    algorithm: Optional[str] = "sha256"

class CrunchHashRequest(BaseModel):
    data: str
    salt: Optional[str] = None
    iterations: Optional[int] = 10000
    algorithm: Optional[str] = "sha256"

# 初始化加密和處理類
text_crypto = TextEncryption()
data_crypto = DataEncryption()
image_crypto = ImageEncryption()
image_transform = ImageTransformation()
text_compressor = TextCompression()
hash_functions = HashFunctions()

@app.get("/")
async def root():
    return {
        "message": "歡迎使用加密與處理 API 服務",
        "version": "2.0.0",
        "categories": {
            "encryption": {
                "text_encrypt": "/encrypt/text",
                "text_decrypt": "/decrypt/text",
                "data_encrypt": "/encrypt/data",
                "data_decrypt": "/decrypt/data",
                "image_encrypt": "/encrypt/image",
                "image_decrypt": "/decrypt/image"
            },
            "compression": {
                "compress_text": "/compress/text",
                "decompress_text": "/decompress/text",
                "compression_stats": "/compress/stats",
                "compare_algorithms": "/compress/compare"
            },
            "image_transformation": {
                "resize": "/transform/image/resize",
                "rotate": "/transform/image/rotate",
                "crop": "/transform/image/crop",
                "filter": "/transform/image/filter",
                "brightness": "/transform/image/brightness",
                "contrast": "/transform/image/contrast",
                "convert_format": "/transform/image/convert",
                "thumbnail": "/transform/image/thumbnail",
                "info": "/transform/image/info"
            },
            "hash": {
                "hash_text": "/hash/text",
                "verify_hash": "/hash/verify",
                "multi_hash": "/hash/multi",
                "crunch_hash": "/hash/crunch",
                "verify_crunch": "/hash/crunch/verify"
            }
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

# 文本壓縮端點
@app.post("/compress/text")
async def compress_text(request: TextCompressRequest):
    try:
        compressed_text = text_compressor.compress_text(request.text, request.algorithm, request.level)
        return {
            "status": "success",
            "compressed_text": compressed_text,
            "algorithm": request.algorithm,
            "compression_level": request.level,
            "message": "文本壓縮成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文本壓縮失敗: {str(e)}")

@app.post("/decompress/text")
async def decompress_text(request: TextDecompressRequest):
    try:
        decompressed_text = text_compressor.decompress_text(request.compressed_text, request.algorithm)
        return {
            "status": "success",
            "decompressed_text": decompressed_text,
            "algorithm": request.algorithm,
            "message": "文本解壓成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文本解壓失敗: {str(e)}")

@app.post("/compress/stats")
async def get_compression_stats(request: TextCompressRequest):
    try:
        stats = text_compressor.get_compression_stats(request.text, request.algorithm, request.level)
        return {
            "status": "success",
            "stats": stats,
            "message": "壓縮統計獲取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"壓縮統計獲取失敗: {str(e)}")

@app.post("/compress/compare")
async def compare_compression_algorithms(text: str = Form(...), level: int = Form(6)):
    try:
        comparison = text_compressor.compare_algorithms(text, level)
        return {
            "status": "success",
            "comparison": comparison,
            "message": "算法比較完成"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"算法比較失敗: {str(e)}")

# 圖像變換端點
@app.post("/transform/image/resize")
async def resize_image(
    width: int = Form(...),
    height: int = Form(...),
    maintain_aspect: bool = Form(True),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        resized_data = image_transform.resize_image(image_data, width, height, maintain_aspect)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(resized_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"resized_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像大小調整失敗: {str(e)}")

@app.post("/transform/image/rotate")
async def rotate_image(
    angle: float = Form(...),
    expand: bool = Form(True),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        rotated_data = image_transform.rotate_image(image_data, angle, expand)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(rotated_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"rotated_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像旋轉失敗: {str(e)}")

@app.post("/transform/image/crop")
async def crop_image(
    left: int = Form(...),
    top: int = Form(...),
    right: int = Form(...),
    bottom: int = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        cropped_data = image_transform.crop_image(image_data, left, top, right, bottom)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(cropped_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"cropped_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像裁剪失敗: {str(e)}")

@app.post("/transform/image/filter")
async def apply_image_filter(
    filter_name: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        filtered_data = image_transform.apply_filter(image_data, filter_name)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(filtered_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"filtered_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"濾鏡應用失敗: {str(e)}")

@app.post("/transform/image/brightness")
async def adjust_brightness(
    factor: float = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        adjusted_data = image_transform.adjust_brightness(image_data, factor)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(adjusted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"brightness_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"亮度調整失敗: {str(e)}")

@app.post("/transform/image/contrast")
async def adjust_contrast(
    factor: float = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        adjusted_data = image_transform.adjust_contrast(image_data, factor)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(adjusted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"contrast_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"對比度調整失敗: {str(e)}")

@app.post("/transform/image/convert")
async def convert_image_format(
    target_format: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        converted_data = image_transform.convert_format(image_data, target_format)
        
        ext = target_format.lower()
        mime_type = f'image/{ext}'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}') as temp_file:
            temp_file.write(converted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type=mime_type,
            filename=f"converted_{file.filename}.{ext}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"格式轉換失敗: {str(e)}")

@app.post("/transform/image/thumbnail")
async def create_thumbnail(
    width: int = Form(128),
    height: int = Form(128),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        thumbnail_data = image_transform.create_thumbnail(image_data, (width, height))
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(thumbnail_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"thumbnail_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"縮略圖創建失敗: {str(e)}")

@app.post("/transform/image/info")
async def get_image_info(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        info = image_transform.get_image_info(image_data)
        
        return {
            "status": "success",
            "image_info": info,
            "message": "圖像信息獲取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像信息獲取失敗: {str(e)}")

# 哈希函數端點
@app.post("/hash/text")
async def hash_text(request: HashRequest):
    try:
        hash_value = hash_functions.hash_text(request.text, request.algorithm)
        return {
            "status": "success",
            "hash": hash_value,
            "algorithm": request.algorithm,
            "message": "文本哈希計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文本哈希計算失敗: {str(e)}")

@app.post("/hash/verify")
async def verify_hash(request: HashVerifyRequest):
    try:
        is_valid = hash_functions.verify_hash(request.text, request.expected_hash, request.algorithm)
        return {
            "status": "success",
            "is_valid": is_valid,
            "algorithm": request.algorithm,
            "message": "哈希驗證完成"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"哈希驗證失敗: {str(e)}")

@app.post("/hash/multi")
async def multi_hash(text: str = Form(...), algorithms: str = Form("md5,sha1,sha256,sha512")):
    try:
        algorithm_list = [alg.strip() for alg in algorithms.split(',')]
        hashes = hash_functions.multi_hash(text, algorithm_list)
        return {
            "status": "success",
            "hashes": hashes,
            "message": "多重哈希計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"多重哈希計算失敗: {str(e)}")

@app.post("/hash/crunch")
async def crunch_hash(request: CrunchHashRequest):
    try:
        result = hash_functions.crunch_hash(
            request.data, 
            request.salt, 
            request.iterations, 
            request.algorithm
        )
        return {
            "status": "success",
            "crunch_hash": result,
            "message": "Crunch Hash 計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Crunch Hash 計算失敗: {str(e)}")

@app.post("/hash/crunch/verify")
async def verify_crunch_hash(
    data: str = Form(...),
    stored_hash: str = Form(...),
    salt: str = Form(...),
    iterations: int = Form(10000),
    algorithm: str = Form("sha256")
):
    try:
        is_valid = hash_functions.verify_crunch_hash(data, stored_hash, salt, iterations, algorithm)
        return {
            "status": "success",
            "is_valid": is_valid,
            "algorithm": algorithm,
            "iterations": iterations,
            "message": "Crunch Hash 驗證完成"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Crunch Hash 驗證失敗: {str(e)}")

@app.post("/hash/file")
async def hash_file(algorithm: str = Form("sha256"), file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        hash_value = hash_functions.hash_file_content(file_content, algorithm)
        return {
            "status": "success",
            "file_hash": hash_value,
            "algorithm": algorithm,
            "filename": file.filename,
            "file_size": len(file_content),
            "message": "文件哈希計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件哈希計算失敗: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 