function navegarA(url) {
    window.location.href = url;
}

// Función para validar el formato de correo electrónico
function validarEmail(email) {
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return regex.test(email);
}

document.addEventListener('DOMContentLoaded', function() {
    // Verificar si existe la tabla de empleados
    const empleadosTable = document.getElementById('empleadosTable');
    if (empleadosTable) {
        // Comprobar si DataTables ya está inicializado
        if (!$.fn.dataTable.isDataTable('#empleadosTable')) {
            // Inicializar DataTable con opciones
            $('#empleadosTable').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json',
                    search: "Buscar empleados por nombre, cédula o rol..."
                },
                responsive: true,
                lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"]],
                pageLength: 10,
                order: [[0, 'asc']],
                columnDefs: [
                    { targets: -1, orderable: false, searchable: false }
                ]
            });
        }
        
        document.querySelectorAll('.btn-ver').forEach(btn => {
            btn.addEventListener('click', function() {
                const empleadoId = this.getAttribute('data-id');
                const row = this.closest('tr');
                const nombre = row.querySelector('.name-cell').textContent.trim();
                console.log(`Ver detalles del empleado ID: ${empleadoId}, Nombre: ${nombre}`);
            });
        });

        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const empleadoId = this.getAttribute('data-id');
                const row = this.closest('tr');
                const nombre = row.querySelector('.name-cell').textContent.trim();
                console.log(`Editar empleado ID: ${empleadoId}, Nombre: ${nombre}`);
            });
        });
        
        document.querySelectorAll('.btn-inactivar').forEach(btn => {
            btn.addEventListener('click', function() {
                const empleadoId = this.getAttribute('data-id');
                const row = this.closest('tr');
                const nombre = row.querySelector('.name-cell').textContent.trim();
                console.log(`Inactivar empleado ID: ${empleadoId}, Nombre: ${nombre}`);
            });
        });
    }
});