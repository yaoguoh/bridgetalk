/**
 * 翻译 API 类型定义
 */

export interface TranslateRequest {
  content: string
  stream?: boolean
  context?: string
}

export interface TranslateResponse {
  translated_content: string
  original_content: string
  direction: string
  detected_perspective: string
  gaps: GapItem[]
  suggestions: string[]
}

export interface GapItem {
  category: string
  description: string
  importance: 'high' | 'medium' | 'low'
}

export interface SSEEvent {
  event: string
  data: unknown
}

export interface PerspectiveDetectedData {
  perspective: 'pm' | 'dev' | 'unknown'
  confidence: number
  reason: string
}

export interface GapsIdentifiedData {
  gaps: GapItem[]
  suggestions: string[]
}

export interface TranslationStartData {
  direction: string
}

export interface ContentDeltaData {
  delta: string
}

export interface MessageDoneData {
  translated_content: string
  detected_perspective: string
  direction: string
  gaps: GapItem[]
  suggestions: string[]
  translation_id: string
}

export interface TranslationRecord {
  id: string
  content: string
  translated_content: string
  direction: string
  detected_perspective: string | null
  gaps: GapItem[]
  created_at: string
}

export type ApiResponse<T> = {
  code: number
  message: string
  data: T
}
