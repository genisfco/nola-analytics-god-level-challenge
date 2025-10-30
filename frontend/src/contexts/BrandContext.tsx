import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface Brand {
  id: number
  name: string
}

interface BrandContextType {
  brandId: number | null
  brandName: string | null
  brands: Brand[]
  setBrand: (id: number, name: string) => void
  loading: boolean
}

const BrandContext = createContext<BrandContextType | undefined>(undefined)

export function BrandProvider({ children }: { children: ReactNode }) {
  const [brandId, setBrandId] = useState<number | null>(() => {
    const saved = localStorage.getItem('selectedBrandId')
    return saved ? parseInt(saved) : null
  })
  
  const [brandName, setBrandName] = useState<string | null>(() => {
    return localStorage.getItem('selectedBrandName')
  })

  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(true)

  // Fetch brands on mount
  useEffect(() => {
    const fetchBrands = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/analytics/brands/list')
        const data = await response.json()
        setBrands(data.brands)
        
        // If no brand selected, select the first one
        if (!brandId && data.brands.length > 0) {
          const firstBrand = data.brands[0]
          setBrand(firstBrand.id, firstBrand.name)
        }
      } catch (error) {
        console.error('Error fetching brands:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchBrands()
  }, [])

  const setBrand = (id: number, name: string) => {
    setBrandId(id)
    setBrandName(name)
    localStorage.setItem('selectedBrandId', id.toString())
    localStorage.setItem('selectedBrandName', name)
  }

  return (
    <BrandContext.Provider value={{ brandId, brandName, brands, setBrand, loading }}>
      {children}
    </BrandContext.Provider>
  )
}

export const useBrand = () => {
  const context = useContext(BrandContext)
  if (!context) {
    throw new Error('useBrand must be used within BrandProvider')
  }
  return context
}

