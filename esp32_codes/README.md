# Códigos para ESP32

Esta pasta contém os códigos Arduino/ESP32 para integração com o sistema de controle do restaurante.

## 📁 Arquivos Disponíveis

### 1. `esp32_serial_rfid.ino` 
**Comunicação Serial (USB) + RFID RC522**

- ✅ Usa módulo RFID RC522
- ✅ 2 botões para definir ENTRADA/SAÍDA
- ✅ Comunicação via cabo USB
- 🔧 Compatível com `config.py` → `MODO_ESP32 = "serial"`

**Hardware necessário:**
- ESP32
- Módulo RFID RC522
- 2x Botões
- Cabos jumper

---

### 2. `esp32_http_rfid.ino`
**Comunicação HTTP (Wi-Fi) + RFID RC522**

- ✅ Usa módulo RFID RC522
- ✅ 2 botões para definir ENTRADA/SAÍDA
- ✅ Comunicação via Wi-Fi
- ✅ Envia dados JSON para API
- 🔧 Compatível com `config.py` → `MODO_ESP32 = "http"`

**Hardware necessário:**
- ESP32
- Módulo RFID RC522
- 2x Botões
- Rede Wi-Fi

**⚠️ Antes de usar, configure:**
```cpp
const char* WIFI_SSID = "SEU_WIFI_AQUI";
const char* WIFI_PASSWORD = "SUA_SENHA_AQUI";
const char* SERVER_URL = "http://192.168.1.100:5000/evento"; // Seu IP
```

---

### 3. `esp32_teste_simples.ino` ⭐ **Recomendado para começar**
**Teste Simples SEM RFID - Apenas Botões**

- ✅ Apenas 2 botões
- ✅ Simula 2 RFIDs fixos (`RFID_A` e `RFID_B`)
- ✅ Alterna automaticamente entre os RFIDs
- ✅ Comunicação via cabo USB
- 🔧 Compatível com `config.py` → `MODO_ESP32 = "serial"`

**Hardware necessário:**
- ESP32
- 2x Botões (ou até pode usar sem!)

**💡 Perfeito para testar o sistema antes de ter o RFID!**

---

## 🔌 Conexões RFID RC522 (para códigos 1 e 2)

| Pino RC522 | Pino ESP32 |
|------------|------------|
| SDA        | GPIO 5     |
| SCK        | GPIO 18    |
| MOSI       | GPIO 23    |
| MISO       | GPIO 19    |
| RST        | GPIO 22    |
| GND        | GND        |
| 3.3V       | 3.3V       |

## 🔘 Conexões dos Botões (todos os códigos)

| Componente      | Pino ESP32 |
|-----------------|------------|
| Botão ENTRADA   | GPIO 15    |
| Botão SAÍDA     | GPIO 4     |
| LED Built-in    | GPIO 2     |

**Esquema do botão:**
```
GPIO -> Botão -> GND
(usa pull-up interno)
```

---

## 📝 Como Usar

### 1️⃣ **Instale o Arduino IDE**
   - Download: https://www.arduino.cc/en/software

### 2️⃣ **Adicione suporte ESP32**
   - Arquivo → Preferências
   - URLs Adicionais: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Ferramentas → Placa → Gerenciador → Instale "ESP32"

### 3️⃣ **Instale bibliotecas necessárias**
   
   **Para códigos com RFID:**
   - Sketch → Incluir Biblioteca → Gerenciar Bibliotecas
   - Instale: `MFRC522` (por GithubCommunity)
   
   **Para código HTTP:**
   - Instale também: `ArduinoJson` (por Benoit Blanchon)

### 4️⃣ **Configure o Python**
   
   No arquivo `config.py`:
   
   **Para modo SERIAL:**
   ```python
   MODO_ESP32 = "serial"
   PORTA_SERIAL = "COM3"  # Windows
   # PORTA_SERIAL = "/dev/ttyUSB0"  # Linux
   ```
   
   **Para modo HTTP:**
   ```python
   MODO_ESP32 = "http"
   HTTP_PORT = 5000
   ```

### 5️⃣ **Faça upload do código**
   - Conecte o ESP32 via USB
   - Selecione a placa: "ESP32 Dev Module"
   - Selecione a porta COM correta
   - Clique em "Upload" (→)

### 6️⃣ **Execute o sistema Python**
   ```bash
   python main.py
   ```

---

## 🧪 Testando

### Modo SERIAL:
1. Upload do código no ESP32
2. Execute `python main.py`
3. Pressione os botões ou aproxime cartões RFID
4. Veja os eventos sendo registrados!

### Modo HTTP:
1. Configure Wi-Fi e IP no código
2. Upload do código no ESP32
3. Execute `python main.py`
4. ESP32 conectará ao Wi-Fi automaticamente
5. Pressione botões ou aproxime cartões

---

## 💡 Dicas

- **Comece com `esp32_teste_simples.ino`** - não precisa de RFID!
- **LED built-in pisca:** 1x = ENTRADA, 2x = SAÍDA
- **Monitor Serial:** Configure para 115200 baud
- **Problemas com RFID?** Confira as conexões SPI
- **Wi-Fi não conecta?** Verifique SSID e senha

---

## 🎯 Compatibilidade

Todos os códigos são **100% compatíveis** com o sistema Python modularizado!

- ✅ `models.py`
- ✅ `gerenciador.py`
- ✅ `esp32_serial.py`
- ✅ `api.py`
- ✅ `config.py`
