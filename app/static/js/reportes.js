// Funcionalidad específica para la vista de reportes

document.addEventListener("DOMContentLoaded", function () {
  // Configuración global de DataTables para traducción al español
  $.extend(true, $.fn.dataTable.defaults, {
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
    },
  });

  // Verificar si existe la tabla de registros
  const registrosTable = document.getElementById("registrosTable");
  if (registrosTable) {
    if (!$.fn.dataTable.isDataTable("#registrosTable")) {
      $("#registrosTable").DataTable({
        language: {
          url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
          search: "Buscar registros: ",
          lengthMenu: "Mostrar _MENU_ registros",
          info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
          infoEmpty: "Mostrando 0 a 0 de 0 registros",
          infoFiltered: "(filtrado de _MAX_ registros totales)",
          paginate: {
            first: "Primero",
            last: "Último",
            next: "Siguiente",
            previous: "Anterior",
          },
          zeroRecords: "No se encontraron registros coincidentes",
        },
        responsive: true,
        lengthMenu: [
          [10, 25, 50, 100, -1],
          [10, 25, 50, 100, "Todos"],
        ],
        pageLength: 25,
        order: [[1, "desc"]], // Ordenar por fecha descendente por defecto
        columnDefs: [
          { targets: [2, 3], orderable: false }, // Deshabilitar ordenamiento en columnas de hora
        ],
      });
    }
  }

  // Manejar el botón de generar Excel
  const generarExcelBtn = document.getElementById("generar-excel");
  if (generarExcelBtn) {
    generarExcelBtn.addEventListener("click", function () {
      // Por ahora solo mostrar un mensaje, la funcionalidad se implementará después
      alert("La funcionalidad de generar Excel se implementará próximamente.");
    });
  }

  // Validación de fechas en el formulario de filtros
  const fechaInicio = document.getElementById("fecha_inicio");
  const fechaFin = document.getElementById("fecha_fin");

  if (fechaInicio && fechaFin) {
    // Validar que la fecha de inicio no sea mayor que la fecha de fin
    function validarFechas() {
      const inicio = new Date(fechaInicio.value);
      const fin = new Date(fechaFin.value);

      if (fechaInicio.value && fechaFin.value && inicio > fin) {
        fechaFin.setCustomValidity(
          "La fecha de fin debe ser mayor o igual a la fecha de inicio"
        );
        fechaFin.reportValidity();
      } else {
        fechaFin.setCustomValidity("");
      }
    }

    fechaInicio.addEventListener("change", validarFechas);
    fechaFin.addEventListener("change", validarFechas);
  }

  // Funcionalidad del campo de búsqueda por nombre
  const busquedaNombre = document.getElementById("busqueda_nombre");
  if (busquedaNombre) {
    // Limpiar búsqueda con botón X
    function crearBotonLimpiar() {
      const botonLimpiar = document.createElement("button");
      botonLimpiar.type = "button";
      botonLimpiar.innerHTML =
        '<span class="material-symbols-outlined">close</span>';
      botonLimpiar.className = "search-clear-btn";
      botonLimpiar.style.cssText = `
        position: absolute;
        right: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: var(--text-light);
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 50%;
        display: none;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
      `;

      botonLimpiar.addEventListener("click", function () {
        busquedaNombre.value = "";
        busquedaNombre.focus();
        botonLimpiar.style.display = "none";
        // Disparar evento de cambio para actualizar la búsqueda
        busquedaNombre.dispatchEvent(new Event("input"));
      });

      return botonLimpiar;
    }

    const botonLimpiar = crearBotonLimpiar();
    const searchContainer = busquedaNombre.parentElement;
    searchContainer.appendChild(botonLimpiar);

    // Mostrar/ocultar botón de limpiar
    busquedaNombre.addEventListener("input", function () {
      if (this.value.length > 0) {
        botonLimpiar.style.display = "flex";
      } else {
        botonLimpiar.style.display = "none";
      }
    });

    // Búsqueda en tiempo real (opcional - se puede habilitar más tarde)
    // busquedaNombre.addEventListener("input", function() {
    //   // Aquí se podría implementar búsqueda en tiempo real
    //   // Por ahora se mantiene la búsqueda al enviar el formulario
    // });
  }

  // Establecer fecha de hoy como valor por defecto para fecha de fin si no está establecida
  if (fechaFin && !fechaFin.value) {
    const hoy = new Date();
    const fechaHoy = hoy.toISOString().split("T")[0];
    fechaFin.value = fechaHoy;
  }

  // Establecer fecha de hace 30 días como valor por defecto para fecha de inicio si no está establecida
  if (fechaInicio && !fechaInicio.value) {
    const hace30Dias = new Date();
    hace30Dias.setDate(hace30Dias.getDate() - 30);
    const fechaHace30Dias = hace30Dias.toISOString().split("T")[0];
    fechaInicio.value = fechaHace30Dias;
  }

  // Traducir elementos de DataTables después de que se cargue
  setTimeout(function () {
    const showEntries = document.querySelector("div.dataTables_length label");
    if (showEntries && showEntries.textContent.includes("Show")) {
      showEntries.innerHTML = showEntries.innerHTML
        .replace("Show", "Mostrar")
        .replace("entries", "registros");
    }

    const info = document.querySelector("div.dataTables_info");
    if (info && info.textContent.includes("Showing")) {
      info.textContent = info.textContent
        .replace("Showing", "Mostrando")
        .replace("to", "a")
        .replace("of", "de")
        .replace("entries", "registros");
    }

    const prev = document.querySelector("a.paginate_button.previous");
    const next = document.querySelector("a.paginate_button.next");
    if (prev && prev.textContent === "Previous") {
      prev.textContent = "Anterior";
    }
    if (next && next.textContent === "Next") {
      next.textContent = "Siguiente";
    }
  }, 100);
});
