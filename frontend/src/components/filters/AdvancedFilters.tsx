import { Filter } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'

interface AdvancedFiltersProps {
  onApply: (filters: ContextFilters) => void
  initialFilters?: ContextFilters
}

export interface ContextFilters {
  weekday?: number
  hourStart?: number
  hourEnd?: number
  channelId?: number
}

const weekdayOptions = [
  { value: 0, label: 'Domingo' },
  { value: 1, label: 'Segunda' },
  { value: 2, label: 'Terça' },
  { value: 3, label: 'Quarta' },
  { value: 4, label: 'Quinta' },
  { value: 5, label: 'Sexta' },
  { value: 6, label: 'Sábado' },
]

const channelOptions = [
  { value: 1, label: 'Presencial' },
  { value: 2, label: 'iFood' },
  { value: 3, label: 'Rappi' },
  { value: 4, label: 'Uber Eats' },
  { value: 5, label: 'WhatsApp' },
  { value: 6, label: 'App Próprio' },
]

const hourRanges = [
  { start: 6, end: 11, label: 'Manhã (6h-11h)' },
  { start: 11, end: 15, label: 'Almoço (11h-15h)' },
  { start: 15, end: 18, label: 'Tarde (15h-18h)' },
  { start: 18, end: 23, label: 'Jantar (18h-23h59m)' },
  { start: 0, end: 6, label: 'Madrugada (0h-6h)' },
]

export function AdvancedFilters({ onApply, initialFilters }: AdvancedFiltersProps) {
  const [weekday, setWeekday] = useState<number | undefined>(initialFilters?.weekday)
  const [hourRange, setHourRange] = useState<{ start: number; end: number } | undefined>(
    initialFilters?.hourStart !== undefined && initialFilters?.hourEnd !== undefined
      ? { start: initialFilters.hourStart, end: initialFilters.hourEnd }
      : undefined
  )
  const [channelId, setChannelId] = useState<number | undefined>(initialFilters?.channelId)
  
  // Usar useRef para rastrear se já aplicamos os filtros iniciais e se é o primeiro render
  const hasAppliedInitialFilters = useRef(false)
  const previousInitialFilters = useRef<string>('')
  const isFirstRender = useRef(true)

  // Criar uma chave única para comparar initialFilters
  const getFiltersKey = (filters?: ContextFilters) => {
    if (!filters) return ''
    return JSON.stringify({
      weekday: filters.weekday,
      hourStart: filters.hourStart,
      hourEnd: filters.hourEnd,
      channelId: filters.channelId
    })
  }

  // Aplicar filtros iniciais automaticamente quando receber (apenas uma vez)
  useEffect(() => {
    const currentKey = getFiltersKey(initialFilters)
    const previousKey = previousInitialFilters.current

    // Só aplica se os filtros realmente mudaram e ainda não foram aplicados
    if (initialFilters && currentKey !== previousKey && currentKey !== '') {
      const hasInitialFilters = 
        initialFilters.weekday !== undefined ||
        initialFilters.channelId !== undefined ||
        (initialFilters.hourStart !== undefined && initialFilters.hourEnd !== undefined)
      
      if (hasInitialFilters && !hasAppliedInitialFilters.current) {
        setWeekday(initialFilters.weekday)
        setChannelId(initialFilters.channelId)
        if (initialFilters.hourStart !== undefined && initialFilters.hourEnd !== undefined) {
          setHourRange({ start: initialFilters.hourStart, end: initialFilters.hourEnd })
        } else {
          setHourRange(undefined)
        }
        
        // Marcar como aplicado e atualizar a referência
        hasAppliedInitialFilters.current = true
        previousInitialFilters.current = currentKey
        
        // Aplicar os filtros apenas uma vez
        onApply({
          weekday: initialFilters.weekday,
          hourStart: initialFilters.hourStart,
          hourEnd: initialFilters.hourEnd,
          channelId: initialFilters.channelId,
        })
      }
    }
    
    // Reset quando initialFilters ficar vazio (usuário limpar filtros manualmente)
    if (!initialFilters || currentKey === '') {
      hasAppliedInitialFilters.current = false
      previousInitialFilters.current = ''
    }
  }, [initialFilters, onApply])

  // Aplicar filtros automaticamente quando o estado local mudar
  useEffect(() => {
    // Não aplicar no primeiro render (componente montando sem filtros iniciais)
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    // Não aplicar se ainda estamos processando filtros iniciais
    if (hasAppliedInitialFilters.current) {
      return
    }

    // Aplicar automaticamente quando os filtros mudarem
    onApply({
      weekday,
      hourStart: hourRange?.start,
      hourEnd: hourRange?.end,
      channelId,
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekday, hourRange, channelId])

  const handleClear = () => {
    // Reset flags quando usuário limpar
    hasAppliedInitialFilters.current = false
    previousInitialFilters.current = ''
    isFirstRender.current = false
    
    setWeekday(undefined)
    setHourRange(undefined)
    setChannelId(undefined)
    onApply({})
  }

  const hasFilters = weekday !== undefined || hourRange !== undefined || channelId !== undefined

  return (
    <div className="bg-card rounded-lg shadow-sm border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-4 h-4 text-primary" />
        <h3 className="font-semibold text-card-foreground">Filtros Contextuais</h3>
      </div>

      <div className="space-y-4">
        {/* Filtros em grid horizontal */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Weekday Filter */}
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-2">
              Dia da Semana
            </label>
            <select
              value={weekday ?? ''}
              onChange={(e) => {
                const newWeekday = e.target.value ? Number(e.target.value) : undefined
                setWeekday(newWeekday)
                // Aplicar automaticamente quando muda
                hasAppliedInitialFilters.current = false
              }}
              className="w-full px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-input"
            >
              <option value="">Todos os dias</option>
              {weekdayOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Hour Range Filter */}
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-2">
              Período do Dia
            </label>
            <select
              value={
                hourRange 
                  ? (hourRanges.some(r => r.start === hourRange.start && r.end === hourRange.end)
                      ? `${hourRange.start}-${hourRange.end}`
                      : '') 
                  : ''
              }
              onChange={(e) => {
                if (!e.target.value) {
                  setHourRange(undefined)
                  hasAppliedInitialFilters.current = false
                  return
                }
                const [start, end] = e.target.value.split('-').map(Number)
                setHourRange({ start, end })
                // Aplicar automaticamente quando muda
                hasAppliedInitialFilters.current = false
              }}
              className="w-full px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-input"
            >
              <option value="">Todos os horários</option>
              {hourRanges.map((range) => (
                <option key={`${range.start}-${range.end}`} value={`${range.start}-${range.end}`}>
                  {range.label}
                </option>
              ))}
            </select>
            {hourRange && !hourRanges.some(r => r.start === hourRange.start && r.end === hourRange.end) && (
              <p className="text-xs text-primary mt-1">
                ⏰ Filtro ativo: {hourRange.start}h - {hourRange.end}h
              </p>
            )}
          </div>

          {/* Channel Filter */}
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-2">
              Canal de Venda
            </label>
            <select
              value={channelId ?? ''}
              onChange={(e) => {
                const newChannelId = e.target.value ? Number(e.target.value) : undefined
                setChannelId(newChannelId)
                // Aplicar automaticamente quando muda
                hasAppliedInitialFilters.current = false
              }}
              className="w-full px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-input"
            >
              <option value="">Todos os canais</option>
              {channelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Clear Button */}
        {hasFilters && (
        <div className="flex gap-2">
            <button
              onClick={handleClear}
              className="w-full px-4 py-2 bg-muted hover:bg-muted/80 text-muted-foreground rounded-md font-medium transition-colors"
            >
              Limpar Filtros
            </button>
          </div>
          )}

        {/* Active Filters Display */}
        {hasFilters && (
          <div className="pt-3 border-t border-border">
            <p className="text-xs font-medium text-muted-foreground mb-2">Filtros ativos:</p>
            <div className="flex flex-wrap gap-2">
              {weekday !== undefined && (
                <span className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-xs rounded-md">
                  {weekdayOptions.find((w) => w.value === weekday)?.label}
                </span>
              )}
              {hourRange && (
                <span className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-xs rounded-md">
                  {hourRanges.find((h) => h.start === hourRange.start && h.end === hourRange.end)?.label 
                    || `${hourRange.start}h - ${hourRange.end}h`}
                </span>
              )}
              {channelId && (
                <span className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-xs rounded-md">
                  {channelOptions.find((c) => c.value === channelId)?.label}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

