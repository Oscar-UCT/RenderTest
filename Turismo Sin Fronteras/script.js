const buttonComidas = document.getElementById("comida-button");
const buttonAlojamiento = document.getElementById("alojamiento-button");
const buttonExcursiones = document.getElementById("excursiones-button");

const servicioComidas = document.getElementById("servicio-comida");
const servicioAlojamiento = document.getElementById("servicio-alojamiento");
const servicioExcursiones = document.getElementById("servicio-excursiones");


buttonComidas.addEventListener('click', () => {
    servicioAlojamiento.style.display = 'none';
    servicioExcursiones.style.display = 'none';
    servicioComidas.style.display = 'flex';
})

buttonAlojamiento.addEventListener('click', () => {
    servicioComidas.style.display = 'none';
    servicioExcursiones.style.display = 'none';
    servicioAlojamiento.style.display = 'flex';
})

buttonExcursiones.addEventListener('click', () => {

    servicioComidas.style.display = 'none';
    servicioAlojamiento.style.display = 'none';
    servicioExcursiones.style.display = 'flex';
})

const backgroundWindow = document.getElementById("cupon-fixed");
const acceptButton = document.getElementById("aceptar-button");

acceptButton.onclick = () => {
    backgroundWindow.style.display = "none";
};

window.onclick = (event) => {
    if (event.target === backgroundWindow) {
        backgroundWindow.style.display = "none";
    }
    else if (event.target === reseñaWindow) {
        reseñaWindow.style.display = "none";
    }
};

const enviarReseña = document.getElementById("enviar-button");

enviarReseña.onclick = () => {
    reseñaWindow.style.display = "none";
};

const comidaID1 = document.getElementById("comida1");
const comidaID2 = document.getElementById("comida2");
const comidaID3 = document.getElementById("comida3");
let seleccionComida;

comidaID1.onclick = () => {
    console.log("Debug");
    seleccionComida = "Asado Familiar 8P";
    mostrarReseñaWindow(seleccionComida);
};

comidaID2.onclick = () => {
    console.log("Debug");

    seleccionComida = "Completos 2P";
    mostrarReseñaWindow(seleccionComida);
};

comidaID3.onclick = () => {
    console.log("Debug");

    seleccionComida = "Tacos 2P";
    mostrarReseñaWindow(seleccionComida);
};

const reseñaWindow = document.getElementById("reseña-fixed");
const reseñaContent = document.getElementById("reseña-content");
const comidaSeleccionadaTexto = document.getElementById("comidaSeleccion");


function mostrarReseñaWindow(comida) {
    reseñaWindow.style.display = "flex";
    reseñaContent.style.display = "flex";
    reseñaContent.style.opacity = "1";

    comidaSeleccionadaTexto.textContent = comida;
};

const estrellas = document.querySelectorAll(".stars .star");

estrellas.forEach((star, index) => {
    star.addEventListener("click", () => {
        estrellas.forEach((img, i) => {
            img.src = i <= index ? "./media/star(1).png" : "./media/star.png"; // Update paths to your images
        });
    });
});