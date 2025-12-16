# -*- coding: utf-8 -*-
import streamlit as st
import hashlib
import json
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Blockchain Segura", page_icon="🔗", layout="wide")

# --- FUNCIONES BLOCKCHAIN ---
def calcular_hash(bloque):
    """Genera el hash SHA-256 de un bloque"""
    bloque_copy = bloque.copy()
    if 'hash' in bloque_copy:
        del bloque_copy['hash']
    # Ordenamos las keys para asegurar que el hash sea consistente
    bloque_str = json.dumps(bloque_copy, sort_keys=True).encode('utf-8')
    return hashlib.sha256(bloque_str).hexdigest()

def crear_bloque(mensaje, hash_anterior):
    """Crea la estructura de un nuevo bloque"""
    bloque = {
        "mensaje": mensaje,
        "timestamp": str(datetime.now()),
        "hash_anterior": hash_anterior
    }
    bloque["hash"] = calcular_hash(bloque)
    return bloque

def verificar_cadena(cadena):
    """Recorre la cadena buscando manipulaciones"""
    errores = []
    for i in range(1, len(cadena)):
        actual = cadena[i]
        anterior = cadena[i-1]
        
        # 1. Verificar enlace (hash anterior)
        if actual['hash_anterior'] != anterior['hash']:
            errores.append(f"🔗 ROTURA DE ENLACE entre Bloque {i-1} y {i}")
        
        # 2. Verificar contenido (hash recalculado)
        hash_recalculado = calcular_hash(actual)
        if hash_recalculado != actual['hash']:
            errores.append(f"⚠️ CONTENIDO ALTERADO en Bloque {i}: El mensaje no coincide con la huella.")
            
    return len(errores) == 0, errores

# --- GESTIÓN DE ESTADO (MEMORIA) ---
if 'blockchain' not in st.session_state:
    # Bloque Génesis (el primero de la cadena)
    genesis = {
        "mensaje": "Bloque Génesis - Inicio del Ledger",
        "timestamp": str(datetime.now()),
        "hash_anterior": "0"
    }
    genesis["hash"] = calcular_hash(genesis)
    st.session_state.blockchain = [genesis]

# --- INTERFAZ GRÁFICA ---
st.title("🔗 Simulador de Blockchain")
st.markdown("""
Esta aplicación permite demostrar cómo funciona una cadena de bloques básica:
* **Inmutabilidad:** Cada bloque depende del anterior.
* **Hashing:** Cualquier cambio rompe la cadena.
""")

# Pestañas para organizar la aplicación
tab1, tab2, tab3 = st.tabs(["📝 Añadir Bloques", "🕵️‍♂️ Validar Cadena", "😈 Zona Hacker"])

# --- PESTAÑA 1: AÑADIR ---
with tab1:
    st.subheader("Registrar Nuevo Mensaje")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        nuevo_mensaje = st.text_input("Datos del bloque:", placeholder="Ej: Juan envía 50 BTC a María")
    
    with col2:
        st.write("") # Espacio para alinear
        st.write("")
        if st.button("Añadir Bloque", use_container_width=True):
            if nuevo_mensaje:
                ultimo_bloque = st.session_state.blockchain[-1]
                nuevo = crear_bloque(nuevo_mensaje, ultimo_bloque['hash'])
                st.session_state.blockchain.append(nuevo)
                st.success("¡Bloque minado y añadido!")
            else:
                st.warning("El mensaje no puede estar vacío.")

    st.divider()
    st.subheader("Libro Mayor (Ledger)")
    # Mostramos los bloques en orden inverso (el más nuevo arriba)
    for i in range(len(st.session_state.blockchain) - 1, -1, -1):
        bloque = st.session_state.blockchain[i]
        with st.expander(f"Bloque #{i} | {bloque['timestamp']}", expanded=(i == len(st.session_state.blockchain)-1)):
            st.code(json.dumps(bloque, indent=4, ensure_ascii=False), language='json')

# --- PESTAÑA 2: VALIDAR ---
with tab2:
    st.subheader("Auditoría de Integridad")
    if st.button("Verificar Blockchain Completa"):
        es_valida, lista_errores = verificar_cadena(st.session_state.blockchain)
        
        if es_valida:
            st.balloons()
            st.success("✅ ESTADO: VÁLIDO. La cadena es íntegra y segura.")
        else:
            st.error("❌ ESTADO: CORRUPTO. Se han detectado manipulaciones.")
            for error in lista_errores:
                st.write(error)

# --- PESTAÑA 3: HACKER ---
with tab3:
    st.subheader("Simulador de Ataque")
    st.warning("Advertencia: Modificar un bloque romperá la cadena de confianza.")
    
    if len(st.session_state.blockchain) > 1:
        indice = st.number_input("Selecciona el ID del bloque a manipular:", 
                                min_value=0, 
                                max_value=len(st.session_state.blockchain)-1, 
                                step=1)
        
        bloque_a_hackear = st.session_state.blockchain[indice]
        st.text(f"Contenido original: {bloque_a_hackear['mensaje']}")
        
        nuevo_texto_falso = st.text_input("Nuevo contenido falso:", value=bloque_a_hackear['mensaje'])
        
        if st.button("Aplicar Hackeo"):
            # Modificamos el mensaje SIN recalcular el hash (simulando alteración maliciosa)
            st.session_state.blockchain[indice]['mensaje'] = nuevo_texto_falso
            st.toast(f"¡Bloque {indice} alterado con éxito!", icon="😈")
            st.info("Ahora ve a la pestaña 'Validar Cadena' para ver el resultado.")
    else:
        st.info("Añade algunos bloques primero para poder hackearlos.")
