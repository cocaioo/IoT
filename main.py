"""
Sistema de Controle de Restaurante Universitário
Integração com ESP32 (RFID) + Câmera (Fila) + Webcam (Fotos)

Arquivo principal que orquestra todos os módulos do sistema
"""

import time

from config import Config
from gerenciador import GerenciadorRestaurante
from esp32_serial import IntegradorESP32Serial
from camera_monitor import MonitorFilaCamera
from api import criar_app


def main():
    """Ponto de entrada do sistema"""
    
    print("\n" + "="*60)
    print("  SISTEMA DE CONTROLE - RESTAURANTE UNIVERSITÁRIO")
    print("="*60 + "\n")
    
    # Inicializa gerenciador (com captura de fotos se habilitado)
    gerenciador = GerenciadorRestaurante(
        habilitar_fotos=Config.HABILITAR_FOTOS,  # ← NOVO
        camera_index=Config.CAMERA_FOTOS_INDEX   # ← NOVO
    )
    print("✓ Gerenciador inicializado\n")
    
    # ==== INTEGRAÇÃO COM ESP32 ====
    
    if Config.MODO_ESP32 == "serial":
        print("📡 Modo: SERIAL (USB)")
        integrador = IntegradorESP32Serial(
            gerenciador, 
            Config.PORTA_SERIAL, 
            Config.BAUDRATE
        )
        if not integrador.iniciar():
            print("\n⚠ Continuando sem ESP32...\n")
    
    elif Config.MODO_ESP32 == "http":
        print("📡 Modo: HTTP (Wi-Fi)")
        print(f"   O ESP32 deve enviar requisições para: http://SEU_IP:{Config.HTTP_PORT}/evento\n")
    
    else:
        print("📡 Modo: Nenhum (ESP32 desabilitado)\n")
    
    # ==== MONITOR DE CÂMERA (FILA) ====
    
    monitor = MonitorFilaCamera(
        gerenciador, 
        Config.CAMERA_INDEX,
        Config.INTERVALO_CAMERA_SEGUNDOS,
        Config.HABILITAR_CAMERA
    )
    monitor.iniciar()
    
    # ==== API HTTP ====
    
    app = criar_app(gerenciador)
    
    print(f"🌐 Iniciando API HTTP em http://{Config.HTTP_HOST}:{Config.HTTP_PORT}")
    print(f"   Acesse http://localhost:{Config.HTTP_PORT}/status para ver o status\n")
    print("="*60)
    print("Sistema rodando! Pressione Ctrl+C para encerrar.")
    print("="*60 + "\n")
    
    try:
        app.run(
            host=Config.HTTP_HOST, 
            port=Config.HTTP_PORT, 
            debug=False, 
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando sistema...")
    
    # ==== FINALIZAÇÃO ====
    
    print(gerenciador.exportar_dados(Config.ARQUIVO_EXPORTACAO))
    print("✓ Sistema encerrado.\n")


if __name__ == "__main__":
    main()