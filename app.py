import streamlit as st
from web3 import Web3
import os

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Notario Blockchain", page_icon="⚖️", layout="centered")

# ESTILOS CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
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
try:
    # ---------------------------------------------------------
    # IMPORTANTE: Asegúrate de que tus secrets.toml estén bien, 
    # o pon tus claves aquí entre comillas si te da error.
    # ---------------------------------------------------------
    RPC_URL = "https://rpc.sepolia.org"
    
    # Intenta leer de los secretos de Streamlit
    try:
        PRIVATE_KEY = st.secrets["PRIVATE_KEY"]
        MY_ADDRESS = st.secrets["MY_ADDRESS"]
    except:
        # SI ESTO FALLA, PON TUS CLAVES AQUÍ ABAJO DIRECTAMENTE (SOLO PARA PRUEBAS):
        PRIVATE_KEY = "0x2238dea54e2e708183e4dd7bddca272662bc21c28293aade9483e7776cc598c2" 
        MY_ADDRESS = "0xB5F33631B98eA9A54D3d3896dFBE6F7cC6D77d7e"
    
    # TU NUEVO CONTRATO (YA PUESTO):
    CONTRACT_ADDRESS = "0x8b4abC6b53Cc7861E2353417837631092E0118F4" 
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # ABI CORRECTO para el contrato 'Notario'
    CONTRACT_ABI = [
        {
            "anonymous": False,
            "inputs": [{"indexed": False, "internalType": "string", "name": "hash", "type": "string"}, {"indexed": False, "internalType": "uint256", "name": "fecha", "type": "uint256"}],
            "name": "NuevoDocumento",
            "type": "event"
        },
        {
            "inputs": [{"internalType": "string", "name": "_hash", "type": "string"}],
            "name": "registrar",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    
except Exception as e:
    st.error(f"⚙️ Error de configuración: {e}")
    st.stop()

# --- INTERFAZ DEL CLIENTE ---

st.title("⚖️ Notario Digital Ethereum")
st.write("Lo que escribas aquí quedará registrado en la Blockchain de Sepolia para siempre.")

with st.container():
    st.write("---")
    
    # 1. El Mensaje
    texto = st.text_input("✍️ Escribe tu texto a registrar:", max_chars=100, placeholder="Ej: Declaro que este documento es original...")
    
    st.write("") 
    
    # 2. EL BOTÓN
    if st.button("🚀 REGISTRAR EN BLOCKCHAIN"):
        if not texto:
            st.warning("⚠️ Escribe algo antes de enviar.")
        else:
            with st.spinner("⛓️ Llamando al Notario Digital... (Espera 15 seg)"):
                try:
                    # 1. Preparamos la transacción
                    nonce = w3.eth.get_transaction_count(MY_ADDRESS)
                    
                    # LLAMAMOS A LA FUNCIÓN 'REGISTRAR' (La que sí existe)
                    tx = contract.functions.registrar(texto).build_transaction({
                        'chainId': 11155111, # Sepolia ID
                        'gas': 500000,       
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                    })
                    
                    # 2. Firmamos
                    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                    
                    # 3. Enviamos
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    
                    # 4. Esperamos confirmación
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    # 5. ÉXITO
                    link = f"https://sepolia.etherscan.io/tx/{w3.to_hex(tx_hash)}"
                    st.success("¡REGISTRADO CORRECTAMENTE!")
                    
                    st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Documento Notariado</h3>
                            <p>Texto registrado: "{texto}"</p>
                            <p>Bloque: #{receipt.blockNumber}</p>
                            <br>
                            <a href="{link}" target="_blank" style="background-color:#155724; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">🔍 VER EN ETHERSCAN</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Hubo un error en la red: {e}")

st.write("---")
st.caption(f"Conectado a contrato: {CONTRACT_ADDRESS}")
