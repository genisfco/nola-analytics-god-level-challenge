import { useState } from 'react'
import { getDefaultDateRange } from '@/lib/utils'
import { DateFilter } from '../filters/DateFilter'
import { AdvancedFilters, ContextFilters } from '../filters/AdvancedFilters'
import { DeliveryAnalysis } from './DeliveryAnalysis'
import { ChurnRiskTable } from './ChurnRiskTable'
import { ProductsByContext } from './ProductsByContext'

export function AdvancedDashboard() {
  const [dateRange, setDateRange] = useState(getDefaultDateRange())
  const [contextFilters, setContextFilters] = useState<ContextFilters>({})

  const handleDateChange = (startDate: string, endDate: string) => {
    setDateRange({ startDate, endDate })
  }

  const handleContextFilters = (filters: ContextFilters) => {
    setContextFilters(filters)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                🔍 Analytics Avançado
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Respostas para as perguntas de Maria
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
        {/* Filters Row */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
          <div className="lg:col-span-2">
            <DateFilter
              startDate={dateRange.startDate}
              endDate={dateRange.endDate}
              onChange={handleDateChange}
            />
          </div>
          <div className="lg:col-span-3">
            <AdvancedFilters onApply={handleContextFilters} />
          </div>
        </div>

        {/* Question 1: Produtos por Contexto */}
        <div className="mb-8">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-foreground mb-1">
              1️⃣ Qual produto vende mais em contextos específicos?
            </h2>
            <p className="text-sm text-muted-foreground">
              Ex: "Qual produto vende mais na quinta à noite no iFood?"
            </p>
          </div>
          <ProductsByContext
            startDate={dateRange.startDate}
            endDate={dateRange.endDate}
            contextFilters={contextFilters}
          />
        </div>

        {/* Question 2: Performance de Entrega */}
        <div className="mb-8">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-foreground mb-1">
              2️⃣ Meu tempo de entrega piorou. Em quais regiões?
            </h2>
            <p className="text-sm text-muted-foreground">
              Análise de performance de entrega por região e evolução temporal
            </p>
          </div>
          <DeliveryAnalysis
            startDate={dateRange.startDate}
            endDate={dateRange.endDate}
          />
        </div>

        {/* Question 3: Clientes em Risco */}
        <div className="mb-8">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-foreground mb-1">
              3️⃣ Quais clientes compraram 3+ vezes mas não voltam há 30 dias?
            </h2>
            <p className="text-sm text-muted-foreground">
              Clientes em risco de churn que precisam de atenção
            </p>
          </div>
          <ChurnRiskTable minPurchases={3} daysInactive={30} limit={50} />
        </div>
      </div>
    </div>
  )
}

