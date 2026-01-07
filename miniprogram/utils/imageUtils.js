const { API_BASE_URL } = require('./config.js');

/**
 * POI 封面图片映射表
 * 用于在没有用户上传图片时，根据 poi_id 提供本地兜底图片
 */
const POI_COVER_MAP = {
  // 京城名胜
  'gugong': '/image/attractions/gugong.png',
  'tiantan': '/image/attractions/tiantan.png',
  'tiananmen': '/image/attractions/tiananmen.png',
  'yiheyuan': '/image/attractions/yiheyuan.png',
  'changcheng': '/image/attractions/changcheng.png',
  'yuanmingyuan': '/image/attractions/yuanmingyuan.png',
  'ditan': '/image/attractions/ditan.png',
  'beihai': '/image/attractions/beihai.png',
  'jingshan': '/image/attractions/jingshan.png',
  'shichahai': '/image/attractions/shichahai.png',
  
  // 胡同文化
  'nanluoguxiang': '/image/attractions/nanluoguxiang.png',
  'wudaoying': '/image/attractions/wudaoying.png',
  'guozijian': '/image/attractions/guozijian.png',
  'yonghegong': '/image/attractions/yonghegong.png',
  
  // 艺术现代
  '798': '/image/attractions/798.png',
  'sanlitun': '/image/attractions/sanlitun.png',
  'guomao': '/image/attractions/guomao.png',
  
  // 宗教寺庙
  'baiyunguan': '/image/attractions/baiyunguan.png',
  'tanzhe': '/image/attractions/tanzhe.png',
  'jietai': '/image/attractions/jietai.png',
  
  // 自然户外
  'xiangshan': '/image/attractions/xiangshan.png',
  'botanical': '/image/attractions/botanical.png',
  'olympic': '/image/attractions/olympic.png'
};

/**
 * 规范化图片 URL
 * 
 * @param {string} rawUrl - 原始图片 URL
 * @param {string} fallbackUrl - 兜底图片 URL（可选，默认使用故宫图片）
 * @returns {string} 规范化后的图片 URL
 */
function normalizeImageSrc(rawUrl, fallbackUrl) {
  // 使用默认兜底图片
  const defaultFallback = fallbackUrl || '/image/attractions/gugong.png';
  
  // 空值处理
  if (!rawUrl || rawUrl === '' || rawUrl === null || rawUrl === undefined) {
    return defaultFallback;
  }
  
  // 转为字符串（防止传入非字符串类型）
  const url = String(rawUrl).trim();
  
  // 空字符串检查
  if (url === '') {
    return defaultFallback;
  }
  
  // wxfile:// 临时文件路径（仅用于发布前预览，不应写入 DB）
  if (url.startsWith('wxfile://')) {
    console.warn('[normalizeImageSrc] wxfile:// 路径仅用于预览:', url);
    return url;
  }
  
  // http://tmp/ 或 https://tmp/ 临时路径（无效，返回兜底）
  if (url.includes('//tmp/') || url.includes('/tmp/')) {
    console.warn('[normalizeImageSrc] 临时路径无效，使用兜底图片:', url);
    return defaultFallback;
  }
  
  // HTTP/HTTPS 完整 URL
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  
  // 相对路径（以 / 开头）
  if (url.startsWith('/')) {
    // 如果是本地静态资源路径（/image/ 开头），直接返回
    if (url.startsWith('/image/')) {
      return url;
    }
    // 否则拼接后端 API 地址（确保不重复拼接）
    return `${API_BASE_URL}${url}`;
  }
  
  // 其他情况（非法格式）
  console.warn('[normalizeImageSrc] 未知格式，使用兜底图片:', url);
  return defaultFallback;
}

/**
 * 根据 POI ID 获取封面图片
 * 
 * @param {string} poiId - POI ID
 * @returns {string} 图片路径
 */
function getPoiCoverImage(poiId) {
  if (!poiId) {
    return '/image/attractions/gugong.png';
  }
  return POI_COVER_MAP[poiId] || '/image/attractions/gugong.png';
}

/**
 * 清理临时图片路径（发布时使用）
 * 如果图片是临时路径（wxfile:// 或 http://tmp/ 或包含 /tmp/），返回空字符串
 * 
 * @param {string} imageUrl - 图片 URL
 * @returns {string} 清理后的 URL（临时路径返回 ''）
 */
function cleanTempImageUrl(imageUrl) {
  if (!imageUrl || imageUrl === '' || imageUrl === null || imageUrl === undefined) {
    return '';
  }
  
  const url = String(imageUrl).trim();
  
  // 临时路径，置空
  if (url.startsWith('wxfile://') || 
      url.includes('//tmp/') || 
      url.includes('/tmp/')) {
    console.log('[cleanTempImageUrl] 清理临时路径:', url);
    return '';
  }
  
  // 其他路径保留
  return imageUrl;
}

module.exports = {
  POI_COVER_MAP,
  normalizeImageSrc,
  getPoiCoverImage,
  cleanTempImageUrl
};
