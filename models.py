"""
Modelos de dados para o Sistema de Controle de Restaurante Universitário
"""

import datetime
from dataclasses import dataclass


@dataclass
class Registro:
    """Representa um registro de entrada/saída"""
    rfid: str
    timestamp: datetime.datetime
    tipo: str  # 'entrada' ou 'saida'

    def to_dict(self):
        """Converte o registro para dicionário"""
        return {
            'rfid': self.rfid,
            'timestamp': self.timestamp.isoformat(),
            'tipo': self.tipo
        }
