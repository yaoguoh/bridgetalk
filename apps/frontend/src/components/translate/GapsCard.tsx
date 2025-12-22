/**
 * 缺失信息卡片组件
 */

import { cn } from '@/utils/cn'
import { AlertCircle } from 'lucide-react'
import type { GapItem } from '@/api/types'

interface GapsCardProps {
  gaps: GapItem[]
  suggestions: string[]
  className?: string
}

export function GapsCard({ gaps, suggestions, className }: GapsCardProps) {
  if (gaps.length === 0 && suggestions.length === 0) return null

  const importanceColor = {
    high: 'text-red-600 bg-red-50',
    medium: 'text-yellow-600 bg-yellow-50',
    low: 'text-gray-600 bg-gray-50',
  }

  return (
    <div
      className={cn(
        'rounded-lg border border-yellow-200 bg-yellow-50 p-4',
        className
      )}
    >
      <div className="flex items-center gap-2 text-yellow-700">
        <AlertCircle className="h-4 w-4" />
        <span className="font-medium">发现可能缺失的信息</span>
      </div>

      {gaps.length > 0 && (
        <ul className="mt-3 space-y-2">
          {gaps.map((gap, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <span
                className={cn(
                  'mt-0.5 rounded px-1.5 py-0.5 text-xs font-medium',
                  importanceColor[gap.importance]
                )}
              >
                {gap.category}
              </span>
              <span className="text-yellow-800">{gap.description}</span>
            </li>
          ))}
        </ul>
      )}

      {suggestions.length > 0 && (
        <div className="mt-3 border-t border-yellow-200 pt-3">
          <p className="text-xs font-medium text-yellow-700">建议补充：</p>
          <ul className="mt-1 space-y-1">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="text-sm text-yellow-800">
                • {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
