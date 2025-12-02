# Sistema de Controle - Restaurante Universitário

Sistema para controle de entrada/saída usando RFID (ESP32) com monitoramento de fila por câmera.

## Arquivos

```
├── main.py              # Inicia o sistema
├── config.py            # Configurações
├── models.py            # Estruturas de dados
├── gerenciador.py       # Controle de entradas/saídas
├── esp32_serial.py      # Comunicação serial com ESP32
├── api.py               # API REST (Flask)
├── camera_monitor.py    # Detecção de pessoas na fila
└── webcam_captura.py    # Captura de fotos/vídeos
```

## Funcionalidades

- Registro de entradas/saídas via RFID
- Cálculo automático de tempo de permanência
- Dashboard web em tempo real
- Detecção de fila por câmera (HOG+SVM)
- Exportação de dados em JSON
- Simulador para testes

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

Configure em `config.py`:
- Modo ESP32 (serial/http)
- Porta serial ou IP do servidor
- Habilitar/desabilitar câmera

Execute:
```bash
python main.py
```

## Dashboard

Acesse `http://localhost:5000` para visualizar:
- Pessoas dentro do restaurante
- Fila detectada pela câmera
- Histórico de entradas/saídas
- Tempos de permanência

## API REST

### Status
```
GET /status
```
Retorna pessoas dentro, fila e RFIDs ativos.

### Registro de evento
```
POST /evento
Content-Type: application/json

{
  "tipo": "ENTRADA",
  "rfid": "RFID_123"
}
```

### Histórico
```
GET /historico?limite=50
```

### Tempos de permanência
```
GET /tempos
GET /tempos?rfid=RFID_123
GET /estatisticas-tempo
```

## ESP32 - Modo HTTP

Configure no arquivo `.ino`:
```cpp
#define MODO_HTTP true
const char* ssid = "IoT";
const char* password = "tudoehiot";
const char* SERVER_URL = "http://10.191.217.193:5000/evento";
```

Ao aproximar cartão RFID, o ESP32 envia POST com JSON.

## ESP32 - Modo Serial

Configure `MODO_HTTP = false` no ESP32 e `MODO_ESP32 = "serial"` em `config.py`.

Comandos via Serial Monitor:
- `E` - Simula entrada
- `S` - Simula saída

## Exportação de Dados

Ao encerrar (Ctrl+C), é gerado `dados_ru.json`:

```json
{
  "pessoas_dentro": ["RFID_002"],
  "historico": [...],
  "estatisticas": {...},
  "tempos_permanencia": [...],
  "exportado_em": "2025-11-30T16:00:00"
}
```

## Hardware

- ESP32 DevKit
- MFRC522 (RFID)
- Webcam (qualquer)

Pinagem MFRC522:
```
SDA  -> GPIO 21
SCK  -> GPIO 18
MOSI -> GPIO 23
MISO -> GPIO 19
RST  -> GPIO 22
```

## Observações

- Dashboard atualiza a cada 3 segundos
- Câmera usa detector HOG+SVM (melhor performance)
- Suporta múltiplos cartões simultâneos
- Thread-safe para operações concorrentes  
