-- =============================================================================
-- Proyecto: Backend Bancario - Base de Datos de Riesgo
-- Autor: William Lujan Arispe (Ingeniero de Sistemas)
-- Fecha: Febrero 2026
-- Descripción: Script SQL para estructurar y analizar cartera de créditos.
--              Demuestra DDL, DML, JOINs, CASE WHEN y análisis de morosidad.
-- Herramienta: SQLiteOnline.com / SQLite / cualquier RDBMS compatible
-- =============================================================================


-- ═══════════════════════════════════════════════════════════════════════════
-- PASO 1: ARQUITECTURA (DDL - Data Definition Language)
-- Creamos el esquema relacional con Primary Keys y Foreign Keys
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Crear la tabla de CLIENTES (Datos demográficos)
CREATE TABLE Clientes (
    id_cliente INT PRIMARY KEY,
    edad INT,
    genero VARCHAR(10),
    trabajo VARCHAR(50),
    vivienda VARCHAR(20)
);

-- 2. Crear la tabla de PRESTAMOS (Datos financieros)
-- Esta tabla se conecta con Clientes mediante una Foreign Key
CREATE TABLE Prestamos (
    id_prestamo INT PRIMARY KEY,
    id_cliente INT,
    monto DECIMAL(10,2),
    proposito VARCHAR(50),
    riesgo VARCHAR(10), -- 'Good' o 'Bad'
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);


-- ═══════════════════════════════════════════════════════════════════════════
-- PASO 2: INGESTA DE DATOS (DML - Data Manipulation Language)
-- Muestra representativa basada en el German Credit Data real
-- ═══════════════════════════════════════════════════════════════════════════

-- Insertar datos de prueba en CLIENTES
INSERT INTO Clientes VALUES 
(1, 22, 'Mujer', 'Calificado', 'Propia'),
(2, 45, 'Hombre', 'No calificado', 'Gratis'),
(3, 33, 'Hombre', 'Profesional', 'Alquiler'),
(4, 28, 'Mujer', 'Calificado', 'Alquiler'),
(5, 50, 'Hombre', 'Ejecutivo', 'Propia');

-- Insertar datos de prueba en PRESTAMOS
-- Fíjate cómo algunos son 'Bad' (Riesgo)
INSERT INTO Prestamos VALUES 
(101, 1, 5000.00, 'Radio/TV', 'Bad'),
(102, 2, 1200.00, 'Educacion', 'Good'),
(103, 3, 9500.00, 'Auto Nuevo', 'Bad'),
(104, 4, 2500.00, 'Muebles', 'Good'),
(105, 5, 15000.00, 'Negocios', 'Good'),
(106, 1, 800.00, 'Reparaciones', 'Bad'); -- El cliente 1 pidió otro préstamo


-- ═══════════════════════════════════════════════════════════════════════════
-- PASO 3: ANÁLISIS (DQL - Data Query Language)
-- Consultas de inteligencia de negocio sobre la cartera
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── 3.1 CONSULTA MAESTRA DE RIESGO ──────────────────────────────────────
-- "¿Cuánto dinero hemos prestado por categoría y cuántos son de alto riesgo?"
-- Técnicas: JOIN, GROUP BY, CASE WHEN, Agregaciones
SELECT 
    p.proposito AS Categoria,
    COUNT(*) AS Total_Prestamos,
    SUM(p.monto) AS Dinero_Total_Prestado,
    -- Aquí calculamos cuántos son tóxicos (Bad)
    SUM(CASE WHEN p.riesgo = 'Bad' THEN 1 ELSE 0 END) AS Prestamos_Riesgosos,
    -- Calculamos el % de Riesgo
    ROUND(CAST(SUM(CASE WHEN p.riesgo = 'Bad' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) || '%' AS Tasa_Morosidad
FROM Prestamos p
JOIN Clientes c ON p.id_cliente = c.id_cliente
GROUP BY p.proposito
ORDER BY Dinero_Total_Prestado DESC;


-- ─── 3.2 PERFIL DE CLIENTES MOROSOS ──────────────────────────────────────
-- "¿Quiénes son los clientes que no pagan? ¿Qué tienen en común?"
SELECT 
    c.id_cliente,
    c.edad,
    c.genero,
    c.trabajo,
    c.vivienda,
    COUNT(p.id_prestamo) AS Num_Prestamos,
    SUM(p.monto) AS Deuda_Total,
    SUM(CASE WHEN p.riesgo = 'Bad' THEN p.monto ELSE 0 END) AS Monto_En_Riesgo
FROM Clientes c
JOIN Prestamos p ON c.id_cliente = p.id_cliente
GROUP BY c.id_cliente
HAVING SUM(CASE WHEN p.riesgo = 'Bad' THEN 1 ELSE 0 END) > 0
ORDER BY Monto_En_Riesgo DESC;


-- ─── 3.3 RESUMEN EJECUTIVO DE LA CARTERA ─────────────────────────────────
-- KPIs globales: exactamente lo que mostramos en Power BI
SELECT
    COUNT(*) AS Total_Prestamos,
    SUM(monto) AS Monto_Total_Prestado,
    SUM(CASE WHEN riesgo = 'Bad' THEN monto ELSE 0 END) AS Monto_En_Riesgo,
    ROUND(CAST(SUM(CASE WHEN riesgo = 'Bad' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) || '%' AS Tasa_Morosidad_Global,
    ROUND(AVG(monto), 2) AS Monto_Promedio_Prestamo
FROM Prestamos;


-- ─── 3.4 ANÁLISIS POR TIPO DE VIVIENDA ──────────────────────────────────
-- "¿Los que alquilan son más riesgosos que los propietarios?"
SELECT
    c.vivienda,
    COUNT(*) AS Total_Prestamos,
    ROUND(AVG(p.monto), 2) AS Monto_Promedio,
    SUM(CASE WHEN p.riesgo = 'Bad' THEN 1 ELSE 0 END) AS Malos,
    ROUND(CAST(SUM(CASE WHEN p.riesgo = 'Bad' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) || '%' AS Tasa_Morosidad
FROM Prestamos p
JOIN Clientes c ON p.id_cliente = c.id_cliente
GROUP BY c.vivienda
ORDER BY Tasa_Morosidad DESC;


-- ─── 3.5 TOP CLIENTES POR EXPOSICIÓN ────────────────────────────────────
-- "¿Quién nos debe más dinero?" (Útil para gestión de cobranzas)
SELECT
    c.id_cliente,
    c.genero || ', ' || c.edad || ' años, ' || c.trabajo AS Perfil_Cliente,
    SUM(p.monto) AS Exposicion_Total,
    GROUP_CONCAT(p.proposito, ' | ') AS Propositos,
    GROUP_CONCAT(p.riesgo, ' | ') AS Estados_Riesgo
FROM Clientes c
JOIN Prestamos p ON c.id_cliente = p.id_cliente
GROUP BY c.id_cliente
ORDER BY Exposicion_Total DESC;


-- =============================================================================
-- FIN DEL SCRIPT
-- Resultado esperado: 5 consultas que demuestran JOIN, CASE WHEN, 
-- GROUP BY, HAVING, agregaciones y análisis de riesgo crediticio.
-- =============================================================================
