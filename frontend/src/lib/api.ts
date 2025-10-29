const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface DateRange {
  startDate: string;
  endDate: string;
  storeIds?: number[];
  channelIds?: number[];
}

export interface OverviewMetrics {
  total_sales: number;
  total_revenue: number;
  average_ticket: number;
  completed_sales: number;
  cancelled_sales: number;
  cancellation_rate: number;
  total_customers: number;
}

export interface ProductRanking {
  product_id: number;
  product_name: string;
  category: string | null;
  times_sold: number;
  total_quantity: number;
  total_revenue: number;
}

export interface ChannelMetrics {
  channel_id: number;
  channel_name: string;
  channel_type: string;
  total_sales: number;
  total_revenue: number;
  average_ticket: number;
  revenue_share: number;
}

export interface SalesTrend {
  date: string;
  total_sales: number;
  total_revenue: number;
  average_ticket: number;
  completed_sales: number;
  cancelled_sales: number;
}

export interface HourlyDistribution {
  hour: number;
  total_sales: number;
  total_revenue: number;
  average_ticket: number;
}

export interface DeliveryPerformance {
  avg_delivery_time: number;
  avg_production_time: number;
  total_deliveries: number;
  on_time_deliveries: number;
  on_time_rate: number;
}

export interface DeliveryByRegion {
  city: string;
  state: string;
  total_deliveries: number;
  avg_delivery_time: number;
  avg_production_time: number;
  on_time_rate: number;
  delivery_time_trend: number;
}

export interface ChurnRiskCustomer {
  customer_id: number;
  customer_name: string;
  email: string | null;
  phone_number: string | null;
  total_purchases: number;
  total_spent: number;
  last_purchase_date: string;
  days_since_last_purchase: number;
  avg_days_between_purchases: number;
  favorite_channel: string;
  favorite_product: string | null;
}

export interface ProductByContext {
  product_id: number;
  product_name: string;
  category: string | null;
  times_sold: number;
  total_revenue: number;
  avg_price: number;
  context: Record<string, any>;
}

export class AnalyticsAPI {
  static async getOverview(params: DateRange) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
      ...(params.channelIds?.length && { channel_ids: params.channelIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/overview?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch overview');
    return response.json();
  }

  static async getTopProducts(params: DateRange & { limit?: number }) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      limit: String(params.limit || 10),
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
      ...(params.channelIds?.length && { channel_ids: params.channelIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/products/top?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch top products');
    return response.json();
  }

  static async getChannelMetrics(params: DateRange) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/channels?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch channels');
    return response.json();
  }

  static async getSalesTrend(params: DateRange) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
      ...(params.channelIds?.length && { channel_ids: params.channelIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/sales/trend?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch sales trend');
    return response.json();
  }

  static async getHourlyDistribution(params: DateRange) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
      ...(params.channelIds?.length && { channel_ids: params.channelIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/sales/hourly?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch hourly distribution');
    return response.json();
  }

  // Advanced Analytics
  static async getDeliveryPerformance(params: DateRange) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/delivery/performance?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch delivery performance');
    return response.json();
  }

  static async getChurnRiskCustomers(minPurchases: number = 3, daysInactive: number = 30, limit: number = 100) {
    const queryParams = new URLSearchParams({
      min_purchases: String(minPurchases),
      days_inactive: String(daysInactive),
      limit: String(limit),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/customers/churn-risk?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch churn risk customers');
    return response.json();
  }

  static async getProductsByContext(
    params: DateRange & {
      weekday?: number;
      hourStart?: number;
      hourEnd?: number;
      channelId?: number;
      limit?: number;
    }
  ) {
    const queryParams = new URLSearchParams({
      start_date: params.startDate,
      end_date: params.endDate,
      ...(params.weekday !== undefined && { weekday: String(params.weekday) }),
      ...(params.hourStart !== undefined && { hour_start: String(params.hourStart) }),
      ...(params.hourEnd !== undefined && { hour_end: String(params.hourEnd) }),
      ...(params.channelId && { channel_id: String(params.channelId) }),
      ...(params.limit && { limit: String(params.limit) }),
      ...(params.storeIds?.length && { store_ids: params.storeIds.join(',') }),
    });

    const response = await fetch(`${API_BASE_URL}/analytics/products/by-context?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch products by context');
    return response.json();
  }
}
