# 🏦 Dashboard Estratégico de Riesgo Crediticio
## Guía de Implementación en Power BI

---

## 📁 Archivos Generados por el ETL

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `Fact_Prestamos.csv` | Tabla de Hechos | 1,000 préstamos con montos, duraciones, scores y estado de riesgo |
| `Dim_Cliente.csv` | Dimensión | Perfil demográfico: edad, género, empleo, vivienda, historial |
| `Dim_Proposito.csv` | Dimensión | Catálogo de propósitos del crédito (Auto, Educación, Negocio...) |
| `Dim_Tiempo.csv` | Dimensión | Calendario con año, mes, trimestre, día de semana |
| `Dim_Riesgo.csv` | Dimensión | Catálogo Good/Bad con colores |
| `Tabla_Completa.csv` | Flat Table | Tabla desnormalizada completa (backup para análisis rápido) |

---

## 🔗 PASO 1: Importar Datos en Power BI

1. Abrir **Power BI Desktop**
2. **Inicio → Obtener datos → Texto/CSV**
3. Importar en este orden:
   - `Fact_Prestamos.csv`
   - `Dim_Cliente.csv`
   - `Dim_Proposito.csv`
   - `Dim_Tiempo.csv`
   - `Dim_Riesgo.csv`
4. En el Editor de Power Query, verificar tipos de datos:
   - Montos → **Número decimal**
   - IDs → **Número entero**
   - Fechas → **Fecha**
   - Textos → **Texto**

---

## ⭐ PASO 2: Crear Relaciones (Star Schema)

En la vista **Modelo**, crear estas relaciones:

```
                    ┌──────────────┐
                    │ Dim_Tiempo   │
                    │  ID_Tiempo   │
                    └──────┬───────┘
                           │ 1:N
    ┌──────────────┐  ┌────┴───────────┐  ┌──────────────┐
    │ Dim_Cliente   │  │ Fact_Prestamos │  │ Dim_Proposito│
    │  ID_Cliente   ├──┤  ID_Cliente    │  │ ID_Proposito │
    └──────────────┘  │  ID_Proposito──├──┘              │
         1:N          │  ID_Tiempo     │  └──────────────┘
                      │  Estado_Riesgo │         1:N
                      └────┬───────────┘
                           │
                    ┌──────┴───────┐
                    │ Dim_Riesgo   │
                    │Estado_Riesgo │
                    └──────────────┘
```

### Configuración de cada relación:

| Desde (Fact) | Hacia (Dim) | Columna Fact | Columna Dim | Cardinalidad | Dirección Filtro |
|---|---|---|---|---|---|
| Fact_Prestamos | Dim_Cliente | ID_Cliente | ID_Cliente | N:1 | Única |
| Fact_Prestamos | Dim_Proposito | ID_Proposito | ID_Proposito | N:1 | Única |
| Fact_Prestamos | Dim_Tiempo | ID_Tiempo | ID_Tiempo | N:1 | Única |
| Fact_Prestamos | Dim_Riesgo | Estado_Riesgo | Estado_Riesgo | N:1 | Única |

---

## 🧮 PASO 3: Crear Medidas DAX

Ir a **Modelado → Nueva Medida** y copiar cada fórmula del archivo `dax_measures.dax`.

### Medidas mínimas requeridas (en orden de prioridad):

1. **Tasa_Morosidad** — Usada en casi todas las visualizaciones
2. **Total_Prestado** — KPI de tarjeta
3. **Monto_Riesgo** — KPI de tarjeta
4. **Total_Creditos** — KPI de tarjeta
5. **Score_Promedio** — KPI de tarjeta
6. **Concentracion_Riesgo** — Gráfico de dona
7. **Indice_Riesgo_Relativo** — Análisis avanzado
8. **Perdida_Esperada** — Análisis avanzado

---

## 📊 PASO 4: Diseño del Dashboard (3 Páginas)

### 🎨 Paleta de Colores Recomendada

| Uso | Color | HEX |
|-----|-------|-----|
| Good / Positivo | Verde | `#2ECC71` |
| Bad / Negativo | Rojo | `#E74C3C` |
| Fondo | Gris oscuro | `#2C3E50` |
| Tarjetas | Blanco | `#FFFFFF` |
| Acentos | Azul | `#3498DB` |
| Warning | Naranja | `#F39C12` |

---

### 📄 PÁGINA 1: Resumen Ejecutivo (Para el Gerente)

**Título:** "Resumen Ejecutivo — Cartera de Crédito"

#### Fila Superior — KPIs (4 Tarjetas)

| Posición | Medida | Formato | Icono sugerido |
|----------|--------|---------|----------------|
| Izquierda | Tasa_Morosidad | Porcentaje | 🔴 |
| Centro-Izq | Total_Prestado | Moneda DM | 💰 |
| Centro-Der | Monto_Riesgo | Moneda DM (rojo) | 💸 |
| Derecha | Total_Creditos | Número | 📋 |

**Configuración de tarjetas:**
- Tamaño de fuente del valor: 28-32pt
- Color de fondo: Blanco con sombra
- Etiqueta debajo en gris claro

#### Fila Media — 2 Gráficos principales

**Izquierda: Gráfico de Barras Horizontal**
- **Eje Y:** `Dim_Proposito[Proposito]`
- **Valor:** `[Tasa_Morosidad]`
- **Ordenar:** Mayor a menor
- **Formato condicional:** Degradado rojo (mayor = más rojo)
- **Insight esperado:** "Los créditos para autos usados y vacaciones tienen la mayor tasa de impago"

**Derecha: Gráfico de Dona**
- **Leyenda:** `Fact_Prestamos[Estado_Riesgo]`
- **Valores:** `[Total_Creditos]`
- **Colores:** Good=#2ECC71, Bad=#E74C3C
- **Etiqueta central:** Tasa_Morosidad como dato destacado

#### Fila Inferior — Tendencia temporal

**Gráfico de Líneas + Barras Combinado (ancho completo)**
- **Eje X:** `Dim_Tiempo[Nombre_Mes]` (ordenado cronológicamente)
- **Barras:** `[Total_Creditos]` (azul claro)
- **Línea:** `[Tasa_Morosidad]` (rojo, eje secundario)
- **Insight:** Detectar si la morosidad crece o decrece con el tiempo

#### Segmentadores (Slicers) — Barra lateral o superior

| Slicer | Campo | Tipo |
|--------|-------|------|
| Año | `Dim_Tiempo[Anio]` | Botones |
| Trimestre | `Dim_Tiempo[Trimestre]` | Botones |
| Riesgo | `Fact_Prestamos[Estado_Riesgo]` | Botones |

---

### 📄 PÁGINA 2: Perfil de Riesgo (Para el Analista)

**Título:** "Análisis de Perfil de Riesgo del Cliente"

#### Visualización Principal — Scatter Plot

**Gráfico de Dispersión (mitad superior, ancho completo)**
- **Eje X:** `Dim_Cliente[Edad]`
- **Eje Y:** `Fact_Prestamos[Monto]`
- **Leyenda/Color:** `Fact_Prestamos[Estado_Riesgo]` (Rojo=Bad, Verde=Good)
- **Tamaño (opcional):** `Fact_Prestamos[Duracion]`
- **Tooltip personalizado:**
  - Score_Cliente
  - Proposito
  - Cuota_Mensual

**Insight clave:** "Los jóvenes (18-25) que solicitan montos >5,000 DM tienen una probabilidad de impago significativamente mayor"

#### Visualización IA — Decomposition Tree

**Árbol de Descomposición (mitad inferior izquierda)**
- **Analizar:** `[Tasa_Morosidad]`
- **Explicar por (en este orden):**
  1. `Dim_Cliente[Estado_Civil]`
  2. `Dim_Cliente[Empleo_Desde]`
  3. `Dim_Cliente[Vivienda]`
  4. `Dim_Cliente[Status_Cuenta]`
- **Configuración:** Activar "AI splits" para que Power BI sugiera automáticamente la mejor variable

**Insight esperado:** "Los solteros desempleados que alquilan y tienen cuenta en sobregiro tienen 65%+ de tasa de morosidad"

#### Visualización Complementaria — Mapa de Calor

**Matriz (Heat Map) (mitad inferior derecha)**
- **Filas:** `Dim_Cliente[Rango_Edad]`
- **Columnas:** `Dim_Cliente[Empleo_Desde]`
- **Valores:** `[Tasa_Morosidad]`
- **Formato condicional:** Escala de color (Verde → Amarillo → Rojo)

#### Segmentadores

| Slicer | Campo |
|--------|-------|
| Género | `Dim_Cliente[Genero]` |
| Categoría Score | `Dim_Cliente[Categoria_Score]` |
| Vivienda | `Dim_Cliente[Vivienda]` |

---

### 📄 PÁGINA 3: Score y Predicción (Para Data Science)

**Título:** "Score Crediticio y Modelo de Predicción"

#### Fila Superior — KPIs de Score

| Tarjeta | Medida | Color |
|---------|--------|-------|
| Score Promedio Global | Score_Promedio | Azul |
| Score Buenos Pagadores | Score_Buenos | Verde |
| Score Morosos | Score_Malos | Rojo |
| Brecha de Score | Brecha_Score | Naranja |

#### Sección Central Izquierda — Distribución de Score

**Histograma (Gráfico de Barras Agrupadas)**
- **Eje X:** `Dim_Cliente[Categoria_Score]` (bins de score)
- **Valores:** `[Total_Creditos]` agrupado por `Estado_Riesgo`
- **Colores:** Verde para Good, Rojo para Bad
- **Insight:** "A partir de Score 600, la proporción de buenos pagadores domina claramente"

#### Sección Central Derecha — Simulador de Corte

**Tabla con formato condicional**
- **Filas:** Categoría_Score (Muy Alto Riesgo, Alto Riesgo, Medio, Bajo)
- **Columnas:**
  - Total Créditos
  - Tasa de Morosidad (con barras de datos)
  - Monto en Riesgo
  - Pérdida Esperada

#### Sección Inferior — Key Influencers (IA de Power BI)

**Visual: Key Influencers**
- **Analizar:** `Fact_Prestamos[Estado_Riesgo]` = "Bad"
- **Explicar por:**
  - `Dim_Cliente[Status_Cuenta]`
  - `Dim_Cliente[Historial_Crediticio]`
  - `Dim_Cliente[Empleo_Desde]`
  - `Fact_Prestamos[Duracion]`
  - `Fact_Prestamos[Monto]`
  - `Dim_Cliente[Rango_Edad]`

**Insight esperado:** "El factor #1 que incrementa el riesgo de mora es tener una cuenta en sobregiro (<0 DM), que aumenta la probabilidad de impago en 2.5x"

---

## 🎨 PASO 5: Formato y Tema

### Crear un tema personalizado (archivo JSON):

Ir a **Vista → Temas → Personalizar tema actual** y configurar:

```json
{
  "name": "Credit Risk Theme",
  "dataColors": ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6", "#1ABC9C"],
  "background": "#F5F6FA",
  "foreground": "#2C3E50",
  "tableAccent": "#3498DB"
}
```

### Tips de diseño profesional:
- ✅ Usar fondo gris claro (#F5F6FA) en vez de blanco puro
- ✅ Títulos de página con fuente Segoe UI Semibold, 18pt
- ✅ Subtítulos y etiquetas en gris (#7F8C8D)
- ✅ Bordes redondeados en tarjetas (Radio: 8px)
- ✅ Sombras sutiles en los contenedores
- ✅ Logo del banco ficticio en la esquina superior izquierda
- ❌ No usar más de 6 colores distintos
- ❌ No saturar con más de 7 visualizaciones por página

---

## 📤 PASO 6: Publicación y Presentación

### Preparar para demo:
1. **Agregar bookmarks** para navegar entre páginas con botones
2. **Crear tooltips personalizados** (página oculta con detalle al hover)
3. **Agregar navegación** con botones entre las 3 páginas
4. **Probar con filtros** para verificar que todo responde correctamente

### Narrativa para presentación:

> "Este dashboard analiza una cartera de 1,000 créditos del Banco XYZ. 
> Descubrimos que la tasa de morosidad global es del ~30%, concentrada 
> principalmente en jóvenes de 18-25 años que solicitan créditos para 
> autos usados. Nuestra recomendación es implementar un umbral de 
> Score mínimo de 550 puntos, lo que reduciría la tasa de impago al 
> ~15% manteniendo el 75% del volumen de créditos aprobados."

---

## ✅ Checklist Final

- [ ] Datos importados correctamente (6 tablas)
- [ ] Relaciones creadas en modelo estrella
- [ ] Medidas DAX funcionando (mínimo 8)
- [ ] Página 1: Resumen Ejecutivo con 4 KPIs + 3 gráficos
- [ ] Página 2: Scatter Plot + Decomposition Tree + Heat Map
- [ ] Página 3: Score Analysis + Key Influencers
- [ ] Segmentadores funcionales en cada página
- [ ] Formato condicional aplicado
- [ ] Tema de colores consistente
- [ ] Tooltips personalizados
- [ ] Navegación entre páginas
- [ ] Insights documentados en cada gráfico
