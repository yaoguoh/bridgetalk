/**
 * 视角指示器组件
 */

import { cn } from '@/utils/cn'
import { User, Code } from 'lucide-react'

interface PerspectiveIndicatorProps {
  perspective: 'pm' | 'dev' | 'unknown' | null
  confidence?: number
  reason?: string
  className?: string
}

export function PerspectiveIndicator({
  perspective,
  confidence,
  reason,
  className,
}: PerspectiveIndicatorProps) {
  if (!perspective) return null

  const config = {
    pm: {
      label: '产品视角',
      icon: User,
      color: 'bg-blue-100 text-blue-700 border-blue-200',
      description: '将翻译为开发语言',
    },
    dev: {
      label: '开发视角',
      icon: Code,
      color: 'bg-green-100 text-green-700 border-green-200',
      description: '将翻译为产品语言',
    },
    unknown: {
      label: '未识别',
      icon: User,
      color: 'bg-gray-100 text-gray-700 border-gray-200',
      description: '无法确定视角',
    },
  }

  const { label, icon: Icon, color, description } = config[perspective]

  return (
    <div className={cn('rounded-lg border p-3', color, className)}>
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4" />
        <span className="font-medium">{label}</span>
        {confidence !== undefined && (
          <span className="text-xs opacity-70">
            ({Math.round(confidence * 100)}%)
          </span>
        )}
      </div>
      <p className="mt-1 text-sm opacity-80">{description}</p>
      {reason && <p className="mt-1 text-xs opacity-60">{reason}</p>}
    </div>
  )
}
