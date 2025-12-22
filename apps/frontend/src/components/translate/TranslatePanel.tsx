/**
 * 翻译面板组件
 */

import { useState } from 'react'
import { cn } from '@/utils/cn'
import { Send, Loader2, RotateCcw } from 'lucide-react'
import { useTranslate } from '@/hooks/useTranslate'
import { PerspectiveIndicator } from './PerspectiveIndicator'
import { GapsCard } from './GapsCard'

export function TranslatePanel() {
  const [input, setInput] = useState('')
  const [context, setContext] = useState('')
  const {
    isLoading,
    perspective,
    gaps,
    suggestions,
    content,
    direction,
    error,
    translate,
    reset,
  } = useTranslate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    await translate({
      content: input.trim(),
      context: context.trim() || undefined,
    })
  }

  const handleReset = () => {
    setInput('')
    setContext('')
    reset()
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      {/* 标题 */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">BridgeTalk</h1>
        <p className="mt-2 text-gray-600">
          帮助产品经理和开发工程师更好地理解彼此
        </p>
      </div>

      {/* 输入区域 */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="content"
            className="block text-sm font-medium text-gray-700"
          >
            输入内容
          </label>
          <textarea
            id="content"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入产品需求或技术方案，AI 会自动识别并翻译..."
            className={cn(
              'mt-1 block w-full rounded-lg border border-gray-300 px-4 py-3',
              'focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20',
              'resize-none text-gray-900 placeholder:text-gray-400'
            )}
            rows={6}
            disabled={isLoading}
          />
        </div>

        <div>
          <label
            htmlFor="context"
            className="block text-sm font-medium text-gray-700"
          >
            补充上下文（可选）
          </label>
          <textarea
            id="context"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="提供额外的背景信息..."
            className={cn(
              'mt-1 block w-full rounded-lg border border-gray-300 px-4 py-3',
              'focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20',
              'resize-none text-gray-900 placeholder:text-gray-400'
            )}
            rows={2}
            disabled={isLoading}
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              'flex items-center gap-2 rounded-lg px-6 py-2.5 font-medium text-white',
              'bg-blue-600 hover:bg-blue-700',
              'disabled:cursor-not-allowed disabled:opacity-50',
              'transition-colors'
            )}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                翻译中...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                开始翻译
              </>
            )}
          </button>

          {(content || error) && (
            <button
              type="button"
              onClick={handleReset}
              className={cn(
                'flex items-center gap-2 rounded-lg px-4 py-2.5 font-medium',
                'border border-gray-300 text-gray-700 hover:bg-gray-50',
                'transition-colors'
              )}
            >
              <RotateCcw className="h-4 w-4" />
              重置
            </button>
          )}
        </div>
      </form>

      {/* 错误提示 */}
      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* 结果区域 */}
      {(perspective || content) && (
        <div className="mt-8 space-y-4">
          {/* 视角识别结果 */}
          <PerspectiveIndicator
            perspective={perspective?.perspective ?? null}
            confidence={perspective?.confidence}
            reason={perspective?.reason}
          />

          {/* 缺失信息提示 */}
          <GapsCard gaps={gaps} suggestions={suggestions} />

          {/* 翻译结果 */}
          {content && (
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="font-medium text-gray-900">翻译结果</h3>
                {direction && (
                  <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600">
                    {direction === 'pm_to_dev' ? '产品 → 开发' : '开发 → 产品'}
                  </span>
                )}
              </div>
              <div className="prose prose-sm max-w-none whitespace-pre-wrap text-gray-700">
                {content}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
