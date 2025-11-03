import { AlertCircle, TrendingUp, AlertTriangle, CheckCircle, ArrowRight, RefreshCw } from 'lucide-react'
import { Insight, InsightPriority } from '@/types/insights'
import { formatCurrency } from '@/lib/utils'
import type { InsightContext } from '../../App'

interface InsightsPanelProps {
  insights?: Insight[]
  isLoading?: boolean
  lastUpdate?: Date
  currentDateRange?: {
    startDate: string
    endDate: string
    storeIds?: number[]
  }
  onNavigateToDetail?: (context: InsightContext) => void
}

export function InsightsPanel({ 
  insights = [], 
  isLoading = false, 
  lastUpdate,
  currentDateRange,
  onNavigateToDetail
}: InsightsPanelProps) {
  if (isLoading) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-card-foreground flex items-center gap-2">
            🔍 Insights Automáticos
          </h2>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <RefreshCw className="w-4 h-4 animate-spin" />
            Analisando dados...
          </div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse bg-muted/20 rounded-lg h-24" />
          ))}
        </div>
      </div>
    )
  }

  if (!insights || insights.length === 0) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-card-foreground flex items-center gap-2">
            🔍 Insights Automáticos
          </h2>
          {lastUpdate && (
            <span className="text-sm text-muted-foreground">
              Atualizado há {getTimeAgo(lastUpdate)}
            </span>
          )}
        </div>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mb-3" />
          <p className="text-lg font-medium text-card-foreground">Tudo OK! 🎉</p>
          <p className="text-sm text-muted-foreground mt-1">
            Nenhum alerta crítico detectado no momento
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-card-foreground flex items-center gap-2">
          🔍 Insights Automáticos
        </h2>
        {lastUpdate && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <RefreshCw className="w-4 h-4" />
            Atualizado há {getTimeAgo(lastUpdate)}
          </div>
        )}
      </div>

      <div className="space-y-4">
        {insights.map((insight) => (
          <InsightCard 
            key={insight.id} 
            insight={insight}
            currentDateRange={currentDateRange}
            onNavigateToDetail={onNavigateToDetail}
          />
        ))}
      </div>
    </div>
  )
}

interface InsightCardProps {
  insight: Insight
  currentDateRange?: {
    startDate: string
    endDate: string
    storeIds?: number[]
  }
  onNavigateToDetail?: (context: InsightContext) => void
}

function InsightCard({ insight, currentDateRange, onNavigateToDetail }: InsightCardProps) {
  const { icon: Icon, color, bgColor, borderColor } = getPriorityStyle(insight.priority)
  
  // Função para converter contexto do insight em filtros
  const handleNavigateToDetail = () => {
    if (!onNavigateToDetail || !currentDateRange) return

    // Mapear dia da semana de português para número (DOW do PostgreSQL: 0=domingo, 6=sábado)
    const weekdayMap: Record<string, number> = {
      'domingo': 0,
      'segunda-feira': 1,
      'terça-feira': 2,
      'quarta-feira': 3,
      'quinta-feira': 4,
      'sexta-feira': 5,
      'sábado': 6
    }

    // Pegar primeiro dia da semana se houver
    const weekday = insight.context.affected_days?.[0]
      ? weekdayMap[insight.context.affected_days[0].toLowerCase()]
      : undefined

    // Pegar primeira hora e criar range de 1 hora
    const hour = insight.context.affected_hours?.[0]
    const hourStart = hour !== undefined ? hour : undefined
    const hourEnd = hour !== undefined ? hour + 1 : undefined

    // Para insights de comparação de lojas, não filtrar por loja específica
    // Assim o usuário pode comparar o desempenho entre todas as lojas
    // Identificamos insights de comparação de lojas quando há only affected_stores
    // sem affected_days, affected_hours ou affected_channels
    const isStoreComparisonInsight = 
      Boolean(insight.context.affected_stores && insight.context.affected_stores.length > 0) &&
      !Boolean(insight.context.affected_days && insight.context.affected_days.length > 0) &&
      !Boolean(insight.context.affected_hours && insight.context.affected_hours.length > 0) &&
      !Boolean(insight.context.affected_channels && insight.context.affected_channels.length > 0)
    const shouldIncludeStoreFilter = !isStoreComparisonInsight

    const context: InsightContext = {
      dateRange: {
        startDate: currentDateRange.startDate,
        endDate: currentDateRange.endDate
      },
      storeIds: shouldIncludeStoreFilter && insight.context.affected_stores && insight.context.affected_stores.length > 0
        ? insight.context.affected_stores
        : undefined,
      contextFilters: {
        weekday,
        hourStart,
        hourEnd,
        channelId: insight.context.affected_channels?.[0]
      }
    }

    onNavigateToDetail(context)
  }
  
  return (
    <div 
      className={`rounded-lg border-l-4 ${borderColor} ${bgColor} p-4 transition-all hover:shadow-md`}
    >
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${color} bg-opacity-10 flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${color}`} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-base font-semibold text-card-foreground mb-1">
            {insight.title}
          </h3>

          {/* Description */}
          <p className="text-sm text-muted-foreground mb-3">
            {insight.description}
          </p>

          {/* Impact */}
          <div className="flex items-center gap-4 mb-3 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Impacto:</span>
              <span className={`text-sm font-bold ${color}`}>
                {formatCurrency(insight.impact.value)}/{insight.impact.period === 'monthly' ? 'mês' : 'ano'}
              </span>
            </div>

            {insight.recommendation.estimated_roi && (
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground">ROI Estimado:</span>
                <span className="text-sm font-bold text-green-600">
                  {formatCurrency(insight.recommendation.estimated_roi)}
                </span>
              </div>
            )}
          </div>

          {/* Recommendation */}
          <div className="bg-card/50 rounded-lg p-3 mb-3">
            <div className="flex items-start gap-2">
              <span className="text-xs font-bold text-primary mt-0.5">💡</span>
              <div className="flex-1">
                <p className="text-xs font-medium text-muted-foreground mb-1">Ação Recomendada:</p>
                <p className="text-sm text-card-foreground">
                  {insight.recommendation.action}
                </p>
              </div>
            </div>
          </div>

          {/* Context Tags */}
          {(insight.context.affected_days || insight.context.affected_hours) && (
            <div className="flex items-center gap-2 flex-wrap mb-3">
              {insight.context.affected_days && insight.context.affected_days.length > 0 && (
                <span className="text-xs bg-muted px-2 py-1 rounded">
                  📅 {insight.context.affected_days.join(', ')}
                </span>
              )}
              {insight.context.affected_hours && insight.context.affected_hours.length > 0 && (
                <span className="text-xs bg-muted px-2 py-1 rounded">
                  🕐 {insight.context.affected_hours.map(h => `${h}h`).join(', ')}
                </span>
              )}
              {insight.context.data_points && insight.context.data_points > 0 && (
                <span className="text-xs bg-muted px-2 py-1 rounded">
                  📊 {insight.context.data_points} pedidos
                </span>
              )}
            </div>
          )}

          {/* Action Link */}
          {onNavigateToDetail && (
            (Boolean(insight.context.affected_stores?.length) ||
            Boolean(insight.context.affected_channels?.length) ||
            Boolean(insight.context.affected_days?.length) ||
            Boolean(insight.context.affected_hours?.length)) && (
              <button
                onClick={handleNavigateToDetail}
                className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline cursor-pointer transition-colors"
              >
                Ver Análise Detalhada
                <ArrowRight className="w-4 h-4" />
              </button>
            )
          )}
        </div>
      </div>
    </div>
  )
}

function getPriorityStyle(priority: InsightPriority) {
  switch (priority) {
    case 'critical':
      return {
        icon: AlertCircle,
        color: 'text-red-600',
        bgColor: 'bg-red-50 dark:bg-red-950/20',
        borderColor: 'border-red-500'
      }
    case 'attention':
      return {
        icon: AlertTriangle,
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
        borderColor: 'border-yellow-500'
      }
    case 'positive':
      return {
        icon: TrendingUp,
        color: 'text-green-600',
        bgColor: 'bg-green-50 dark:bg-green-950/20',
        borderColor: 'border-green-500'
      }
    default:
      return {
        icon: AlertTriangle,
        color: 'text-gray-600',
        bgColor: 'bg-gray-50 dark:bg-gray-950/20',
        borderColor: 'border-gray-500'
      }
  }
}

function getTimeAgo(date: Date): string {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)
  
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}min`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`
  return `${Math.floor(seconds / 86400)}d`
}

