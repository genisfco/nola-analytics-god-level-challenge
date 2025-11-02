import { cn } from '@/lib/utils'
import { LucideIcon } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  variant?: 'primary' | 'secondary' | 'accent'
}

export function KPICard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend,
  variant = 'primary' 
}: KPICardProps) {
  const variantStyles = {
    primary: 'border-l-4 border-primary bg-primary/5',
    secondary: 'border-l-4 border-secondary bg-secondary/5',
    accent: 'border-l-4 border-chart-3 bg-chart-3/5',
  }

  return (
    <div className={cn(
      'bg-card rounded-lg shadow-sm border border-border p-6 transition-all hover:shadow-md h-full flex flex-col',
      variantStyles[variant]
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground mb-1">
            {title}
          </p>
          <p className="text-3xl font-bold text-card-foreground mb-1">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-muted-foreground">
              {subtitle}
            </p>
          )}
          {trend && (
            <div className={cn(
              'inline-flex items-center gap-1 text-xs font-medium mt-2 px-2 py-1 rounded-full',
              trend.isPositive 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            )}>
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={cn(
            'p-3 rounded-full',
            variant === 'primary' && 'bg-primary/10 text-primary',
            variant === 'secondary' && 'bg-secondary/10 text-secondary',
            variant === 'accent' && 'bg-chart-3/10 text-chart-3'
          )}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  )
}

