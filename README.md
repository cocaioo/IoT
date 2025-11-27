# Sistema de Controle de Restaurante Universitário

Sistema modularizado para controle de entrada/saída de pessoas usando RFID (ESP32) e monitoramento de fila com câmera.

## Estrutura do Projeto

```
trabalho_TÓPICOSEMREDE/
├── main.py              # Ponto de entrada - orquestra todos os módulos
├── config.py            # Configurações centralizadas do sistema
├── models.py            # Modelos de dados (Registro)
├── gerenciador.py       # Lógica de gerenciamento do restaurante
├── esp32_serial.py      # Integração com ESP32 via serial
├── camera_monitor.py    # Monitoramento de fila com câmera
├── api.py               # API HTTP REST (Flask)
└── requirements.txt     # Dependências do projeto
```

## Módulos

### `models.py`
Contém as estruturas de dados:
- `Registro`: Representa uma entrada/saída com RFID, timestamp e tipo

### `gerenciador.py`
Classe `GerenciadorRestaurante` - núcleo do sistema:
- Registra entradas e saídas
- Controla pessoas dentro do restaurante
- Mantém histórico e estatísticas
- Gerencia contagem da fila
- Exporta dados para JSON

### `esp32_serial.py`
Classe `IntegradorESP32Serial`:
- Comunicação serial (USB) com ESP32
- Processa comandos ENTRADA/SAIDA/STATUS
- Envia respostas JSON para o ESP32

### `camera_monitor.py`
Classe `MonitorFilaCamera`:
- Usa OpenCV para detectar pessoas na fila
- Background subtraction para contagem
- Atualiza o gerenciador periodicamente

### `api.py`
API REST usando Flask:
- `POST /evento` - Registrar entrada/saída (para ESP32 via Wi-Fi)
- `GET /status` - Status atual do restaurante
- `GET /estatisticas` - Estatísticas do dia
- `GET /historico` - Histórico de registros

### `config.py`
Configurações centralizadas:
- Modo de integração ESP32 (serial/http/nenhum)
- Portas serial e HTTP
- Parâmetros da câmera
- Arquivo de exportação

### `main.py`
Orquestra todos os módulos:
- Inicializa o gerenciador
- Configura ESP32 (serial ou HTTP)
- Inicia monitor de câmera
- Sobe a API HTTP
- Exporta dados ao encerrar

## Como Usar

1. Ajuste as configurações em `config.py`
2. Execute: `python main.py`
3. O sistema iniciará conforme configurado

## Endpoints da API

- **Status**: `http://localhost:5000/status`
- **Estatísticas**: `http://localhost:5000/estatisticas?data=2025-11-26`
- **Histórico**: `http://localhost:5000/historico?limite=50`
- **Evento**: `POST http://localhost:5000/evento`
  ```json
  {
    "tipo": "ENTRADA",
    "rfid": "RFID_123"
  }
  ```

## Benefícios da Modularização

✅ **Legibilidade**: Cada módulo tem uma responsabilidade clara  
✅ **Manutenção**: Fácil localizar e modificar funcionalidades  
✅ **Testabilidade**: Módulos podem ser testados independentemente  
✅ **Reutilização**: Classes podem ser usadas em outros projetos  
✅ **Escalabilidade**: Novos módulos podem ser adicionados facilmente  
