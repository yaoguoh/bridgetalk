import { cn } from '@/utils/cn'

type MainCenterProps = {
  children: React.ReactNode
  className?: string
  containerClassName?: string
  contentClassName?: string
}

export function MainCenter({
  children,
  className,
  containerClassName,
  contentClassName,
}: MainCenterProps) {
  return (
    <div className={cn('min-h-screen w-full bg-slate-100 p-3 sm:p-4', containerClassName)}>
      <section
        className={cn(
          'min-h-[calc(100vh-1.5rem)] w-full rounded-lg border border-slate-200/40 bg-white shadow-sm sm:min-h-[calc(100vh-2rem)]',
          className
        )}
      >
        <div className={cn('mx-auto w-full max-w-5xl px-6 py-10 sm:px-8 sm:py-12', contentClassName)}>
          {children}
        </div>
      </section>
    </div>
  )
}
