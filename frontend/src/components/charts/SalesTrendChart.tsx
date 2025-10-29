import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { formatCurrency, formatDate } from '@/lib/utils'
import { SalesTrend } from '@/lib/api'

interface SalesTrendChartProps {
  data: SalesTrend[]
}

export function SalesTrendChart({ data }: SalesTrendChartProps) {
  const chartData = data.map(item => ({
    date: formatDate(item.date),
    revenue: item.total_revenue,
    sales: item.total_sales,
    ticket: item.average_ticket,
  }))

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6">
      <h3 className="text-lg font-semibold text-card-foreground mb-4">
        📈 Evolução de Vendas
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <YAxis 
            yAxisId="left"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            tickFormatter={(value) => `R$ ${(value / 1000).toFixed(0)}k`}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <Tooltip 
            formatter={(value: number, name: string) => {
              if (name === 'revenue' || name === 'ticket') {
                return formatCurrency(value)
              }
              return value
            }}
            labelStyle={{ color: '#1c293a' }}
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="revenue" 
            stroke="#fd6263" 
            strokeWidth={3}
            name="Faturamento"
            dot={{ fill: '#fd6263', r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="sales" 
            stroke="#8b1721" 
            strokeWidth={2}
            name="Vendas"
            dot={{ fill: '#8b1721', r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

