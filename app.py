import streamlit as st
from web3 import Web3
import os

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Inmortaliza tu Mensaje", page_icon="✨", layout="centered")

# ESTILOS CSS (Para que no parezca una herramienta técnica)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 20px;
        border-radius: 10px;
        padding: 10px;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN AL CEREBRO (Tu Wallet paga) ---
# Intentamos conectar usando los secretos de la nube
try:
    # Si estamos en Streamlit Cloud, usamos st.secrets
    RPC_URL = "https://rpc.sepolia.org" # O usa st.secrets["RPC_URL"] si prefieres
    PRIVATE_KEY = st.secrets["PRIVATE_KEY"]
    MY_ADDRESS = st.secrets["MY_ADDRESS"]
    CONTRACT_ADDRESS = "0x8b4abC6b53Cc7861E2353417837631092E0118F4" # <--- ¡CAMBIA ESTO!
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # ABI Mínimo necesario
    CONTRACT_ABI = [
        {"inputs":[{"internalType":"string","name":"_texto","type":"string"},{"internalType":"string","name":"_tipo","type":"string"}],"name":"crearMensaje","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}
    ]
    
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
except Exception as e:
    st.error("⚙️ Error de configuración del sistema. Contacta al administrador.")
    st.stop()

# --- INTERFAZ DEL CLIENTE ---

st.title("✨ Deja tu huella eterna")
st.write("Escribe un mensaje, una promesa o una profecía. Nosotros la grabaremos en la Blockchain para siempre. Sin registros. Sin costes para ti.")

with st.container():
    st.write("---")
    
    # 1. El Mensaje
    texto = st.text_input("✍️ Tu Mensaje (Máx 40 caracteres):", max_chars=40, placeholder="Ej: Te amaré siempre, Ana.")
    
    # 2. El Tipo (Visual)
    tipo = st.radio("🎨 Elige el estilo de tu tarjeta:", ["Escrito (Elegante)", "Contrato (Serio)", "Profecia (Místico)"], horizontal=True)
    
    # Mapeo de nombres para el contrato
    tipo_real = "Escrito"
    if "Contrato" in tipo: tipo_real = "Contrato"
    if "Profecia" in tipo: tipo_real = "Profecia"

    st.write("") # Espacio
    
    # 3. EL BOTÓN MÁGICO
    if st.button("🚀 INMORTALIZAR AHORA (Gratis)"):
        if not texto:
            st.warning("⚠️ Por favor, escribe algo antes de enviar.")
        else:
            with st.spinner("⛓️ Grabando en piedra digital... (Esto tarda unos 15 segs)"):
                try:
                    # AQUI OCURRE LA MAGIA AUTOMÁTICA
                    # 1. Preparamos la transacción con TU cuenta
                    nonce = w3.eth.get_transaction_count(MY_ADDRESS)
                    
                    tx = contract.functions.crearMensaje(texto, tipo_real).build_transaction({
                        'chainId': 11155111, # Sepolia
                        'gas': 500000,       # Límite de gas
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                    })
                    
                    # 2. Firmamos con TU clave privada (El cliente no la ve)
                    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    
                    # 3. Enviamos
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    
                    # 4. Esperamos confirmación (Opcional, para asegurar el link)
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    # 5. MOSTRAR RESULTADO
                    link = f"https://sepolia.etherscan.io/tx/{w3.to_hex(tx_hash)}"
                    st.success("¡HECHO! Tu mensaje es eterno.")
                    
                    st.markdown(f"""
                        <div class="success-box">
                            <h3>📜 Certificado de Inmortalidad</h3>
                            <p>Tu mensaje "{texto}" ha quedado registrado en el bloque #{receipt.blockNumber}.</p>
                            <p>Nadie podrá borrarlo jamás.</p>
                            <br>
                            <a href="{link}" target="_blank" style="background-color:#155724; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">🔍 VER PRUEBA EN BLOCKCHAIN</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Hubo un error en la red. Inténtalo de nuevo. ({e})")

st.write("---")
st.caption("🔒 Servicio garantizado por tecnología Blockchain Ethereum.")
