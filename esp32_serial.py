"""
Integração com ESP32 via comunicação serial (USB)
"""

import json
import threading
import time
import queue
from typing import Dict

from gerenciador import GerenciadorRestaurante


class IntegradorESP32Serial:
    """Integração com ESP32 via porta serial (USB)"""
    
    def __init__(self, gerenciador: GerenciadorRestaurante, 
                 porta: str = '/dev/ttyUSB0', 
                 baudrate: int = 115200):
        self.gerenciador = gerenciador
        self.porta = porta
        self.baudrate = baudrate
        self.ativo = False
        self.serial = None
        self.fila_comandos = queue.Queue()  # Fila para comandos E/S
    
    def iniciar(self):
        """Inicia comunicação serial"""
        try:
            import serial
            self.serial = serial.Serial(self.porta, self.baudrate, timeout=1)
            self.ativo = True
            print(f"✓ Conexão serial estabelecida em {self.porta}")
            
            # Thread para ler dados continuamente
            thread = threading.Thread(target=self._loop_leitura, daemon=True)
            thread.start()
            
            return True
        
        except ImportError:
            print("❌ Biblioteca pyserial não instalada!")
            print("   Instale com: pip install pyserial")
            return False
        except Exception as e:
            print(f"❌ Erro ao conectar serial: {e}")
            print(f"   Verifique se a porta {self.porta} está correta")
            print("   No Windows use algo como 'COM3', no Linux '/dev/ttyUSB0'")
            return False
    
    def _loop_leitura(self):
        """Loop que lê comandos do ESP32 e envia comandos da fila"""
        print("📡 Aguardando comandos do ESP32...\n")
        
        while self.ativo:
            try:
                # Envia comandos E/S se houver na fila
                if not self.fila_comandos.empty():
                    comando = self.fila_comandos.get()
                    self.serial.write(comando.encode())
                    self.serial.flush()
                    print(f"[Python → ESP32] Comando enviado: {comando}")
                
                # Lê do ESP32
                if self.serial.in_waiting:
                    linha = self.serial.readline().decode('utf-8').strip()
                    
                    if linha and not linha.startswith('='):  # Ignora linhas decorativas
                        print(f"[ESP32 → Python] {linha}")
                        self._processar_comando(linha)
            
            except Exception as e:
                print(f"❌ Erro ao ler/escrever serial: {e}")
            
            time.sleep(0.05)
    
    def _processar_comando(self, comando: str):
        """Processa comando recebido do ESP32"""
        try:
            # Formato: "ENTRADA:RFID_123" ou "SAIDA:RFID_456"
            if ':' not in comando:
                return
            
            partes = comando.split(':', 1)
            if len(partes) != 2:
                return
            
            tipo, rfid = partes
            tipo = tipo.strip().upper()
            rfid = rfid.strip()
            
            resultado = None
            
            if tipo == 'ENTRADA':
                resultado = self.gerenciador.registrar_entrada(rfid)
            elif tipo == 'SAIDA':
                resultado = self.gerenciador.registrar_saida(rfid)
            elif tipo == 'STATUS':
                resultado = self.gerenciador.obter_status_atual()
            
            if resultado:
                self._enviar_resposta(resultado)
        
        except Exception as e:
            print(f"❌ Erro ao processar comando: {e}")
    
    def _enviar_resposta(self, resposta: Dict):
        """Envia resposta JSON para o ESP32"""
        try:
            mensagem = json.dumps(resposta, ensure_ascii=False) + '\n'
            self.serial.write(mensagem.encode('utf-8'))
            print(f"[Python → ESP32] {resposta.get('mensagem', 'OK')}")
        
        except Exception as e:
            print(f"❌ Erro ao enviar resposta: {e}")
    
    def enviar_comando_esp32(self, comando: str):
        """Adiciona comando E ou S na fila para enviar ao ESP32"""
        if self.ativo and self.serial:
            self.fila_comandos.put(comando)
        else:
            print("❌ Serial não está ativa para enviar comandos.")
    
    def parar(self):
        """Para a comunicação serial"""
        self.ativo = False
        if self.serial:
            self.serial.close()
        print("Serial encerrada.")