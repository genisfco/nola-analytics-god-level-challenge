import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, subDays, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value)
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

export function formatDate(dateString: string): string {
  // Usar parseISO para evitar problemas de timezone
  // parseISO interpreta a string como data local ao invés de UTC
  return format(parseISO(dateString), 'dd/MM/yyyy', { locale: ptBR })
}

export function getDefaultDateRange() {
  const endDate = new Date()
  const startDate = subDays(endDate, 6) // 7 dias no total (hoje + 6 dias anteriores)
  
  return {
    startDate: format(startDate, 'yyyy-MM-dd'),
    endDate: format(endDate, 'yyyy-MM-dd'),
    storeIds: undefined as number[] | undefined,
    channelIds: undefined as number[] | undefined,
  }
}
