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
- **⏱️ Calcula tempo de permanência de cada pessoa**
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
- **⏱️ `GET /tempos` - Tempos de permanência (todos ou por RFID)**
- **⏱️ `GET /estatisticas-tempo` - Estatísticas de tempo (média, mín, máx)**

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

### 📊 **Controle e Status**
- **Status atual**: `http://localhost:5000/status`
  - Retorna pessoas dentro, fila, RFIDs ativos

- **Estatísticas diárias**: `http://localhost:5000/estatisticas?data=2025-11-30`
  - Total de entradas/saídas, pico de pessoas, horários de pico

- **Histórico**: `http://localhost:5000/historico?limite=50`
  - Últimos N registros de entrada/saída

### ⏱️ **Tempo de Permanência** (NOVO!)

- **Tempos de permanência**: `http://localhost:5000/tempos`
  - Lista todos os tempos de permanência registrados
  - **Filtrar por pessoa**: `http://localhost:5000/tempos?rfid=RFID_001`
  
  **Exemplo de resposta:**
  ```json
  [
    {
      "rfid": "RFID_001",
      "entrada": "2025-11-30T14:30:15.123456",
      "saida": "2025-11-30T15:15:45.789012",
      "duracao_segundos": 2730,
      "duracao_formatada": "45min 30s"
    }
  ]
  ```

- **Estatísticas de tempo**: `http://localhost:5000/estatisticas-tempo`
  - Tempo médio, mínimo e máximo de permanência
  
  **Exemplo de resposta:**
  ```json
  {
    "total_visitas": 10,
    "tempo_medio_segundos": 1800,
    "tempo_medio_formatado": "30min 0s",
    "tempo_minimo_segundos": 600,
    "tempo_minimo_formatado": "10min 0s",
    "tempo_maximo_segundos": 3600,
    "tempo_maximo_formatado": "1h 0min 0s"
  }
  ```

### 📝 **Registro de Eventos**
- **Evento**: `POST http://localhost:5000/evento`
  ```json
  {
    "tipo": "ENTRADA",
    "rfid": "RFID_123"
  }
  ```
  
  **Resposta de SAÍDA (inclui tempo):**
  ```json
  {
    "sucesso": true,
    "mensagem": "Saída registrada com sucesso",
    "rfid": "RFID_001",
    "timestamp": "2025-11-30T15:15:45.789012",
    "pessoas_dentro": 0,
    "tempo_permanencia": {
      "rfid": "RFID_001",
      "entrada": "2025-11-30T14:30:15.123456",
      "saida": "2025-11-30T15:15:45.789012",
      "duracao_segundos": 2730,
      "duracao_formatada": "45min 30s"
    }
  }
  ```

## Benefícios da Modularização

✅ **Legibilidade**: Cada módulo tem uma responsabilidade clara  
✅ **Manutenção**: Fácil localizar e modificar funcionalidades  
✅ **Testabilidade**: Módulos podem ser testados independentemente  
✅ **Reutilização**: Classes podem ser usadas em outros projetos  
✅ **Escalabilidade**: Novos módulos podem ser adicionados facilmente  

## 📦 Dados Exportados (`dados_ru.json`)

Ao encerrar o sistema (Ctrl+C), é gerado automaticamente um arquivo JSON com:

```json
{
  "pessoas_dentro": ["RFID_002"],
  "historico": [
    {
      "rfid": "RFID_001",
      "timestamp": "2025-11-30T14:30:15.123456",
      "tipo": "entrada"
    },
    {
      "rfid": "RFID_001",
      "timestamp": "2025-11-30T15:15:45.789012",
      "tipo": "saida"
    }
  ],
  "estatisticas": {
    "2025-11-30": {
      "total_entradas": 5,
      "total_saidas": 4,
      "pico_pessoas": 3,
      "horarios_pico": ["14:45:30"]
    }
  },
  "pessoas_na_fila": 2,
  "tempos_permanencia": [
    {
      "rfid": "RFID_001",
      "entrada": "2025-11-30T14:30:15.123456",
      "saida": "2025-11-30T15:15:45.789012",
      "duracao_segundos": 2730,
      "duracao_formatada": "45min 30s"
    }
  ],
  "estatisticas_tempo": {
    "total_visitas": 4,
    "tempo_medio_segundos": 1800,
    "tempo_medio_formatado": "30min 0s",
    "tempo_minimo_segundos": 600,
    "tempo_minimo_formatado": "10min 0s",
    "tempo_maximo_segundos": 2730,
    "tempo_maximo_formatado": "45min 30s"
  },
  "exportado_em": "2025-11-30T16:00:00.000000"
}
```

### 🔍 Estrutura dos dados:

- **`pessoas_dentro`**: RFIDs atualmente no RU
- **`historico`**: Todos os registros de entrada/saída
- **`estatisticas`**: Dados diários (entradas, saídas, pico)
- **`pessoas_na_fila`**: Último valor da câmera
- **⏱️ `tempos_permanencia`**: Todos os tempos calculados
- **⏱️ `estatisticas_tempo`**: Médias e análises de tempo
- **`exportado_em`**: Timestamp da exportação  
