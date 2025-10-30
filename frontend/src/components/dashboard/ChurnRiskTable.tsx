import { useQuery } from '@tanstack/react-query'
import { UserX, Mail, Phone, Calendar, Heart } from 'lucide-react'
import { useApi } from '@/hooks/useApi'
import { useBrand } from '@/contexts/BrandContext'
import { ChurnRiskCustomer } from '@/lib/api'
import { formatCurrency, formatNumber } from '@/lib/utils'

interface ChurnRiskResponse {
  customers: ChurnRiskCustomer[]
  total_at_risk: number
  criteria: {
    min_purchases: number
    days_inactive: number
  }
  period: {
    analysis_date: string
  }
}

interface ChurnRiskTableProps {
  minPurchases?: number
  daysInactive?: number
  limit?: number
  storeIds?: number[]
}

export function ChurnRiskTable({ 
  minPurchases = 3, 
  daysInactive = 30, 
  limit = 10,
  storeIds
}: ChurnRiskTableProps) {
  const { fetchApi } = useApi()
  const { brandId } = useBrand()

  const { data, isLoading } = useQuery<ChurnRiskResponse>({
    queryKey: ['churn-risk', minPurchases, daysInactive, limit, storeIds, brandId],
    queryFn: () => fetchApi<ChurnRiskResponse>('/customers/churn-risk', {
      min_purchases: minPurchases,
      days_inactive: daysInactive,
      limit,
      store_ids: storeIds && storeIds.length > 0 ? storeIds : undefined,
    }),
    enabled: !!brandId,
  })

  if (isLoading) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <p className="text-muted-foreground text-center">Carregando clientes em risco...</p>
      </div>
    )
  }

  if (!data || !data.customers || data.customers.length === 0) {
    return (
      <div className="bg-card rounded-lg shadow-sm border border-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <Heart className="w-5 h-5 text-green-600" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Clientes em Risco
          </h3>
        </div>
        <div className="text-center py-8">
          <Heart className="w-12 h-12 text-green-600 mx-auto mb-2" />
          <p className="text-muted-foreground">
            Nenhum cliente em risco! Todos estão ativos. 🎉
          </p>
        </div>
      </div>
    )
  }

  const customers: ChurnRiskCustomer[] = data.customers

  const storeFilterLabel = storeIds && storeIds.length > 0 
    ? `${storeIds.length} loja${storeIds.length > 1 ? 's' : ''}`
    : null

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <UserX className="w-5 h-5 text-red-600" />
          <h3 className="text-lg font-semibold text-card-foreground">
            Clientes em Risco
          </h3>
          {storeFilterLabel && (
            <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-md font-medium">
              {storeFilterLabel}
            </span>
          )}
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-red-600">{customers.length}</p>
          <p className="text-xs text-muted-foreground">
            {minPurchases}+ compras • {daysInactive}+ dias inativos
          </p>
        </div>
      </div>

      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>💡 Dica:</strong> Esses clientes já demonstraram interesse comprando {minPurchases}+ vezes,
          mas não voltam há {daysInactive}+ dias. Considere enviar cupons ou ofertas personalizadas!
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                Cliente
              </th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-muted-foreground">
                Compras
              </th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-muted-foreground">
                Total Gasto
              </th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-muted-foreground">
                Dias Inativo
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                Canal Favorito
              </th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-muted-foreground">
                Produto Favorito
              </th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => {
              const urgency =
                customer.days_since_last_purchase > 60
                  ? 'critical'
                  : customer.days_since_last_purchase > 45
                  ? 'high'
                  : 'medium'

              return (
                <tr
                  key={customer.customer_id}
                  className="border-b border-border last:border-0 hover:bg-primary/5 transition-colors"
                >
                  <td className="py-3 px-4">
                    <div>
                      <p className="text-sm font-medium text-card-foreground">
                        {customer.customer_name}
                      </p>
                      <div className="flex gap-2 mt-1">
                        {customer.email && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Mail className="w-3 h-3" />
                            {customer.email.length > 20
                              ? customer.email.substring(0, 20) + '...'
                              : customer.email}
                          </span>
                        )}
                        {customer.phone_number && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Phone className="w-3 h-3" />
                            {customer.phone_number}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-sm font-semibold rounded-md">
                      {formatNumber(customer.total_purchases)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <p className="text-sm font-semibold text-card-foreground">
                      {formatCurrency(customer.total_spent)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      ~{formatCurrency(customer.total_spent / customer.total_purchases)}/compra
                    </p>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <div className="flex flex-col items-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-sm font-semibold rounded-md ${
                          urgency === 'critical'
                            ? 'bg-red-100 text-red-700'
                            : urgency === 'high'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        <Calendar className="w-3 h-3" />
                        {customer.days_since_last_purchase}d
                      </span>
                      <span className="text-xs text-muted-foreground mt-1">
                        Última: {new Date(customer.last_purchase_date).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-sm text-card-foreground">
                      {customer.favorite_channel}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-sm text-card-foreground">
                      {customer.favorite_product || '-'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {data.total_at_risk > limit && (
        <div className="mt-4 text-center">
          <p className="text-sm text-muted-foreground">
            Mostrando {limit} de {data.total_at_risk} clientes em risco
          </p>
        </div>
      )}
    </div>
  )
}

