"""
Uploads API：文件上传接口
提供图片上传功能，用于社区分享的封面图片
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import uuid
import logging
from pathlib import Path

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# 设置日志
logger = logging.getLogger("uvicorn.error")

# 上传配置
UPLOAD_DIR = Path("static/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# ============ Response 模型 ============

class UploadImageResponse(BaseModel):
    """图片上传响应"""
    url: str


# ============ API 端点 ============

@router.post("/image", response_model=UploadImageResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片
    
    接收 multipart/form-data，保存到 static/uploads/，返回 URL
    
    Args:
        file: 上传的图片文件
    
    Returns:
        { "url": "http://127.0.0.1:8000/static/uploads/xxx.jpg" }
    
    Raises:
        HTTPException 400: 文件类型不支持或文件过大
        HTTPException 500: 保存失败
    """
    logger.info(f"[upload_image] 开始上传图片，文件名={file.filename}")
    
    # 1. 验证文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.error(f"[upload_image] 不支持的文件类型: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 2. 读取文件内容并验证大小
    try:
        contents = await file.read()
        file_size = len(contents)
        logger.info(f"[upload_image] 文件大小: {file_size} bytes")
        
        if file_size > MAX_FILE_SIZE:
            logger.error(f"[upload_image] 文件过大: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"文件过大: {file_size / 1024 / 1024:.2f}MB，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
    except Exception as e:
        logger.error(f"[upload_image] 读取文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")
    
    # 3. 确保上传目录存在
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"[upload_image] 上传目录: {UPLOAD_DIR}")
    except Exception as e:
        logger.error(f"[upload_image] 创建上传目录失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建上传目录失败: {str(e)}")
    
    # 4. 生成唯一文件名（使用 UUID）
    file_uuid = uuid.uuid4()
    unique_filename = f"{file_uuid}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    logger.info(f"[upload_image] 保存路径: {file_path}")
    
    # 5. 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"[upload_image] ✅ 文件保存成功: {file_path}")
    except Exception as e:
        logger.error(f"[upload_image] 保存文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    # 6. 生成访问 URL
    # 假设后端运行在 http://127.0.0.1:8000
    # 实际部署时应从配置文件读取 BASE_URL
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    file_url = f"{base_url}/static/uploads/{unique_filename}"
    
    logger.info(f"[upload_image] ✅ 上传成功，URL: {file_url}")
    
    return UploadImageResponse(url=file_url)


# ============ curl 验证示例 ============
"""
# 上传图片
curl -X POST http://127.0.0.1:8000/api/uploads/image \
  -F "file=@/path/to/your/image.jpg"

# 响应示例
{
  "url": "http://127.0.0.1:8000/static/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
}
"""
