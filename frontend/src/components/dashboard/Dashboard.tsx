import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useApi } from '@/hooks/useApi'
import { useBrand } from '@/contexts/BrandContext'
import { getDefaultDateRange, formatCurrency, formatNumber, formatPercent } from '@/lib/utils'
import { KPICard } from './KPICard'
import { DateFilter } from '../filters/DateFilter'
import { StoreFilter } from '../filters/StoreFilter'
import { SalesTrendChart } from '../charts/SalesTrendChart'
import { ChannelChart } from '../charts/ChannelChart'
import { AverageTicketChart } from '../charts/AverageTicketChart'
import { InsightsPanel } from '../insights'
import { DollarSign, ShoppingCart, Users, TrendingUp, XCircle, CheckCircle } from 'lucide-react'
import type { InsightsResponse } from '@/types/insights'
import type { InsightContext } from '../../App'
import type { OverviewMetrics, ProductRanking, ChannelMetrics, SalesTrend } from '@/lib/api'

// Adicionar interfaces de resposta da API
interface OverviewResponse {
  metrics: OverviewMetrics
  period: {
    days: number
    start_date: string
    end_date: string
  }
}

interface TrendResponse {
  trend: SalesTrend[]
}

interface ChannelsResponse {
  channels: ChannelMetrics[]
}

interface ProductsResponse {
  products: ProductRanking[]
}

interface DashboardProps {
  onNavigateToAdvanced?: (context: InsightContext) => void
}

export function Dashboard({ onNavigateToAdvanced }: DashboardProps) {
  const [dateRange, setDateRange] = useState(getDefaultDateRange())
  const { fetchApi } = useApi()
  const { brandId } = useBrand()

  const { data: overview, isLoading: overviewLoading } = useQuery<OverviewResponse>({
    queryKey: ['overview', dateRange, brandId],
    queryFn: () => fetchApi<OverviewResponse>('/overview', {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      store_ids: dateRange.storeIds,
      channel_ids: dateRange.channelIds,
    }),
    enabled: !!brandId,
  })

  const { data: trend, isLoading: trendLoading } = useQuery<TrendResponse>({
    queryKey: ['trend', dateRange, brandId],
    queryFn: () => fetchApi<TrendResponse>('/sales/trend', {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      store_ids: dateRange.storeIds,
      channel_ids: dateRange.channelIds,
    }),
    enabled: !!brandId,
  })

  const { data: channels, isLoading: channelsLoading } = useQuery<ChannelsResponse>({
    queryKey: ['channels', dateRange, brandId],
    queryFn: () => fetchApi<ChannelsResponse>('/channels', {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      store_ids: dateRange.storeIds,
    }),
    enabled: !!brandId,
  })

  const { data: products } = useQuery<ProductsResponse>({
    queryKey: ['products', dateRange, brandId],
    queryFn: () => fetchApi<ProductsResponse>('/products/top', {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      limit: 5,
      store_ids: dateRange.storeIds,
      channel_ids: dateRange.channelIds,
    }),
    enabled: !!brandId,
  })

  const { data: insights, isLoading: insightsLoading } = useQuery<InsightsResponse>({
    queryKey: ['insights', dateRange, brandId],
    queryFn: () => fetchApi('/insights/automatic', {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      store_ids: dateRange.storeIds,
      limit: 5
    }),
    enabled: !!brandId,
    refetchInterval: 5 * 60 * 1000 // Atualizar a cada 5 minutos
  })

  const handleDateChange = (startDate: string, endDate: string) => {
    setDateRange({ ...dateRange, startDate, endDate })
  }

  const handleStoreFilter = (storeIds: number[]) => {
    setDateRange({ ...dateRange, storeIds })
  }

  const metrics = overview?.metrics

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8">
        {/* Primeira linha: DateFilter à esquerda, 6 cards ao lado */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8 items-stretch">
          {/* DateFilter */}
          <div className="lg:col-span-3 flex">
            <div className="w-full h-full">
              <DateFilter
                startDate={dateRange.startDate}
                endDate={dateRange.endDate}
                onChange={handleDateChange}
              />
            </div>
          </div>

          {/* 6 KPI Cards em grid 3x2 */}
          <div className="lg:col-span-9 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {overviewLoading ? (
              <div className="col-span-full text-center py-8 text-muted-foreground">
                Carregando métricas...
              </div>
            ) : metrics && (
              <>
                <div className="h-full">
                  <KPICard
                    title="Faturamento Total"
                    value={formatCurrency(metrics.total_revenue)}
                    subtitle={`${formatNumber(metrics.completed_sales)} vendas completadas`}
                    icon={DollarSign}
                    variant="primary"
                  />
                </div>
                <div className="h-full">
                  <KPICard
                    title="Ticket Médio"
                    value={formatCurrency(metrics.average_ticket)}
                    subtitle={`${formatNumber(metrics.total_sales)} vendas no total`}
                    icon={ShoppingCart}
                    variant="secondary"
                  />
                </div>
                <div className="h-full">
                  <KPICard
                    title="Clientes Únicos"
                    value={formatNumber(metrics.total_customers)}
                    subtitle="Compraram no período"
                    icon={Users}
                    variant="accent"
                  />
                </div>
                <div className="h-full">
                  <KPICard
                    title="Taxa de Conclusão"
                    value={formatPercent(
                      (metrics.completed_sales / metrics.total_sales) * 100
                    )}
                    subtitle={`${formatNumber(metrics.completed_sales)} de ${formatNumber(metrics.total_sales)}`}
                    icon={CheckCircle}
                    variant="primary"
                  />
                </div>
                <div className="h-full">
                  <KPICard
                    title="Taxa de Cancelamento"
                    value={formatPercent(metrics.cancellation_rate)}
                    subtitle={`${formatNumber(metrics.cancelled_sales)} cancelamentos`}
                    icon={XCircle}
                    variant="secondary"
                  />
                </div>
                <div className="h-full">
                  <KPICard
                    title="Vendas Totais"
                    value={formatNumber(metrics.total_sales)}
                    subtitle={`${overview.period.days} dias`}
                    icon={TrendingUp}
                    variant="accent"
                  />
                </div>
              </>
            )}
          </div>
        </div>

        {/* Segunda linha: StoreFilter, ChannelChart, AverageTicketChart */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8 items-stretch">
          {/* StoreFilter à esquerda */}
          <div className="lg:col-span-3 flex">
            <div className="w-full">
              <StoreFilter
                onApply={handleStoreFilter}
                initialStores={dateRange.storeIds}
              />
            </div>
          </div>

          {/* ChannelChart no meio */}
          <div className="lg:col-span-4 h-full flex">
            {channelsLoading ? (
              <div className="bg-card rounded-lg shadow-sm border border-border p-6 w-full flex items-center justify-center">
                <p className="text-muted-foreground">Carregando gráfico...</p>
              </div>
            ) : channels?.channels && (
              <div className="w-full h-full">
                <ChannelChart data={channels.channels} />
              </div>
            )}
          </div>

          {/* AverageTicketChart à direita */}
          <div className="lg:col-span-5 h-full flex">
            {trendLoading ? (
              <div className="bg-card rounded-lg shadow-sm border border-border p-6 w-full flex items-center justify-center">
                <p className="text-muted-foreground">Carregando gráfico...</p>
              </div>
            ) : trend?.trend && (
              <div className="w-full h-full">
                <AverageTicketChart data={trend.trend} />
              </div>
            )}
          </div>
        </div>

        {/* Terceira linha: SalesTrendChart e Top 5 Produtos lado a lado */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* SalesTrendChart */}
          {trendLoading ? (
            <div className="bg-card rounded-lg shadow-sm border border-border p-6 h-96 flex items-center justify-center">
              <p className="text-muted-foreground">Carregando gráfico...</p>
            </div>
          ) : trend?.trend && (
            <SalesTrendChart data={trend.trend} />
          )}

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

        {/* Última linha: Insights Panel */}
        <InsightsPanel 
          insights={insights?.insights}
          isLoading={insightsLoading}
          lastUpdate={insights?.generated_at ? new Date(insights.generated_at) : undefined}
          currentDateRange={dateRange}
          onNavigateToDetail={onNavigateToAdvanced}
        />
      </div>
    </div>
  )
}

