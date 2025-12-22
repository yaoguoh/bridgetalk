import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import { RootLayout } from '@/components/layout/RootLayout'
import { ChatPage } from '@/pages/ChatPage'
import { HistoryPage } from '@/pages/HistoryPage'
import { HomePage } from '@/pages/HomePage'

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        path: '/',
        element: <HomePage />,
      },
      {
        path: '/chat',
        element: <ChatPage />,
      },
      {
        path: '/chat/:id',
        element: <ChatPage />,
      },
      {
        path: '/history',
        element: <HistoryPage />,
      },
    ],
  },
])

export function Router() {
  return <RouterProvider router={router} />
}
