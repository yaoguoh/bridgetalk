/**
 * 应用根布局组件
 */

import { Outlet } from 'react-router-dom'

import { Header } from './Header'

export function RootLayout() {
  return (
    <div className="min-h-screen w-full bg-slate-100 p-4">
      <div className="min-h-[calc(100vh-2rem)] w-full rounded-lg border border-slate-200 bg-white shadow-sm">
        <Header />
        <Outlet />
      </div>
    </div>
  )
}
