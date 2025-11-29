"""
Gerenciador principal do Restaurante Universitário
"""

import datetime
import json
import threading
from typing import Dict, List, Optional
from collections import defaultdict

from models import Registro
from webcam_captura import CapturaWebcam  # ← NOVO IMPORT


class GerenciadorRestaurante:
    """Classe principal para gerenciar o restaurante"""
    
    def __init__(self, habilitar_fotos: bool = True, camera_index: int = 0):
        """
        Args:
            habilitar_fotos: Se True, captura foto da webcam a cada entrada/saída
            camera_index: Índice da webcam (0 = padrão)
        """
        self.pessoas_dentro: set = set()
        self.historico: List[Registro] = []
        self.estatisticas_diarias = defaultdict(lambda: {
            'total_entradas': 0,
            'total_saidas': 0,
            'pico_pessoas': 0,
            'horarios_pico': []
        })
        
        # Controle da fila
        self.pessoas_na_fila: int = 0
        self.ultima_atualizacao_fila: Optional[datetime.datetime] = None
        
        self.lock = threading.Lock()
        
        # ← NOVO: Módulo de captura de fotos
        self.habilitar_fotos = habilitar_fotos
        if self.habilitar_fotos:
            self.captura = CapturaWebcam(camera_index=camera_index)
        else:
            self.captura = None
            print("⚠ Captura de fotos desabilitada")
    
    def registrar_entrada(self, rfid: str) -> Dict:
        """Registra entrada de uma pessoa"""
        with self.lock:
            timestamp = datetime.datetime.now()
            
            if rfid in self.pessoas_dentro:
                return {
                    'sucesso': False,
                    'mensagem': 'Pessoa já está dentro do restaurante',
                    'rfid': rfid
                }
            
            self.pessoas_dentro.add(rfid)
            registro = Registro(rfid, timestamp, 'entrada')
            self.historico.append(registro)
            
            data_hoje = timestamp.date().isoformat()
            stats = self.estatisticas_diarias[data_hoje]
            stats['total_entradas'] += 1
            
            pessoas_atual = len(self.pessoas_dentro)
            if pessoas_atual > stats['pico_pessoas']:
                stats['pico_pessoas'] = pessoas_atual
                stats['horarios_pico'] = [timestamp.strftime('%H:%M:%S')]
            elif pessoas_atual == stats['pico_pessoas']:
                stats['horarios_pico'].append(timestamp.strftime('%H:%M:%S'))
            
            print(f"✓ ENTRADA registrada: {rfid} | Pessoas dentro: {pessoas_atual}")
            
            # ← NOVO: Captura foto da webcam
            if self.captura:
                self.captura.capturar_foto(rfid, "entrada")
            
            return {
                'sucesso': True,
                'mensagem': 'Entrada registrada com sucesso',
                'rfid': rfid,
                'timestamp': timestamp.isoformat(),
                'pessoas_dentro': pessoas_atual
            }
    
    def registrar_saida(self, rfid: str) -> Dict:
        """Registra saída de uma pessoa"""
        with self.lock:
            timestamp = datetime.datetime.now()
            
            if rfid not in self.pessoas_dentro:
                return {
                    'sucesso': False,
                    'mensagem': 'Pessoa não está dentro do restaurante',
                    'rfid': rfid
                }
            
            self.pessoas_dentro.remove(rfid)
            registro = Registro(rfid, timestamp, 'saida')
            self.historico.append(registro)
            
            data_hoje = timestamp.date().isoformat()
            stats = self.estatisticas_diarias[data_hoje]
            stats['total_saidas'] += 1
            
            pessoas_atual = len(self.pessoas_dentro)
            print(f"✓ SAÍDA registrada: {rfid} | Pessoas dentro: {pessoas_atual}")
            
            # ← NOVO: Captura foto da webcam
            if self.captura:
                self.captura.capturar_foto(rfid, "saida")
            
            return {
                'sucesso': True,
                'mensagem': 'Saída registrada com sucesso',
                'rfid': rfid,
                'timestamp': timestamp.isoformat(),
                'pessoas_dentro': pessoas_atual
            }
    
    def obter_status_atual(self) -> Dict:
        """Retorna status atual do restaurante"""
        with self.lock:
            return {
                'pessoas_dentro': len(self.pessoas_dentro),
                'rfids_dentro': list(self.pessoas_dentro),
                'pessoas_na_fila': self.pessoas_na_fila,
                'ultima_atualizacao_fila': self.ultima_atualizacao_fila.isoformat()
                if self.ultima_atualizacao_fila else None,
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def obter_estatisticas(self, data: Optional[str] = None) -> Dict:
        """Retorna estatísticas do dia"""
        if data is None:
            data = datetime.date.today().isoformat()
        
        with self.lock:
            stats = self.estatisticas_diarias.get(data, {
                'total_entradas': 0,
                'total_saidas': 0,
                'pico_pessoas': 0,
                'horarios_pico': []
            })
            
            return {
                'data': data,
                'estatisticas': stats,
                'pessoas_dentro_agora': len(self.pessoas_dentro),
                'pessoas_na_fila_agora': self.pessoas_na_fila
            }
    
    def obter_historico(self, limite: int = 100) -> List[Dict]:
        """Retorna histórico de registros"""
        with self.lock:
            return [reg.to_dict() for reg in self.historico[-limite:]]
    
    def atualizar_fila(self, qtd: int):
        """Atualiza contagem de pessoas na fila (chamado pela câmera)"""
        with self.lock:
            self.pessoas_na_fila = max(0, int(qtd))
            self.ultima_atualizacao_fila = datetime.datetime.now()
    
    def exportar_dados(self, arquivo: str = 'dados_ru.json') -> str:
        """Exporta todos os dados para JSON"""
        with self.lock:
            dados = {
                'pessoas_dentro': list(self.pessoas_dentro),
                'historico': [reg.to_dict() for reg in self.historico],
                'estatisticas': dict(self.estatisticas_diarias),
                'pessoas_na_fila': self.pessoas_na_fila,
                'exportado_em': datetime.datetime.now().isoformat()
            }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            return f"Dados exportados para {arquivo}"