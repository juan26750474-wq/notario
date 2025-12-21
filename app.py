import streamlit as st
from web3 import Web3
import hashlib # Necesario para las huellas digitales de las fotos
import urllib.parse # NUEVO: Necesario para enviar el texto a la otra web

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Notario Blockchain Pro", page_icon="⚖️", layout="centered")

# ESTILOS CSS
st.markdown("""
    <style>
    /* Ocultar menú de Streamlit */
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
    /* Estilo diferente para el botón de enlace externo */
    .stLinkButton>a {
        width: 100%;
        background-color: #27AE60 !important;
        color: white !important;
        font-size: 20px;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
        text-align: center;
        display: block;
        text-decoration: none;
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
    
    # GESTIÓN DE SECRETOS (SEGURIDAD)
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
    st.write("---")

# --- INTERFAZ PRINCIPAL ---
st.title("⚖️ Registro Oficial Blockchain")

# 1. FORMULARIO COMÚN
st.markdown("### 📝 Redacción del Documento")

col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("👤 Nombre del Solicitante:", placeholder="Ej: Ana García")
with col2:
    identificador = st.text_input("🆔 DNI/Email (Opcional):", placeholder="Opcional")

mensaje = st.text_area("✍️ Contenido a Certificar:", height=150, placeholder="Escribe aquí tu contrato, declaración, poema o carta completa...")

st.markdown("#### 📎 Adjuntar Evidencia (Foto/PDF)")
archivo = st.file_uploader("Sube un archivo (Se guardará su Huella Digital):", type=['png', 'jpg', 'pdf', 'txt'])

hash_archivo = "Sin adjuntos"
nombre_archivo = ""

if archivo is not None:
    bytes_data = archivo.getvalue()
    hash_object = hashlib.sha256(bytes_data)
    hash_archivo = hash_object.hexdigest()
    nombre_archivo = archivo.name
    st.success(f"✅ Huella calculada: {hash_archivo[:10]}...")

st.write("---")

# Preparamos el texto final independientemente del modo
texto_final = ""
if nombre and mensaje:
    texto_final = f"AUTOR: {nombre} ({identificador}) | DICE: {mensaje}"
    if archivo:
        texto_final += f" | ADJUNTO: {nombre_archivo} (SHA256: {hash_archivo})"

# 2. SELECTOR DE MODO DE FIRMA
st.subheader("🚀 Selecciona el Método de Firma")
modo = st.radio(
    "¿Quién va a pagar la transacción?",
    ["👤 Firma el Notario dando fe por el Cliente", "🦊 Contratos debería firmar el Cliente (Con MetaMask)"],
    horizontal=True
)

st.write("")

if modo == "👤 Firma el Notario dando fe por el Cliente":
    # --- MODO 1: FIRMAS TÚ ---
    st.info("ℹ️ El documento se registrará usando la cuenta del Notario.")
    boton = st.button("🚀 REGISTRAR DOCUMENTO AHORA")

    if boton:
        if not nombre or not mensaje:
            st.warning("⚠️ Falta Nombre o Mensaje.")
        else:
            with st.spinner("⛓️ Grabando en Bloque..."):
                try:
                    nonce = w3.eth.get_transaction_count(MY_ADDRESS)
                    tx = contract.functions.registrar(texto_final).build_transaction({
                        'chainId': 11155111, 'gas': 500000, 'gasPrice': w3.eth.gas_price, 'nonce': nonce
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
                            <a href="{link}" target="_blank">🔍 <b>VER EN ETHERSCAN</b></a>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

else:
    # --- MODO 2: FIRMA EL CLIENTE ---
    st.warning("⚠️ En este modo típico de contratos, el cliente será redirigido para firmar con su propia Billetera.")
    
    if not nombre or not mensaje:
        st.error("✍️ Por favor, rellena los datos arriba antes de continuar.")
    else:
        st.markdown("#### Revisión del Texto a Enviar:")
        st.code(texto_final, language="text")
        
        # --- AQUÍ ESTÁ LA MAGIA DEL ENLACE ---
        # 1. Codificamos el texto para que pueda viajar en una URL (cambia espacios por %20, etc)
        texto_codificado = urllib.parse.quote(texto_final)
        
        # 2. Construimos la URL completa con el parámetro ?texto=
        # CAMBIA ESTA URL SI TU ARCHIVO HTML ESTÁ EN OTRO SITIO
        URL_BASE = "http://aprendidos.es/notaria/firma.html"
        URL_COMPLETA = f"{URL_BASE}?texto={texto_codificado}"
        
        st.write("")
        # Este botón abre tu HTML en una pestaña nueva con los datos ya cargados
        st.link_button("➡️ ABRIR PORTAL DE FIRMA (Con datos cargados)", URL_COMPLETA)
