/**
 * Markdown 预览/编辑器组件
 * 支持预览模式（Markdown 渲染）和编辑模式（原始文本）切换
 */

import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Eye, Pencil, Loader2, Copy, Check } from 'lucide-react'

import { cn } from '@/utils/cn'
import './markdown.css'

type MarkdownEditorProps = {
  value: string
  onChange?: (value: string) => void
  readOnly?: boolean
  isStreaming?: boolean
  className?: string
}

type CodeBlockProps = {
  className?: string
  children?: React.ReactNode
}

function CodeBlock({ className, children }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const match = /language-(\w+)/.exec(className || '')
  const language = match ? match[1] : ''
  const codeString = String(children).replace(/\n$/, '')

  const handleCopy = async () => {
    await navigator.clipboard.writeText(codeString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!match) {
    return (
      <code className="rounded bg-slate-100 px-1.5 py-0.5 text-sm font-mono text-slate-800">
        {children}
      </code>
    )
  }

  return (
    <div className="group relative">
      <button
        type="button"
        onClick={handleCopy}
        className={cn(
          'absolute right-2 top-2 rounded p-1.5 text-slate-400 opacity-0 transition-opacity',
          'hover:bg-slate-200 hover:text-slate-600',
          'group-hover:opacity-100'
        )}
        title="复制代码"
      >
        {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
      </button>
      <SyntaxHighlighter
        style={oneLight}
        language={language}
        PreTag="div"
        customStyle={{
          margin: 0,
          borderRadius: '0.5rem',
          fontSize: '0.875rem',
        }}
      >
        {codeString}
      </SyntaxHighlighter>
    </div>
  )
}

export function MarkdownEditor({
  value,
  onChange,
  readOnly = false,
  isStreaming = false,
  className,
}: MarkdownEditorProps) {
  const [mode, setMode] = useState<'preview' | 'edit'>('preview')
  const [editValue, setEditValue] = useState(value)
  const contentRef = useRef<HTMLDivElement>(null)

  // 流式输出时自动滚动到底部
  useEffect(() => {
    if (isStreaming && contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }, [value, isStreaming])

  const handleModeChange = (newMode: 'preview' | 'edit') => {
    if (newMode === 'edit' && (readOnly || isStreaming)) return

    // 从编辑模式切换到预览模式时，触发 onChange
    if (mode === 'edit' && newMode === 'preview') {
      onChange?.(editValue)
    }

    // 从预览模式切换到编辑模式时，同步最新值
    if (mode === 'preview' && newMode === 'edit') {
      setEditValue(value)
    }

    setMode(newMode)
  }

  const canEdit = !readOnly && !isStreaming

  return (
    <div className={cn('flex flex-col', className)}>
      {/* 顶部工具栏 - GitHub 风格 */}
      <div className="flex items-center justify-between border-b border-slate-200">
        {/* 左侧标签页 */}
        <div className="flex">
          <button
            type="button"
            onClick={() => handleModeChange('preview')}
            className={cn(
              'relative px-4 py-2 text-sm font-medium transition-colors',
              mode === 'preview'
                ? 'text-slate-900'
                : 'text-slate-500 hover:text-slate-700'
            )}
          >
            预览
            {mode === 'preview' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-orange-500" />
            )}
          </button>
          <button
            type="button"
            onClick={() => handleModeChange('edit')}
            disabled={!canEdit}
            className={cn(
              'relative px-4 py-2 text-sm font-medium transition-colors',
              mode === 'edit'
                ? 'text-slate-900'
                : 'text-slate-500 hover:text-slate-700',
              !canEdit && 'cursor-not-allowed opacity-50'
            )}
          >
            编辑
            {mode === 'edit' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-orange-500" />
            )}
          </button>
        </div>

        {/* 右侧工具图标 */}
        <div className="flex items-center gap-1 pr-2">
          {isStreaming ? (
            <div className="flex items-center gap-1.5 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-xs">生成中...</span>
            </div>
          ) : (
            <>
              <button
                type="button"
                onClick={() => handleModeChange('preview')}
                className={cn(
                  'rounded p-1.5 transition-colors',
                  mode === 'preview'
                    ? 'bg-slate-100 text-slate-700'
                    : 'text-slate-400 hover:bg-slate-100 hover:text-slate-600'
                )}
                title="预览模式"
              >
                <Eye className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => handleModeChange('edit')}
                disabled={!canEdit}
                className={cn(
                  'rounded p-1.5 transition-colors',
                  mode === 'edit'
                    ? 'bg-slate-100 text-slate-700'
                    : 'text-slate-400 hover:bg-slate-100 hover:text-slate-600',
                  !canEdit && 'cursor-not-allowed opacity-50'
                )}
                title="编辑模式"
              >
                <Pencil className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* 内容区域 */}
      {mode === 'preview' ? (
        <div
          ref={contentRef}
          className="markdown-body mt-4 min-h-0 flex-1 overflow-y-auto"
        >
          {value ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code: ({ className, children, ...props }) => {
                  const isInline = !className
                  if (isInline) {
                    return (
                      <code
                        className="rounded bg-slate-100 px-1.5 py-0.5 text-sm font-mono text-slate-800"
                        {...props}
                      >
                        {children}
                      </code>
                    )
                  }
                  return <CodeBlock className={className}>{children}</CodeBlock>
                },
              }}
            >
              {value}
            </ReactMarkdown>
          ) : (
            <p className="text-slate-400 italic">暂无内容</p>
          )}
        </div>
      ) : (
        <textarea
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          className={cn(
            'mt-4 min-h-0 flex-1 w-full resize-none rounded-lg border border-slate-200 p-3',
            'font-mono text-sm text-slate-700',
            'focus:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-100'
          )}
          placeholder="输入 Markdown 内容..."
        />
      )}
    </div>
  )
}
