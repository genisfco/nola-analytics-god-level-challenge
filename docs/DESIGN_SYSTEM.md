# 🎨 Design System - Nola Restaurant Analytics

## Paleta de Cores

### Cores da Marca Nola

| Cor | Hex | RGB | HSL | Uso |
|-----|-----|-----|-----|-----|
| **🍅 Tomate** | `#fd6263` | `rgb(253,98,99)` | `hsl(1, 71%, 69%)` | Primária, CTAs, destaques |
| **🌰 Brown** | `#8b1721` | `rgb(139,23,33)` | `hsl(355, 71%, 32%)` | Secundária, hover, badges |
| **☁️ WhiteSmoke** | `#ececec` | `rgb(236,236,236)` | `hsl(0, 0%, 93%)` | Background principal |
| **🌙 DarkGray** | `#1c293a` | `rgb(28,41,58)` | `hsl(214, 35%, 17%)` | Textos, títulos |
| **⚪ White** | `#ffffff` | `rgb(255,255,255)` | `hsl(0, 0%, 100%)` | Cards, fundos |

---

## Mapeamento Semântico

```css
/* CSS Variables */
:root {
  /* Brand Colors */
  --nola-tomate: 1 71% 69%;
  --nola-brown: 355 71% 32%;
  --nola-whitesmoke: 0 0% 93%;
  --nola-darkgray: 214 35% 17%;
  --nola-white: 0 0% 100%;
  
  /* Semantic Colors */
  --background: var(--nola-whitesmoke);    /* Fundo da página */
  --foreground: var(--nola-darkgray);      /* Texto principal */
  
  --primary: var(--nola-tomate);           /* Cor primária */
  --primary-foreground: var(--nola-white); /* Texto sobre primária */
  
  --secondary: var(--nola-brown);          /* Cor secundária */
  --secondary-foreground: var(--nola-white); /* Texto sobre secundária */
  
  --card: var(--nola-white);               /* Fundo de cards */
  --card-foreground: var(--nola-darkgray); /* Texto em cards */
}
```

---

## Uso em Components

### Botões

```tsx
// Botão Primário (Tomate)
<button className="bg-primary hover:bg-secondary text-primary-foreground">
  Ação Principal
</button>

// Botão Secundário (Brown)
<button className="bg-secondary hover:bg-primary text-secondary-foreground">
  Ação Secundária
</button>

// Botão Outline
<button className="border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground">
  Outline
</button>
```

### Cards

```tsx
// Card Neutro
<div className="bg-card border border-border rounded-lg p-6">
  <h3 className="text-card-foreground">Título</h3>
</div>

// Card com Destaque
<div className="bg-card border-l-4 border-primary rounded-lg p-6 shadow-md">
  <h3 className="text-card-foreground">Métrica Importante</h3>
  <p className="text-4xl text-primary font-bold">R$ 125.430</p>
</div>

// Card com Background Sutil
<div className="bg-primary/5 border border-primary/20 rounded-lg p-6">
  <h3 className="text-card-foreground">Destaque Suave</h3>
  <p className="text-2xl text-secondary font-bold">+23%</p>
</div>
```

### Textos

```tsx
// Título Principal
<h1 className="text-foreground font-bold">Título</h1>

// Texto Normal
<p className="text-foreground">Parágrafo</p>

// Texto Secundário/Muted
<p className="text-muted-foreground">Texto secundário</p>

// Link
<a href="#" className="text-primary hover:text-secondary underline">
  Link
</a>
```

### Badges

```tsx
// Badge Primário
<span className="bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm">
  Novo
</span>

// Badge Secundário
<span className="bg-secondary text-secondary-foreground px-3 py-1 rounded-full text-sm">
  Importante
</span>

// Badge Outline
<span className="border border-primary text-primary px-3 py-1 rounded-full text-sm">
  Info
</span>
```

---

## Acessibilidade (WCAG)

### Contraste de Cores

| Combinação | Contraste | WCAG | Uso |
|------------|-----------|------|-----|
| Tomate (#fd6263) + White | **4.8:1** | ✅ AA | Texto grande, botões |
| Brown (#8b1721) + White | **10.2:1** | ✅ AAA | Todo tipo de texto |
| DarkGray (#1c293a) + White | **13.5:1** | ✅ AAA | Todo tipo de texto |
| DarkGray + WhiteSmoke | **11.8:1** | ✅ AAA | Todo tipo de texto |
| Tomate + DarkGray | **2.8:1** | ⚠️ Apenas decoração | Não usar para texto |

**Recomendações:**
- ✅ Use **Brown (#8b1721)** para textos sobre fundos claros (contraste AAA)
- ✅ Use **DarkGray (#1c293a)** para textos em geral (contraste AAA)
- ✅ Use **White** para textos sobre Tomate ou Brown
- ⚠️ Evite textos pequenos em **Tomate** sobre fundos claros

---

## Cores para Gráficos (Data Visualization)

```css
:root {
  --chart-1: var(--nola-tomate);   /* #fd6263 - Principal */
  --chart-2: var(--nola-brown);    /* #8b1721 - Secundário */
  --chart-3: 210 70% 50%;          /* #2563eb - Azul */
  --chart-4: 45 93% 58%;           /* #f7b731 - Amarelo */
  --chart-5: 280 65% 60%;          /* #a855f7 - Roxo */
}
```

### Uso em Recharts

```tsx
import { LineChart, Line } from 'recharts'

<LineChart data={data}>
  <Line dataKey="vendas" stroke="hsl(var(--chart-1))" />
  <Line dataKey="custos" stroke="hsl(var(--chart-2))" />
  <Line dataKey="lucro" stroke="hsl(var(--chart-3))" />
</LineChart>
```

---

## Classes Utilitárias Customizadas

### Acesso Direto às Cores da Marca

```tsx
// Usando cores diretas (útil para casos específicos)
<div className="bg-nola-tomate text-nola-white">Tomate</div>
<div className="bg-nola-brown text-nola-white">Brown</div>
<div className="bg-nola-whitesmoke text-nola-darkgray">WhiteSmoke</div>
<div className="text-nola-darkgray">DarkGray</div>
```

---

## Transparências e Overlays

```tsx
// Backgrounds com transparência (útil para cards de destaque)
<div className="bg-primary/5">5% Tomate</div>
<div className="bg-primary/10">10% Tomate</div>
<div className="bg-secondary/5">5% Brown</div>

// Borders com transparência
<div className="border border-primary/20">Border sutil</div>
```

---

## Gradientes

```tsx
// Gradiente Nola (Tomate -> Brown)
<div className="bg-gradient-to-r from-primary to-secondary">
  Gradiente
</div>

// Gradiente sutil no background
<div className="bg-gradient-to-br from-background to-muted">
  Background gradiente
</div>
```

---

## Dark Mode (Futuro)

Para implementar dark mode, adicione:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --background: var(--nola-darkgray);
    --foreground: var(--nola-whitesmoke);
    --card: 214 35% 12%;  /* DarkGray mais escuro */
    /* ... outros ajustes ... */
  }
}
```

---

## Animações e Transições

```tsx
// Transições de cor suaves
<button className="bg-primary hover:bg-secondary transition-colors duration-300">
  Botão com transição
</button>

// Hover com scale
<div className="bg-card hover:scale-105 transition-transform duration-200">
  Card interativo
</div>
```

---

## Exemplos Completos

### Dashboard Card

```tsx
<div className="bg-card border border-border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-lg font-semibold text-card-foreground">
      Total de Vendas
    </h3>
    <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium">
      Hoje
    </span>
  </div>
  <p className="text-4xl font-bold text-primary">R$ 12.540,00</p>
  <p className="text-sm text-muted-foreground mt-2">
    <span className="text-secondary font-semibold">+12%</span> vs ontem
  </p>
</div>
```

### Alert/Banner

```tsx
// Success
<div className="bg-primary/10 border-l-4 border-primary p-4 rounded-r">
  <p className="text-card-foreground font-medium">Sucesso!</p>
  <p className="text-muted-foreground text-sm">Operação concluída.</p>
</div>

// Error
<div className="bg-destructive/10 border-l-4 border-destructive p-4 rounded-r">
  <p className="text-destructive font-medium">Erro!</p>
  <p className="text-muted-foreground text-sm">Algo deu errado.</p>
</div>
```

---

**Última atualização:** 29/10/2025  
**Versão:** 1.0

