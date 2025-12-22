import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Clock, Loader2, MessageSquare, User, Code } from 'lucide-react'

import { cn } from '@/utils/cn'

type TranslationItem = {
  id: string
  content: string
  translated_content: string
  direction: string
  detected_perspective: string | null
  gaps: Array<{ category: string; description: string; importance: string }>
  created_at: string
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type HistoryData = {
  content: TranslationItem[]
  total: number
  page: number
  size: number
  total_pages: number
}

export function HistoryPage() {
  const [items, setItems] = useState<TranslationItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 10

  useEffect(() => {
    const fetchHistory = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await fetch(`/api/translate/history?page=${page}&size=${pageSize}`)
        if (!response.ok) {
          throw new Error('获取历史记录失败')
        }
        const result: ApiResponse<HistoryData> = await response.json()
        if (result.code !== 200) {
          throw new Error(result.message || '获取历史记录失败')
        }
        setItems(result.data.content)
        setTotal(result.data.total)
      } catch (err) {
        setError(err instanceof Error ? err.message : '未知错误')
      } finally {
        setIsLoading(false)
      }
    }

    fetchHistory()
  }, [page])

  const totalPages = Math.ceil(total / pageSize)

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col px-6 py-8 sm:px-10 sm:py-10">
      <h1 className="mb-6 text-xl font-semibold text-slate-900">历史记录</h1>

      {/* Content */}
      {isLoading ? (
        <div className="flex flex-1 items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center py-12 text-slate-500">
          <MessageSquare className="mb-4 h-12 w-12 text-slate-300" />
          <p>暂无翻译记录</p>
          <Link
            to="/chat"
            className="mt-4 text-sm text-indigo-600 hover:text-indigo-500"
          >
            开始第一次翻译
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {items.map((item) => (
              <Link
                key={item.id}
                to={`/chat/${item.id}`}
                className="block rounded-xl border border-slate-200 bg-white p-4 transition-shadow hover:shadow-md"
              >
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
                        item.detected_perspective === 'pm'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-green-100 text-green-700'
                      )}
                    >
                      {item.detected_perspective === 'pm' ? (
                        <User className="h-3 w-3" />
                      ) : (
                        <Code className="h-3 w-3" />
                      )}
                      {item.detected_perspective === 'pm' ? '产品视角' : '开发视角'}
                    </span>
                    <span className="text-xs text-slate-400">
                      {item.direction === 'pm_to_dev' ? '→ 开发' : '→ 产品'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-slate-400">
                    <Clock className="h-3 w-3" />
                    {formatDate(item.created_at)}
                  </div>
                </div>
                <p className="text-sm text-slate-600">
                  {truncateText(item.content, 100)}
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  {truncateText(item.translated_content, 150)}
                </p>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                上一页
              </button>
              <span className="text-sm text-slate-500">
                {page} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
