import { format } from 'date-fns'
import { Calendar } from 'lucide-react'
import { useState, useEffect } from 'react'

interface DateFilterProps {
  startDate: string
  endDate: string
  onChange: (startDate: string, endDate: string) => void
}

export function DateFilter({ startDate, endDate, onChange }: DateFilterProps) {
  const [localStart, setLocalStart] = useState(startDate)
  const [localEnd, setLocalEnd] = useState(endDate)

  // Sincronizar quando props mudarem (ex: vindo de insight)
  useEffect(() => {
    setLocalStart(startDate)
    setLocalEnd(endDate)
    // Aplicar automaticamente quando as props mudarem (vindo de insight)
    // Isso garante que os filtros sejam aplicados sem precisar clicar em "Aplicar"
    onChange(startDate, endDate)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startDate, endDate])

  const quickRanges = [
    { label: 'Últimos 15 dias', days: 15 },
    { label: 'Últimos 30 dias', days: 30 },
    { label: 'Últimos 90 dias', days: 90 },    
  ]

  const applyQuickRange = (days: number) => {
    const end = new Date()
    const start = new Date(end)
    start.setDate(start.getDate() - days)
    
    const startStr = format(start, 'yyyy-MM-dd')
    const endStr = format(end, 'yyyy-MM-dd')
    
    setLocalStart(startStr)
    setLocalEnd(endStr)
    onChange(startStr, endStr)
  }

  const handleDateChange = (type: 'start' | 'end', value: string) => {
    if (type === 'start') {
      setLocalStart(value)
      onChange(value, localEnd)
    } else {
      setLocalEnd(value)
      onChange(localStart, value)
    }
  }

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-4 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <Calendar className="w-4 h-4 text-primary" />
        <h3 className="font-semibold text-card-foreground">Período</h3>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {quickRanges.map((range) => (
          <button
            key={range.days}
            onClick={() => applyQuickRange(range.days)}
            className="px-3 py-1.5 text-sm bg-primary/10 hover:bg-primary/20 text-primary rounded-md transition-colors font-medium"
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* Espaço flexível para empurrar campos de data para baixo */}
      <div className="flex-1"></div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Data Inicial
          </label>
          <input
            type="date"
            value={localStart}
            onChange={(e) => handleDateChange('start', e.target.value)}
            className="w-full px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Data Final
          </label>
          <input
            type="date"
            value={localEnd}
            onChange={(e) => handleDateChange('end', e.target.value)}
            className="w-full px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>
    </div>
  )
}

