"""
API HTTP usando Flask para comunicação com ESP32 e consultas
"""

from flask import Flask, request, jsonify

from gerenciador import GerenciadorRestaurante


# Instância do gerenciador (será injetada pelo main)
gerenciador: GerenciadorRestaurante = None


def criar_app(gerenciador_instancia: GerenciadorRestaurante) -> Flask:
    """Cria e configura a aplicação Flask"""
    global gerenciador
    gerenciador = gerenciador_instancia
    
    app = Flask(__name__)
    
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
    </style>
</head>
<body>
    <div class="container">
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
        
        <p class="refresh-info">⟳ Atualização automática a cada 3 segundos</p>
    </div>
    
    <script>
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
                        <div class="stat-value">${status.pessoas_fila || 0}</div>
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
