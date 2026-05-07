/**
 * api.js — 后端接口请求封装
 *
 * 作用：
 *   把对后端（fraud-detector，localhost:8000）的请求封装成函数，
 *   组件只需要调用函数，不用关心 URL 怎么写。
 *
 * 用到的库：axios
 *   axios 是 JavaScript 里最常用的 HTTP 请求库，
 *   类似于 Python 里的 requests。
 */

import axios from 'axios';

// 后端地址（fraud-detector 的 FastAPI 服务）
const BASE_URL = 'http://localhost:8000';

/**
 * 获取最近的交易列表
 * @param {number} limit - 获取几条，默认50
 */
export async function fetchTransactions(limit = 50) {
  const res = await axios.get(`${BASE_URL}/transactions?limit=${limit}`);
  return res.data.data;  // 返回交易数组
}

/**
 * 获取统计数据（总数、欺诈数、欺诈率等）
 */
export async function fetchStats() {
  const res = await axios.get(`${BASE_URL}/stats`);
  return res.data;
}

/**
 * 检查后端是否在线
 */
export async function checkHealth() {
  try {
    await axios.get(`${BASE_URL}/health`);
    return true;
  } catch {
    return false;
  }
}
