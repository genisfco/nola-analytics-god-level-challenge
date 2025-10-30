/**
 * TypeScript types for Insights
 */

export type InsightPriority = 'critical' | 'attention' | 'positive'

export type InsightType = 
  | 'performance_issue'
  | 'opportunity'
  | 'churn_risk'
  | 'revenue_anomaly'
  | 'success_pattern'

export interface InsightImpact {
  metric: string
  value: number
  currency: string
  period: string
}

export interface InsightContext {
  affected_stores?: number[]
  affected_channels?: number[]
  affected_days?: string[]
  affected_hours?: number[]
  affected_products?: number[]
  data_points?: number
}

export interface InsightRecommendation {
  action: string
  estimated_roi?: number
  difficulty: 'easy' | 'medium' | 'hard'
  link_to?: string
}

export interface Insight {
  id: string
  type: InsightType
  priority: InsightPriority
  title: string
  description: string
  impact: InsightImpact
  context: InsightContext
  recommendation: InsightRecommendation
  detected_at: string
  confidence_score: number
}

export interface InsightsResponse {
  insights: Insight[]
  total: number
  generated_at: string
  period: {
    start_date: string
    end_date: string
    days: number
  }
}

