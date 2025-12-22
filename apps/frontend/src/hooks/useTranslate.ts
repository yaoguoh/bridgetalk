/**
 * SSE 翻译 Hook
 */

import { useState, useCallback, useRef } from 'react'
import type {
  TranslateRequest,
  PerspectiveDetectedData,
  GapsIdentifiedData,
  ContentDeltaData,
  MessageDoneData,
  GapItem,
  ApiResponse,
  TranslationRecord,
} from '@/api/types'

export type TranslateState = {
  isLoading: boolean
  translationId: string | null
  originalContent: string
  perspective: PerspectiveDetectedData | null
  gaps: GapItem[]
  suggestions: string[]
  content: string
  direction: string | null
  error: string | null
}

const initialState: TranslateState = {
  isLoading: false,
  translationId: null,
  originalContent: '',
  perspective: null,
  gaps: [],
  suggestions: [],
  content: '',
  direction: null,
  error: null,
}

export function useTranslate() {
  const [state, setState] = useState<TranslateState>(initialState)
  const abortControllerRef = useRef<AbortController | null>(null)

  const reset = useCallback(() => {
    setState(initialState)
  }, [])

  const handleSSEEvent = useCallback((event: { event: string; data: unknown }) => {
    switch (event.event) {
      case 'perspective_detected':
        setState((prev) => ({
          ...prev,
          perspective: event.data as PerspectiveDetectedData,
        }))
        break

      case 'gaps_identified': {
        const gapsData = event.data as GapsIdentifiedData
        setState((prev) => ({
          ...prev,
          gaps: gapsData.gaps,
          suggestions: gapsData.suggestions,
        }))
        break
      }

      case 'translation_start':
        setState((prev) => ({
          ...prev,
          direction: (event.data as { direction: string }).direction,
        }))
        break

      case 'content_delta':
        setState((prev) => ({
          ...prev,
          content: prev.content + (event.data as ContentDeltaData).delta,
        }))
        break

      case 'message_done': {
        const doneData = event.data as MessageDoneData
        setState((prev) => ({
          ...prev,
          isLoading: false,
          translationId: doneData.translation_id,
          content: doneData.translated_content,
          direction: doneData.direction,
        }))
        break
      }

      case 'error':
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: (event.data as { message: string }).message,
        }))
        break
    }
  }, [])

  const translate = useCallback(async (request: TranslateRequest) => {
    // 取消之前的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // 重置状态
    setState({
      ...initialState,
      isLoading: true,
      originalContent: request.content,
    })

    // 创建新的 AbortController
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('/api/translate/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...request,
          stream: true,
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // 解析 SSE 事件
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEvent = ''
        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.slice(6).trim()
            continue
          }

          if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim()
            if (!dataStr || !currentEvent) continue

            try {
              const data = JSON.parse(dataStr)
              handleSSEEvent({ event: currentEvent, data })
              currentEvent = ''
            } catch {
              // 忽略解析错误
            }
          }

          // 空行重置 event
          if (line.trim() === '') {
            currentEvent = ''
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return
      }
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : '翻译失败',
      }))
    }
  }, [handleSSEEvent])

  const loadTranslation = useCallback(async (id: string) => {
    setState({
      ...initialState,
      isLoading: true,
    })

    try {
      const response = await fetch(`/api/translate/${id}`)
      if (!response.ok) {
        throw new Error('加载翻译记录失败')
      }

      const result: ApiResponse<TranslationRecord> = await response.json()
      if (result.code !== 200) {
        throw new Error(result.message || '加载翻译记录失败')
      }

      const record = result.data
      setState({
        isLoading: false,
        translationId: record.id,
        originalContent: record.content,
        perspective: record.detected_perspective
          ? {
              perspective: record.detected_perspective as 'pm' | 'dev' | 'unknown',
              confidence: 1,
              reason: '',
            }
          : null,
        gaps: record.gaps,
        suggestions: [],
        content: record.translated_content,
        direction: record.direction,
        error: null,
      })
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : '加载失败',
      }))
    }
  }, [])

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setState((prev) => ({
      ...prev,
      isLoading: false,
    }))
  }, [])

  return {
    ...state,
    translate,
    loadTranslation,
    reset,
    cancel,
  }
}
