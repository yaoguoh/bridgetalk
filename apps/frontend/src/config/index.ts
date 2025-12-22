/**
 * 应用配置
 *
 * 使用 Vite 环境变量：
 * - 开发环境：通过 proxy 转发到 localhost:8001
 * - 生产环境：通过 VITE_API_BASE_URL 指定 API 地址
 */

export const config = {
  /**
   * API 基础 URL
   * - 开发环境：空字符串（使用 vite proxy）
   * - 生产环境：通过 VITE_API_BASE_URL 环境变量配置
   */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '',

  /**
   * 应用名称
   */
  appName: 'BridgeTalk',

  /**
   * 应用版本
   */
  appVersion: '1.0.0',
} as const

export type AppConfig = typeof config
