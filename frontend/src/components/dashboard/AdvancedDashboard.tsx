import { useState, useEffect, useMemo } from 'react'
import { getDefaultDateRange } from '@/lib/utils'
import { DateFilter } from '../filters/DateFilter'
import { StoreFilter } from '../filters/StoreFilter'
import { AdvancedFilters, ContextFilters } from '../filters/AdvancedFilters'
import { DeliveryAnalysis } from './DeliveryAnalysis'
import { ChurnRiskTable } from './ChurnRiskTable'
import { ProductsByContext } from './ProductsByContext'
import type { InsightContext } from '../../App'

interface AdvancedDashboardProps {
  insightContext?: InsightContext | null
}

export function AdvancedDashboard({ insightContext }: AdvancedDashboardProps) {
  const [dateRange, setDateRange] = useState(getDefaultDateRange())
  const [contextFilters, setContextFilters] = useState<ContextFilters>({})
  
  // Verificar se os filtros atuais são diferentes dos filtros do insight original
  const showInsightBadge = useMemo(() => {
    if (!insightContext) return false
    
    // Comparar datas
    const datesMatch = 
      insightContext.dateRange?.startDate === dateRange.startDate &&
      insightContext.dateRange?.endDate === dateRange.endDate
    
    // Comparar lojas (ordenar e comparar arrays)
    const insightStores = (insightContext.storeIds || []).sort().join(',')
    const currentStores = (dateRange.storeIds || []).sort().join(',')
    const storesMatch = insightStores === currentStores
    
    // Comparar filtros contextuais
    const insightFilters = JSON.stringify({
      weekday: insightContext.contextFilters?.weekday,
      hourStart: insightContext.contextFilters?.hourStart,
      hourEnd: insightContext.contextFilters?.hourEnd,
      channelId: insightContext.contextFilters?.channelId
    })
    const currentFilters = JSON.stringify({
      weekday: contextFilters.weekday,
      hourStart: contextFilters.hourStart,
      hourEnd: contextFilters.hourEnd,
      channelId: contextFilters.channelId
    })
    const filtersMatch = insightFilters === currentFilters
    
    // Badge só aparece se tudo ainda estiver igual ao insight original
    return datesMatch && storesMatch && filtersMatch
  }, [insightContext, dateRange, contextFilters])

  // Aplicar contexto do insight automaticamente
  useEffect(() => {
    if (insightContext) {
      if (insightContext.dateRange) {
        setDateRange(prev => ({
          ...prev,
          startDate: insightContext.dateRange!.startDate,
          endDate: insightContext.dateRange!.endDate
        }))
      }
      if (insightContext.storeIds && insightContext.storeIds.length > 0) {
        setDateRange(prev => ({
          ...prev,
          storeIds: insightContext.storeIds
        }))
      }
      if (insightContext.contextFilters) {
        setContextFilters(insightContext.contextFilters)
      }
    }
  }, [insightContext])

  const handleDateChange = (startDate: string, endDate: string) => {
    setDateRange({ ...dateRange, startDate, endDate })
  }

  const handleStoreFilter = (storeIds: number[]) => {
    setDateRange({ ...dateRange, storeIds })
  }

  const handleContextFilters = (filters: ContextFilters) => {
    setContextFilters(filters)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8">
        {/* Badge se veio de insight e filtros ainda são os mesmos */}
        {showInsightBadge && (
          <div className="mb-6 p-4 bg-primary/10 border border-primary/20 rounded-lg">
            <p className="text-sm text-primary font-medium">
              🔍 Visualizando dados do insight detectado
            </p>
          </div>
        )}

        {/* Filters Row */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
          <div className="lg:col-span-2 space-y-4">
            <DateFilter
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              onChange={handleDateChange}
            />
            <StoreFilter
              onApply={handleStoreFilter}
              initialStores={dateRange.storeIds}
            />
          </div>
          <div className="lg:col-span-3">
            <AdvancedFilters 
              onApply={handleContextFilters}
              initialFilters={contextFilters}
            />
          </div>
        </div>

        {/* Análise de Produtos mais vendidos */}
        <div className="mb-8">          
          <ProductsByContext
            startDate={dateRange.startDate}
            endDate={dateRange.endDate}
            contextFilters={contextFilters}
            storeIds={dateRange.storeIds}
          />
        </div>

        {/* Análise de Performance de Entrega */}
        <div className="mb-8">
          
          <DeliveryAnalysis
            startDate={dateRange.startDate}
            endDate={dateRange.endDate}
            contextFilters={contextFilters}
            storeIds={dateRange.storeIds}
          />
        </div>

        {/* Análise de Clientes em Risco */}
        <div className="mb-8">          
          <ChurnRiskTable 
            minPurchases={3} 
            daysInactive={30}
            storeIds={dateRange.storeIds}
          />
        </div>
      </div>
    </div>
  )
}

