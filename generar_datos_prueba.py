"""
Script para generar datos de prueba de visitantes para VisitaSegura.

Este script genera:
- 20 visitantes por cada sector (Financiamiento, CITT, Auditorio, Administración)
- Total: 80 visitantes
- Todos con el RUT de prueba: 11.111.111-1
- Nombres diferentes y realistas
- Distribuidos durante diciembre 2024 (diferentes días)
- Respetando la regla: si un RUT está dentro, no puede reingresar hasta salir
- Guarda en MongoDB (nube) y archivo JSON (local)

Uso:
    python generar_datos_prueba.py
"""

import random
from datetime import datetime, timedelta
from typing import List
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.visitors.models import Visitor
from core.visitors.storage import JsonVisitorStorage, MongoVisitorStorage
from database import connect_db, get_visitantes_collection


# RUT de prueba único
RUT_PRUEBA = "11.111.111-1"

# Sectores disponibles
SECTORES = ["Financiamiento", "CITT", "Auditorio", "Administración"]

# Nombres chilenos realistas para generar datos variados
NOMBRES = [
    "Juan Pérez González",
    "María Rodríguez Silva",
    "Carlos López Martínez",
    "Ana Fernández Torres",
    "Pedro González Ramírez",
    "Laura Martínez Sánchez",
    "Diego Herrera Muñoz",
    "Sofía Díaz Vargas",
    "Andrés Morales Castro",
    "Valentina Soto Rojas",
    "Sebastián Vega Campos",
    "Camila Flores Núñez",
    "Fernando Guzmán Moreno",
    "Isidora Jiménez Álvarez",
    "Nicolás Cruz Salazar",
    "Francisca Espinoza Medina",
    "Matías Contreras Fuentes",
    "Amanda Ruiz Cortés",
    "Benjamín Vargas Ríos",
    "Javiera Muñoz Valdés",
    "Tomás Ortega Paredes",
    "Catalina Navarro Soto",
    "Ignacio Silva Castro",
    "Antonia Valenzuela Reyes",
    "Maximiliano Torres Salas",
    "Constanza Méndez Peña",
    "Joaquín Ramírez Campos",
    "Trinidad Morales Vásquez",
    "Felipe Ávila Rojas",
    "Rocío Figueroa Carrasco",
    "Gabriel Pino Cáceres",
    "Dominga Segura Pizarro",
    "Vicente Tapia Araya",
    "Macarena Riquelme Orellana",
    "Rodrigo Salgado Sepúlveda",
    "Natalia Mendoza Correa",
    "Fabián Zambrano Vergara",
    "Isabella Cáceres Hernández",
    "Emiliano Venegas Bravo",
    "Florencia Araya Sanhueza",
    "Cristóbal Troncoso Barrientos",
    "Rafaela Campos Molina",
    "Gonzalo Pizarro Zamora",
    "Josefa Leiva Ulloa",
    "Bastián Rojas Bustamante",
    "Emma Valdés Jara",
    "Javier Saavedra Farías",
    "Antonella Quintana Godoy",
    "Federico Urbina Quiroz",
    "María Jesús Zapata Neira",
    "Agustín Durán Retamal",
    "Amparo Vilches Cuevas",
    "Bruno Alarcón Yáñez",
    "Gabriela Quiroz Vidal",
    "Alonso Parra Valenzuela",
    "Amanda Vergara Parra",
    "Simón Cisterna Aguilera",
    "Josefina Rivas Ibáñez",
    "Leonardo Acevedo Garrido",
    "Paula Escobar Urrutia",
    "Emilio Arancibia Bustos",
    "Daniela Henríquez Mansilla",
    "Renato Orellana Pérez",
    "Renata Espinoza Ponce",
    "Gaspar Moraga Araya",
    "María Paz Bustamante Concha",
    "Bautista Bravo Gutiérrez",
    "Catalina Jara Bustos",
    "Franco Aravena San Martín",
    "Fernanda Osorio Ríos",
    "Martín Correa González",
    "Paz Miranda Escalona",
    "Lucas Poblete Cáceres",
    "Soledad Oyarzún Riveros",
    "Santiago Guerrero Salazar",
    "Flora Ramírez Núñez",
    "Luciano Farías Vergara",
    "Carla Vidal Paredes",
    "Mateo Medina Quiroz",
    "Elisa Cortés Vásquez",
    "Alfredo Barraza Silva",
    "Maite Gálvez Riquelme",
    "Arturo Acevedo Muñoz",
    "Sofía Valdés Carrasco",
    "Dante Salinas Hidalgo",
]

# Acompañantes realistas
ACOMPAÑANTES = [
    "María González",
    "Pedro Martínez",
    "Ana López",
    "Carlos Silva",
    "Laura Rodríguez",
    "Diego Fernández",
    "Sofía Herrera",
    "Andrés Díaz",
    "Valentina Morales",
    "Sebastián Vega",
    "Camila Flores",
    "Fernando Guzmán",
    "Isidora Jiménez",
    "Nicolás Cruz",
    "Francisca Espinoza",
    "Matías Contreras",
    "Amanda Ruiz",
    "Benjamín Vargas",
    "Javiera Muñoz",
    "Tomás Ortega",
]

# Mes objetivo: Diciembre 2024
MES_OBJETIVO = 12
AÑO_OBJETIVO = 2024


def generar_fecha_aleatoria(mes: int, año: int, dia_min: int = 1, dia_max: int = 31) -> datetime:
    """Genera una fecha aleatoria durante el mes especificado."""
    dia = random.randint(dia_min, dia_max)
    
    # Validar que el día existe en el mes
    try:
        fecha = datetime(año, mes, dia)
    except ValueError:
        # Si el día no existe (ej: 31 de febrero), usar el último día válido
        dia_max_valido = 31
        while dia_max_valido > 0:
            try:
                fecha = datetime(año, mes, dia_max_valido)
                break
            except ValueError:
                dia_max_valido -= 1
        else:
            fecha = datetime(año, mes, 1)
    
    # Generar hora aleatoria entre 8:00 y 18:00
    hora = random.randint(8, 18)
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    
    return fecha.replace(hour=hora, minute=minuto, second=segundo)


def generar_fecha_salida(fecha_ingreso: datetime) -> datetime:
    """
    Genera una fecha de salida después de la fecha de ingreso.
    Crea estadías variadas y realistas:
    - Entre 30 minutos y 5 horas de duración
    - Con minutos aleatorios para mayor realismo
    """
    # Duración en minutos: entre 30 min (0.5h) y 300 min (5h)
    # Distribución más realista: más probabilidad de visitas cortas
    duraciones_minutos = [
        30, 45, 60, 75, 90,  # 30min - 1.5h (visitas cortas)
        120, 150, 180,       # 2h - 3h (visitas medianas)
        240, 300             # 4h - 5h (visitas largas)
    ]
    
    minutos_duracion = random.choice(duraciones_minutos)
    
    # Agregar variación adicional de minutos (0-30 min) para mayor realismo
    minutos_extra = random.randint(0, 30)
    minutos_totales = minutos_duracion + minutos_extra
    
    return fecha_ingreso + timedelta(minutes=minutos_totales)


def generar_visitantes_por_sector(
    sector: str,
    cantidad: int,
    rut: str,
    nombres_disponibles: List[str],
    acompañantes_disponibles: List[str],
    mes: int,
    año: int
) -> List[Visitor]:
    """
    Genera visitantes para un sector específico.
    
    Respetando la regla: si un RUT está dentro, no puede reingresar hasta salir.
    Generamos visitas históricas donde solo la más reciente puede estar "Dentro".
    """
    visitantes = []
    nombres_usados = nombres_disponibles.copy()
    random.shuffle(nombres_usados)
    
    # Generar fechas con distribución optimizada para el gráfico de "últimos 7 días":
    # - Asegurar visitas visibles en días 01, 02, 03, 04 de diciembre
    # - Distribuir el resto durante todo el mes para historial completo
    fechas_ingreso = []
    
    # Días prioritarios para el gráfico (01-04 de diciembre)
    dias_grafico = [1, 2, 3, 4]
    
    # 50% de las visitas en los días del gráfico (distribuidas equitativamente)
    visitas_grafico = cantidad // 2
    visitas_por_dia_grafico = visitas_grafico // len(dias_grafico)
    
    # Generar visitas en días del gráfico
    for dia in dias_grafico:
        for _ in range(visitas_por_dia_grafico):
            fecha = generar_fecha_aleatoria(mes, año, dia, dia)
            fechas_ingreso.append(fecha)
    
    # Si quedan visitas por asignar en días del gráfico, distribuirlas aleatoriamente
    visitas_restantes_grafico = visitas_grafico - (visitas_por_dia_grafico * len(dias_grafico))
    for _ in range(visitas_restantes_grafico):
        dia = random.choice(dias_grafico)
        fecha = generar_fecha_aleatoria(mes, año, dia, dia)
        fechas_ingreso.append(fecha)
    
    # El resto de visitas (50%) distribuidas en todo el mes para historial completo
    cantidad_resto = cantidad - len(fechas_ingreso)
    
    # Distribución del resto: 30% en últimos días de noviembre + 70% en diciembre
    for i in range(cantidad_resto):
        if i < cantidad_resto * 0.3:  # 30% en últimos días de noviembre
            dia = random.randint(27, 30)
            fecha = generar_fecha_aleatoria(11, año, dia, dia)
        else:  # 70% distribuido en diciembre
            # Priorizar primeros días pero también distribuir en todo el mes
            if random.random() < 0.4:
                dia = random.randint(5, 15)  # Días 05-15
            else:
                dia = random.randint(1, 31)  # Todo el mes
            
            fecha = generar_fecha_aleatoria(mes, año, dia, dia)
        
        fechas_ingreso.append(fecha)
    
    # Mezclar las fechas antes de ordenar cronológicamente
    random.shuffle(fechas_ingreso)
    
    # Ordenar fechas cronológicamente (la más antigua primero)
    fechas_ingreso.sort()
    
    for i, fecha_ingreso in enumerate(fechas_ingreso):
        # Seleccionar nombre (ciclar si se acaban)
        nombre = nombres_usados[i % len(nombres_usados)]
        
        # Seleccionar acompañante aleatorio
        acompañante = random.choice(acompañantes_disponibles)
        
        # Solo el visitante más reciente (último) puede estar "Dentro"
        # Todos los anteriores deben estar "Fuera" con fecha de salida
        es_el_ultimo = (i == len(fechas_ingreso) - 1)
        
        if es_el_ultimo:
            # Solo el último puede estar dentro (pero le damos 50% probabilidad)
            estado = "Dentro" if random.random() < 0.5 else "Fuera"
            fecha_salida = None if estado == "Dentro" else generar_fecha_salida(fecha_ingreso)
        else:
            # Todos los anteriores deben estar fuera
            estado = "Fuera"
            fecha_salida = generar_fecha_salida(fecha_ingreso)
            
            # Asegurar que la salida sea antes del siguiente ingreso (si hay siguiente)
            if i < len(fechas_ingreso) - 1:
                siguiente_ingreso = fechas_ingreso[i + 1]
                if fecha_salida >= siguiente_ingreso:
                    # La salida debe ser al menos 1 minuto antes del siguiente ingreso
                    fecha_salida = siguiente_ingreso - timedelta(minutes=1)
        
        # Crear visitante con fecha específica
        visitante = Visitor(
            rut=rut,
            nombre_completo=nombre,
            acompañante=acompañante,
            sector=sector,
            estado=estado,
            usuario_registrador="Sistema - Datos de Prueba"
        )
        
        # Sobrescribir fecha de ingreso con la fecha generada
        visitante.fecha_ingreso = fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S")
        
        if fecha_salida:
            visitante.fecha_salida = fecha_salida.strftime("%Y-%m-%d %H:%M:%S")
        
        visitantes.append(visitante)
    
    return visitantes


def guardar_en_mongodb(visitantes: List[Visitor]) -> bool:
    """Guarda los visitantes en MongoDB."""
    try:
        print("\n📡 Intentando guardar en MongoDB...")
        
        if not connect_db():
            print("⚠️ No se pudo conectar a MongoDB. Saltando guardado en nube.")
            return False
        
        collection = get_visitantes_collection()
        if collection is None:
            print("⚠️ No se pudo obtener la colección de MongoDB. Saltando guardado en nube.")
            return False
        
        # Borrar visitantes existentes del RUT de prueba (para evitar duplicados)
        rut_prueba = visitantes[0].rut if visitantes else None
        if rut_prueba:
            eliminados = collection.delete_many({"rut": rut_prueba})
            if eliminados.deleted_count > 0:
                print(f"   ℹ️  Eliminados {eliminados.deleted_count} visitantes existentes con RUT {rut_prueba}")
        
        # Convertir visitantes a diccionarios
        documentos = [v.to_dict() for v in visitantes]
        
        # Insertar en MongoDB
        if documentos:
            collection.insert_many(documentos)
            print(f"✅ Guardados {len(visitantes)} visitantes en MongoDB (nube)")
        else:
            print("⚠️ No hay visitantes para guardar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar en MongoDB: {e}")
        return False


def guardar_en_json(visitantes: List[Visitor], archivo: str = "visitors.json") -> bool:
    """Guarda los visitantes en archivo JSON local."""
    try:
        print(f"\n💾 Guardando en archivo JSON local ({archivo})...")
        
        storage = JsonVisitorStorage(archivo)
        if storage.save(visitantes):
            print(f"✅ Guardados {len(visitantes)} visitantes en archivo JSON local")
            return True
        else:
            print("❌ Error al guardar en archivo JSON")
            return False
            
    except Exception as e:
        print(f"❌ Error al guardar en JSON: {e}")
        return False


def normalizar_estados_visitantes(visitantes: List[Visitor], rut: str) -> None:
    """
    Normaliza los estados de los visitantes para respetar la regla:
    Solo un visitante con el mismo RUT puede estar 'Dentro' a la vez.
    
    Ordena todos los visitantes cronológicamente y asegura que solo el más reciente
    (si existe) pueda estar 'Dentro'. Los demás deben estar 'Fuera' con fecha de salida.
    """
    # Filtrar solo los visitantes con el RUT especificado
    visitantes_rut = [v for v in visitantes if v.rut == rut]
    
    if not visitantes_rut:
        return
    
    # Ordenar por fecha de ingreso (más antiguo primero)
    visitantes_rut.sort(key=lambda v: v.fecha_ingreso)
    
    # Encontrar el visitante más reciente
    visitante_mas_reciente = visitantes_rut[-1]
    
    # Marcar todos como "Fuera" primero
    for visitante in visitantes_rut:
        if visitante.estado == "Dentro":
            visitante.estado = "Fuera"
            
            # Si no tiene fecha de salida, generarla
            if not visitante.fecha_salida:
                fecha_ingreso = datetime.strptime(visitante.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
                fecha_salida = generar_fecha_salida(fecha_ingreso)
                
                # Asegurar que la salida sea antes del siguiente ingreso (si existe)
                idx = visitantes_rut.index(visitante)
                if idx < len(visitantes_rut) - 1:
                    siguiente = visitantes_rut[idx + 1]
                    siguiente_ingreso = datetime.strptime(siguiente.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
                    if fecha_salida >= siguiente_ingreso:
                        fecha_salida = siguiente_ingreso - timedelta(minutes=1)
                
                visitante.fecha_salida = fecha_salida.strftime("%Y-%m-%d %H:%M:%S")
    
    # Solo el más reciente puede estar "Dentro" (50% probabilidad para variedad)
    if random.random() < 0.5:
        visitante_mas_reciente.estado = "Dentro"
        visitante_mas_reciente.fecha_salida = None
    else:
        # Si decidimos que el más reciente también esté fuera, asegurar su salida
        visitante_mas_reciente.estado = "Fuera"
        if not visitante_mas_reciente.fecha_salida:
            fecha_ingreso = datetime.strptime(visitante_mas_reciente.fecha_ingreso, "%Y-%m-%d %H:%M:%S")
            fecha_salida = generar_fecha_salida(fecha_ingreso)
            visitante_mas_reciente.fecha_salida = fecha_salida.strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Función principal que genera y guarda los datos de prueba."""
    print("=" * 60)
    print("🚀 GENERADOR DE DATOS DE PRUEBA - VISITASEGURA")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Este script generará nuevos datos de prueba.")
    print("   Si ya existen visitantes en MongoDB, serán reemplazados.")
    print("   El archivo JSON local también será reemplazado.\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada.")
        return
    
    print(f"\n📋 Configuración:")
    print(f"   - RUT de prueba: {RUT_PRUEBA}")
    print(f"   - Visitantes por sector: 20")
    print(f"   - Sectores: {', '.join(SECTORES)}")
    print(f"   - Total de visitantes: {20 * len(SECTORES)}")
    print(f"   - Mes objetivo: Diciembre {AÑO_OBJETIVO}")
    print()
    
    todos_visitantes = []
    
    # Generar visitantes para cada sector
    nombres_restantes = NOMBRES.copy()
    random.shuffle(nombres_restantes)
    
    for sector in SECTORES:
        print(f"📦 Generando 20 visitantes para sector: {sector}...")
        
        visitantes_sector = generar_visitantes_por_sector(
            sector=sector,
            cantidad=20,
            rut=RUT_PRUEBA,
            nombres_disponibles=nombres_restantes,
            acompañantes_disponibles=ACOMPAÑANTES,
            mes=MES_OBJETIVO,
            año=AÑO_OBJETIVO
        )
        
        todos_visitantes.extend(visitantes_sector)
        
        # Rotar nombres para que cada sector tenga nombres diferentes
        nombres_restantes = nombres_restantes[20:] + nombres_restantes[:20]
        
        dentro = sum(1 for v in visitantes_sector if v.estado == "Dentro")
        fuera = sum(1 for v in visitantes_sector if v.estado == "Fuera")
        print(f"   ✅ Generados: {len(visitantes_sector)} visitantes ({dentro} dentro, {fuera} fuera)")
    
    # Normalizar estados para respetar la regla: solo un RUT puede estar "Dentro" a la vez
    print(f"\n🔧 Normalizando estados (respetando regla de RUT único 'Dentro')...")
    normalizar_estados_visitantes(todos_visitantes, RUT_PRUEBA)
    
    print(f"\n📊 Resumen total:")
    print(f"   - Total de visitantes generados: {len(todos_visitantes)}")
    dentro_total = sum(1 for v in todos_visitantes if v.estado == 'Dentro')
    fuera_total = sum(1 for v in todos_visitantes if v.estado == 'Fuera')
    print(f"   - Dentro: {dentro_total}")
    print(f"   - Fuera: {fuera_total}")
    
    # Guardar en ambos lugares
    print("\n" + "=" * 60)
    print("💾 GUARDANDO DATOS")
    print("=" * 60)
    
    guardado_mongo = guardar_en_mongodb(todos_visitantes)
    guardado_json = guardar_en_json(todos_visitantes)
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    
    if guardado_mongo:
        print("✅ Datos guardados en MongoDB (nube)")
    else:
        print("⚠️ No se guardaron datos en MongoDB (puede estar offline)")
    
    if guardado_json:
        print("✅ Datos guardados en archivo JSON (local)")
    else:
        print("❌ Error al guardar en archivo JSON")
    
    if guardado_mongo or guardado_json:
        print(f"\n🎉 ¡Se generaron exitosamente {len(todos_visitantes)} visitantes de prueba!")
        print(f"   Puedes revisar los datos en la aplicación VisitaSegura.")
    else:
        print("\n❌ No se pudieron guardar los datos en ningún lugar.")
        print("   Revisa los errores anteriores.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso cancelado por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

