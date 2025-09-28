document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("primary-navigation");

  if (!toggle || !nav) return;

  function setExpanded(isOpen) {
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute("aria-label", isOpen ? "Cerrar menú" : "Abrir menú");
    if (isOpen) {
      nav.classList.add("is-open");
    } else {
      nav.classList.remove("is-open");
    }
  }

  toggle.addEventListener("click", function () {
    var isOpen = nav.classList.contains("is-open");
    setExpanded(!isOpen);
  });

  // Close nav when clicking outside on small screens
  document.addEventListener("click", function (e) {
    var isClickInside = nav.contains(e.target) || toggle.contains(e.target);
    if (!isClickInside && nav.classList.contains("is-open")) {
      setExpanded(false);
    }
  });

  // Close on escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      setExpanded(false);
      toggle.focus();
    }
  });
});





