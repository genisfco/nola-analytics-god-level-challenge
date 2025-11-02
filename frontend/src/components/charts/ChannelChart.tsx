import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { ChannelMetrics } from '@/lib/api'
import { formatCurrency, formatPercent } from '@/lib/utils'

interface ChannelChartProps {
  data: ChannelMetrics[]
}

const COLORS = ['#fd6263', '#8b1721', '#3b82f6', '#f59e0b', '#10b981', '#6366f1']

export function ChannelChart({ data }: ChannelChartProps) {
  const chartData = data.map(item => ({
    name: item.channel_name,
    value: item.total_revenue,
    share: item.revenue_share,
  }))

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold text-card-foreground mb-4">
        🛵 Distribuição por Canal
      </h3>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ share }) => formatPercent(share)}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

