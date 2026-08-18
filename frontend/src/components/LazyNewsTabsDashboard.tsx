import { Suspense, lazy } from 'react'

const NewsTabsDashboard = lazy(() => import('./NewsTabsDashboard'))

export default function LazyNewsTabsDashboard() {
  return (
    <Suspense fallback={<div className="text-center py-8 text-gold-300">Loading market news...</div>}>
      <NewsTabsDashboard />
    </Suspense>
  )
}
