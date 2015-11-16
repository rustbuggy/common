////////////////////////////////////////////////////////////////////////////
//
//  This file is part of RTIMULib-Teensy
//
//  Copyright (c) 2014-2015, richards-tech
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of 
//  this software and associated documentation files (the "Software"), to deal in 
//  the Software without restriction, including without limitation the rights to use, 
//  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the 
//  Software, and to permit persons to whom the Software is furnished to do so, 
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all 
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
//  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
//  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#include <SPI.h>
#include <EEPROM.h>
#include "RTIMULib.h"
#include "RTIMUMagCal.h"

RTIMU *imu;                                           // the IMU object
RTIMUSettings *settings;                              // the settings object
RTIMUMagCal *magCal;                                  // the mag calibration object
unsigned long lastDisplay;

//  SERIAL_PORT_SPEED defines the speed to use for the debug serial port

#define  SERIAL_PORT_SPEED  57600

//  DISPLAY_INTERVAL sets the rate at which results are displayed

#define DISPLAY_INTERVAL  200                         // interval between min/max displays

void setup()
{
    int errcode;

    Serial3.begin(SERIAL_PORT_SPEED);
   
    settings = new RTIMUSettings();
    imu = RTIMU::createIMU(settings);                        // create the imu object
  
    if ((errcode = imu->IMUInit()) < 0) {
      Serial3.print("Failed to init IMU: "); Serial3.println(errcode);
    }
    
    Serial3.print("TeensyMagCal starting using device "); Serial3.println(imu->IMUName());
    Serial3.println("Enter s to save current data to SD card");

    imu->setCompassCalibrationMode(true);
    magCal = new RTIMUMagCal(settings);
    magCal->magCalInit();
    lastDisplay = millis();
}

void loop()
{  
    unsigned long now = millis();
  
    if (imu->IMURead()) {                                 // get the latest data
        magCal->newMinMaxData(imu->getIMUData().compass);
        if ((now - lastDisplay) >= DISPLAY_INTERVAL) {
            lastDisplay = now;
            Serial3.println("-------");
            Serial3.print("minX: "); Serial3.print(magCal->m_magMin.data(0));
            Serial3.print(" maxX: "); Serial3.print(magCal->m_magMax.data(0)); Serial3.println();
            Serial3.print("minY: "); Serial3.print(magCal->m_magMin.data(1));
            Serial3.print(" maxY: "); Serial3.print(magCal->m_magMax.data(1)); Serial3.println();
            Serial3.print("minZ: "); Serial3.print(magCal->m_magMin.data(2));
            Serial3.print(" maxZ: "); Serial3.print(magCal->m_magMax.data(2)); Serial3.println();
        }
    }
  
    if (Serial3.available()) {
        if (Serial3.read() == 's') {                  // save the data
            magCal->magCalSaveMinMax();
            Serial3.print("Mag cal data saved for device "); Serial3.println(imu->IMUName());
            while(1) ;
        }
    }
}
