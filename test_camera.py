"""
Script de diagnóstico para problemas de cámara
"""
import sys
print("Python version:", sys.version)
print("\n" + "="*50)

# Test 1: OpenCV
print("\n1. Probando OpenCV...")
try:
    import cv2
    print(f"✓ OpenCV instalado: {cv2.__version__}")
    
    # Intentar abrir cámara
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Cámara funciona correctamente")
            print(f"  Resolución: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("✗ Cámara abierta pero no puede capturar frames")
        cap.release()
    else:
        print("✗ No se pudo abrir la cámara")
        print("\nIntentando con otros backends...")
        
        # Probar otros backends
        backends = [
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Auto"),
        ]
        
        for backend, name in backends:
            cap = cv2.VideoCapture(0, backend)
            if cap.isOpened():
                print(f"✓ {name} funciona")
                cap.release()
                break
            else:
                print(f"✗ {name} falló")
        
except ImportError as e:
    print(f"✗ Error importando OpenCV: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*50)

# Test 2: pyzbar
print("\n2. Probando pyzbar...")
try:
    from pyzbar import pyzbar
    print("✓ pyzbar importado correctamente")
    
    # Verificar librería zbar
    try:
        import pyzbar.pyzbar as pz
        print("✓ Librería zbar disponible")
    except Exception as e:
        print(f"✗ Error con librería zbar: {e}")
        
except ImportError as e:
    print(f"✗ Error importando pyzbar: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*50)

# Test 3: PySide6
print("\n3. Probando PySide6...")
try:
    from PySide6.QtWidgets import QApplication
    print("✓ PySide6 importado correctamente")
except ImportError as e:
    print(f"✗ Error importando PySide6: {e}")

print("\n" + "="*50)
print("\n✓ Diagnóstico completo")
print("\nSi ves errores arriba, esas son las librerías que necesitas reparar.")




