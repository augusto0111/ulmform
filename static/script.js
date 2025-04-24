document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-cotizacion");
    const resultado = document.getElementById("resultado");
    const visor = document.getElementById("visor3d");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);

            try {
                const response = await fetch("/subir", {
                    method: "POST",
                    body: formData
                });

                const text = await response.text();

                let data;
                try {
                    data = JSON.parse(text);
                } catch {
                    resultado.innerHTML = `<p class="error">❌ Error al procesar cotización (respuesta inválida)</p>`;
                    return;
                }

                if (data.error) {
                    resultado.innerHTML = `<p class="error">❌ ${data.error}</p>`;
                    return;
                }

                resultado.innerHTML = `
                    <p><strong>Archivo:</strong> ${data.archivo}</p>
                    <p><strong>Tecnología 3D:</strong> ${data.tecnologia}</p>
                    <p><strong>Material:</strong> ${data.material}</p>
                    <p><strong>Relleno:</strong> ${data.infill}%</p>
                    <p><strong>Cantidad:</strong> ${data.cantidad}</p>
                    <p><strong>Peso estimado:</strong> ${data.gramos} g</p>
                    <p><strong>Precio unitario:</strong> $${data.precio_unitario}</p>
                    <p><strong>Total:</strong> <span style="color:#FF7A00; font-weight:bold;">$${data.total}</span></p>
                    <div class="botones">
                        <button id="confirmarBtn" class="btn-principal">Confirmar compra</button>
                        <button id="carritoBtn" class="btn-secundario">Agregar al carrito</button>
                    </div>
                `;
document.getElementById("stl-viewer").style.display = "block";

                if (visor) {
                    visor.innerHTML = '';
                    cargarVisorSTL(data.archivo);
                }

                setTimeout(() => configurarBotones(data), 100);
            } catch (error) {
                resultado.innerHTML = `<p class="error">❌ Error al procesar cotización (JS)</p>`;
                console.error("Error JS:", error);
            }
        });
    }

    // Confirmar carrito completo
    const btnCarritoConfirmar = document.getElementById("btnConfirmarCarrito");
    if (btnCarritoConfirmar) {
        btnCarritoConfirmar.addEventListener("click", async () => {
            try {
                const res = await fetch("/confirmar_carrito", { method: "POST" });
                const json = await res.json();
                mostrarToast(json.mensaje || json.error);
                if (json.mensaje) {
                    setTimeout(() => {
                        window.location.href = "/historial";  // Redirecciona
                    }, 2000);
                }
            } catch {
                mostrarToast("❌ Error al confirmar el carrito");
            }
        });
    }


    // Botones para eliminar del carrito
    document.querySelectorAll(".btnEliminarItem").forEach(btn => {
        btn.addEventListener("click", async () => {
            const index = btn.dataset.index;
            const res = await fetch(`/eliminar_item_carrito/${index}`, { method: "POST" });
            const json = await res.json();
            mostrarToast(json.mensaje || json.error);
            if (json.mensaje) {setTimeout(() => window.location.href = "/historial", 2000);
}

            });
        });
    });

function configurarBotones(cotizacion) {
    const confirmarBtn = document.getElementById("confirmarBtn");
    const carritoBtn = document.getElementById("carritoBtn");

    if (confirmarBtn) {
        confirmarBtn.addEventListener("click", async () => {
            const res = await fetch("/confirmar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(cotizacion)
            });
            const json = await res.json();
            mostrarToast(json.mensaje || json.error);
            if (json.mensaje) setTimeout(() => window.location.href = "/historial", 1500);
        });
    }

    if (carritoBtn) {
        carritoBtn.addEventListener("click", async () => {
            const res = await fetch("/agregar_carrito", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(cotizacion)
            });
            const json = await res.json();
            mostrarToast(json.mensaje || json.error);
            if (json.mensaje) setTimeout(() => window.location.href = "/carrito", 1500);
        });
    }
}

function mostrarToast(mensaje) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.className = "toast";
        document.body.appendChild(toast);
    }
    toast.innerText = mensaje;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

function cargarVisorSTL(nombreArchivo) {
    const contenedor = document.getElementById('visor3d');
    contenedor.innerHTML = '';
    document.getElementById("stl-viewer").style.display = "block";

    // Responsive resize
    const width = contenedor.clientWidth;
    const height = contenedor.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    contenedor.appendChild(renderer.domElement);

    const loader = new THREE.STLLoader();
    loader.load('/uploads/' + nombreArchivo, (geometry) => {
        const material = new THREE.MeshNormalMaterial();
        const mesh = new THREE.Mesh(geometry, material);

        geometry.computeBoundingBox();
        const size = geometry.boundingBox.getSize(new THREE.Vector3());

        // Centrar y escalar la pieza
        const center = geometry.boundingBox.getCenter(new THREE.Vector3());
        mesh.geometry.translate(-center.x, -center.y, -center.z);

        scene.add(mesh);
        camera.position.z = Math.max(size.x, size.y, size.z) * 2.5;

        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(1, 1, 1).normalize();
        scene.add(light);

        const animate = function () {
            requestAnimationFrame(animate);
            mesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        };

        animate();
    });

    // Hacerlo responsive cuando se cambia el tamaño de la ventana
    window.addEventListener('resize', () => {
        const newWidth = contenedor.clientWidth;
        const newHeight = contenedor.clientHeight;
        renderer.setSize(newWidth, newHeight);
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
    });
}


