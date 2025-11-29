/*
 * ESP32 - Sistema de Controle de Restaurante
 * Modo: SERIAL (USB) CONTROLADO PELO TECLADO (E / S)
 * 
 * Hardware necessário:
 * - ESP32
 * - Módulo RFID RC522
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
 * LÓGICA:
 * - Python (PC) envia um caractere pela serial:
 *    'E' -> próxima leitura de cartão será ENTRADA
 *    'S' -> próxima leitura de cartão será SAIDA
 * - ESP32 aguarda um cartão RFID
 * - Quando um cartão é lido, o ESP32 envia:
 *    "ENTRADA:RFID_xxxxx"  ou  "SAIDA:RFID_xxxxx"
 */

#include <SPI.h>
#include <MFRC522.h>

// Pinos do RFID
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
  
  // Inicializa SPI e RFID
  SPI.begin();
  rfid.PCD_Init();
  
  // Configura LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("===========================================");
  Serial.println("  ESP32 - Sistema de Controle de Restaurante");
  Serial.println("  Modo: SERIAL CONTROLADO POR TECLADO (E/S)");
  Serial.println("===========================================");
  Serial.println("Use:");
  Serial.println("  'E' para marcar próxima leitura como ENTRADA");
  Serial.println("  'S' para marcar próxima leitura como SAIDA");
  Serial.println();
  Serial.println("Modo atual: ENTRADA");
  Serial.println("Aguardando comandos do PC e cartões RFID...\n");
}

void loop() {
  // 1) Verifica se chegou algum comando do PC (Python/teclado)
  if (Serial.available()) {
    char comando = Serial.read();
    if (comando == 'E') {
      modoAtual = "ENTRADA";
      Serial.println(">> Modo alterado para ENTRADA");
    } else if (comando == 'S') {
      modoAtual = "SAIDA";
      Serial.println(">> Modo alterado para SAIDA");
    }
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
  
  // 4) Obtém o ID do cartão
  String rfidID = obterRFID();
  unsigned long agora = millis();
  
  // Evita leituras duplicadas muito próximas do mesmo cartão
  if (rfidID != ultimoRFID || (agora - ultimaLeitura) > INTERVALO_LEITURA) {
    ultimoRFID = rfidID;
    ultimaLeitura = agora;
    
    // Envia evento conforme o modo atual
    enviarEvento(modoAtual, rfidID);
    piscarLED(modoAtual == "ENTRADA" ? 1 : 2);
    
    Serial.println("✓ Cartão processado como " + modoAtual + "\n");
  }
  
  // 5) Finaliza comunicação com o cartão
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  
  delay(100);
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
  // Formato esperado pelo Python: "TIPO:RFID"
  Serial.println(tipo + ":" + rfid);

  // Pequeno delay pra dar tempo do PC ler
  delay(50);
}

void piscarLED(int vezes) {
  for (int i = 0; i < vezes; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}