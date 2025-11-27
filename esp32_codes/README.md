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

## 📝 Como Usar - Passo a Passo Completo

### 🔧 **PARTE 1: Preparando o Arduino IDE**

#### 1️⃣ **Instale o Arduino IDE**
   - Baixe em: https://www.arduino.cc/en/software
   - Execute o instalador (Next, Next, Install...)
   - Abra o Arduino IDE

#### 2️⃣ **Adicione suporte para ESP32**
   
   **a)** Vá em: `Arquivo` → `Preferências`
   
   **b)** No campo **"URLs Adicionais para Gerenciadores de Placas"**, cole:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
   
   **c)** Clique em `OK`
   
   **d)** Vá em: `Ferramentas` → `Placa` → `Gerenciador de Placas...`
   
   **e)** Procure por **"esp32"** e instale **"esp32 by Espressif Systems"**
   
   **f)** Aguarde o download terminar (pode demorar alguns minutos)

#### 3️⃣ **Instale as bibliotecas necessárias**
   
   **Para códigos com RFID** (`esp32_serial_rfid.ino` e `esp32_http_rfid.ino`):
   
   - `Sketch` → `Incluir Biblioteca` → `Gerenciar Bibliotecas...`
   - Procure e instale:
     - **MFRC522** (by GithubCommunity)
     - **ArduinoJson** (by Benoit Blanchon) - apenas para HTTP
   
   **Para código simples** (`esp32_teste_simples.ino`):
   - ✅ Não precisa instalar nada! Já funciona!

---

### 🎯 **PARTE 2: Gravando o código no ESP32**

#### 4️⃣ **Abra o código .ino**
   
   - No Arduino IDE: `Arquivo` → `Abrir...`
   - Navegue até a pasta `esp32_codes/`
   - **Recomendado para começar:** `esp32_teste_simples.ino`

#### 5️⃣ **Conecte o ESP32 ao computador**
   
   - Conecte o ESP32 via **cabo USB**
   - O Windows deve instalar o driver automaticamente
   
   **⚠️ Se a porta COM não aparecer:**
   - Seu ESP32 provavelmente usa chip CP210x ou CH340
   - Baixe o driver apropriado:
     - **CP210x**: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
     - **CH340**: http://www.wch.cn/downloads/CH341SER_EXE.html

#### 6️⃣ **Configure a placa e porta**
   
   **a)** `Ferramentas` → `Placa` → `ESP32 Arduino` → **"ESP32 Dev Module"**
   
   **b)** `Ferramentas` → `Porta` → Selecione a porta COM (ex: COM3, COM4, COM5...)
   
   **c)** Mantenha as outras configurações padrão

#### 7️⃣ **Faça o Upload! 🚀**
   
   - Clique no botão **→** (Upload) no canto superior esquerdo
   - Aguarde compilar (você verá: "Compilando...")
   - Aguarde fazer upload (verá: "Uploading...")
   - Se pedir, **segure o botão BOOT** no ESP32 durante o upload
   - Quando terminar, verá: **"Hard resetting via RTS pin..."**
   - ✅ **Pronto! Código gravado com sucesso!**

#### 8️⃣ **Abra o Monitor Serial para testar**
   
   - `Ferramentas` → `Monitor Serial` (ou Ctrl+Shift+M)
   - Configure para **115200 baud** (menu suspenso no canto inferior direito)
   - Você deve ver mensagens do ESP32!

---

### 💻 **PARTE 3: Configure o Python**

#### 9️⃣ **Configure o arquivo `config.py`**
   
   Volte para a pasta raiz do projeto e edite `config.py`:
   
   **Para modo SERIAL** (cabo USB):
   ```python
   MODO_ESP32 = "serial"
   PORTA_SERIAL = "COM3"  # Ajuste para sua porta (veja no Arduino IDE)
   BAUDRATE = 115200
   ```
   
   **Para modo HTTP** (Wi-Fi):
   ```python
   MODO_ESP32 = "http"
   HTTP_HOST = "0.0.0.0"
   HTTP_PORT = 5000
   ```
   
   **⚠️ Lembre-se:** Se usar HTTP, configure Wi-Fi e IP no código `.ino` antes de fazer upload!

#### 🔟 **Execute o sistema Python**
   
   Abra um terminal na pasta do projeto e execute:
   ```bash
   python main.py
   ```
   
   Você deve ver:
   ```
   ============================================
     SISTEMA DE CONTROLE - RESTAURANTE UNIVERSITÁRIO
   ============================================
   
   ✓ Gerenciador inicializado
   📡 Aguardando comandos do ESP32...
   ```

---

### 🎉 **PARTE 4: Testando o Sistema Completo**

#### 1️⃣ **Com `esp32_teste_simples.ino`:**
   - Pressione o **botão ENTRADA** (GPIO 15)
   - Veja no Monitor Serial: `ENTRADA:RFID_A`
   - Veja no Python: `✓ ENTRADA registrada: RFID_A | Pessoas dentro: 1`
   - Pressione novamente: agora será `RFID_B`
   - Pressione **botão SAÍDA** (GPIO 4) para registrar saída

#### 2️⃣ **Com códigos RFID:**
   - Aproxime um cartão RFID do leitor
   - Segure o **botão ENTRADA** ou **SAÍDA**
   - O sistema registra automaticamente!

#### 3️⃣ **Consulte a API:**
   
   Abra o navegador em:
   - **Status:** http://localhost:5000/status
   - **Estatísticas:** http://localhost:5000/estatisticas
   - **Histórico:** http://localhost:5000/historico

---

### 🔍 **Fluxo Completo Resumido:**

```
1. Instala Arduino IDE
2. Adiciona suporte ESP32
3. Instala bibliotecas (se necessário)
4. Abre código .ino no Arduino IDE
5. Conecta ESP32 via USB
6. Seleciona placa "ESP32 Dev Module"
7. Seleciona porta COM
8. Clica em Upload (→)
9. Abre Monitor Serial (115200 baud)
10. Configura config.py no Python
11. Executa python main.py
12. Pressiona botões no ESP32
13. Vê registros acontecendo em tempo real! 🎊
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

## ⚠️ **Problemas Comuns e Soluções**

| Problema | Solução |
|----------|---------|
| 🔴 Porta COM não aparece no Arduino IDE | Instale o driver: CP210x ou CH340 (links acima) |
| 🔴 Erro "A fatal error occurred: Failed to connect" | Segure o botão **BOOT** no ESP32 durante upload |
| 🔴 Monitor Serial mostra caracteres estranhos | Configure para **115200 baud** |
| 🔴 "Connecting..." infinito | Aperte o botão **RST** no ESP32 |
| 🔴 Python não detecta serial | Verifique a porta em `config.py` (mesma do Arduino IDE) |
| 🔴 Wi-Fi não conecta (modo HTTP) | Verifique SSID e senha no código `.ino` |
| 🔴 RFID não lê cartão | Confira conexões SPI (tabela acima) |
| 🔴 Botão não funciona | Use resistor pull-up ou `INPUT_PULLUP` |

---

## 🎯 **Qual código usar?**

| Situação | Código Recomendado |
|----------|-------------------|
| 🎓 **Apenas testando/aprendendo** | `esp32_teste_simples.ino` |
| 🏃 **Não tem RFID ainda** | `esp32_teste_simples.ino` |
| 💳 **Tem RFID + cabo USB** | `esp32_serial_rfid.ino` |
| 📡 **Tem RFID + quer Wi-Fi** | `esp32_http_rfid.ino` |
| ⚡ **Quer o mais rápido** | `esp32_serial_rfid.ino` (serial é mais rápido) |
| 🌐 **Precisa de mobilidade** | `esp32_http_rfid.ino` (sem fio) |

---

## 🎯 Compatibilidade

Todos os códigos são **100% compatíveis** com o sistema Python modularizado!

- ✅ `models.py`
- ✅ `gerenciador.py`
- ✅ `esp32_serial.py`
- ✅ `api.py`
- ✅ `config.py`
