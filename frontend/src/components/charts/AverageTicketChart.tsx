import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { formatCurrency, formatDate } from '@/lib/utils'
import { SalesTrend } from '@/lib/api'

interface AverageTicketChartProps {
  data: SalesTrend[]
}

export function AverageTicketChart({ data }: AverageTicketChartProps) {
  const chartData = data.map(item => ({
    date: formatDate(item.date),
    ticket: item.average_ticket,
  }))

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold text-card-foreground mb-4">
        💰 Evolução de Ticket Médio
      </h3>
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
          <defs>
            <linearGradient id="ticketGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b1721" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#8b1721" stopOpacity={0.05}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            hide={true}
          />
          <YAxis 
            hide={true}
          />
          <Tooltip 
            formatter={(value: number) => formatCurrency(value)}
            labelStyle={{ color: '#1c293a' }}
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <Area 
            type="monotone" 
            dataKey="ticket" 
            stroke="#8b1721" 
            strokeWidth={3}
            fill="url(#ticketGradient)"
            fillOpacity={1}
            name="Ticket Médio"
            dot={false}
            activeDot={false}
          />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
