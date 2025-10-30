import { useState } from 'react'
import { Dashboard } from './components/dashboard/Dashboard'
import { AdvancedDashboard } from './components/dashboard/AdvancedDashboard'
import { BrandSelector } from './components/BrandSelector'
import { BarChart3, Search } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'advanced'>('overview')

  return (
    <div className="min-h-screen bg-background">
      {/* Brand Selector */}
      <BrandSelector />

      {/* Tab Navigation */}
      <div className="bg-card border-b border-border sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-6">
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'overview'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Dashboard Geral
            </button>
            <button
              onClick={() => setActiveTab('advanced')}
              className={`flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'advanced'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Search className="w-4 h-4" />
              Analytics Avançado              
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'overview' ? <Dashboard /> : <AdvancedDashboard />}
    </div>
  )
}

export default App

