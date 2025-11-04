import { useBrand } from '../contexts/BrandContext'
import { useCallback } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/v1/analytics`
  : '/api/v1/analytics'

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
  const buildUrl = useCallback((endpoint: string, params?: Record<string, any>): string => {
    const searchParams = new URLSearchParams()
    
    // Adiciona brand_id automaticamente se existir
    if (brandId) {
      searchParams.append('brand_id', brandId.toString())
    }
    
    // Adiciona outros parâmetros
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          // Se for array, converte para string separada por vírgula
          if (Array.isArray(value)) {
            if (value.length > 0) {
              searchParams.append(key, value.join(','))
            }
          } else {
            searchParams.append(key, String(value))
          }
        }
      })
    }
    
    const queryString = searchParams.toString()
    return `${API_BASE_URL}${endpoint}${queryString ? '?' + queryString : ''}`
  }, [brandId])

  /**
   * Faz uma requisição GET à API
   */
  const fetchApi = useCallback(async <T>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<T> => {
    const url = buildUrl(endpoint, params)
    
    try {
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }
      
      return response.json()
    } catch (error) {
      // Re-throw para que o componente possa tratar
      throw error
    }
  }, [buildUrl])

  return {
    buildUrl,
    fetchApi,
  }
}

