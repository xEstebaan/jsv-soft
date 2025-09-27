# Funcionalidad de Reportes - JSV Soft

## Descripción

Se ha implementado la funcionalidad de reportes para administradores que permite visualizar y filtrar el historial de entradas y salidas de los empleados.

## Características Implementadas

### 1. Vista de Reportes (`/admin/reportes`)

- **Métricas en tiempo real**: Total de empleados, entradas y salidas del día
- **Filtros avanzados**: Por empleado específico y rango de fechas
- **Tabla de registros**: Muestra empleado, fecha, hora de entrada y hora de salida
- **Diseño responsive**: Adaptable a diferentes tamaños de pantalla

### 2. Funcionalidades de Filtrado

- **Filtro por empleado**: Dropdown con todos los empleados registrados
- **Filtro por fecha**: Rango de fechas con validación
- **Filtros combinables**: Se pueden usar múltiples filtros simultáneamente

### 3. Interfaz de Usuario

- **Sidebar consistente**: Mantiene el mismo diseño que la vista de empleados
- **Navegación activa**: El enlace de "Reportes" se marca como activo
- **Métricas visuales**: Tarjetas con información clave
- **Tabla interactiva**: Con DataTables para búsqueda y paginación

## Archivos Creados/Modificados

### Nuevos Archivos

- `app/templates/admin/reportes.html` - Template principal de reportes
- `app/static/css/reportes.css` - Estilos específicos para reportes
- `app/static/js/reportes.js` - Funcionalidad JavaScript para reportes
- `test_reportes.py` - Script para generar datos de prueba

### Archivos Modificados

- `app/routers/admin.py` - Agregada ruta `/admin/reportes`
- `app/__init__.py` - Registrado el blueprint de admin
- `app/templates/admin/vista_empleados.html` - Enlace a reportes funcional

## Estructura de la Vista

### Métricas

- **Total Empleados**: Número total de empleados registrados
- **Entradas Hoy**: Cantidad de entradas registradas hoy
- **Salidas Hoy**: Cantidad de salidas registradas hoy

### Filtros

- **Empleado**: Dropdown con lista de todos los empleados
- **Fecha Inicio**: Campo de fecha para el inicio del rango
- **Fecha Fin**: Campo de fecha para el fin del rango
- **Botón Filtrar**: Aplica los filtros seleccionados

### Tabla de Registros

- **Empleado**: Nombre completo del empleado
- **Fecha**: Fecha del registro
- **Hora de Entrada**: Hora de entrada (si aplica)
- **Hora de Salida**: Hora de salida (si aplica)

## Uso

### Acceso a la Vista

1. Iniciar sesión como administrador
2. Navegar a la vista de empleados (`/admin/empleados`)
3. Hacer clic en "Reportes" en la sidebar

### Aplicar Filtros

1. Seleccionar un empleado específico (opcional)
2. Establecer rango de fechas (opcional)
3. Hacer clic en "Filtrar"

### Navegación

- La vista mantiene los filtros aplicados en la URL
- Se puede compartir la URL con filtros específicos
- Los filtros se mantienen al recargar la página

## Datos de Prueba

Para generar datos de prueba, ejecutar:

```bash
python test_reportes.py
```

Este script creará:

- 5 empleados de prueba
- Registros de entrada y salida para los últimos 30 días
- Solo para días laborables (lunes a viernes)
- Horarios realistas de entrada (7:00-9:00) y salida (16:00-19:00)

## Próximas Implementaciones

### Funcionalidad Pendiente

- **Generar Excel**: Botón para exportar reportes a Excel
- **Filtros adicionales**: Por tipo de registro, rango de horas
- **Gráficos**: Visualizaciones de datos
- **Reportes programados**: Generación automática de reportes

### Mejoras Futuras

- **Paginación mejorada**: Para grandes volúmenes de datos
- **Caché de consultas**: Para mejorar el rendimiento
- **Exportación PDF**: Además de Excel
- **Filtros guardados**: Para consultas frecuentes

## Consideraciones Técnicas

### Base de Datos

- Utiliza las tablas existentes: `Registro`, `Persona`, `Empleado`, `TipoRegistro`
- Consultas optimizadas con JOINs
- Filtros aplicados a nivel de base de datos

### Rendimiento

- DataTables para paginación del lado del cliente
- Consultas limitadas por fecha para evitar sobrecarga
- Índices recomendados en `fecha_hora` y `id_persona`

### Seguridad

- Acceso restringido a administradores
- Validación de parámetros de entrada
- Sanitización de datos de salida

## Dependencias

### Frontend

- jQuery 3.6.0
- DataTables 1.11.5
- Bootstrap 5.0.1
- Material Symbols (Google Fonts)

### Backend

- Flask 3.1.2
- SQLAlchemy 3.1.1
- Python 3.13

## Notas de Desarrollo

- El diseño sigue el patrón establecido en la vista de empleados
- Los estilos son consistentes con el sistema de diseño existente
- La funcionalidad es completamente responsive
- El código está documentado y es mantenible
