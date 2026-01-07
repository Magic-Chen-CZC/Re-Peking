import sys
from pathlib import Path

from loguru import logger

from config import settings

# 移除默认的 handler
logger.remove()

# 配置控制台输出：彩色高亮，INFO 级别以上
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
)

# 确保日志目录存在
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置文件输出：每天 0 点轮转，保留 7 天，DEBUG 级别以上
logger.add(
    "logs/app.log",
    rotation="00:00",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    encoding="utf-8",
)

# 导出 logger 供其他模块使用
__all__ = ["logger"]
