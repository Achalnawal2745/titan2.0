import { useState, useEffect } from 'react'
import { Line, Bar } from 'recharts'

interface AnalyticsMetrics {
  totalEvents: number
  uniqueUsers: number
  avgSessionDuration: number
  bounceRate: number
  topPages: Array<{ path: string; views: number }>
  topEvents: Array<{ name: string; count: number }>
  userGrowth: Array<{ date: string; users: number }>
}

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d') // 7d, 30d, 90d

  useEffect(() => {
    fetchMetrics(timeRange)
  }, [timeRange])

  const fetchMetrics = async (range: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/analytics?range=${range}`)
      const data = await response.json()
      setMetrics(data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    )
  }

  return (
    <div className="analytics-dashboard p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Events"
          value={metrics?.totalEvents || 0}
          icon="📊"
        />
        <MetricCard
          title="Unique Users"
          value={metrics?.uniqueUsers || 0}
          icon="👥"
        />
        <MetricCard
          title="Avg Session"
          value={`${Math.round((metrics?.avgSessionDuration || 0) / 60)}m`}
          icon="⏱️"
        />
        <MetricCard
          title="Bounce Rate"
          value={`${metrics?.bounceRate || 0}%`}
          icon="↩️"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Growth Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">User Growth</h3>
          {/* Add Line chart here with metrics.userGrowth data */}
        </div>

        {/* Top Events Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Events</h3>
          {/* Add Bar chart here with metrics.topEvents data */}
        </div>
      </div>

      {/* Top Pages Table */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Top Pages</h3>
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Page</th>
              <th className="text-right py-2">Views</th>
            </tr>
          </thead>
          <tbody>
            {metrics?.topPages.map((page, i) => (
              <tr key={i} className="border-b">
                <td className="py-2">{page.path}</td>
                <td className="text-right py-2">{page.views.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function MetricCard({ title, value, icon }: { title: string; value: string | number; icon: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  )
}
