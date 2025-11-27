/*
 * ESP32 - Sistema de Controle de Restaurante
 * Modo: COMUNICAÇÃO HTTP (Wi-Fi)
 * 
 * Hardware necessário:
 * - ESP32
 * - Módulo RFID RC522
 * - 2x Botões (simulando entrada/saída)
 * 
 * Conexões RFID RC522:
 * SDA  -> GPIO 5
 * SCK  -> GPIO 18
 * MOSI -> GPIO 23
 * MISO -> GPIO 19
 * RST  -> GPIO 22
 * GND  -> GND
 * 3.3V -> 3.3V
 * 
 * Conexões Botões:
 * Botão ENTRADA -> GPIO 15 (com pull-up)
 * Botão SAÍDA   -> GPIO 4  (com pull-up)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>

// ========== CONFIGURAÇÕES Wi-Fi ==========
const char* WIFI_SSID = "SEU_WIFI_AQUI";        // ALTERE AQUI
const char* WIFI_PASSWORD = "SUA_SENHA_AQUI";   // ALTERE AQUI

// ========== CONFIGURAÇÕES DO SERVIDOR ==========
const char* SERVER_URL = "http://192.168.1.100:5000/evento"; // ALTERE O IP AQUI

// Pinos do RFID
#define SS_PIN 5
#define RST_PIN 22

// Pinos dos botões
#define BTN_ENTRADA 15
#define BTN_SAIDA 4

// LED de status (built-in)
#define LED_PIN 2

MFRC522 rfid(SS_PIN, RST_PIN);

String ultimoRFID = "";
unsigned long ultimaLeitura = 0;
const unsigned long INTERVALO_LEITURA = 2000; // 2 segundos entre leituras

void setup() {
  Serial.begin(115200);
  
  // Inicializa SPI e RFID
  SPI.begin();
  rfid.PCD_Init();
  
  // Configura botões
  pinMode(BTN_ENTRADA, INPUT_PULLUP);
  pinMode(BTN_SAIDA, INPUT_PULLUP);
  
  // Configura LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("===========================================");
  Serial.println("  ESP32 - Sistema de Controle de Restaurante");
  Serial.println("  Modo: HTTP (Wi-Fi)");
  Serial.println("===========================================\n");
  
  // Conecta ao Wi-Fi
  conectarWiFi();
  
  Serial.println("\nAguardando cartões RFID...\n");
}

void loop() {
  // Verifica conexão Wi-Fi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi desconectado! Reconectando...");
    conectarWiFi();
  }
  
  // Lê RFID
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String rfidID = obterRFID();
    unsigned long agora = millis();
    
    // Evita leituras duplicadas muito próximas
    if (rfidID != ultimoRFID || (agora - ultimaLeitura) > INTERVALO_LEITURA) {
      ultimoRFID = rfidID;
      ultimaLeitura = agora;
      
      // Verifica qual botão foi pressionado
      bool btnEntrada = digitalRead(BTN_ENTRADA) == LOW;
      bool btnSaida = digitalRead(BTN_SAIDA) == LOW;
      
      if (btnEntrada) {
        enviarEvento("ENTRADA", rfidID);
        piscarLED(1);
      } else if (btnSaida) {
        enviarEvento("SAIDA", rfidID);
        piscarLED(2);
      } else {
        // Se nenhum botão pressionado, assume ENTRADA por padrão
        enviarEvento("ENTRADA", rfidID);
        piscarLED(1);
      }
    }
    
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }
  
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
    conteudo += String(rfid.uid.uidByte[i], HEX);
  }
  conteudo.toUpperCase();
  return "RFID_" + conteudo;
}

void enviarEvento(String tipo, String rfid) {
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
  
  Serial.println("Enviando: " + jsonString);
  
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
