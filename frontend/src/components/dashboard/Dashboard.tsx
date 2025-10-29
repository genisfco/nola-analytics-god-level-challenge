import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AnalyticsAPI } from '@/lib/api'
import { getDefaultDateRange, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'
import { KPICard } from './KPICard'
import { DateFilter } from '../filters/DateFilter'
import { SalesTrendChart } from '../charts/SalesTrendChart'
import { ChannelChart } from '../charts/ChannelChart'
import { DollarSign, ShoppingCart, Users, TrendingUp, XCircle, CheckCircle } from 'lucide-react'

export function Dashboard() {
  const [dateRange, setDateRange] = useState(getDefaultDateRange())

  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['overview', dateRange],
    queryFn: () => AnalyticsAPI.getOverview(dateRange),
  })

  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: ['trend', dateRange],
    queryFn: () => AnalyticsAPI.getSalesTrend(dateRange),
  })

  const { data: channels, isLoading: channelsLoading } = useQuery({
    queryKey: ['channels', dateRange],
    queryFn: () => AnalyticsAPI.getChannelMetrics(dateRange),
  })

  const { data: products } = useQuery({
    queryKey: ['products', dateRange],
    queryFn: () => AnalyticsAPI.getTopProducts({ ...dateRange, limit: 5 }),
  })

  const handleDateChange = (startDate: string, endDate: string) => {
    setDateRange({ startDate, endDate })
  }

  const metrics = overview?.metrics

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                🍔 Analytics Dashboard
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Nola God Level Challenge • 2025
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground">
                {dateRange.startDate} até {dateRange.endDate}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          {/* Filtros */}
          <div className="lg:col-span-1">
            <DateFilter
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              onChange={handleDateChange}
            />
          </div>

          {/* KPIs */}
          <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {overviewLoading ? (
              <div className="col-span-full text-center py-8 text-muted-foreground">
                Carregando métricas...
              </div>
            ) : metrics && (
              <>
                <KPICard
                  title="Faturamento Total"
                  value={formatCurrency(metrics.total_revenue)}
                  subtitle={`${formatNumber(metrics.completed_sales)} vendas completadas`}
                  icon={DollarSign}
                  variant="primary"
                />
                <KPICard
                  title="Ticket Médio"
                  value={formatCurrency(metrics.average_ticket)}
                  subtitle={`${formatNumber(metrics.total_sales)} vendas no total`}
                  icon={ShoppingCart}
                  variant="secondary"
                />
                <KPICard
                  title="Clientes Únicos"
                  value={formatNumber(metrics.total_customers)}
                  subtitle="Compraram no período"
                  icon={Users}
                  variant="accent"
                />
                <KPICard
                  title="Taxa de Conclusão"
                  value={formatPercent(
                    (metrics.completed_sales / metrics.total_sales) * 100
                  )}
                  subtitle={`${formatNumber(metrics.completed_sales)} de ${formatNumber(metrics.total_sales)}`}
                  icon={CheckCircle}
                  variant="primary"
                />
                <KPICard
                  title="Taxa de Cancelamento"
                  value={formatPercent(metrics.cancellation_rate)}
                  subtitle={`${formatNumber(metrics.cancelled_sales)} cancelamentos`}
                  icon={XCircle}
                  variant="secondary"
                />
                <KPICard
                  title="Vendas Totais"
                  value={formatNumber(metrics.total_sales)}
                  subtitle={`${overview.period.days} dias`}
                  icon={TrendingUp}
                  variant="accent"
                />
              </>
            )}
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {trendLoading ? (
            <div className="bg-card rounded-lg shadow-sm border border-border p-6 h-96 flex items-center justify-center">
              <p className="text-muted-foreground">Carregando gráfico...</p>
            </div>
          ) : trend?.trend && (
            <SalesTrendChart data={trend.trend} />
          )}

          {channelsLoading ? (
            <div className="bg-card rounded-lg shadow-sm border border-border p-6 h-96 flex items-center justify-center">
              <p className="text-muted-foreground">Carregando gráfico...</p>
            </div>
          ) : channels?.channels && (
            <ChannelChart data={channels.channels} />
          )}
        </div>

        {/* Top Products Table */}
        {products?.products && products.products.length > 0 && (
          <div className="bg-card rounded-lg shadow-sm border border-border p-6">
            <h3 className="text-lg font-semibold text-card-foreground mb-4">
              🏆 Top 5 Produtos Mais Vendidos
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                      #
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                      Produto
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                      Categoria
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                      Vendas
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                      Faturamento
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {products.products.map((product, index) => (
                    <tr 
                      key={product.product_id}
                      className="border-b border-border last:border-0 hover:bg-primary/5 transition-colors"
                    >
                      <td className="py-3 px-4 text-sm font-bold text-primary">
                        {index + 1}
                      </td>
                      <td className="py-3 px-4 text-sm font-medium text-card-foreground">
                        {product.product_name}
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {product.category || '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-right text-card-foreground">
                        {formatNumber(product.times_sold)}
                      </td>
                      <td className="py-3 px-4 text-sm text-right font-semibold text-primary">
                        {formatCurrency(product.total_revenue)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

