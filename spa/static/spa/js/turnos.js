document.addEventListener('DOMContentLoaded', function () {
    const fecha = document.querySelector('input[type="date"]');

    if (fecha) {
        const hoy = new Date().toISOString().split('T')[0];
        fecha.min = hoy;
    }
});