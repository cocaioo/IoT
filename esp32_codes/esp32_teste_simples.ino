/*
 * ESP32 - TESTE SIMPLES SEM RFID
 * Modo: SERIAL
 * 
 * Use este código para testar o sistema sem o módulo RFID
 * Apenas com 2 botões
 * 
 * Hardware necessário:
 * - ESP32
 * - 2x Botões
 * 
 * Conexões:
 * Botão ENTRADA -> GPIO 15 (com pull-up interno)
 * Botão SAÍDA   -> GPIO 4  (com pull-up interno)
 * LED Built-in  -> GPIO 2  (já integrado)
 */

// Pinos dos botões
#define BTN_ENTRADA 15
#define BTN_SAIDA 4

// LED de status (built-in)
#define LED_PIN 2

// RFIDs simulados (você tem 2, então usamos 2 IDs fixos)
String rfids[] = {"RFID_A", "RFID_B"};
int rfidAtual = 0;

unsigned long ultimaPressao = 0;
const unsigned long DEBOUNCE = 500; // Anti-bounce de 500ms

void setup() {
  Serial.begin(115200);
  
  // Configura botões
  pinMode(BTN_ENTRADA, INPUT_PULLUP);
  pinMode(BTN_SAIDA, INPUT_PULLUP);
  
  // Configura LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("===========================================");
  Serial.println("  ESP32 - TESTE SIMPLES (SEM RFID)");
  Serial.println("  Modo: SERIAL");
  Serial.println("===========================================");
  Serial.println("Botão ENTRADA -> GPIO 15");
  Serial.println("Botão SAÍDA   -> GPIO 4");
  Serial.println("\nPressione os botões para testar!\n");
}

void loop() {
  unsigned long agora = millis();
  
  // Lê botões
  bool btnEntrada = digitalRead(BTN_ENTRADA) == LOW;
  bool btnSaida = digitalRead(BTN_SAIDA) == LOW;
  
  // Debounce
  if ((btnEntrada || btnSaida) && (agora - ultimaPressao) > DEBOUNCE) {
    ultimaPressao = agora;
    
    String rfid = rfids[rfidAtual];
    
    if (btnEntrada) {
      enviarEvento("ENTRADA", rfid);
      piscarLED(1);
    } else if (btnSaida) {
      enviarEvento("SAIDA", rfid);
      piscarLED(2);
    }
    
    // Alterna entre os 2 RFIDs
    rfidAtual = (rfidAtual + 1) % 2;
  }
  
  delay(50);
}

void enviarEvento(String tipo, String rfid) {
  // Formato esperado pelo Python: "TIPO:RFID"
  Serial.println(tipo + ":" + rfid);
  Serial.println("(Usando RFID: " + rfid + ")");
  
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
