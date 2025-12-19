import streamlit as st
from web3 import Web3
import hashlib # Necesario para las huellas digitales de las fotos

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Notario Blockchain Pro", page_icon="⚖️", layout="centered")

# ESTILOS CSS
st.markdown("""
    <style>
    /* ESTO OCULTA EL MENÚ Y LA BARRA SUPERIOR */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        width: 100%;
        background-color: #2E86C1;
        color: white;
        font-size: 20px;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN AL CEREBRO ---
try:
    RPC_URL = "https://ethereum-sepolia.publicnode.com"
    
    # ------------------------------------------------------------------
    # GESTIÓN DE SECRETOS (SEGURIDAD)
    # ------------------------------------------------------------------
    try:
        PRIVATE_KEY = st.secrets["PRIVATE_KEY"]
        MY_ADDRESS = st.secrets["MY_ADDRESS"]
    except (FileNotFoundError, KeyError):
        st.error("⚠️ FALTAN LAS CLAVES DE SEGURIDAD")
        st.warning("El código no tiene acceso a la clave privada. Por favor, configúrala en los 'Secrets' de Streamlit Cloud.")
        st.stop()

    CONTRACT_ADDRESS = "0x8b4abC6b53Cc7861E2353417837631092E0118F4" 
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    CONTRACT_ABI = [
        {"anonymous": False,"inputs": [{"indexed": False, "internalType": "string", "name": "hash", "type": "string"}, {"indexed": False, "internalType": "uint256", "name": "fecha", "type": "uint256"}],"name": "NuevoDocumento","type": "event"},
        {"inputs": [{"internalType": "string", "name": "_hash", "type": "string"}],"name": "registrar","outputs": [],"stateMutability": "nonpayable","type": "function"}
    ]
    
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
except Exception as e:
    st.error(f"⚙️ Error de configuración: {e}")
    st.stop()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1909/1909746.png", width=100)
    st.markdown("## 👨‍⚖️ Notaría Digital")
    st.info(f"**ADMINISTRADOR**\n\nOperativo")
    st.code(MY_ADDRESS, language="text")
    st.caption("Los archivos adjuntos no se suben a la red, solo se registra su huella digital (Hash SHA256) para garantizar privacidad.")
    st.write("---")

# --- INTERFAZ PRINCIPAL ---
st.title("⚖️ Registro Oficial Blockchain")
st.markdown("### Certificación de Textos y Documentos")

with st.container():
    st.write("---")
    
    # 1. DATOS
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("👤 Nombre del Solicitante:", placeholder="Ej: Ana García")
    with col2:
        identificador = st.text_input("🆔 DNI/Email (Opcional):", placeholder="Opcional")

    # 2. TEXTO GRANDE
    mensaje = st.text_area("✍️ Contenido a Certificar:", height=150, placeholder="Escribe aquí tu contrato, declaración, poema o carta completa...")
    
    # 3. SUBIDA DE ARCHIVOS
    st.markdown("#### 📎 Adjuntar Evidencia (Foto/PDF)")
    archivo = st.file_uploader("Sube un archivo para certificar que existe hoy (Se guardará su Huella Digital):", type=['png', 'jpg', 'pdf', 'txt'])
    
    hash_archivo = "Sin adjuntos"
    nombre_archivo = ""
    
    if archivo is not None:
        bytes_data = archivo.getvalue()
        hash_object = hashlib.sha256(bytes_data)
        hash_archivo = hash_object.hexdigest()
        nombre_archivo = archivo.name
        
        st.success(f"✅ Archivo procesado. Huella Digital: {hash_archivo[:15]}...")
        st.caption("Esta huella es única. Si cambias un solo píxel de la foto, la huella cambiará.")

    st.write("---")
    
    # 4. BOTÓN DE REGISTRO DIRECTO
    st.write("") 
    boton = st.button("🚀 REGISTRAR DOCUMENTO")

    if boton:
        if not nombre or not mensaje:
            st.warning("⚠️ Falta Nombre o Mensaje.")
        else:
            texto_final = f"AUTOR: {nombre} ({identificador}) | DICE: {mensaje}"
            
            if archivo:
                texto_final += f" | ADJUNTO: {nombre_archivo} (SHA256: {hash_archivo})"
            
            with st.spinner("⛓️ Grabando en Bloque..."):
                try:
                    nonce = w3.eth.get_transaction_count(MY_ADDRESS)
                    
                    tx = contract.functions.registrar(texto_final).build_transaction({
                        'chainId': 11155111, 
                        'gas': 500000,       
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                    })
                    
                    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    link = f"https://sepolia.etherscan.io/tx/{w3.to_hex(tx_hash)}"
                    
                    st.success("¡REGISTRO COMPLETADO!")
                    
                    st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Certificado Emitido</h3>
                            <p><strong>Autor:</strong> {nombre}</p>
                            <p><strong>Contenido:</strong> {mensaje[:50]}...</p>
                            {'<p><strong>📎 Archivo Certificado:</strong> ' + nombre_archivo + '</p>' if archivo else ''}
                            <hr>
                            <a href="{link}" target="_blank" style="text-decoration:none;">🔍 <b>VER PRUEBA EN ETHERSCAN</b></a>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
