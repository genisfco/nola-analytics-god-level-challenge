import { useState } from 'react'
import { getDefaultDateRange } from '@/lib/utils'
import { DateFilter } from '../filters/DateFilter'
import { StoreFilter } from '../filters/StoreFilter'
import { AdvancedFilters, ContextFilters } from '../filters/AdvancedFilters'
import { DeliveryAnalysis } from './DeliveryAnalysis'
import { ChurnRiskTable } from './ChurnRiskTable'
import { ProductsByContext } from './ProductsByContext'

export function AdvancedDashboard() {
  const [dateRange, setDateRange] = useState(getDefaultDateRange())
  const [contextFilters, setContextFilters] = useState<ContextFilters>({})

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
            <AdvancedFilters onApply={handleContextFilters} />
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
          <ChurnRiskTable minPurchases={3} daysInactive={30}/>
        </div>
      </div>
    </div>
  )
}

