-- ============================================================================
-- ÍNDICES PARA OTIMIZAR PERFORMANCE
-- ============================================================================
-- Created: 2025-10-30
-- Purpose: Adicionar índices para queries de analytics e churn risk

-- Sales table - principal tabela de consultas
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_store_id ON sales(store_id);
CREATE INDEX IF NOT EXISTS idx_sales_channel_id ON sales(channel_id);
CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at);
CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(sale_status_desc);

-- Índice composto para queries de churn (customer + status + data)
CREATE INDEX IF NOT EXISTS idx_sales_customer_status_date 
    ON sales(customer_id, sale_status_desc, created_at DESC);

-- Índice composto para filtro por marca (store + brand)
CREATE INDEX IF NOT EXISTS idx_stores_brand_id ON stores(brand_id);

-- Customers table
CREATE INDEX IF NOT EXISTS idx_customers_id ON customers(id);

-- Product sales (para queries de produto favorito)
CREATE INDEX IF NOT EXISTS idx_product_sales_sale_id ON product_sales(sale_id);
CREATE INDEX IF NOT EXISTS idx_product_sales_product_id ON product_sales(product_id);

-- Índice composto para queries com brand_id
CREATE INDEX IF NOT EXISTS idx_sales_store_status_customer 
    ON sales(store_id, sale_status_desc, customer_id) 
    WHERE customer_id IS NOT NULL;

-- Channels (para queries de canal favorito)
CREATE INDEX IF NOT EXISTS idx_channels_id ON channels(id);

-- Products
CREATE INDEX IF NOT EXISTS idx_products_id ON products(id);

ANALYZE sales;
ANALYZE customers;
ANALYZE stores;
ANALYZE product_sales;
ANALYZE channels;
ANALYZE products;

