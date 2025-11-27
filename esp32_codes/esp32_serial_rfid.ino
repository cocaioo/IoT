/*
 * ESP32 - Sistema de Controle de Restaurante
 * Modo: COMUNICAÇÃO SERIAL (USB)
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

#include <SPI.h>
#include <MFRC522.h>

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
  Serial.println("  Modo: SERIAL");
  Serial.println("===========================================");
  Serial.println("Aguardando cartões RFID...\n");
}

void loop() {
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

String obterRFID() {
  String conteudo = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    conteudo += String(rfid.uid.uidByte[i], HEX);
  }
  conteudo.toUpperCase();
  return "RFID_" + conteudo;
}

void enviarEvento(String tipo, String rfid) {
  // Formato esperado pelo Python: "TIPO:RFID"
  Serial.println(tipo + ":" + rfid);
  
  // Aguarda resposta do Python (opcional)
  delay(100);
  if (Serial.available()) {
    String resposta = Serial.readStringUntil('\n');
    Serial.println("Resposta: " + resposta);
  }
}

void piscarLED(int vezes) {
  for (int i = 0; i < vezes; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}
