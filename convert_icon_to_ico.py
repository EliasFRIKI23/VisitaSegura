"""
Script para convertir Main_logo.png a Main_logo.ico
Este script debe ejecutarse antes de generar el EXE para tener el icono correcto.
"""
from PIL import Image
from pathlib import Path

def convert_png_to_ico():
    """Convierte Main_logo.png a Main_logo.ico"""
    input_path = Path('core/ui/icons/Main_logo.png')
    output_path = Path('core/ui/icons/Main_logo.ico')
    
    if not input_path.exists():
        print(f"❌ Error: No se encontró {input_path}")
        print("   Asegúrate de que el archivo Main_logo.png existe en core/ui/icons/")
        return False
    
    try:
        # Abrir la imagen PNG
        img = Image.open(input_path)
        
        # Convertir a RGB si es necesario (ICO no soporta RGBA directamente)
        if img.mode == 'RGBA':
            # Crear una imagen RGB con fondo blanco
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Usar canal alpha como máscara
            img = rgb_img
        
        # Guardar como ICO con múltiples tamaños (Windows requiere esto)
        # Crear una lista de tamaños estándar para iconos de Windows
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Asegurarnos de que la imagen sea cuadrada
        size = max(img.size)
        square_img = Image.new('RGB', (size, size), (255, 255, 255))
        offset = ((size - img.size[0]) // 2, (size - img.size[1]) // 2)
        square_img.paste(img, offset)
        
        # Crear lista de iconos en diferentes tamaños
        ico_sizes = []
        for s in sizes:
            resized = square_img.resize(s, Image.Resampling.LANCZOS)
            ico_sizes.append(resized)
        
        # Guardar como ICO
        square_img.save(output_path, format='ICO', sizes=[(s.width, s.height) for s in ico_sizes])
        
        print(f"✅ Icono convertido exitosamente!")
        print(f"   Entrada: {input_path}")
        print(f"   Salida:  {output_path}")
        print(f"   Tamaños: {', '.join([f'{s}x{s}' for s in [16, 32, 48, 64, 128, 256]])}")
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir el icono: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Convirtiendo Main_logo.png a Main_logo.ico...")
    success = convert_png_to_ico()
    if success:
        print("\n✨ ¡Listo! Ahora puedes generar el EXE con el icono.")
    else:
        print("\n⚠️ Hubo un problema. Revisa los errores arriba.")

