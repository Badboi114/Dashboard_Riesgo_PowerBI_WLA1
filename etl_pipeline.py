"""
=============================================================================
 ETL PIPELINE — Dashboard Estratégico de Riesgo Crediticio
 Dataset: German Credit Data (UCI / Kaggle)
 Autor: Data Analyst | Ingeniería de Datos
 Fecha: 2026-02-09
=============================================================================
 Este script realiza:
   1. Descarga del dataset crudo desde UCI ML Repository
   2. Decodificación de TODOS los atributos codificados → texto legible
   3. Feature Engineering (Rango_Edad, Score_Cliente simulado)
   4. Modelado en Star Schema → Fact_Prestamos + 4 Dimensiones
   5. Exportación a CSV listos para Power BI
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime, timedelta
import random

# ─── CONFIGURACIÓN ─────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Semilla para reproducibilidad
random.seed(42)
np.random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════
# PASO 1: DESCARGA DEL DATASET CRUDO
# ═══════════════════════════════════════════════════════════════════════════
def descargar_dataset():
    """Descarga el German Credit Data desde UCI ML Repository."""
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.data"
    filepath = os.path.join(RAW_DIR, "german_credit.data")
    
    if os.path.exists(filepath):
        print("✅ Dataset crudo ya existe. Saltando descarga.")
        return filepath
    
    print("📥 Descargando German Credit Data desde UCI...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(filepath, 'w') as f:
            f.write(response.text)
        print(f"✅ Dataset descargado: {filepath}")
    except Exception as e:
        print(f"⚠️  Error descargando: {e}")
        print("📋 Generando dataset sintético basado en distribución original...")
        return None
    
    return filepath


# ═══════════════════════════════════════════════════════════════════════════
# PASO 2: CARGA Y DECODIFICACIÓN COMPLETA
# ═══════════════════════════════════════════════════════════════════════════

# Nombres originales de las 20 columnas del dataset
COLUMN_NAMES = [
    'Status_Cuenta',        # A1
    'Duracion_Meses',       # A2
    'Historial_Crediticio',  # A3
    'Proposito',             # A4
    'Monto_Credito',        # A5
    'Cuenta_Ahorro',        # A6
    'Empleo_Desde',         # A7
    'Tasa_Cuota',           # A8
    'Estado_Personal_Sexo', # A9
    'Otros_Deudores',       # A10
    'Residencia_Desde',     # A11
    'Propiedad',            # A12
    'Edad',                 # A13
    'Otros_Planes_Cuota',   # A14
    'Vivienda',             # A15
    'Creditos_Existentes',  # A16
    'Trabajo',              # A17
    'Personas_Dependientes', # A18
    'Telefono',             # A19
    'Extranjero',           # A20
    'Riesgo'                # Target: 1=Good, 2=Bad
]

# ── DICCIONARIOS DE DECODIFICACIÓN COMPLETOS ──────────────────────────────

DECODE_STATUS_CUENTA = {
    'A11': '< 0 DM (Sobregiro)',
    'A12': '0 - 200 DM (Bajo balance)',
    'A13': '>= 200 DM (Buen balance)',
    'A14': 'Sin cuenta corriente'
}

DECODE_HISTORIAL = {
    'A30': 'Sin créditos / todos pagados',
    'A31': 'Todos créditos pagados en este banco',
    'A32': 'Créditos existentes pagados puntualmente',
    'A33': 'Retraso en pagos pasados',
    'A34': 'Cuenta crítica / créditos en otros bancos'
}

DECODE_PROPOSITO = {
    'A40': 'Auto (Nuevo)',
    'A41': 'Auto (Usado)',
    'A42': 'Muebles/Equipamiento',
    'A43': 'Radio/Televisión',
    'A44': 'Electrodomésticos',
    'A45': 'Reparaciones',
    'A46': 'Educación',
    'A47': 'Vacaciones',
    'A48': 'Recapacitación',
    'A49': 'Negocio',
    'A410': 'Otros'
}

DECODE_AHORRO = {
    'A61': '< 100 DM',
    'A62': '100 - 500 DM',
    'A63': '500 - 1000 DM',
    'A64': '>= 1000 DM',
    'A65': 'Sin cuenta de ahorro'
}

DECODE_EMPLEO = {
    'A71': 'Desempleado',
    'A72': '< 1 año',
    'A73': '1 - 4 años',
    'A74': '4 - 7 años',
    'A75': '>= 7 años'
}

DECODE_ESTADO_SEXO = {
    'A91': 'Hombre - Divorciado/Separado',
    'A92': 'Mujer - Divorciada/Separada/Casada',
    'A93': 'Hombre - Soltero',
    'A94': 'Hombre - Casado/Viudo',
    'A95': 'Mujer - Soltera'
}

DECODE_OTROS_DEUDORES = {
    'A101': 'Ninguno',
    'A102': 'Co-solicitante',
    'A103': 'Garante'
}

DECODE_PROPIEDAD = {
    'A121': 'Bienes raíces',
    'A122': 'Seguro de vida / Ahorro',
    'A123': 'Auto u otros bienes',
    'A124': 'Sin propiedad conocida'
}

DECODE_OTROS_PLANES = {
    'A141': 'Banco',
    'A142': 'Tiendas',
    'A143': 'Ninguno'
}

DECODE_VIVIENDA = {
    'A151': 'Alquiler',
    'A152': 'Propia',
    'A153': 'Gratuita'
}

DECODE_TRABAJO = {
    'A171': 'Desempleado / No calificado - No residente',
    'A172': 'No calificado - Residente',
    'A173': 'Empleado calificado',
    'A174': 'Alta gerencia / Autónomo'
}

DECODE_TELEFONO = {
    'A191': 'No',
    'A192': 'Sí'
}

DECODE_EXTRANJERO = {
    'A201': 'Sí',
    'A202': 'No'
}


def cargar_y_decodificar(filepath):
    """Carga el dataset crudo y aplica TODAS las decodificaciones."""
    
    if filepath and os.path.exists(filepath):
        print("📂 Cargando dataset crudo...")
        df = pd.read_csv(filepath, sep=' ', header=None, names=COLUMN_NAMES)
    else:
        print("🔧 Generando dataset sintético...")
        df = generar_dataset_sintetico()
        
    print(f"   → {len(df)} registros cargados, {len(df.columns)} columnas")
    
    # ── Decodificar target: 1=Good, 2=Bad ──
    df['Riesgo'] = df['Riesgo'].map({1: 'Good', 2: 'Bad'})
    
    # ── Aplicar TODAS las decodificaciones ──
    print("🔄 Decodificando atributos...")
    
    decodificaciones = {
        'Status_Cuenta': DECODE_STATUS_CUENTA,
        'Historial_Crediticio': DECODE_HISTORIAL,
        'Proposito': DECODE_PROPOSITO,
        'Cuenta_Ahorro': DECODE_AHORRO,
        'Empleo_Desde': DECODE_EMPLEO,
        'Estado_Personal_Sexo': DECODE_ESTADO_SEXO,
        'Otros_Deudores': DECODE_OTROS_DEUDORES,
        'Propiedad': DECODE_PROPIEDAD,
        'Otros_Planes_Cuota': DECODE_OTROS_PLANES,
        'Vivienda': DECODE_VIVIENDA,
        'Trabajo': DECODE_TRABAJO,
        'Telefono': DECODE_TELEFONO,
        'Extranjero': DECODE_EXTRANJERO
    }
    
    for col, mapping in decodificaciones.items():
        df[col] = df[col].map(mapping).fillna(df[col])
        decoded_count = df[col].isin(mapping.values()).sum()
        print(f"   ✓ {col}: {decoded_count}/{len(df)} valores decodificados")
    
    # ── Separar Género y Estado Civil ──
    df['Genero'] = df['Estado_Personal_Sexo'].apply(
        lambda x: 'Masculino' if 'Hombre' in str(x) else 'Femenino'
    )
    df['Estado_Civil'] = df['Estado_Personal_Sexo'].apply(extraer_estado_civil)
    
    return df


def extraer_estado_civil(texto):
    """Extrae el estado civil del campo combinado."""
    texto = str(texto)
    if 'Soltero' in texto or 'Soltera' in texto:
        return 'Soltero/a'
    elif 'Casado' in texto or 'Casada' in texto:
        return 'Casado/a'
    elif 'Divorciado' in texto or 'Divorciada' in texto or 'Separado' in texto:
        return 'Divorciado/a'
    elif 'Viudo' in texto:
        return 'Viudo/a'
    return 'Desconocido'


def generar_dataset_sintetico():
    """Genera un dataset sintético con la misma distribución que el German Credit Data."""
    n = 1000
    data = {
        'Status_Cuenta': np.random.choice(['A11', 'A12', 'A13', 'A14'], n, p=[0.27, 0.27, 0.06, 0.40]),
        'Duracion_Meses': np.random.choice([6, 12, 18, 24, 36, 48, 60], n),
        'Historial_Crediticio': np.random.choice(['A30', 'A31', 'A32', 'A33', 'A34'], n, p=[0.04, 0.05, 0.53, 0.09, 0.29]),
        'Proposito': np.random.choice(['A40', 'A41', 'A42', 'A43', 'A46', 'A49'], n, p=[0.23, 0.10, 0.18, 0.28, 0.05, 0.16]),
        'Monto_Credito': np.random.lognormal(mean=7.8, sigma=0.7, size=n).astype(int),
        'Cuenta_Ahorro': np.random.choice(['A61', 'A62', 'A63', 'A64', 'A65'], n, p=[0.60, 0.10, 0.06, 0.05, 0.19]),
        'Empleo_Desde': np.random.choice(['A71', 'A72', 'A73', 'A74', 'A75'], n, p=[0.06, 0.17, 0.34, 0.17, 0.26]),
        'Tasa_Cuota': np.random.choice([1, 2, 3, 4], n, p=[0.20, 0.23, 0.25, 0.32]),
        'Estado_Personal_Sexo': np.random.choice(['A91', 'A92', 'A93', 'A94'], n, p=[0.05, 0.31, 0.55, 0.09]),
        'Otros_Deudores': np.random.choice(['A101', 'A102', 'A103'], n, p=[0.91, 0.04, 0.05]),
        'Residencia_Desde': np.random.choice([1, 2, 3, 4], n, p=[0.13, 0.31, 0.15, 0.41]),
        'Propiedad': np.random.choice(['A121', 'A122', 'A123', 'A124'], n, p=[0.28, 0.23, 0.33, 0.16]),
        'Edad': np.random.normal(loc=35, scale=11, size=n).clip(19, 75).astype(int),
        'Otros_Planes_Cuota': np.random.choice(['A141', 'A142', 'A143'], n, p=[0.14, 0.05, 0.81]),
        'Vivienda': np.random.choice(['A151', 'A152', 'A153'], n, p=[0.18, 0.71, 0.11]),
        'Creditos_Existentes': np.random.choice([1, 2, 3, 4], n, p=[0.63, 0.33, 0.03, 0.01]),
        'Trabajo': np.random.choice(['A171', 'A172', 'A173', 'A174'], n, p=[0.02, 0.20, 0.63, 0.15]),
        'Personas_Dependientes': np.random.choice([1, 2], n, p=[0.85, 0.15]),
        'Telefono': np.random.choice(['A191', 'A192'], n, p=[0.60, 0.40]),
        'Extranjero': np.random.choice(['A201', 'A202'], n, p=[0.04, 0.96]),
        'Riesgo': np.random.choice([1, 2], n, p=[0.70, 0.30])
    }
    return pd.DataFrame(data)


# ═══════════════════════════════════════════════════════════════════════════
# PASO 3: FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════

def feature_engineering(df):
    """Crea columnas derivadas para análisis más profundo."""
    print("\n⚙️  Feature Engineering...")
    
    # ── 1. Rango de Edad ──
    bins = [17, 25, 35, 50, 100]
    labels = ['18-25 (Joven)', '26-35 (Adulto Joven)', '36-50 (Adulto)', '50+ (Senior)']
    df['Rango_Edad'] = pd.cut(df['Edad'], bins=bins, labels=labels, right=True)
    print(f"   ✓ Rango_Edad creado: {df['Rango_Edad'].value_counts().to_dict()}")
    
    # ── 2. Score de Cliente Simulado (300-850, como FICO) ──
    # Basado en: historial + status cuenta + empleo + vivienda
    score_base = 500
    
    # Componente: Historial Crediticio (+/- puntos)
    historial_score = df['Historial_Crediticio'].map({
        'Sin créditos / todos pagados': 80,
        'Todos créditos pagados en este banco': 60,
        'Créditos existentes pagados puntualmente': 40,
        'Retraso en pagos pasados': -50,
        'Cuenta crítica / créditos en otros bancos': -80
    }).fillna(0)
    
    # Componente: Status de Cuenta
    cuenta_score = df['Status_Cuenta'].map({
        '>= 200 DM (Buen balance)': 70,
        '0 - 200 DM (Bajo balance)': 20,
        '< 0 DM (Sobregiro)': -40,
        'Sin cuenta corriente': -20
    }).fillna(0)
    
    # Componente: Empleo
    empleo_score = df['Empleo_Desde'].map({
        '>= 7 años': 60,
        '4 - 7 años': 40,
        '1 - 4 años': 20,
        '< 1 año': -10,
        'Desempleado': -50
    }).fillna(0)
    
    # Componente: Vivienda
    vivienda_score = df['Vivienda'].map({
        'Propia': 50,
        'Alquiler': 10,
        'Gratuita': -10
    }).fillna(0)
    
    # Componente: Ratio Monto/Duración (menor ratio = menos riesgo)
    ratio = df['Monto_Credito'] / (df['Duracion_Meses'] + 1)
    ratio_score = pd.cut(ratio, bins=[0, 100, 200, 500, float('inf')],
                          labels=[50, 20, -10, -40]).astype(float).fillna(0)
    
    # Score final con ruido aleatorio
    noise = np.random.normal(0, 30, len(df))
    df['Score_Cliente'] = (score_base + historial_score + cuenta_score + 
                            empleo_score + vivienda_score + ratio_score + noise)
    df['Score_Cliente'] = df['Score_Cliente'].clip(300, 850).astype(int)
    
    print(f"   ✓ Score_Cliente: min={df['Score_Cliente'].min()}, "
          f"max={df['Score_Cliente'].max()}, mean={df['Score_Cliente'].mean():.0f}")
    
    # ── 3. Categoría de Score ──
    score_bins = [299, 500, 600, 700, 850]
    score_labels = ['Muy Alto Riesgo (300-500)', 'Alto Riesgo (501-600)', 
                    'Riesgo Medio (601-700)', 'Bajo Riesgo (701-850)']
    df['Categoria_Score'] = pd.cut(df['Score_Cliente'], bins=score_bins, labels=score_labels)
    
    # ── 4. Cuota Mensual Estimada ──
    df['Cuota_Mensual'] = (df['Monto_Credito'] / df['Duracion_Meses']).round(2)
    print(f"   ✓ Cuota_Mensual calculada")
    
    # ── 5. Rango de Monto ──
    monto_bins = [0, 1000, 3000, 5000, 10000, float('inf')]
    monto_labels = ['Micro (<1K)', 'Pequeño (1K-3K)', 'Mediano (3K-5K)', 
                    'Grande (5K-10K)', 'Muy Grande (>10K)']
    df['Rango_Monto'] = pd.cut(df['Monto_Credito'], bins=monto_bins, labels=monto_labels)
    
    # ── 6. Generar Fechas Simuladas (para Dim_Tiempo) ──
    fecha_inicio = datetime(2023, 1, 1)
    fecha_fin = datetime(2025, 12, 31)
    dias_rango = (fecha_fin - fecha_inicio).days
    fechas = [fecha_inicio + timedelta(days=random.randint(0, dias_rango)) for _ in range(len(df))]
    df['Fecha_Solicitud'] = fechas
    df['Anio'] = df['Fecha_Solicitud'].dt.year
    df['Mes'] = df['Fecha_Solicitud'].dt.month
    df['Nombre_Mes'] = df['Fecha_Solicitud'].dt.strftime('%B')
    df['Trimestre'] = df['Fecha_Solicitud'].dt.quarter
    df['Dia_Semana'] = df['Fecha_Solicitud'].dt.day_name()
    
    print(f"   ✓ Fechas simuladas: {df['Anio'].value_counts().to_dict()}")
    
    return df


# ═══════════════════════════════════════════════════════════════════════════
# PASO 4: MODELADO STAR SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

def crear_star_schema(df):
    """Divide el DataFrame limpio en esquema de estrella para Power BI."""
    print("\n⭐ Creando Star Schema...")
    
    # ── Asignar IDs ──
    df['ID_Prestamo'] = range(1, len(df) + 1)
    df['ID_Cliente'] = range(1001, 1001 + len(df))
    
    # Generar ID_Proposito basado en el propósito único
    propositos_unicos = df['Proposito'].unique()
    proposito_map = {p: i+1 for i, p in enumerate(propositos_unicos)}
    df['ID_Proposito'] = df['Proposito'].map(proposito_map)
    
    # Generar ID_Tiempo basado en fecha
    fechas_unicas = df['Fecha_Solicitud'].dt.date.unique()
    fecha_map = {f: i+1 for i, f in enumerate(sorted(fechas_unicas))}
    df['ID_Tiempo'] = df['Fecha_Solicitud'].dt.date.map(fecha_map)
    
    # ═══════════════════════════════════════════════════════════════════
    # TABLA DE HECHOS: Fact_Prestamos
    # ═══════════════════════════════════════════════════════════════════
    fact_prestamos = df[[
        'ID_Prestamo', 'ID_Cliente', 'ID_Proposito', 'ID_Tiempo',
        'Monto_Credito', 'Duracion_Meses', 'Tasa_Cuota',
        'Cuota_Mensual', 'Creditos_Existentes', 'Score_Cliente',
        'Riesgo'
    ]].copy()
    
    fact_prestamos.rename(columns={
        'Monto_Credito': 'Monto',
        'Duracion_Meses': 'Duracion',
        'Tasa_Cuota': 'Tasa',
        'Riesgo': 'Estado_Riesgo'
    }, inplace=True)
    
    print(f"   ✓ Fact_Prestamos: {fact_prestamos.shape[0]} filas, {fact_prestamos.shape[1]} columnas")
    
    # ═══════════════════════════════════════════════════════════════════
    # DIMENSIÓN: Dim_Cliente
    # ═══════════════════════════════════════════════════════════════════
    dim_cliente = df[[
        'ID_Cliente', 'Edad', 'Rango_Edad', 'Genero', 'Estado_Civil',
        'Trabajo', 'Empleo_Desde', 'Vivienda', 'Propiedad',
        'Status_Cuenta', 'Cuenta_Ahorro', 'Historial_Crediticio',
        'Telefono', 'Extranjero', 'Personas_Dependientes',
        'Otros_Deudores', 'Otros_Planes_Cuota',
        'Categoria_Score', 'Rango_Monto'
    ]].copy()
    
    print(f"   ✓ Dim_Cliente: {dim_cliente.shape[0]} filas, {dim_cliente.shape[1]} columnas")
    
    # ═══════════════════════════════════════════════════════════════════
    # DIMENSIÓN: Dim_Proposito
    # ═══════════════════════════════════════════════════════════════════
    dim_proposito = pd.DataFrame({
        'ID_Proposito': [proposito_map[p] for p in propositos_unicos],
        'Proposito': propositos_unicos,
        'Categoria_Proposito': [categorizar_proposito(p) for p in propositos_unicos]
    }).sort_values('ID_Proposito').reset_index(drop=True)
    
    print(f"   ✓ Dim_Proposito: {dim_proposito.shape[0]} propósitos únicos")
    
    # ═══════════════════════════════════════════════════════════════════
    # DIMENSIÓN: Dim_Tiempo
    # ═══════════════════════════════════════════════════════════════════
    dim_tiempo_data = []
    for fecha, id_tiempo in sorted(fecha_map.items(), key=lambda x: x[1]):
        fecha_dt = pd.Timestamp(fecha)
        dim_tiempo_data.append({
            'ID_Tiempo': id_tiempo,
            'Fecha': fecha,
            'Anio': fecha_dt.year,
            'Mes': fecha_dt.month,
            'Nombre_Mes': fecha_dt.strftime('%B'),
            'Trimestre': f'Q{fecha_dt.quarter}',
            'Dia_Semana': fecha_dt.day_name(),
            'Es_FinDeSemana': 1 if fecha_dt.weekday() >= 5 else 0
        })
    dim_tiempo = pd.DataFrame(dim_tiempo_data)
    
    print(f"   ✓ Dim_Tiempo: {dim_tiempo.shape[0]} fechas únicas")
    
    # ═══════════════════════════════════════════════════════════════════
    # DIMENSIÓN: Dim_Riesgo (Extra — para segmentación)
    # ═══════════════════════════════════════════════════════════════════
    dim_riesgo = pd.DataFrame({
        'ID_Riesgo': [1, 2],
        'Estado_Riesgo': ['Good', 'Bad'],
        'Descripcion': ['Crédito pagado correctamente', 'Crédito en mora / impago'],
        'Etiqueta_ES': ['Bueno', 'Malo'],
        'Color_HEX': ['#2ECC71', '#E74C3C']
    })
    
    print(f"   ✓ Dim_Riesgo: 2 categorías")
    
    # ═══════════════════════════════════════════════════════════════════
    # TABLA PLANA (Alternativa completa para análisis exploratorio)
    # ═══════════════════════════════════════════════════════════════════
    tabla_completa = df[[
        'ID_Prestamo', 'Edad', 'Rango_Edad', 'Genero', 'Estado_Civil',
        'Trabajo', 'Empleo_Desde', 'Vivienda', 'Propiedad',
        'Status_Cuenta', 'Cuenta_Ahorro', 'Historial_Crediticio',
        'Proposito', 'Monto_Credito', 'Duracion_Meses', 'Tasa_Cuota',
        'Cuota_Mensual', 'Score_Cliente', 'Categoria_Score',
        'Rango_Monto', 'Creditos_Existentes', 'Personas_Dependientes',
        'Otros_Deudores', 'Otros_Planes_Cuota', 'Telefono', 'Extranjero',
        'Riesgo', 'Fecha_Solicitud', 'Anio', 'Mes', 'Nombre_Mes',
        'Trimestre', 'Dia_Semana'
    ]].copy()
    
    print(f"   ✓ Tabla_Completa: {tabla_completa.shape[0]} filas, {tabla_completa.shape[1]} columnas")
    
    return {
        'Fact_Prestamos': fact_prestamos,
        'Dim_Cliente': dim_cliente,
        'Dim_Proposito': dim_proposito,
        'Dim_Tiempo': dim_tiempo,
        'Dim_Riesgo': dim_riesgo,
        'Tabla_Completa': tabla_completa
    }


def categorizar_proposito(proposito):
    """Agrupa propósitos en categorías más amplias."""
    categorias = {
        'Auto (Nuevo)': 'Vehículos',
        'Auto (Usado)': 'Vehículos',
        'Muebles/Equipamiento': 'Hogar',
        'Radio/Televisión': 'Hogar',
        'Electrodomésticos': 'Hogar',
        'Reparaciones': 'Hogar',
        'Educación': 'Personal',
        'Vacaciones': 'Personal',
        'Recapacitación': 'Personal',
        'Negocio': 'Negocio',
        'Otros': 'Otros'
    }
    return categorias.get(proposito, 'Otros')


# ═══════════════════════════════════════════════════════════════════════════
# PASO 5: EXPORTACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def exportar_tablas(tablas):
    """Exporta todas las tablas a CSV para Power BI."""
    print("\n💾 Exportando tablas a CSV...")
    
    for nombre, df in tablas.items():
        filepath = os.path.join(PROCESSED_DIR, f"{nombre}.csv")
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   ✓ {nombre}.csv → {df.shape[0]} filas, {df.shape[1]} cols ({size_kb:.1f} KB)")
    
    print(f"\n📁 Archivos exportados en: {PROCESSED_DIR}")


# ═══════════════════════════════════════════════════════════════════════════
# PASO 6: REPORTE DE CALIDAD DE DATOS
# ═══════════════════════════════════════════════════════════════════════════

def reporte_calidad(tablas):
    """Genera un reporte de calidad de datos."""
    print("\n" + "="*70)
    print("📊 REPORTE DE CALIDAD DE DATOS")
    print("="*70)
    
    fact = tablas['Fact_Prestamos']
    cliente = tablas['Dim_Cliente']
    completa = tablas['Tabla_Completa']
    
    # Métricas clave
    total = len(fact)
    bad = len(fact[fact['Estado_Riesgo'] == 'Bad'])
    good = len(fact[fact['Estado_Riesgo'] == 'Good'])
    default_rate = bad / total * 100
    
    print(f"\n   Total Préstamos:         {total:,}")
    print(f"   Buenos (Good):           {good:,} ({good/total*100:.1f}%)")
    print(f"   Malos  (Bad):            {bad:,} ({bad/total*100:.1f}%)")
    print(f"   🔴 Tasa de Morosidad:    {default_rate:.1f}%")
    print(f"   💰 Monto Total Prestado: {fact['Monto'].sum():,.0f} DM")
    print(f"   💸 Monto en Riesgo:      {fact[fact['Estado_Riesgo']=='Bad']['Monto'].sum():,.0f} DM")
    print(f"   📈 Monto Promedio:       {fact['Monto'].mean():,.0f} DM")
    print(f"   📊 Score Promedio:       {fact['Score_Cliente'].mean():.0f}")
    
    # Nulos
    print(f"\n   Valores nulos en Fact:   {fact.isnull().sum().sum()}")
    print(f"   Valores nulos en Dim_Cliente: {cliente.isnull().sum().sum()}")
    
    # Distribución por propósito
    print(f"\n   📋 Tasa de Morosidad por Propósito:")
    for _, row in completa.groupby('Proposito').agg(
        Total=('Riesgo', 'count'),
        Bad=('Riesgo', lambda x: (x == 'Bad').sum())
    ).assign(Tasa=lambda x: (x['Bad'] / x['Total'] * 100).round(1)).sort_values('Tasa', ascending=False).iterrows():
        bar = "█" * int(row['Tasa'] / 2)
        print(f"      {_:30s} {row['Tasa']:5.1f}% {bar}")
    
    print(f"\n   📋 Tasa de Morosidad por Rango de Edad:")
    for _, row in completa.groupby('Rango_Edad').agg(
        Total=('Riesgo', 'count'),
        Bad=('Riesgo', lambda x: (x == 'Bad').sum())
    ).assign(Tasa=lambda x: (x['Bad'] / x['Total'] * 100).round(1)).sort_values('Tasa', ascending=False).iterrows():
        bar = "█" * int(row['Tasa'] / 2)
        print(f"      {str(_):30s} {row['Tasa']:5.1f}% {bar}")
    
    print("\n" + "="*70)
    print("✅ ETL COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"""
📂 Archivos generados en: {PROCESSED_DIR}
   
   Para Power BI:
   ┌──────────────────────────────────────────────────┐
   │  1. Fact_Prestamos.csv    (Tabla de Hechos)      │
   │  2. Dim_Cliente.csv       (Dimensión Clientes)   │
   │  3. Dim_Proposito.csv     (Dimensión Propósito)  │
   │  4. Dim_Tiempo.csv        (Dimensión Tiempo)     │
   │  5. Dim_Riesgo.csv        (Dimensión Riesgo)     │
   │  6. Tabla_Completa.csv    (Flat Table Backup)     │
   └──────────────────────────────────────────────────┘
   
   Siguiente paso: Importar en Power BI Desktop
   → Obtener Datos → Texto/CSV → Seleccionar archivos
   → Crear relaciones entre IDs
""")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*70)
    print("🏦 DASHBOARD ESTRATÉGICO DE RIESGO CREDITICIO")
    print("   ETL Pipeline — German Credit Data")
    print("="*70)
    
    # 1. Descargar
    filepath = descargar_dataset()
    
    # 2. Cargar y Decodificar
    df = cargar_y_decodificar(filepath)
    
    # 3. Feature Engineering
    df = feature_engineering(df)
    
    # 4. Star Schema
    tablas = crear_star_schema(df)
    
    # 5. Exportar
    exportar_tablas(tablas)
    
    # 6. Reporte
    reporte_calidad(tablas)
