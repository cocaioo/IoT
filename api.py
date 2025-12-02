"""
API HTTP usando Flask para comunicação com ESP32 e consultas
"""

from flask import Flask, request, jsonify, Response

from gerenciador import GerenciadorRestaurante
from simulador import SimuladorRestaurante
import time


# Instância do gerenciador (será injetada pelo main)
gerenciador: GerenciadorRestaurante = None
simulador: SimuladorRestaurante = None
monitor_camera = None


def criar_app(gerenciador_instancia: GerenciadorRestaurante, monitor_instancia=None) -> Flask:
    global gerenciador
    gerenciador = gerenciador_instancia
    simulador = SimuladorRestaurante(gerenciador)
    monitor_camera = monitor_instancia
    
    app = Flask(__name__)

    def gerar_frames():
        while True:
            if monitor_camera:
                frame = monitor_camera.obter_frame()
                if frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    # Se não tiver frame ainda, espera um pouco para não travar a CPU
                    time.sleep(0.1)
            else:
                break
    
            # Pequena pausa para liberar recursos do servidor para outras rotas
            time.sleep(0.01)

    @app.route('/video_feed')
    def video_feed():
        """Rota que transmite o vídeo"""
        return Response(gerar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route("/simular/entrada", methods=["POST"])
    def simular_entrada():
        res = simulador.simular_entrada()
        return jsonify(res)

    @app.route("/simular/saida", methods=["POST"])
    def simular_saida():
        res = simulador.simular_saida()
        return jsonify(res)

    @app.route("/simular/fila", methods=["POST"])
    def simular_fila():
        dados = request.json
        qtd = int(dados.get('qtd', 0))
        simulador.simular_fila(qtd)
        return jsonify({'sucesso': True, 'fila': qtd})
    
    @app.route("/evento", methods=["POST"])
    def evento():
        """
        Endpoint para ESP32 enviar eventos via HTTP
        Body JSON: {"tipo": "ENTRADA" ou "SAIDA", "rfid": "RFID_123"}
        """
        print("\n🔔 Requisição recebida em /evento")
        print(f"   Headers: {dict(request.headers)}")
        print(f"   Body raw: {request.get_data()}")
        
        dados = request.get_json(silent=True)
        print(f"   JSON parsed: {dados}")
        
        if not dados:
            print("   ❌ JSON inválido!")
            return jsonify({"erro": "JSON inválido"}), 400
        
        tipo = dados.get("tipo", "").upper()
        rfid = dados.get("rfid")
        
        print(f"   Tipo: {tipo}, RFID: {rfid}")
        
        if not rfid or tipo not in ("ENTRADA", "SAIDA"):
            print("   ❌ Campos inválidos!")
            return jsonify({"erro": "Campos 'tipo' ou 'rfid' inválidos"}), 400
        
        if tipo == "ENTRADA":
            resp = gerenciador.registrar_entrada(rfid)
        else:
            resp = gerenciador.registrar_saida(rfid)
        
        print(f"   ✓ Resposta: {resp}\n")
        return jsonify(resp)
    
    @app.route("/status", methods=["GET"])
    def status():
        """Retorna status atual do restaurante"""
        return jsonify(gerenciador.obter_status_atual())
    
    @app.route("/", methods=["GET"])
    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """Página HTML bonita para visualizar o sistema"""
        html = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Controle - Restaurante Universitário</title>
    <style>
    
        /* Camera Container */
        .camera-container { text-align: center; }
        .camera-feed { 
            width: 100%; 
            max-width: 500px; 
            border-radius: 8px; 
            border: 3px solid #333;
            background: #000;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        
        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .table-container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow-x: auto;
        }
        
        h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .badge-entrada {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-saida {
            background: #f8d7da;
            color: #721c24;
        }
        
        .badge-dentro {
            background: #cce5ff;
            color: #004085;
        }
        
        .refresh-info {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .sim-toolbar {
            background: #2c3e50; color: white; padding: 15px; 
            border-radius: 8px; margin-bottom: 20px;
            display: flex; align-items: center; gap: 10px;
        }
        
        .sim-btn {
            padding: 8px 15px; border: none; border-radius: 4px; 
            cursor: pointer; font-weight: bold; color: white;
        }
        .btn-green { background: #27ae60; }
        .btn-red { background: #c0392b; }
        .btn-blue { background: #2980b9; }
        .sim-input { padding: 8px; width: 60px; border-radius: 4px; border: none; }
    </style>
</head>
<body>
    <div class="container">
    
        <div class="sim-toolbar">
            <strong>🛠️ Simulador:</strong>
            <button onclick="simular('entrada')" class="sim-btn btn-green">+ Entrar Pessoa</button>
            <button onclick="simular('saida')" class="sim-btn btn-red">- Sair Pessoa</button>
            
            <div style="margin-left: auto; display:flex; gap: 5px;">
                <input type="number" id="simFilaQtd" class="sim-input" placeholder="0">
                <button onclick="simularFila()" class="sim-btn btn-blue">Set Fila</button>
            </div>
        </div>
        
        <header>
            <h1>🍽️ Sistema de Controle - Restaurante Universitário</h1>
            <p class="subtitle">Monitoramento em tempo real de entradas e saídas</p>
        </header>
        
        <div class="stats-grid" id="stats">
            <!-- Carregado via JavaScript -->
        </div>
        
        <div class="table-container">
            <h2>📊 Registro de Permanência</h2>
            <table id="temposTable">
                <thead>
                    <tr>
                        <th>RFID</th>
                        <th>Entrada</th>
                        <th>Saída</th>
                        <th>Tempo de Permanência</th>
                    </tr>
                </thead>
                <tbody id="temposBody">
                    <!-- Carregado via JavaScript -->
                </tbody>
            </table>
        </div>
        
        <div class="table-container" style="margin-top: 30px;">
            <h2>👥 Pessoas Dentro do Restaurante</h2>
            <table id="dentroTable">
                <thead>
                    <tr>
                        <th>RFID</th>
                        <th>Horário de Entrada</th>
                        <th>Tempo Decorrido</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="dentroBody">
                    <!-- Carregado via JavaScript -->
                </tbody>
            </table>
        </div>
        
        <div class="card camera-container">
            <h2>🎥 Câmera da Fila</h2>
            <p>Detecção em tempo real</p>
            <img src="/video_feed" class="camera-feed" alt="Carregando câmera...">
            
            <div style="margin-top: 15px; font-size: 1.2em;">
                Pessoas na Fila (Detecção): <strong id="num-fila">0</strong>
            </div>
        </div>
        
        <p class="refresh-info">⟳ Atualização automática a cada 3 segundos</p>
        
        <div id="toast">Ação realizada</div>
    </div>
    
    <script>
    
        function mostrarToast(msg) {
            var x = document.getElementById("toast");
            x.innerText = msg;
            x.className = "show";
            setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
        }
        
        async function simular(acao) {
            try {
                const res = await fetch(`/simular/${acao}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ acao: acao }),
                });
                const data = await res.json();
                
                if(data.mensagem) mostrarToast(data.mensagem);
                else mostrarToast("Sucesso: " + acao);
                
                atualizarDados(); 
            } catch (e) { console.error(e); }
        }

        async function simularFila() {
            const inputEl = document.getElementById('simFilaQtd');
            if (!inputEl) {
                console.error("Erro: Input 'simFilaQtd' não encontrado!");
                return;
            }
            const qtd = inputEl.value;
            
            await fetch('/simular/fila', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ acao: 'fila', qtd: qtd }),
            });
            mostrarToast("Fila definida: " + qtd);
            atualizarDados();
        }
        
        function formatarTempo(segundos) {
            const horas = Math.floor(segundos / 3600);
            const minutos = Math.floor((segundos % 3600) / 60);
            const segs = segundos % 60;
            
            let resultado = [];
            if (horas > 0) resultado.push(horas + "h");
            if (minutos > 0) resultado.push(minutos + "min");
            if (segs > 0 || resultado.length === 0) resultado.push(segs + "s");
            
            return resultado.join(" ");
        }
        
        function calcularTempoDecorrido(entrada) {
            const entradaDate = new Date(entrada);
            const agora = new Date();
            const diff = Math.floor((agora - entradaDate) / 1000);
            return formatarTempo(diff);
        }
        
        async function atualizarDados() {
            try {
                // Status geral
                const statusResp = await fetch("/status");
                const status = await statusResp.json();
                
                document.getElementById("stats").innerHTML = `
                    <div class="stat-card">
                        <div class="stat-label">👥 Pessoas Dentro</div>
                        <div class="stat-value">${status.pessoas_dentro || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">📥 Entradas Hoje</div>
                        <div class="stat-value">${status.entradas_hoje || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">📤 Saídas Hoje</div>
                        <div class="stat-value">${status.saidas_hoje || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">👨‍👩‍👧‍👦 Fila (Câmera)</div>
                        <div class="stat-value">${status.pessoas_na_fila || 0}</div>
                    </div>
                `;
                
                // Tempos de permanência
                const temposResp = await fetch("/tempos");
                const tempos = await temposResp.json();
                
                const temposBody = document.getElementById("temposBody");
                if (tempos.length === 0) {
                    temposBody.innerHTML = `<tr><td colspan="4" class="empty-state">Nenhum registro ainda</td></tr>`;
                } else {
                    temposBody.innerHTML = tempos.slice(0, 20).map(t => `
                        <tr>
                            <td><strong>${t.rfid}</strong></td>
                            <td>${new Date(t.entrada).toLocaleString("pt-BR")}</td>
                            <td>${new Date(t.saida).toLocaleString("pt-BR")}</td>
                            <td><strong>${t.duracao_formatada}</strong></td>
                        </tr>
                    `).join("");
                }
                
                // Pessoas dentro
                const dentroBody = document.getElementById("dentroBody");
                const pessoasDentro = status.rfids_dentro || [];
                
                if (pessoasDentro.length === 0) {
                    dentroBody.innerHTML = `<tr><td colspan="4" class="empty-state">Nenhuma pessoa dentro no momento</td></tr>`;
                } else {
                    const historico = await fetch("/historico?limite=100");
                    const registros = await historico.json();
                    
                    dentroBody.innerHTML = pessoasDentro.map(rfid => {
                        // Encontra última entrada (tipo em minúsculo)
                        const ultimaEntrada = registros.find(r => r.rfid === rfid && r.tipo.toLowerCase() === "entrada");
                        const entrada = ultimaEntrada ? ultimaEntrada.timestamp : "--";
                        const tempoDecorrido = ultimaEntrada ? calcularTempoDecorrido(entrada) : "--";
                        
                        return `
                            <tr>
                                <td><strong>${rfid}</strong></td>
                                <td>${entrada !== "--" ? new Date(entrada).toLocaleString("pt-BR") : "--"}</td>
                                <td><strong>${tempoDecorrido}</strong></td>
                                <td><span class="badge badge-dentro">Dentro</span></td>
                            </tr>
                        `;
                    }).join("");
                }
                
            } catch (error) {
                console.error("Erro ao carregar dados:", error);
            }
        }
        
        // Atualiza a cada 3 segundos
        atualizarDados();
        setInterval(atualizarDados, 3000);
    </script>
</body>
</html>
        '''
        return html
    
    @app.route("/estatisticas", methods=["GET"])
    def estatisticas():
        """Retorna estatísticas (opcional: ?data=2025-01-10)"""
        data = request.args.get("data")
        return jsonify(gerenciador.obter_estatisticas(data))
    
    @app.route("/historico", methods=["GET"])
    def historico():
        """Retorna histórico (opcional: ?limite=50)"""
        try:
            limite = int(request.args.get("limite", 100))
        except ValueError:
            limite = 100
        return jsonify(gerenciador.obter_historico(limite))
    
    @app.route("/tempos", methods=["GET"])
    def tempos_permanencia():
        """Retorna tempos de permanência (opcional: ?rfid=RFID_123)"""
        rfid = request.args.get("rfid")
        return jsonify(gerenciador.obter_tempos_permanencia(rfid))
    
    @app.route("/estatisticas-tempo", methods=["GET"])
    def estatisticas_tempo():
        """Retorna estatísticas de tempo de permanência"""
        return jsonify(gerenciador.obter_estatisticas_tempo())
    
    return app
