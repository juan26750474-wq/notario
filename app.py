<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crea tus Mensajes Para Siempre</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js"></script>
    <style>
        body { background-color: #111; color: #eee; font-family: 'Courier New', Courier, monospace; text-align: center; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: #222; padding: 30px; border-radius: 15px; box-shadow: 0 0 20px rgba(0,255,0,0.2); }
        h1 { color: #00ff88; text-transform: uppercase; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 5px; border: none; font-size: 16px; }
        input, select { background: #333; color: white; border: 1px solid #444; }
        button { cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-connect { background: #ff9900; color: black; }
        .btn-mint { background: #00ff88; color: black; }
        .btn-transfer { background: #00bfff; color: black; }
        button:hover { opacity: 0.8; }
        #status { margin-top: 20px; font-size: 14px; color: #aaa; word-break: break-all; }
        .hidden { display: none; }
    </style>
</head>
<body>

    <div class="container">
        <h1>📜 Mensajes Eternos</h1>
        <p>Inmortaliza tus palabras en la Blockchain.</p>

        <button id="connectBtn" class="btn-connect" onclick="conectarWallet()">🔌 Conectar MetaMask</button>
        <p id="walletAddress" style="color:#ff9900; font-size: 12px;"></p>

        <hr style="border-color: #333; margin: 20px 0;">

        <div id="app" class="hidden">
            <h3>1. Crear Nuevo Mensaje</h3>
            <input type="text" id="mensajeInput" placeholder="Escribe tu mensaje eterno..." maxlength="50">
            <select id="tipoInput">
                <option value="Escrito">📝 Escrito Personal</option>
                <option value="Contrato">⚖️ Contrato / Acuerdo</option>
                <option value="Profecia">🔮 Profecía</option>
            </select>
            <button class="btn-mint" onclick="crearMensaje()">Grabar en Blockchain ⛏️</button>

            <br><br>

            <h3>2. Regalar / Transferir</h3>
            <input type="number" id="idInput" placeholder="ID del NFT (ej: 1)">
            <input type="text" id="destinatarioInput" placeholder="Dirección destino (0x...)">
            <button class="btn-transfer" onclick="transferir()">Transferir Propiedad 🎁</button>
        </div>

        <p id="status"></p>
    </div>

    <script>
        // --- CONFIGURACIÓN ---
        // ⚠️ PEGA AQUÍ LA DIRECCIÓN DE TU CONTRATO QUE CREASTE EN REMIX
        const CONTRACT_ADDRESS = "0xTU_DIRECCION_DE_CONTRATO_AQUI"; 
        
        // El ABI Mínimo para que la web entienda el contrato
        const ABI = [
            "function crearMensaje(string memory _texto, string memory _tipo) public returns (uint256)",
            "function safeTransferFrom(address from, address to, uint256 tokenId) public"
        ];

        let provider, signer, contract;

        // 1. CONECTAR METAMASK
        async function conectarWallet() {
            if (window.ethereum) {
                try {
                    provider = new ethers.providers.Web3Provider(window.ethereum);
                    await provider.send("eth_requestAccounts", []); // Pide permiso al usuario
                    signer = provider.getSigner();
                    const address = await signer.getAddress();
                    
                    document.getElementById("walletAddress").innerText = "Conectado: " + address;
                    document.getElementById("connectBtn").classList.add("hidden");
                    document.getElementById("app").classList.remove("hidden");
                    
                    // Conectamos con el contrato
                    contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, signer);
                    mostrarStatus("🟢 Sistema listo. Esperando órdenes.");
                } catch (error) {
                    mostrarStatus("🔴 Error: " + error.message);
                }
            } else {
                alert("Necesitas instalar MetaMask!");
            }
        }

        // 2. FUNCIÓN CREAR MENSAJE
        async function crearMensaje() {
            const texto = document.getElementById("mensajeInput").value;
            const tipo = document.getElementById("tipoInput").value;
            
            if (!texto) return alert("Escribe algo!");

            try {
                mostrarStatus("⏳ MetaMask se abrirá. Confirma la transacción...");
                const tx = await contract.crearMensaje(texto, tipo);
                mostrarStatus("⛏️ Minando en la Blockchain... Espere...");
                await tx.wait(); // Esperamos a que se confirme
                mostrarStatus("🎉 ¡ÉXITO! Mensaje grabado para siempre. Hash: " + tx.hash);
            } catch (error) {
                mostrarStatus("❌ Error: " + error.message);
            }
        }

        // 3. FUNCIÓN TRANSFERIR
        async function transferir() {
            const id = document.getElementById("idInput").value;
            const to = document.getElementById("destinatarioInput").value;
            const from = await signer.getAddress();

            if (!id || !to) return alert("Faltan datos");

            try {
                mostrarStatus("⏳ Pidiendo permiso de traspaso...");
                const tx = await contract.safeTransferFrom(from, to, id);
                mostrarStatus("🚚 Transfiriendo propiedad... Espere...");
                await tx.wait();
                mostrarStatus("✅ ¡HECHO! El NFT ya no es tuyo.");
            } catch (error) {
                mostrarStatus("❌ Error: " + error.reason || error.message);
            }
        }

        function mostrarStatus(txt) {
            document.getElementById("status").innerText = txt;
        }
    </script>
</body>
</html>
