(function () {
  document.addEventListener('DOMContentLoaded', function() {
    const pinEl = document.getElementById("pin");
    
    // Crear contenedor para mensajes flash si no existe
    let flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
      flashContainer = document.createElement("div");
      flashContainer.className = "flash-messages";
      try {
        const form = document.querySelector("form");
        if (form && form.parentNode) {
          form.parentNode.insertBefore(flashContainer, form);
        }
      } catch (e) {
        console.warn("No se pudo insertar el contenedor flash:", e);
      }
    }

  // Función para formatear números
  function pad(n) {
    return n.toString().padStart(2, "0");
  }

  function showFlashMessage(message, type = "info") {
    if (!flashContainer) return;
    
    // Eliminar mensajes anteriores
    while (flashContainer.firstChild) {
      flashContainer.removeChild(flashContainer.firstChild);
    }

    const messageEl = document.createElement("div");
    messageEl.className = `flash-message ${type}`;
    messageEl.textContent = message;
    flashContainer.appendChild(messageEl);

    // Auto-eliminar después de 5 segundos los mensajes
    setTimeout(() => {
      messageEl.style.opacity = "0";
      messageEl.style.transition = "opacity 0.5s";
      setTimeout(() => messageEl.remove(), 500);
    }, 5000);
  }

    // Manejar la validación del formulario
    if (pinEl) {
      const form = document.querySelector("form");
      if (form) {
        form.addEventListener("submit", function(e) {
          if (!pinEl.value) {
            e.preventDefault();
            showFlashMessage("Por favor ingrese su PIN", "error");
          }
        });
      }
    }

    // Reloj digital y fecha actual
    (function initClock() {
      const clockEl = document.getElementById('clock') || document.getElementById('relojDigital');
      const dateEl = document.getElementById('current-date');

      if (!clockEl && !dateEl) return;

      let baseMs = null;
      if (typeof window.SERVER_NOW_MS !== 'undefined' && !Number.isNaN(Number(window.SERVER_NOW_MS))) {
        baseMs = Number(window.SERVER_NOW_MS);
      }

      function pad(n) { return String(n).padStart(2, '0'); }

      function update(now) {
        const d = new Date(now);
        const hh = pad(d.getHours());
        const mm = pad(d.getMinutes());
        const ss = pad(d.getSeconds());

        if (clockEl) clockEl.textContent = `${hh}:${mm}:${ss}`;

        if (dateEl) {
          // Formatear fecha como "DD-Mes-YYYY" en español
          const day = pad(d.getDate());
          const monthNames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
          const month = monthNames[d.getMonth()];
          const year = d.getFullYear();
          dateEl.textContent = `${day}-${month}-${year}`;
        }
      }

      // Inicializar y actualizar cada segundo
      if (baseMs) {
        const offset = Date.now() - baseMs;
        update(baseMs + offset);
        setInterval(() => update(baseMs + (Date.now() - offset)), 1000);
      } else {
        update(Date.now());
        setInterval(() => update(Date.now()), 1000);
      }

    })();
  });
})();