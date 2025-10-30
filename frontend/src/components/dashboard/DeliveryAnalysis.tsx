import { useQuery } from '@tanstack/react-query'
import { Truck, Clock, MapPin, TrendingDown, TrendingUp } from 'lucide-react'
import { useApi } from '@/hooks/useApi'
import { useBrand } from '@/contexts/BrandContext'
import { DeliveryPerformance, DeliveryByRegion } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { ContextFilters } from '../filters/AdvancedFilters'

interface DeliveryPerformanceResponse {
  overall: DeliveryPerformance
  by_region?: DeliveryByRegion[]
}

interface DeliveryAnalysisProps {
  startDate: string
  endDate: string
  contextFilters?: ContextFilters
  storeIds?: number[]
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${minutes}m ${secs}s`
}

export function DeliveryAnalysis({ startDate, endDate, contextFilters, storeIds }: DeliveryAnalysisProps) {
  const { fetchApi } = useApi()
  const { brandId } = useBrand()

  const { data, isLoading } = useQuery<DeliveryPerformanceResponse>({
    queryKey: ['delivery-performance', startDate, endDate, contextFilters, storeIds, brandId],
    queryFn: () => fetchApi<DeliveryPerformanceResponse>('/delivery/performance', {
      start_date: startDate,
      end_date: endDate,
      weekday: contextFilters?.weekday,
      hour_start: contextFilters?.hourStart,
      hour_end: contextFilters?.hourEnd,
      channel_id: contextFilters?.channelId,
      store_ids: storeIds && storeIds.length > 0 ? storeIds : undefined,
    }),
    enabled: !!brandId,
  })

  if (isLoading) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <p className="text-muted-foreground text-center">Carregando análise de entrega...</p>
      </div>
    )
  }

  if (!data) return null

  const overall: DeliveryPerformance = data.overall
  const regions: DeliveryByRegion[] = data.by_region || []

  // Build filter labels
  const weekdayNames = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
  const channelNames: Record<number, string> = {
    1: 'Presencial',
    2: 'iFood',
    3: 'Rappi',
    4: 'Uber Eats',
    5: 'WhatsApp',
    6: 'App Próprio',
  }

  const contextLabel = []
  if (contextFilters?.weekday !== undefined) {
    contextLabel.push(weekdayNames[contextFilters.weekday])
  }
  if (contextFilters?.hourStart !== undefined && contextFilters?.hourEnd !== undefined) {
    contextLabel.push(`${contextFilters.hourStart}h-${contextFilters.hourEnd}h`)
  }
  if (contextFilters?.channelId !== undefined) {
    contextLabel.push(channelNames[contextFilters.channelId])
  }

  const storeFilterLabel = storeIds && storeIds.length > 0 
    ? `${storeIds.length} loja${storeIds.length > 1 ? 's' : ''}`
    : null

  return (
    <div className="space-y-6">
      {/* Overall Metrics */}
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-card-foreground">
              Performance de Entrega
              {contextLabel.length > 0 && <span className="text-muted-foreground font-normal"> - {contextLabel.join(' • ')}</span>}
            </h3>
          </div>
          {storeFilterLabel && (
            <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-md font-medium">
              {storeFilterLabel}
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-primary/5 border-l-4 border-primary rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-primary" />
              <p className="text-sm font-medium text-muted-foreground">Tempo Médio de Entrega</p>
            </div>
            <p className="text-2xl font-bold text-card-foreground">
              {formatTime(overall.avg_delivery_time)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {formatNumber(overall.total_deliveries)} entregas
            </p>
          </div>

          <div className="p-4 bg-secondary/5 border-l-4 border-secondary rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-secondary" />
              <p className="text-sm font-medium text-muted-foreground">Tempo de Produção</p>
            </div>
            <p className="text-2xl font-bold text-card-foreground">
              {formatTime(overall.avg_production_time)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Tempo médio</p>
          </div>

          <div className="p-4 bg-chart-3/5 border-l-4 border-chart-3 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-chart-3" />
              <p className="text-sm font-medium text-muted-foreground">Taxa de Pontualidade</p>
            </div>
            <p className="text-2xl font-bold text-card-foreground">
              {overall.on_time_rate.toFixed(1)}%
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {formatNumber(overall.on_time_deliveries)} no prazo
            </p>
          </div>

          <div className="p-4 bg-chart-4/5 border-l-4 border-chart-4 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Truck className="w-4 h-4 text-chart-4" />
              <p className="text-sm font-medium text-muted-foreground">Tempo Total</p>
            </div>
            <p className="text-2xl font-bold text-card-foreground">
              {formatTime(overall.avg_delivery_time + overall.avg_production_time)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Produção + Entrega</p>
          </div>
        </div>
      </div>

      {/* Regions Table */}
      {regions.length > 0 && (
        <div className="bg-card rounded-lg shadow-sm border border-border p-6">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-card-foreground">
              Performance por Região
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                    Cidade
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                    Estado
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                    Entregas
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                    Tempo Médio
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                    Pontualidade
                  </th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-muted-foreground">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {regions.slice(0, 10).map((region, index) => {
                  const isGood = region.on_time_rate >= 80
                  const isWarning = region.on_time_rate >= 60 && region.on_time_rate < 80
                  const isBad = region.on_time_rate < 60

                  return (
                    <tr
                      key={`${region.city}-${region.state}-${index}`}
                      className="border-b border-border last:border-0 hover:bg-primary/5 transition-colors"
                    >
                      <td className="py-3 px-4 text-sm font-medium text-card-foreground">
                        {region.city}
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {region.state}
                      </td>
                      <td className="py-3 px-4 text-sm text-right text-card-foreground">
                        {formatNumber(region.total_deliveries)}
                      </td>
                      <td className="py-3 px-4 text-sm text-right text-card-foreground">
                        {formatTime(region.avg_delivery_time)}
                      </td>
                      <td className="py-3 px-4 text-sm text-right font-semibold">
                        <span
                          className={
                            isGood
                              ? 'text-green-600'
                              : isWarning
                              ? 'text-yellow-600'
                              : 'text-red-600'
                          }
                        >
                          {region.on_time_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        {isGood && (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                            <TrendingUp className="w-3 h-3" />
                            Bom
                          </span>
                        )}
                        {isWarning && (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                            Atenção
                          </span>
                        )}
                        {isBad && (
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                            <TrendingDown className="w-3 h-3" />
                            Crítico
                          </span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {regions.length > 10 && (
            <div className="mt-4 text-center">
              <p className="text-sm text-muted-foreground">
                Mostrando 10 de {regions.length} regiões
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

