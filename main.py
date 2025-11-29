"""
Sistema de Controle de Restaurante Universitário
Integração com ESP32 (RFID) + Câmera (Fila)

Arquivo principal que orquestra todos os módulos do sistema
"""

import time
import threading
import sys

from config import Config
from gerenciador import GerenciadorRestaurante
from esp32_serial import IntegradorESP32Serial
from camera_monitor import MonitorFilaCamera
from api import criar_app


def loop_leitura_teclado(integrador_serial):
    """Loop para ler comandos do teclado e enviar para o ESP32."""
    print("\n" + "="*60)
    print("  CONTROLE DE MODO RFID (TECLADO)")
    print("="*60)
    print("  Digite 'E' para ENTRADA")
    print("  Digite 'S' para SAÍDA")
    print("  (Pressione Enter após digitar)")
    print("="*60 + "\n")
    
    while True:
        try:
            comando_teclado = input("> ").strip().upper()
            if comando_teclado == 'E':
                integrador_serial.enviar_comando_esp32('E')
                print("✓ Modo ENTRADA enviado ao ESP32")
            elif comando_teclado == 'S':
                integrador_serial.enviar_comando_esp32('S')
                print("✓ Modo SAÍDA enviado ao ESP32")
            elif comando_teclado == 'Q':
                print("Saindo do controle de teclado...")
                break
            else:
                print("⚠ Comando inválido. Use 'E', 'S' ou 'Q'.")
        except EOFError:
            break
        except Exception as e:
            print(f"Erro na leitura do teclado: {e}")
            break


def main():
    """Ponto de entrada do sistema"""
    
    print("\n" + "="*60)
    print("  SISTEMA DE CONTROLE - RESTAURANTE UNIVERSITÁRIO")
    print("="*60 + "\n")
    
    # Inicializa gerenciador
    gerenciador = GerenciadorRestaurante()
    print("✓ Gerenciador inicializado\n")
    
    # ==== INTEGRAÇÃO COM ESP32 ====
    
    integrador = None
    
    if Config.MODO_ESP32 == "serial":
        print("📡 Modo: SERIAL (USB)")
        integrador = IntegradorESP32Serial(
            gerenciador, 
            Config.PORTA_SERIAL, 
            Config.BAUDRATE
        )
        if not integrador.iniciar():
            print("\n⚠ Continuando sem ESP32...\n")
            integrador = None
    
    elif Config.MODO_ESP32 == "http":
        print("📡 Modo: HTTP (Wi-Fi)")
        print(f"   O ESP32 deve enviar requisições para: http://SEU_IP:{Config.HTTP_PORT}/evento\n")
    
    else:
        print("📡 Modo: Nenhum (ESP32 desabilitado)\n")
    
    # ==== MONITOR DE CÂMERA ====
    
    monitor = MonitorFilaCamera(
        gerenciador, 
        Config.CAMERA_INDEX,
        Config.INTERVALO_CAMERA_SEGUNDOS,
        Config.HABILITAR_CAMERA
    )
    monitor.iniciar()
    
    # ==== THREAD DE LEITURA DO TECLADO (se modo serial) ====
    
    thread_teclado = None
    if integrador and Config.MODO_ESP32 == "serial":
        thread_teclado = threading.Thread(target=loop_leitura_teclado, args=(integrador,))
        thread_teclado.daemon = True
        thread_teclado.start()
    
    # ==== API HTTP ====
    
    if Config.MODO_ESP32 == "http" or True:  # Sempre inicia API para consultas
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
    else:
        print("="*60)
        print("Sistema rodando! Pressione Ctrl+C para encerrar.")
        print("="*60 + "\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Encerrando sistema...")
    
    # ==== FINALIZAÇÃO ====
    
    if integrador:
        integrador.parar()
    
    monitor.parar()
    
    print(gerenciador.exportar_dados(Config.ARQUIVO_EXPORTACAO))
    print("✓ Sistema encerrado.\n")


if __name__ == "__main__":
    main()