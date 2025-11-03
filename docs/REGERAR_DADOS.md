# 🔄 Regenerar Dados do Banco

> **Nota:** Para a primeira geração de dados, veja [README.md](../README.md#2-gere-os-dados-primeira-vez)

Este guia é útil apenas quando você precisa **resetar e regenerar** os dados do zero.

O script `generate_data.py` já cria automaticamente:
- ✅ 7 brands (proprietários)
- ✅ 50 lojas distribuídas
- ✅ Produtos, itens e canais por brand
- ✅ ~500k vendas em 6 meses

## 📊 O que será gerado

**7 Brands criados automaticamente:**
- Maria - Burguer Boutique (3 lojas)
- João - Pizza & Cia (8 lojas)
- Ana - Sushi House (7 lojas)
- Carlos - Food Center (8 lojas)
- Pedro - Restaurante Popular (8 lojas)
- Lucia - Bistrô Moderno (8 lojas)
- Roberto - Fast Food Network (8 lojas)

## 🚀 Como Regenerar (Reset Completo)

### Opção 1: Reset completo com volumes (Recomendado)

Remove tudo (containers, volumes, dados) e começa do zero:

```bash
# 1. Parar e remover TUDO (containers + volumes)
docker compose down -v

# 2. Subir PostgreSQL (schema será criado automaticamente via volume mount)
docker compose up -d postgres

# 3. Aguardar inicialização (5-10 segundos)
# Windows PowerShell:
Start-Sleep -Seconds 10
# Linux/Mac:
# sleep 10

# 4. Gerar dados (cria automaticamente 7 brands + 50 lojas + ~500k vendas)
docker compose run --rm data-generator

# 5. Verificar (opcional)
docker compose exec postgres psql -U challenge challenge_db -c "SELECT b.name, COUNT(s.id) as stores FROM brands b LEFT JOIN stores s ON s.brand_id = b.id GROUP BY b.id, b.name ORDER BY b.id;"
```

### Opção 2: Apenas resetar banco (sem perder volumes)

Útil se você quer manter containers rodando mas resetar só os dados:

```bash
# 1. Dropar e recriar banco (mantém containers)
docker exec -it analytics-db psql -U challenge -d postgres -c "DROP DATABASE IF EXISTS challenge_db;"
docker exec -it analytics-db psql -U challenge -d postgres -c "CREATE DATABASE challenge_db;"

# 2. Criar schema (schema.sql está montado como volume, mas pode precisar rodar manualmente)
Get-Content database/schema.sql | docker exec -i analytics-db psql -U challenge -d challenge_db

# 3. Gerar dados
docker compose run --rm data-generator
```

## ⏱️ Tempo Estimado

- ⏱️ **10-15 minutos** para gerar ~500k vendas
- ✅ **7 brands** criados automaticamente
- ✅ **50 lojas** distribuídas entre os brands
- ✅ **Isolamento**: Cada brand tem seus próprios produtos, itens e canais

## ✅ Verificação

Após a geração, o script mostrará automaticamente:

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
    ...
```

## 📝 Notas Importantes

- ✅ O script **já cria automaticamente** os 7 brands - não precisa configurar nada
- ✅ Cada brand tem **canais próprios** (Presencial, iFood, Rappi, etc.)
- ✅ Vendas usam apenas produtos do **mesmo brand da loja**
- ✅ Para **primeira geração**, veja o README.md (não precisa deste guia)

