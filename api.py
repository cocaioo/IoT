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
