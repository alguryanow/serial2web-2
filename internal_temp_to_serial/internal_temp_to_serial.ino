// source: https://code.google.com/p/tinkerit/wiki/SecretThermometer

long readTemp() {
  long result;
  // Read temperature sensor against 1.1V reference
  ADMUX = _BV(REFS1) | _BV(REFS0) | _BV(MUX3);
  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Convert
  while (bit_is_set(ADCSRA,ADSC));
  result = ADCL;
  result |= ADCH<<8;
  result = (result - 125) * 1075;
  return result;
}

void setup() {
  Serial.begin(115200);
}

int count = 0;
long offset = 0;

void loop() {
  String s = "Температура: " + String( readTemp()+offset, DEC );
  Serial.println( s );
  delay( 2000 );

  s = getStringFromSerial();
  if( s != "" ){
    offset = s.toInt();
  }
}

String inputString = "";
String returnString = "";

String getStringFromSerial()
{
  while( Serial.available() ){
    char inChar = Serial.read();
    if( inChar == '\r' || inChar == '\n' ){
      String returnString = inputString;
      inputString = "";
      return returnString;
    } else {
      inputString += inChar;
    }
  }
  return "";
}


