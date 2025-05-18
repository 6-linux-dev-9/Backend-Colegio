from PIL import Image
import io

UBICACION_PERFIL_USUARIO = "profile_users"
UBICACION_PRODUCTOS = "productos"

def comprimir_imagen(archivo, calidad=85, max_ancho=800):
    imagen = Image.open(archivo)

    # Convertir a RGB si está en modo con canal alfa
    if imagen.mode in ("RGBA", "P"):
        imagen = imagen.convert("RGB")

    # Redimensionar si es más ancha que el máximo permitido
    if imagen.width > max_ancho:
        proporcion = max_ancho / float(imagen.width)
        alto = int((float(imagen.height) * float(proporcion)))
        imagen = imagen.resize((max_ancho, alto), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    imagen.save(buffer, format="JPEG", quality=calidad, optimize=True)
    buffer.seek(0)
    return buffer


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def extension_permitida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
