"""
Configurações do sistema de controle do restaurante
"""


class Config:
    """Configurações centralizadas do sistema"""
    
    # ==== INTEGRAÇÃO COM ESP32 ====
    # Opções: "serial", "http" ou "nenhum"
    MODO_ESP32 = "http"
    
    # Configurações para modo SERIAL
    PORTA_SERIAL = "COM7"
    BAUDRATE = 115200
    
    # Configurações para modo HTTP
    HTTP_HOST = "0.0.0.0"
    HTTP_PORT = 5000
    
    # ==== CÂMERA - MONITORAMENTO DE FILA ====
    HABILITAR_CAMERA = False  # True para ativar monitoramento de fila (contagem de pessoas)
    CAMERA_INDEX = 0    # 0 = webcam padrão
    INTERVALO_CAMERA_SEGUNDOS = 3  # Intervalo entre atualizações
    
    # Parâmetros de detecção
    AREA_MINIMA_PESSOA = 1500  # Área mínima para considerar como pessoa
    
    # ==== CAPTURA DE FOTOS (WEBCAM) ====  ← NOVO
    HABILITAR_FOTOS = False  # True para capturar foto da webcam a cada entrada/saída
    CAMERA_FOTOS_INDEX = 0  # 0 = webcam padrão (pode ser diferente da câmera de fila)
    
    # ==== EXPORTAÇÃO DE DADOS ====
    ARQUIVO_EXPORTACAO = "dados_ru.json"