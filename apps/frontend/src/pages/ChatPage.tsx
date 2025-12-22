import { useEffect, useState, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Loader2, Send, User, Code } from 'lucide-react'

import { MarkdownEditor } from '@/components/markdown'
import { useTranslate, type TranslateState } from '@/hooks/useTranslate'
import { cn } from '@/utils/cn'

const quickStarts = [
  '我们想做一个智能推荐，提高用户停留时长。',
  '订单服务需要支持幂等与重试，接口需要怎么设计？',
  '请帮我把"开发实现难度高"解释成产品能理解的语言。',
]

type EmptyStateProps = {
  input: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void
  onQuickStart: (question: string) => void
}

type ChatResultsProps = {
  isLoading: boolean
  content: TranslateState['content']
  error: TranslateState['error']
  direction: TranslateState['direction']
  perspective: TranslateState['perspective']
  gaps: TranslateState['gaps']
  onContentChange: (value: string) => void
}

type InputDockProps = {
  input: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void
}

function EmptyState({
  input,
  isLoading,
  onInputChange,
  onSubmit,
  onQuickStart,
}: EmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4">
      <div className="mb-10 flex flex-col items-center gap-2 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 className="text-2xl font-medium tracking-tight text-slate-800">
          输入需求，对齐理解
        </h1>
        <p className="text-sm text-slate-500">
          自动识别视角，翻译成对方理解的语言
        </p>
      </div>

      <form
        onSubmit={onSubmit}
        className="w-full max-w-2xl animate-in fade-in slide-in-from-bottom-6 duration-500 delay-100"
      >
        <div
          className={cn(
            'group relative overflow-hidden rounded-2xl border bg-white transition-all duration-300',
            'border-slate-200/80 shadow-lg shadow-slate-200/50',
            'focus-within:border-indigo-300 focus-within:shadow-xl focus-within:shadow-indigo-500/10'
          )}
        >
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-linear-to-r from-transparent via-indigo-400/50 to-transparent opacity-0 transition-opacity group-focus-within:opacity-100" />

          <textarea
            value={input}
            onChange={(event) => onInputChange(event.target.value)}
            placeholder="描述你的需求、技术方案或沟通难点..."
            rows={4}
            className="w-full resize-none bg-transparent px-5 py-4 text-base leading-relaxed text-slate-800 outline-none placeholder:text-slate-400"
          />

          <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="inline-flex items-center gap-1">
                <kbd className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-500">
                  Enter
                </kbd>
                发送
              </span>
            </div>
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={cn(
                'inline-flex h-9 items-center gap-2 rounded-xl px-4 text-sm font-medium transition-all duration-200',
                'bg-indigo-600 text-white shadow-md shadow-indigo-500/25',
                'hover:bg-indigo-500 hover:shadow-lg hover:shadow-indigo-500/30',
                'disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none'
              )}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  发送
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      <div className="mt-8 flex w-full max-w-md flex-col gap-3 animate-in fade-in slide-in-from-bottom-8 duration-500 delay-200">
        {quickStarts.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onQuickStart(question)}
            className={cn(
              'w-full rounded-xl border px-4 py-3 text-left text-sm transition-all duration-200',
              'border-slate-200 bg-white/80 text-slate-600 backdrop-blur-sm',
              'hover:border-indigo-200 hover:bg-indigo-50/80 hover:text-indigo-700'
            )}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}

function ChatResults({
  isLoading,
  content,
  error,
  direction,
  perspective,
  gaps,
  onContentChange,
}: ChatResultsProps) {
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isLoading && contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }, [content, isLoading])

  const hasAnalysisData = perspective || gaps.length > 0

  const perspectiveConfig = {
    pm: {
      label: '产品视角',
      icon: User,
      description: '将翻译为开发语言',
    },
    dev: {
      label: '开发视角',
      icon: Code,
      description: '将翻译为产品语言',
    },
    unknown: {
      label: '未识别',
      icon: User,
      description: '无法确定视角',
    },
  }

  return (
    <div ref={contentRef} className="flex min-h-0 flex-1 gap-8 pb-4">
      {/* 主内容区 - GitHub 风格 3/4 宽度 */}
      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        {/* 翻译结果 */}
        <div className="flex min-h-0 flex-1 flex-col rounded-md border border-slate-200">
          <div className="flex shrink-0 items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-900">翻译结果</h2>
            {direction && (
              <span className="text-xs text-slate-500">
                {direction === 'pm_to_dev' ? '产品 → 开发' : '开发 → 产品'}
              </span>
            )}
          </div>
          <div className="flex min-h-0 flex-1 flex-col p-4">
            {content ? (
              <MarkdownEditor
                value={content}
                onChange={onContentChange}
                isStreaming={isLoading}
                readOnly={isLoading}
                className="min-h-0 flex-1"
              />
            ) : isLoading ? (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                正在翻译...
              </div>
            ) : error ? (
              <div className="text-sm text-red-600">{error}</div>
            ) : null}
          </div>
        </div>
      </div>

      {/* 右侧边栏 - GitHub 风格 1/4 宽度 */}
      {!isLoading && hasAnalysisData && (
        <div className="hidden w-80 shrink-0 lg:block">
          <div className="sticky top-0 space-y-4">
            {/* 视角识别 */}
            {perspective && (() => {
              const config = perspectiveConfig[perspective.perspective ?? 'unknown']
              const IconComponent = config.icon
              return (
                <div className="border-b border-slate-200 pb-4">
                  <h3 className="mb-2 text-xs font-semibold text-slate-900">视角识别</h3>
                  <div className="flex items-center gap-2">
                    <IconComponent className="h-4 w-4 text-slate-500" />
                    <span className="text-xs text-slate-600">{config.label}</span>
                    {perspective.confidence !== undefined && (
                      <span className="text-xs text-slate-400">
                        {Math.round(perspective.confidence * 100)}%
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{config.description}</p>
                </div>
              )
            })()}

            {/* 缺失信息 */}
            {gaps.length > 0 && (
              <div>
                <h3 className="mb-2 text-xs font-semibold text-slate-900">可能缺失的信息</h3>
                <ul className="space-y-3">
                  {gaps.map((gap, index) => (
                    <li key={index} className="flex gap-2">
                      <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-amber-100 text-[10px] font-medium text-amber-700">
                        {index + 1}
                      </span>
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-slate-700">{gap.category}</p>
                        <p className="text-xs text-slate-500">{gap.description}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function InputDock({
  input,
  isLoading,
  onInputChange,
  onSubmit,
}: InputDockProps) {
  return (
    <div className="sticky bottom-0 border-t border-slate-200 bg-white/90 backdrop-blur">
      <form onSubmit={onSubmit} className="mx-auto flex w-full max-w-3xl flex-col gap-2 py-4">
        <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
          <textarea
            value={input}
            onChange={(event) => onInputChange(event.target.value)}
            placeholder="继续提问..."
            rows={1}
            className="w-full resize-none text-sm text-slate-900 outline-none placeholder:text-slate-400"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              'inline-flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 text-white shadow-sm',
              'disabled:cursor-not-allowed disabled:bg-slate-300'
            )}
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
        <span className="text-right text-xs text-slate-400">按 Enter 发送，Shift+Enter 换行</span>
      </form>
    </div>
  )
}

export function ChatPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const [editedContent, setEditedContent] = useState<string | null>(null)
  const {
    isLoading,
    translationId,
    perspective,
    gaps,
    content,
    direction,
    error,
    translate,
    loadTranslation,
  } = useTranslate()

  // 加载已有翻译记录
  useEffect(() => {
    if (id) {
      loadTranslation(id)
    }
  }, [id, loadTranslation])

  // 翻译完成后更新 URL
  useEffect(() => {
    if (translationId && !id) {
      navigate(`/chat/${translationId}`, { replace: true })
    }
  }, [translationId, id, navigate])

  const displayContent = editedContent ?? content

  const hasResult = Boolean(displayContent || error)
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!input.trim() || isLoading) return

    setEditedContent(null)

    await translate({
      content: input.trim(),
    })
  }

  const handleQuickStart = (question: string) => {
    setInput(question)
  }

  const handleContentChange = (value: string) => {
    setEditedContent(value)
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-130px)] w-full max-w-7xl flex-col px-6 py-6 sm:px-8 sm:py-8">
      {/* Main Content */}
      <div className="flex min-h-0 flex-1 flex-col">
        {!hasResult && !isLoading ? (
          <EmptyState
            input={input}
            isLoading={isLoading}
            onInputChange={setInput}
            onSubmit={handleSubmit}
            onQuickStart={handleQuickStart}
          />
        ) : (
          <ChatResults
            isLoading={isLoading}
            content={displayContent}
            error={error}
            direction={direction}
            perspective={perspective}
            gaps={gaps}
            onContentChange={handleContentChange}
          />
        )}
      </div>

      {/* Input Dock */}
      {(hasResult || isLoading) && (
        <InputDock
          input={input}
          isLoading={isLoading}
          onInputChange={setInput}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  )
}
