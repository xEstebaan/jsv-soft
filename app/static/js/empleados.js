function navegarA(url) {
    window.location.href = url;
}

// Función para validar el formato de correo electrónico
function validarEmail(email) {
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return regex.test(email);
}

document.addEventListener('DOMContentLoaded', function() {
    // Configuración global de DataTables para traducción al español
    $.extend(true, $.fn.dataTable.defaults, {
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
        }
    });

    // Verificar si existe la tabla de empleados
    const empleadosTable = document.getElementById('empleadosTable');
    if (empleadosTable) {
        if (!$.fn.dataTable.isDataTable('#empleadosTable')) {
            $('#empleadosTable').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json',
                    search: "Buscar empleados: ",
                    lengthMenu: "Mostrar _MENU_ registros",
                    info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                    infoEmpty: "Mostrando 0 a 0 de 0 registros",
                    infoFiltered: "(filtrado de _MAX_ registros totales)",
                    paginate: {
                        first: "Primero",
                        last: "Último",
                        next: "Siguiente",
                        previous: "Anterior"
                    },
                    zeroRecords: "No se encontraron registros coincidentes"
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
                window.location.href = `/admin/empleados/ver/${empleadoId}`;
            });
        });

        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const empleadoId = this.getAttribute('data-id');
                window.location.href = `/admin/empleados/editar/${empleadoId}`;
            });
        });
        
        document.querySelectorAll('.btn-inactivar').forEach(btn => {
            btn.addEventListener('click', function() {
                const empleadoId = this.getAttribute('data-id');
                const row = this.closest('tr');
                const nombre = row.querySelector('.name-cell').textContent.trim();
                
                if (confirm(`¿Está seguro que desea inactivar al empleado: ${nombre}?`)) {

                }
            });
        });
    }
});