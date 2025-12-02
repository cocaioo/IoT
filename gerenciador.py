"""
Gerenciador principal do Restaurante Universitário
"""

import datetime
import json
import threading
from typing import Dict, List, Optional
from collections import defaultdict

from models import Registro


class GerenciadorRestaurante:
    """Classe principal para gerenciar o restaurante"""
    
    def __init__(self):
        """Inicializa o gerenciador do restaurante"""
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
        
        # ← NOVO: Controle de tempo de permanência
        self.horarios_entrada: Dict[str, datetime.datetime] = {}  # rfid -> timestamp entrada
        self.tempos_permanencia: List[Dict] = []  # histórico de tempos
        
        self.lock = threading.Lock()
    
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
            
            # ← NOVO: Registra horário de entrada
            self.horarios_entrada[rfid] = timestamp
            
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
            
            # ← NOVO: Calcula tempo de permanência
            tempo_permanencia = None
            if rfid in self.horarios_entrada:
                entrada = self.horarios_entrada[rfid]
                duracao = timestamp - entrada
                tempo_permanencia = {
                    'rfid': rfid,
                    'entrada': entrada.isoformat(),
                    'saida': timestamp.isoformat(),
                    'duracao_segundos': int(duracao.total_seconds()),
                    'duracao_formatada': self._formatar_duracao(duracao)
                }
                self.tempos_permanencia.append(tempo_permanencia)
                del self.horarios_entrada[rfid]
                
                print(f"⏱️  Tempo de permanência: {tempo_permanencia['duracao_formatada']}")
            
            data_hoje = timestamp.date().isoformat()
            stats = self.estatisticas_diarias[data_hoje]
            stats['total_saidas'] += 1
            
            pessoas_atual = len(self.pessoas_dentro)
            print(f"✓ SAÍDA registrada: {rfid} | Pessoas dentro: {pessoas_atual}")
            
            return {
                'sucesso': True,
                'mensagem': 'Saída registrada com sucesso',
                'rfid': rfid,
                'timestamp': timestamp.isoformat(),
                'pessoas_dentro': pessoas_atual,
                'tempo_permanencia': tempo_permanencia
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
    
    def _formatar_duracao(self, duracao: datetime.timedelta) -> str:
        """Formata timedelta em string legível"""
        segundos_totais = int(duracao.total_seconds())
        horas = segundos_totais // 3600
        minutos = (segundos_totais % 3600) // 60
        segundos = segundos_totais % 60
        
        if horas > 0:
            return f"{horas}h {minutos}min {segundos}s"
        elif minutos > 0:
            return f"{minutos}min {segundos}s"
        else:
            return f"{segundos}s"
    
    def obter_tempos_permanencia(self, rfid: Optional[str] = None) -> List[Dict]:
        """
        Retorna histórico de tempos de permanência
        
        Args:
            rfid: Se especificado, retorna apenas os tempos desse RFID
        """
        with self.lock:
            if rfid:
                return [t for t in self.tempos_permanencia if t['rfid'] == rfid]
            return self.tempos_permanencia.copy()
    
    def obter_estatisticas_tempo(self) -> Dict:
        """Retorna estatísticas sobre tempos de permanência"""
        with self.lock:
            if not self.tempos_permanencia:
                return {
                    'total_visitas': 0,
                    'tempo_medio_segundos': 0,
                    'tempo_medio_formatado': '0s',
                    'tempo_minimo': None,
                    'tempo_maximo': None
                }
            
            duracoes = [t['duracao_segundos'] for t in self.tempos_permanencia]
            tempo_medio = sum(duracoes) / len(duracoes)
            
            return {
                'total_visitas': len(self.tempos_permanencia),
                'tempo_medio_segundos': int(tempo_medio),
                'tempo_medio_formatado': self._formatar_duracao(datetime.timedelta(seconds=tempo_medio)),
                'tempo_minimo_segundos': min(duracoes),
                'tempo_minimo_formatado': self._formatar_duracao(datetime.timedelta(seconds=min(duracoes))),
                'tempo_maximo_segundos': max(duracoes),
                'tempo_maximo_formatado': self._formatar_duracao(datetime.timedelta(seconds=max(duracoes)))
            }
    
    def exportar_dados(self, arquivo: str = 'dados_ru.json') -> str:
        """Exporta todos os dados para JSON"""
        with self.lock:
            dados = {
                'pessoas_dentro': list(self.pessoas_dentro),
                'historico': [reg.to_dict() for reg in self.historico],
                'estatisticas': dict(self.estatisticas_diarias),
                'pessoas_na_fila': self.pessoas_na_fila,
                'tempos_permanencia': self.tempos_permanencia,  # ← NOVO
                'estatisticas_tempo': self.obter_estatisticas_tempo(),  # ← NOVO
                'exportado_em': datetime.datetime.now().isoformat()
            }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            return f"Dados exportados para {arquivo}"