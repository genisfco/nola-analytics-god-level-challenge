# 🔄 Regenerar Dados com Múltiplos Brands

Este arquivo explica como regenerar os dados do banco com 7 brands diferentes.

## 📊 Distribuição dos Dados

### Brands (Proprietários)
1. **Maria - Burguer Boutique** → 3 lojas
2. **João - Pizza & Cia** → 8 lojas
3. **Ana - Sushi House** → 7 lojas
4. **Carlos - Food Center** → 8 lojas
5. **Pedro - Restaurante Popular** → 8 lojas
6. **Lucia - Bistrô Moderno** → 8 lojas
7. **Roberto - Fast Food Network** → 8 lojas

**Total: 50 lojas**

## 🚀 Como Executar

### Opção 1: Reset completo (Recomendado)

```bash
# 1. Parar e remover containers e volumes
docker compose down -v

# 2. Subir apenas o PostgreSQL
docker compose up -d postgres

# 3. Aguardar PostgreSQL iniciar (5-10 segundos)
Start-Sleep -Seconds 10

# 4. Criar schema
Get-Content database/schema.sql | docker exec -i analytics-db psql -U challenge -d challenge_db

# 5. Gerar dados (via Docker)
docker run --rm -it --network nola-god-level_analytics-network -v ${PWD}:/app -w /app python:3.11-slim bash -c "pip install -q psycopg2-binary faker && python database/generate_data.py --db-url postgresql://challenge:challenge_2024@analytics-db:5432/challenge_db"

# 6. Verificar resultado
docker exec -it analytics-db psql -U challenge -d challenge_db -c "SELECT b.name, COUNT(s.id) as stores FROM brands b LEFT JOIN stores s ON s.brand_id = b.id GROUP BY b.id, b.name ORDER BY b.id;"
```

### Opção 2: Apenas dropar e recriar

```bash
# 1. Dropar e recriar banco
docker exec -it analytics-db psql -U challenge -d postgres -c "DROP DATABASE IF EXISTS challenge_db;"
docker exec -it analytics-db psql -U challenge -d postgres -c "CREATE DATABASE challenge_db;"

# 2. Criar schema
Get-Content database/schema.sql | docker exec -i analytics-db psql -U challenge -d challenge_db

# 3. Gerar dados (via Docker)
docker run --rm -it --network nola-god-level_analytics-network -v ${PWD}:/app -w /app python:3.11-slim bash -c "pip install -q psycopg2-binary faker && python database/generate_data.py --db-url postgresql://challenge:challenge_2024@analytics-db:5432/challenge_db"

# 4. Verificar
docker exec -it analytics-db psql -U challenge -d challenge_db -c "SELECT b.name, COUNT(s.id) as stores FROM brands b LEFT JOIN stores s ON s.brand_id = b.id GROUP BY b.id, b.name;"
```

## ⏱️ Tempo Estimado

- Geração de dados: ~10-15 minutos
- ~500k vendas serão geradas
- Distribuídas proporcionalmente entre os 7 brands

## ✅ Verificações

Após a geração, você deve ver no output:

```
✓ Data generation complete!
  Total Stores: 50
  Total Products: ~490
  Total Items/Complements: ~252
  Total Customers: 10,000
  Total Sales: ~500,000
  
  Distribution by Brand:
    • Maria - Burguer Boutique: 3 stores, ~30,000 sales
    • João - Pizza & Cia: 8 stores, ~80,000 sales
    • Ana - Sushi House: 7 stores, ~70,000 sales
    • Carlos - Food Center: 8 stores, ~80,000 sales
    • Pedro - Restaurante Popular: 8 stores, ~80,000 sales
    • Lucia - Bistrô Moderno: 8 stores, ~80,000 sales
    • Roberto - Fast Food Network: 8 stores, ~80,000 sales
```

## 🎯 Próximos Passos

Após regenerar os dados, você precisará:

1. ✅ Criar endpoint no backend: `/api/v1/analytics/brands/list`
2. ✅ Adicionar parâmetro `brand_id` em todos os endpoints
3. ✅ Criar `BrandContext` no frontend
4. ✅ Criar componente `BrandSelector`
5. ✅ Atualizar todas as queries do frontend para incluir `brand_id`

## 📝 Notas

- Cada brand tem seus próprios channels (Presencial, iFood, Rappi, etc.)
- Cada brand tem seus próprios produtos e itens
- As vendas são geradas apenas com produtos do mesmo brand da loja
- Maria terá proporcionalmente menos vendas (3 lojas) comparado aos outros

