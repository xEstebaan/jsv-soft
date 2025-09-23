function navegarA(url) {
    window.location.href = url;
}

// Función para validar el formato de correo electrónico
function validarEmail(email) {
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return regex.test(email);
}