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
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "JSON inválido"}), 400
        
        tipo = dados.get("tipo", "").upper()
        rfid = dados.get("rfid")
        
        if not rfid or tipo not in ("ENTRADA", "SAIDA"):
            return jsonify({"erro": "Campos 'tipo' ou 'rfid' inválidos"}), 400
        
        if tipo == "ENTRADA":
            resp = gerenciador.registrar_entrada(rfid)
        else:
            resp = gerenciador.registrar_saida(rfid)
        
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
    
    return app
