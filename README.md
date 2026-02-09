# 🏦 Dashboard Estratégico de Riesgo Crediticio

## Análisis de Cartera y Predicción de Morosidad

---

## 📋 Descripción del Proyecto

Un banco ficticio está perdiendo dinero porque aprueba créditos a personas que no pagan. Este proyecto identifica patrones de riesgo para reducir la tasa de impagos (Default Rate) y mejorar la calidad de la cartera.

El sistema consta de dos componentes:
- **Frontend Analítico:** Dashboard interactivo en Power BI con 3 páginas y 20+ medidas DAX.
- **Backend SQL:** Base de datos relacional con consultas avanzadas de riesgo crediticio.

## 🛠️ Tecnologías

| Componente | Tecnología | Uso |
|------------|------------|-----|
| ETL Pipeline | Python 3 + Pandas + NumPy | Descarga, limpieza, transformación y modelado Star Schema |
| Visualización | Power BI Desktop | Dashboard de 3 páginas con IA (Decomposition Tree, Key Influencers) |
| Base de Datos | SQL (ANSI Standard) | DDL, DML, DQL — Compatible con PostgreSQL/SQLite/MySQL |
| Versionamiento | Git + GitHub | Control de versiones y portafolio profesional |

## 📂 Estructura del Proyecto

```
Credit_Risk_Dashboard/
├── README.md                    ← Este archivo
├── etl_pipeline.py              ← Pipeline ETL completo (Python/Pandas)
├── analisis_riesgo.sql          ← Backend SQL con 5 consultas analíticas
├── dax_measures.dax             ← 20+ medidas DAX para Power BI
├── POWER_BI_GUIDE.md            ← Guía paso a paso del dashboard
└── data/
    ├── raw/
    │   └── german_credit.data   ← Dataset crudo (UCI ML Repository)
    └── processed/
        ├── Fact_Prestamos.csv   ← Tabla de Hechos (1,000 préstamos)
        ├── Dim_Cliente.csv      ← Dimensión Clientes (19 atributos)
        ├── Dim_Proposito.csv    ← Dimensión Propósito (10 categorías)
        ├── Dim_Tiempo.csv       ← Dimensión Tiempo (672 fechas)
        ├── Dim_Riesgo.csv       ← Dimensión Riesgo (Good/Bad)
        └── Tabla_Completa.csv   ← Tabla desnormalizada (33 columnas)
```

## 📊 Hallazgos Clave

| Métrica | Valor |
|---------|-------|
| 🔴 **Tasa de Morosidad Global** | **30.0%** |
| 💰 Monto Total Prestado | 3,271,258 DM |
| 💸 Monto en Riesgo | 1,181,438 DM |
| 📊 Score Promedio | 574 / 850 |
| 👤 Mayor riesgo por edad | **18-25 años (42.1%)** |
| 🎯 Mayor riesgo por propósito | **Educación (44.0%)** |

### Insight Principal
> *"Los jóvenes de 18-25 años que solicitan créditos para educación con cuentas en sobregiro representan el segmento de mayor riesgo. Implementar un umbral de Score ≥ 550 reduciría la morosidad al ~15% manteniendo el 75% del volumen."*

## 🔍 Componente SQL — Base de Datos de Riesgo

El archivo `analisis_riesgo.sql` demuestra:

| Paso | Técnica SQL | Descripción |
|------|-------------|-------------|
| DDL | `CREATE TABLE`, PK/FK | Arquitectura relacional Clientes ↔ Préstamos |
| DML | `INSERT INTO` | Ingesta de datos de prueba |
| DQL 1 | `JOIN` + `CASE WHEN` + `GROUP BY` | Tasa de morosidad por categoría |
| DQL 2 | `HAVING` + Agregaciones | Perfil de clientes morosos |
| DQL 3 | `SUM` + `AVG` + `ROUND` | KPIs ejecutivos de cartera |
| DQL 4 | Segmentación | Análisis de riesgo por vivienda |
| DQL 5 | `GROUP_CONCAT` + `ORDER BY` | Top clientes por exposición |

## 📈 Componente Power BI — Dashboard de 3 Páginas

1. **Resumen Ejecutivo** — KPIs, morosidad por propósito, tendencia temporal
2. **Perfil de Riesgo** — Scatter Plot (Edad vs Monto), Decomposition Tree (IA), Heat Map
3. **Score y Predicción** — Distribución de scores, Key Influencers (IA), simulador de corte

### Medidas DAX Principales
- `Tasa_Morosidad` — % de créditos Bad / Total
- `Monto_Riesgo` — Exposición financiera total en mora
- `Score_Cliente` — Score simulado tipo FICO (300-850)
- `Perdida_Esperada` — PD × LGD × EAD (Basilea II simplificado)
- `Indice_Riesgo_Relativo` — Comparación segmento vs promedio global

## 🚀 Cómo Ejecutar

### ETL Pipeline (Python)
```bash
python3 -m venv env && source env/bin/activate
pip install pandas numpy requests
python3 etl_pipeline.py
```

### SQL (cualquier motor)
1. Abrir `analisis_riesgo.sql` en SQLiteOnline.com o tu RDBMS preferido
2. Ejecutar bloques en orden: CREATE → INSERT → SELECT

### Power BI
1. Abrir Power BI Desktop
2. Obtener datos → Texto/CSV → Importar archivos de `data/processed/`
3. Crear relaciones según el Star Schema documentado en `POWER_BI_GUIDE.md`
4. Copiar medidas DAX de `dax_measures.dax`

## 📚 Dataset

**German Credit Data** — UCI Machine Learning Repository  
1,000 registros con 20 atributos originales, decodificados y enriquecidos a 33 columnas.

---

*Autor: William Lujan Arispe | Ingeniero de Sistemas*  
*Fecha: Febrero 2026*
