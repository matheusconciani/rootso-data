#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHTesp.h>

const int LARGURA_TELA = 128;
const int ALTURA_TELA = 64;
const int PINO_SDA_OLED = 21;
const int PINO_SCL_OLED = 22;
const int ENDERECO_OLED = 0x3C;

const int PINO_DHT = 15;
const int PINO_LDR = 34;
const int PINO_BOTAO_N = 32;
const int PINO_BOTAO_P = 25;
const int PINO_BOTAO_K = 26;
const int PINO_RELE = 27;

const float UMIDADE_LIGA = 40.0;
const float UMIDADE_DESLIGA = 45.0;
const int RELE_LIGADO = HIGH;
const int RELE_DESLIGADO = LOW;

// A leitura do DHT22 precisa respeitar um intervalo mínimo entre amostras.
const unsigned long INTERVALO_LEITURA = 2500;
unsigned long ultimaLeitura = 0;

// Cada registro emitido representa uma hora no histórico simulado.
int ano = 2026;
int mes = 10;
int dia = 5;
int hora = 8;
int minuto = 32;

Adafruit_SSD1306 tela(LARGURA_TELA, ALTURA_TELA, &Wire, -1);
DHTesp sensorDHT;

float temperatura = NAN;
float umidade = NAN;
float phSimulado = 0.0;
int leituraLDR = 0;
bool bombaLigada = false;
bool nitrogenioAdequado = false;
bool fosforoAdequado = false;
bool potassioAdequado = false;

void avancarHoraSimulada() {
  hora++;
  if (hora < 24) {
    return;
  }

  hora = 0;
  dia++;

  int diasNoMes = 31;
  if (mes == 4 || mes == 6 || mes == 9 || mes == 11) {
    diasNoMes = 30;
  } else if (mes == 2) {
    diasNoMes = 28;
  }

  if (dia <= diasNoMes) {
    return;
  }

  dia = 1;
  mes++;
  if (mes <= 12) {
    return;
  }

  mes = 1;
  ano++;
}

void imprimirDataHora() {
  char dataHora[20];
  snprintf(
    dataHora,
    sizeof(dataHora),
    "%04d-%02d-%02d %02d:%02d:00",
    ano,
    mes,
    dia,
    hora,
    minuto
  );
  Serial.print(dataHora);
}

void emitirRegistroCSV() {
  // Cabeçalho e linhas marcadas como simulator para não confundir com
  // medições físicas reais.
  Serial.print("ROOTSO_CSV;");
  imprimirDataHora();
  Serial.print(";");
  Serial.print(isnan(umidade) ? -1.0 : umidade, 1);
  Serial.print(";");
  Serial.print(phSimulado, 1);
  Serial.print(";");
  Serial.print(fosforoAdequado ? 1 : 0);
  Serial.print(";");
  Serial.print(potassioAdequado ? 1 : 0);
  Serial.print(";");
  Serial.print(bombaLigada ? 1 : 0);
  Serial.println(";simulador");
}

void atualizarSensores() {
  TempAndHumidity dados = sensorDHT.getTempAndHumidity();
  temperatura = dados.temperature;
  umidade = dados.humidity;
  leituraLDR = analogRead(PINO_LDR);
  phSimulado = (leituraLDR / 4095.0) * 14.0;
  nitrogenioAdequado = digitalRead(PINO_BOTAO_N) == LOW;
  fosforoAdequado = digitalRead(PINO_BOTAO_P) == LOW;
  potassioAdequado = digitalRead(PINO_BOTAO_K) == LOW;
}

void controlarIrrigacao() {
  if (isnan(umidade)) {
    bombaLigada = false;
  } else if (!bombaLigada && umidade < UMIDADE_LIGA) {
    bombaLigada = true;
  } else if (bombaLigada && umidade >= UMIDADE_DESLIGA) {
    bombaLigada = false;
  }

  digitalWrite(PINO_RELE, bombaLigada ? RELE_LIGADO : RELE_DESLIGADO);
}

void atualizarTela() {
  tela.clearDisplay();
  tela.setTextColor(SSD1306_WHITE);
  tela.setTextSize(1);
  tela.setCursor(0, 0);
  tela.println("ROOTSO | FASE 3");
  tela.setCursor(0, 12);
  tela.print("Umidade: ");
  tela.print(isnan(umidade) ? 0.0 : umidade, 1);
  tela.println("%");
  tela.setCursor(0, 24);
  tela.print("pH simulado: ");
  tela.println(phSimulado, 1);
  tela.setCursor(0, 36);
  tela.print("P:");
  tela.print(fosforoAdequado ? "OK " : "-- ");
  tela.print("K:");
  tela.println(potassioAdequado ? "OK" : "--");
  tela.setCursor(0, 48);
  tela.print("Bomba: ");
  tela.println(bombaLigada ? "LIGADA" : "DESLIGADA");
  tela.display();
}

void setup() {
  Serial.begin(115200);
  pinMode(PINO_BOTAO_N, INPUT_PULLUP);
  pinMode(PINO_BOTAO_P, INPUT_PULLUP);
  pinMode(PINO_BOTAO_K, INPUT_PULLUP);
  pinMode(PINO_RELE, OUTPUT);
  digitalWrite(PINO_RELE, RELE_DESLIGADO);

  Wire.begin(PINO_SDA_OLED, PINO_SCL_OLED);
  if (!tela.begin(SSD1306_SWITCHCAPVCC, ENDERECO_OLED)) {
    Serial.println("Erro ao iniciar o OLED.");
    while (true) {
      delay(10);
    }
  }

  sensorDHT.setup(PINO_DHT, DHTesp::DHT22);
  tela.clearDisplay();
  tela.setTextColor(SSD1306_WHITE);
  tela.setTextSize(1);
  tela.setCursor(0, 0);
  tela.println("ROOTSO FASE 3");
  tela.println("Iniciando...");
  tela.display();

  Serial.println("ROOTSO_CSV;data_hora;umidade;ph;fosforo;potassio;bomba;origem");
  delay(5000);
}

void loop() {
  unsigned long agora = millis();
  if (agora - ultimaLeitura < INTERVALO_LEITURA) {
    return;
  }

  ultimaLeitura = agora;
  atualizarSensores();
  controlarIrrigacao();
  emitirRegistroCSV();
  atualizarTela();
  avancarHoraSimulada();
}
