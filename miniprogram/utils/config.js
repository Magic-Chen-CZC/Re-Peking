/**
 * 应用配置文件
 * 统一管理 API 地址、环境变量等配置
 */

// 环境配置
const ENV = 'dev'; // 可选值：'dev', 'prod'

// API 基础地址配置
const API_BASE_URLS = {
  dev: 'http://127.0.0.1:8000',
  prod: 'https://api.yourapp.com' // 替换为实际生产环境域名
};

// 当前环境的 API 基础地址
const API_BASE_URL = API_BASE_URLS[ENV];

module.exports = {
  ENV,
  API_BASE_URL
};
