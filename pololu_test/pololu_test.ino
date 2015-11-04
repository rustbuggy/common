#include <ADC.h>
#include "lookups.h"

#define POLOLU_PIN 15 // A1

ADC* adc;

void setup() {
  pinMode(POLOLU_PIN, INPUT);

  adc = new ADC(); // adc object

  adc->setSamplingSpeed(ADC_VERY_LOW_SPEED); // change the sampling speed
  adc->setConversionSpeed(ADC_VERY_LOW_SPEED); // change the conversion speed
  adc->setResolution(10);
  adc->setAveraging(0);
  
  Serial3.begin(57600);
}

void loop() {
  uint32_t val = adc->analogRead(POLOLU_PIN);
  uint32_t cm = int(fixed(irLookup[val]));
  Serial3.print(val, DEC);
  Serial3.print("   ");
  Serial3.println(cm, DEC);
}
