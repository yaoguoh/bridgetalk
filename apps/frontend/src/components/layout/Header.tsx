/**
 * 全局导航 Header 组件
 */

import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Dialog, DialogPanel } from '@headlessui/react'
import { Menu, X, MessageSquare } from 'lucide-react'

import { cn } from '@/utils/cn'

const navigation = [
  { name: '首页', href: '/' },
  { name: '对话', href: '/chat' },
  { name: '历史', href: '/history' },
]

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (href: string) => {
    if (href === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  return (
    <header className="rounded-t-lg bg-white border-b border-slate-200">
      <nav aria-label="Global" className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
        <div className="flex flex-1">
          <div className="hidden lg:flex lg:gap-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'text-sm font-medium transition-colors',
                  isActive(item.href)
                    ? 'text-indigo-600'
                    : 'text-slate-600 hover:text-slate-900'
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
          <div className="flex lg:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-slate-700"
            >
              <span className="sr-only">打开菜单</span>
              <Menu aria-hidden="true" className="h-6 w-6" />
            </button>
          </div>
        </div>

        <Link to="/" className="flex items-center gap-2">
          <MessageSquare className="h-6 w-6 text-indigo-600" />
          <span className="text-lg font-semibold text-slate-900">BridgeTalk</span>
        </Link>

        <div className="flex flex-1 justify-end">
          <Link
            to="/chat"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 transition-colors"
          >
            开始对话
          </Link>
        </div>
      </nav>

      <Dialog open={mobileMenuOpen} onClose={setMobileMenuOpen} className="lg:hidden">
        <div className="fixed inset-0 z-10 bg-black/20" />
        <DialogPanel className="fixed inset-y-0 left-0 z-20 w-full overflow-y-auto bg-white px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex flex-1">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(false)}
                className="-m-2.5 rounded-md p-2.5 text-slate-700"
              >
                <span className="sr-only">关闭菜单</span>
                <X aria-hidden="true" className="h-6 w-6" />
              </button>
            </div>
            <Link to="/" className="flex items-center gap-2" onClick={() => setMobileMenuOpen(false)}>
              <MessageSquare className="h-6 w-6 text-indigo-600" />
              <span className="text-lg font-semibold text-slate-900">BridgeTalk</span>
            </Link>
            <div className="flex flex-1 justify-end">
              <Link
                to="/chat"
                onClick={() => setMobileMenuOpen(false)}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
              >
                开始对话
              </Link>
            </div>
          </div>
          <div className="mt-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  '-mx-3 block rounded-lg px-3 py-2 text-base font-medium transition-colors',
                  isActive(item.href)
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-slate-700 hover:bg-slate-50'
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </DialogPanel>
      </Dialog>
    </header>
  )
}
