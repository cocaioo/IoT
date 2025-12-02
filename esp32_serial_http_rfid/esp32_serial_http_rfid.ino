/*
 * ESP32 - Sistema de Controle de Restaurante
 * Modo: DUAL (SERIAL + HTTP)
 * 
 * Hardware necessário:
 * - ESP32
 * - Módulo RFID RC522
 * 
 * Conexões RFID RC522:
 * SDA  -> GPIO 21
 * SCK  -> GPIO 18
 * MOSI -> GPIO 23
 * MISO -> GPIO 19
 * RST  -> GPIO 22
 * GND  -> GND
 * 3.3V -> 3.3V
 * 
 * LÓGICA MODO SERIAL:
 * - Python (PC) envia um caractere pela serial:
 *    'E' -> próxima leitura de cartão será ENTRADA
 *    'S' -> próxima leitura de cartão será SAIDA
 * - ESP32 aguarda um cartão RFID
 * - Quando um cartão é lido, o ESP32 envia:
 *    "ENTRADA:RFID_xxxxx"  ou  "SAIDA:RFID_xxxxx"
 * 
 * LÓGICA MODO HTTP:
 * - Mesma lógica de E/S via serial
 * - Envia evento via HTTP POST para o servidor Python
 */

#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============================================================
// CONFIGURAÇÃO: ESCOLHA O MODO AQUI
// ============================================================
#define MODO_HTTP true  // true = envia via HTTP | false = envia via Serial

// ============================================================
// CONFIGURAÇÕES Wi-Fi (somente para MODO_HTTP = true)
// ============================================================
const char* WIFI_SSID = "IoT";
const char* WIFI_PASSWORD = "tudoehiot";
const char* SERVER_URL = "http://10.191.217.193:5000/evento";

#define SS_PIN 21
#define RST_PIN 22

// LED de status (built-in)
#define LED_PIN 2

MFRC522 rfid(SS_PIN, RST_PIN);

// Modo atual de operação: "ENTRADA" ou "SAIDA"
String modoAtual = "ENTRADA";

String ultimoRFID = "";
unsigned long ultimaLeitura = 0;
const unsigned long INTERVALO_LEITURA = 2000; // 2 segundos entre leituras do mesmo cartão

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Inicializa SPI e RFID
  SPI.begin();
  rfid.PCD_Init();
  
  // Configura LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("===========================================");
  Serial.println("  ESP32 - Sistema de Controle de Restaurante");
  
  if (MODO_HTTP) {
    Serial.println("  Modo: HTTP (Wi-Fi)");
    Serial.println("===========================================");
    conectarWiFi();
  } else {
    Serial.println("  Modo: SERIAL (USB)");
    Serial.println("===========================================");
  }
  
  Serial.println("Use:");
  Serial.println("  'E' para marcar próxima leitura como ENTRADA");
  Serial.println("  'S' para marcar próxima leitura como SAIDA");
  Serial.println();
  Serial.println("Modo atual: ENTRADA");
  Serial.println("Aguardando comandos do PC e cartões RFID...\n");
}

void loop() {
  // Verifica conexão Wi-Fi (se estiver em modo HTTP)
  if (MODO_HTTP && WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠ Wi-Fi desconectado! Reconectando...");
    conectarWiFi();
  }
  
  // 1) Verifica se chegou algum comando do PC (Python/teclado)
  bool mudouModo = false;  // flag pra saber se mudou de E/S neste ciclo

  while (Serial.available()) {
    char comando = Serial.read();
    if (comando == 'E') {
      modoAtual = "ENTRADA";
      Serial.println(">> Modo alterado para ENTRADA");
      mudouModo = true;
    } else if (comando == 'S') {
      modoAtual = "SAIDA";
      Serial.println(">> Modo alterado para SAIDA");
      mudouModo = true;
    }
  }

  // Se acabou de mudar de modo, NÃO processa cartão neste ciclo
  if (mudouModo) {
    delay(50);  // pequeno respiro
    return;
  }

  // 2) Verifica se há um cartão presente
  if (!rfid.PICC_IsNewCardPresent()) {
    delay(50);
    return;
  }
  
  // 3) Tenta ler o cartão
  if (!rfid.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }
  
  String rfidID = obterRFID();
  unsigned long agora = millis();
  
  if (rfidID != ultimoRFID || (agora - ultimaLeitura) > INTERVALO_LEITURA) {
    ultimoRFID = rfidID;
    ultimaLeitura = agora;
    
    // Envia evento conforme o modo atual (SERIAL ou HTTP)
    enviarEvento(modoAtual, rfidID);
    piscarLED(modoAtual == "ENTRADA" ? 1 : 2);
    
    Serial.println("✓ Cartão processado como " + modoAtual + "\n");
  }
  
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  
  delay(100);
}


void conectarWiFi() {
  Serial.print("Conectando ao Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ Wi-Fi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ Falha ao conectar Wi-Fi!");
  }
}

String obterRFID() {
  String conteudo = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      conteudo += "0";  // Adiciona zero à esquerda se necessário
    }
    conteudo += String(rfid.uid.uidByte[i], HEX);
  }
  conteudo.toUpperCase();
  return "RFID_" + conteudo;
}

void enviarEvento(String tipo, String rfid) {
  if (MODO_HTTP) {
    // Modo HTTP: envia via POST
    enviarEventoHTTP(tipo, rfid);
  } else {
    // Modo Serial: envia no formato "TIPO:RFID"
    Serial.println(tipo + ":" + rfid);
    delay(50);
  }
}

void enviarEventoHTTP(String tipo, String rfid) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ Wi-Fi desconectado! Não foi possível enviar.");
    return;
  }
  
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  
  // Monta JSON
  StaticJsonDocument<200> doc;
  doc["tipo"] = tipo;
  doc["rfid"] = rfid;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("📤 Enviando: " + jsonString);
  
  int httpCode = http.POST(jsonString);
  
  if (httpCode > 0) {
    String resposta = http.getString();
    Serial.println("✓ Resposta: " + resposta);
  } else {
    Serial.println("✗ Erro HTTP: " + String(httpCode));
  }
  
  http.end();
}

void piscarLED(int vezes) {
  for (int i = 0; i < vezes; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}