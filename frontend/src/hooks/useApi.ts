import { useBrand } from '../contexts/BrandContext'

const API_BASE_URL = 'http://localhost:8000/api/v1/analytics'

interface UseApiReturn {
  buildUrl: (endpoint: string, params?: Record<string, any>) => string
  fetchApi: <T>(endpoint: string, params?: Record<string, any>) => Promise<T>
}

/**
 * Hook para facilitar chamadas à API incluindo automaticamente o brand_id
 * 
 * @example
 * const { fetchApi } = useApi()
 * const data = await fetchApi('/overview', { start_date: '2024-01-01', end_date: '2024-01-31' })
 */
export function useApi(): UseApiReturn {
  const { brandId } = useBrand()

  /**
   * Constrói a URL com os parâmetros, incluindo automaticamente o brand_id
   */
  const buildUrl = (endpoint: string, params?: Record<string, any>): string => {
    const url = new URL(`${API_BASE_URL}${endpoint}`)
    
    // Adiciona brand_id automaticamente se existir
    if (brandId) {
      url.searchParams.append('brand_id', brandId.toString())
    }
    
    // Adiciona outros parâmetros
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          // Se for array, converte para string separada por vírgula
          if (Array.isArray(value)) {
            if (value.length > 0) {
              url.searchParams.append(key, value.join(','))
            }
          } else {
            url.searchParams.append(key, String(value))
          }
        }
      })
    }
    
    return url.toString()
  }

  /**
   * Faz uma requisição GET à API
   */
  const fetchApi = async <T>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<T> => {
    const url = buildUrl(endpoint, params)
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }

  return {
    buildUrl,
    fetchApi,
  }
}

