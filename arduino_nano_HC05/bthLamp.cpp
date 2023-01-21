
  #include <SoftwareSerial.h>
   
  #define RX 3
  #define TX 2
  #define pinLED_Red 9
  #define pinLED_Green 6
  #define pinLED_Blue 5
  unsigned char data[255];
  char tmpDummy;
  String strData;
  int dataCheck = 0;
  float fBright = 0.20;
  float fBrightReq = fBright;
  int iSelctedProgram = 3;

  struct colorSet{
    int R;
    int G;
    int B;
  };
  
  colorSet colorQueue[3];
  unsigned char buff[12];

  int tToChangeColor = 400; //smycka ma cca 100 Hz
  int tToFade = 200;
  int prgFadeCounter = 0;
  int clrID = 0;
  int triggClrChange = 0;

  int rainbwPrescaler = 3;
  int rainbwCounter = 0;
  int programChanged = 0;

  int dataAvailable = 0;



  struct colorSetting{
    int desDuty;
    int clr_direction;
  };

  struct colorSetting clrRed,clrGreen,clrBlue;

  SoftwareSerial HM_10(TX, RX);
  void setup() {
    Serial.begin(9600);
    HM_10.begin(9600);
    pinMode(pinLED_Red, OUTPUT);
    analogWrite(pinLED_Red, 0);

    pinMode(pinLED_Green, OUTPUT);
    analogWrite(pinLED_Green, 0);

    pinMode(pinLED_Blue, OUTPUT);
    analogWrite(pinLED_Blue, 0);
 


    clrRed.desDuty = 180;
    clrRed.clr_direction = -1;

    clrGreen.desDuty = 230;
    clrGreen.clr_direction = -1;

    clrBlue.desDuty = 29;
    clrBlue.clr_direction = -1;

    colorQueue[0].R = clrRed.desDuty;
    colorQueue[0].G = clrGreen.desDuty;
    colorQueue[0].B = clrBlue.desDuty;
  }

  int normalizeColor(int iColor){
    int iRes;
    float fDiv = ((float)iColor/255)*255*fBright;
    iRes = (int)fDiv;

    return iRes;
  }

  void setLEDColor(int R,int G,int B){
    analogWrite(pinLED_Red, normalizeColor(R));
    analogWrite(pinLED_Green, normalizeColor(G));
    analogWrite(pinLED_Blue, normalizeColor(B));
  }


  void countRainbowLedColor(){
    clrRed.desDuty = clrRed.desDuty + clrRed.clr_direction;   //changing values of LEDs
    clrGreen.desDuty = clrGreen.desDuty + 2*clrGreen.clr_direction;
    clrBlue.desDuty = clrBlue.desDuty + 3*clrBlue.clr_direction;
 
    if (clrRed.desDuty >= 255){
      clrRed.desDuty = 255;
      clrRed.clr_direction = -1;
      
    }
    if(clrRed.desDuty <= 0){
      clrRed.desDuty = 0;
      clrRed.clr_direction = 1;
    }

    if (clrGreen.desDuty >= 255){
      clrGreen.desDuty = 255;
      clrGreen.clr_direction = -1;
      
    }
    if(clrGreen.desDuty <= 0){
      clrGreen.desDuty = 0;
      clrGreen.clr_direction = 1;
    }


    if (clrBlue.desDuty >= 255){
      clrBlue.desDuty = 255;
      clrBlue.clr_direction = -1;
      
    }
    if(clrBlue.desDuty <= 0){
      clrBlue.desDuty = 0;
      clrBlue.clr_direction = 1;
    }
    

    
    setLEDColor(clrRed.desDuty, clrGreen.desDuty, clrBlue.desDuty);
  }
  
  void loop() {
    int sLen = 0;
    int i;
    if(programChanged == 1){
      programChanged = 0;
      if(iSelctedProgram == 1){
        clrRed.desDuty = colorQueue[0].R;
        clrRed.clr_direction = -1;

        clrGreen.desDuty = colorQueue[0].G;
        clrGreen.clr_direction = -1;

        clrBlue.desDuty = colorQueue[0].B;
        clrBlue.clr_direction = -1;
      }
      else if(iSelctedProgram == 3){
        clrRed.desDuty = colorQueue[0].R;
        clrGreen.desDuty = colorQueue[0].G;
        clrBlue.desDuty = colorQueue[0].B;

        clrRed.clr_direction = -1;
        clrGreen.clr_direction = -1;
        clrBlue.clr_direction = -1;
      }
    }
    
    switch(iSelctedProgram){
      case 1:
        setLEDColor(clrRed.desDuty,clrGreen.desDuty,clrBlue.desDuty);
        break;
      case 2:
          prgFadeCounter++;
          if((prgFadeCounter >= tToChangeColor) && (prgFadeCounter < (tToChangeColor + tToFade)))
            //fBright = ((float)(fBrightReq*100.0 - (prgFadeCounter - tToChangeColor)))/100.0;
            fBright -= fBrightReq/((float)tToFade);
          if(fBright < 0)
            fBright = 0;
          if((prgFadeCounter >= (tToChangeColor + tToFade)) && (prgFadeCounter < (tToChangeColor + 2*tToFade))){
            if(triggClrChange == 0){
              clrID++;
              if(clrID > 2)
                clrID = 0;
              triggClrChange = 1;
            }
            //fBright = ((float)(prgFadeCounter - (tToChangeColor + tToFade)))/((float)tToFade);
            fBright += fBrightReq/((float)tToFade);
            if(fBright > fBrightReq)
              fBright = fBrightReq;
          }
          if(prgFadeCounter > (tToChangeColor + 2*tToFade)){
            fBright = fBrightReq;
            prgFadeCounter = 0;
            triggClrChange = 0;
          }
          
        clrRed.desDuty = colorQueue[clrID].R;
        clrGreen.desDuty = colorQueue[clrID].G;
        clrBlue.desDuty = colorQueue[clrID].B;

        setLEDColor(clrRed.desDuty,clrGreen.desDuty,clrBlue.desDuty);
        break;
      case 3:
        if(rainbwCounter >= rainbwPrescaler){
          rainbwCounter = 0;
          countRainbowLedColor();
        }
        /*Serial.print(clrRed.desDuty);
        Serial.print(" ");
        Serial.print(clrGreen.desDuty);
        Serial.print(" ");
        Serial.print(clrBlue.desDuty);
        Serial.print("\n");*/
        break;
    }

    delay(10);
    dataCheck++;
    rainbwCounter++;
    
    if(dataCheck > 200){
      dataCheck = 0;  
      sprintf(data,"");
      for(i = 0;i <= 11;i++){
        data[i] = 0;
      }
      i = 0;
      //Serial.print("nic\n");
      //Serial.print(HM_10.read());
      //Serial.print("\n");
      while(HM_10.available()){
        if(dataAvailable == 0)
          dataAvailable = 1;

          if(i <= 11)
            data[i] = HM_10.read();
          else
            tmpDummy = HM_10.read();
          i++;
      }

      if(dataAvailable == 1){
        dataAvailable = 0;
       
        //data[i] = '\n';
                
        for(i = 0;i<12;i++){
          //Serial.print(data[i]);
          buff[i] = data[i];
        }
        //Serial.print("\n");
        //if((iSelctedProgram != ((int)buff[0] - 48)) || (((int)buff[0] - 48)))
        programChanged = 1;
        iSelctedProgram = (int)buff[0] - 48;
        
        if(iSelctedProgram == 1){
          colorQueue[0].R = (int)buff[1];
          colorQueue[0].G = (int)buff[2];
          colorQueue[0].B = (int)buff[3];
          fBrightReq = ((float)buff[10])/100.0;
        }
        else if(iSelctedProgram == 2){
          colorQueue[0].R = (int)buff[1];
          colorQueue[0].G = (int)buff[2];
          colorQueue[0].B = (int)buff[3];

          colorQueue[1].R = (int)buff[4];
          colorQueue[1].G = (int)buff[5];
          colorQueue[1].B = (int)buff[6];

          colorQueue[2].R = (int)buff[7];
          colorQueue[2].G = (int)buff[8];
          colorQueue[2].B = (int)buff[9];

          fBrightReq = ((float)buff[10])/100.0;
        }
        else{
          colorQueue[0].R = 220;//(int)buff[1];
          colorQueue[0].G = 150;//(int)buff[2];
          colorQueue[0].B = 20;//(int)buff[3];
          fBrightReq = ((float)buff[10])/100.0;
        }
        fBright = fBrightReq;
      }
    }
  }
