__version__ = "1.0.0"


import asyncio

from kivy.app import App
#from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.lang import Builder

from kivy.core.window import Window
w,h = Window.size
print(f'w: {w}, h: {h}')
Window.size = (w, h)

from jnius import autoclass,JavaException

# bind bleak's python logger into kivy's logger before importing python module using logging
from kivy.logger import Logger
import logging

logging.Logger.manager.root = Logger


class SayHello(App):
    def __init__(self, **kwargs):
        super(SayHello, self).__init__(**kwargs)

        

        self.root = Builder.load_file("SayHello.kv")

        
        
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.BufferReader = autoclass('java.io.BufferedReader')
        self.InputStream = autoclass('java.io.InputStreamReader')
        self.adapterEnabled = 0
        
        self.socket = None
        self.SendData = None

        self.sliderValue_red = 0.5
        self.sliderValue_green = 0.5
        self.sliderValue_blue = 0.5
        self.sliderValue_brightness = 100

        self.task_sec = None
        

    def build(self):
        self.deviceCount = 0
        self.devices = []
        self.devicesFilt = []
        self.ErrExists = 0
        self.deviceToConnect = ""
        self.deviceConnected = 0

        self.deviceListBtnDefaultText = ""
        self.deviceConnectBtnDefaultText = ""
        self.initRed = 200
        self.initBlue = 120
        self.initGreen = 200
        self.initBrightness = 50
        self.initPrgSelected = 1

        self.sliderValue_red = self.initRed
        self.sliderValue_blue = self.initBlue
        self.sliderValue_green = self.initGreen
        self.sliderValue_brightness = self.initBrightness
        self.selPrgSelected = self.initPrgSelected
        self.sm = FloatLayout()

        self.listDevices = DropDown()
        #self.sm.ids['btnDeviceList'].on_press = self.btnDeviceList_onClick
        self.sm.ids['btnDeviceList'].bind(on_release = self.listDevices.open)
        self.listDevices.bind(on_select=lambda instance, x: setattr(self.sm.ids['btnDeviceList'], 'text', x))
        self.deviceListBtnDefaultText = self.sm.ids['btnDeviceList'].text

        self.sm.ids['btnSearch'].on_press = self.btnSearch_onClick
        self.sm.ids['btnConnect'].disabled = True
        self.sm.ids['btnDeviceList'].disabled = True
        self.sm.ids['btnSend'].disabled = True
        self.sm.ids['btnConnect'].on_press = self.btnConnect_onClick
        self.sm.ids['btnSend'].on_press = self.btnSend_onClick
        self.sm.ids['btnClose'].on_press = self.closeApp
        self.deviceConnectBtnDefaultText = self.sm.ids['btnConnect'].text


        self.sm.ids['sliderBlue'].fbind('value', self.on_slider_val_Blue)
        self.sm.ids['sliderBlue'].value = self.initBlue
        self.sm.ids['sliderRed'].fbind('value', self.on_slider_val_Red)
        self.sm.ids['sliderRed'].value = self.initRed
        self.sm.ids['sliderGreen'].fbind('value', self.on_slider_val_Green)
        self.sm.ids['sliderGreen'].value = self.initGreen
        self.sm.ids['sliderBrightness'].fbind('value', self.on_slider_val_Brightness)
        self.sm.ids['sliderBrightness'].value = self.initBrightness

        self.btnDefaultColor = self.sm.ids['btnRainbow'].background_color

        self.sm.ids['btnOneColor'].on_press = self.setMode_oneColor
        self.sm.ids['btnColorChange'].on_press = self.setMode_colorQueue
        self.sm.ids['btnRainbow'].on_press = self.setMode_rainbow

        self.sm.ids['btnSetClr_1'].on_press = self.btnSetClr_1_onClick
        self.sm.ids['btnSetClr_2'].on_press = self.btnSetClr_2_onClick
        self.sm.ids['btnSetClr_3'].on_press = self.btnSetClr_3_onClick

        self.changeColor()

        self.setMode_oneColor()

        self.sm.ids['btnSend'].on_press = self.btnSend_onClick

        self.task_sec = asyncio.create_task(self.checkBTAdapter())

        return self.sm

    def btnSearch_onClick(self):
        self.sm.ids['btnDeviceList'].text = self.deviceListBtnDefaultText
        self.sm.ids['btnConnect'].text = self.deviceConnectBtnDefaultText
        self.sm.ids['btnConnect'].disabled = True
        self.sm.ids['btnDeviceList'].disabled = True
        self.sm.ids['btnSend'].disabled = True
        
        if self.adapterEnabled == 0:
            self.sm.ids['btnSearch'].disabled = False
            self.line("bluetooth neni zapnuty",1)
        else:
            self.sm.ids['btnSearch'].disabled = True
            task = asyncio.create_task(self.example())

    def btnConnect_onClick(self):
        task = asyncio.create_task(self.connectToDevice())

    def btnSend_onClick(self):
        self.sendData()

    def allowConnectButton(self,btn):
        self.deviceToConnect = btn.text
        self.sm.ids['btnConnect'].disabled = False
        if btn.text != self.deviceToConnect:
            #self.sm.ids['btnConnect'].disabled = False
            self.sm.ids['btnConnect'].text = self.deviceConnectBtnDefaultText


    def filldeviceList(self,deviceName,isFirst = 0):
        if isFirst == 1:
            self.listDevices.clear_widgets()

        btn = Button(text=deviceName, size_hint_y=None, height=44)
        btn.bind(on_release=lambda btn: self.listDevices.select(btn.text))
        btn.bind(on_release=lambda btn: self.allowConnectButton(btn))
        self.listDevices.add_widget(btn)


    async def checkBTAdapter(self):
        while True:
            print("kontrola bt")
            try:
                if self.BluetoothAdapter.getDefaultAdapter().isEnabled() == False:
                    self.adapterEnabled = 0
                else:
                    self.adapterEnabled = 1
            except JavaException as e:
                print("chyba java exception")


            await asyncio.sleep(1)



    def line(self, text, error=False):
        Logger.info("example:" + text)
        self.sm.ids['lblStatus'].text = text
        if error == True:
            self.sm.ids['lblStatus'].background_color = (1,0,0,1)
            self.sm.ids['lblStatus'].color = (1,1,1,1)
        else:
            self.sm.ids['lblStatus'].background_color = (0.5,0.5,0.5,1)
            self.sm.ids['lblStatus'].color = (0,0,0,1)

    def on_stop(self):
        if self.task_sec != None:
            self.task_sec.cancel()
        pass


    async def example(self):
        self.devices = []
        self.devicesFilt = []
        self.deviceCount = 0
        if self.deviceConnected == 1:
            #odpojit

            if self.socket != None:
                try:
                    self.socket.close()
                except JavaException as e:
                    pass

            self.socket = None

            if self.SendData != None:
                try:
                    self.SendData.close()
                except JavaException as e:
                    pass
            
            self.SendData = None

            self.deviceConnected = 0
            self.deviceToConnect = ""
            pass


        self.devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        self.socket = None

        for device in self.devices:
            tmpDevName = device.getName()
            if tmpDevName.find("BT") != -1:
                self.deviceCount += 1
                print("dev: " + tmpDevName)
                self.filldeviceList(tmpDevName,self.deviceCount)
                self.devicesFilt.append(tmpDevName)
        print("cnt: " + str(self.deviceCount))

        if self.deviceCount > 0:
            self.sm.ids['btnConnect'].disabled = True
            self.sm.ids['btnDeviceList'].disabled = False
            self.sm.ids['btnSend'].disabled = True
        
        self.sm.ids['btnSearch'].disabled = False


    async def connectToDevice(self):
        #pruchod nalezenych zarizeni a pripojit
        for device in self.devices:
            if device.getName() == self.deviceToConnect:
                self.socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                try:
                    self.SendData = self.socket.getOutputStream()
                    self.socket.connect()
                    self.deviceConnected = 1
                except JavaException as e:
                    self.line("chyba pri pripojeni!",1)

        if self.deviceConnected == 1:
            self.sm.ids['btnConnect'].disabled = True
            self.sm.ids['btnDeviceList'].disabled = True
            self.sm.ids['btnSend'].disabled = False
            self.sm.ids['btnConnect'].text = "Pripojeno"
            self.line("Pripojeno k " + self.deviceToConnect)
        else:
            self.line("Nepodarilo se pripojit k " + self.deviceToConnect,1)

    def sendData(self):
        msgToSend = "ERROR"
        if self.deviceConnected != 1:
            return
        try:
            msgToSend = self.setMessageToArduino()
            for i in range(11):
                self.SendData.write(msgToSend[i])

            #self.SendData.write(49)
            #self.SendData.write(255)
            #self.SendData.write(0)
            #self.SendData.write(0)
            #self.SendData.write(254)
            #self.SendData.write(0)
            #self.SendData.write(0)
            #self.SendData.write(253)
            #self.SendData.write(0)
            #self.SendData.write(0)
            #self.SendData.write(40)
            #self.SendData.write('\n')
            #self.SendData.flush()
            #self.SendData.write(msgToSend)
        except JavaException as e:
            self.line("Chyba pri zapisu dat do" + self.deviceToConnect,1)
        
    def closeApp(self):
        App.get_running_app().stop()


    def on_slider_val_Red(self,instance,value):
        self.sliderValue_red = int(value)
        self.changeColor()

    def on_slider_val_Green(self,instance,value):
        self.sliderValue_green = int(value)
        self.changeColor()

    def on_slider_val_Blue(self,instance,value):
        self.sliderValue_blue = int(value)
        self.changeColor()

    def changeColor(self):
        color_red = self.sliderValue_red/255
        color_green = self.sliderValue_green/255
        color_blue = self.sliderValue_blue/255
        self.sm.ids['sliderValue'].background_color = (color_red,color_green,color_blue,1)

    def on_slider_val_Brightness(self,instance,value):
        self.sliderValue_brightness = int(value)
        self.sm.ids['brightnessValue'].text = "Jas: " + str(self.sliderValue_brightness) + " %"
        

    def setModeButtonBck(self):
        if self.selPrgSelected == 1:
            self.sm.ids['btnOneColor'].background_color = (0,0,1,1)
            self.sm.ids['btnColorChange'].background_color = self.btnDefaultColor
            self.sm.ids['btnRainbow'].background_color = self.btnDefaultColor
        elif self.selPrgSelected == 2:
            self.sm.ids['btnOneColor'].background_color = self.btnDefaultColor
            self.sm.ids['btnColorChange'].background_color = (0,0,1,1)
            self.sm.ids['btnRainbow'].background_color = self.btnDefaultColor
        elif self.selPrgSelected == 3:
            self.sm.ids['btnOneColor'].background_color = self.btnDefaultColor
            self.sm.ids['btnColorChange'].background_color = self.btnDefaultColor
            self.sm.ids['btnRainbow'].background_color = (0,0,1,1)


    def setMode_oneColor(self):
        self.selPrgSelected = 1
        self.setModeButtonBck()

        self.sm.ids['sliderBlue'].disabled = False
        self.sm.ids['sliderRed'].disabled = False
        self.sm.ids['sliderGreen'].disabled = False

        self.sm.ids['lblClr_1'].opacity = 0
        self.sm.ids['lblClr_2'].opacity = 0
        self.sm.ids['lblClr_3'].opacity = 0
        self.sm.ids['lblClrInfo'].opacity = 0
        
        self.sm.ids['btnSetClr_1'].opacity = 0
        self.sm.ids['btnSetClr_1'].disabled = True
        self.sm.ids['btnSetClr_2'].opacity = 0
        self.sm.ids['btnSetClr_2'].disabled = True
        self.sm.ids['btnSetClr_3'].opacity = 0
        self.sm.ids['btnSetClr_3'].disabled = True

        



        

    def setMode_colorQueue(self):
        self.selPrgSelected = 2
        self.setModeButtonBck()

        self.sm.ids['sliderBlue'].disabled = False
        self.sm.ids['sliderRed'].disabled = False
        self.sm.ids['sliderGreen'].disabled = False

        self.sm.ids['lblClr_1'].opacity = 1
        self.sm.ids['lblClr_2'].opacity = 1
        self.sm.ids['lblClr_3'].opacity = 1
        self.sm.ids['lblClrInfo'].opacity = 1
        
        self.sm.ids['btnSetClr_1'].opacity = 1
        self.sm.ids['btnSetClr_1'].disabled = False
        self.sm.ids['btnSetClr_2'].opacity = 1
        self.sm.ids['btnSetClr_2'].disabled = False
        self.sm.ids['btnSetClr_3'].opacity = 1
        self.sm.ids['btnSetClr_3'].disabled = False
        
        

    def setMode_rainbow(self):
        self.selPrgSelected = 3
        self.setModeButtonBck()

        self.sm.ids['sliderBlue'].disabled = True
        self.sm.ids['sliderRed'].disabled = True
        self.sm.ids['sliderGreen'].disabled = True

        self.sm.ids['lblClr_1'].opacity = 0
        self.sm.ids['lblClr_2'].opacity = 0
        self.sm.ids['lblClr_3'].opacity = 0
        self.sm.ids['lblClrInfo'].opacity = 0
        
        self.sm.ids['btnSetClr_1'].opacity = 0
        self.sm.ids['btnSetClr_1'].disabled = True
        self.sm.ids['btnSetClr_2'].opacity = 0
        self.sm.ids['btnSetClr_2'].disabled = True
        self.sm.ids['btnSetClr_3'].opacity = 0
        self.sm.ids['btnSetClr_3'].disabled = True
        

    def btnSetClr_1_onClick(self):
        self.sm.ids['btnSetClr_1'].background_color = self.sm.ids['sliderValue'].background_color
        #self.setMessageToArduino()

    def btnSetClr_2_onClick(self):
        self.sm.ids['btnSetClr_2'].background_color = self.sm.ids['sliderValue'].background_color

    def btnSetClr_3_onClick(self):
        self.sm.ids['btnSetClr_3'].background_color = self.sm.ids['sliderValue'].background_color

    def getObjectBackColor(self,instName):
        clrRed = 0
        clrGreen = 0
        clrBlue = 0
        objBck = self.sm.ids[instName]

        clrRed = int(objBck.background_color[0]*255)
        clrGreen = int(objBck.background_color[1]*255)
        clrBlue = int(objBck.background_color[2]*255)

        return clrRed,clrGreen,clrBlue

    def setMessageToArduino(self):
        msgByteArray = [0,0,0,0,0,0,0,0,0,0,0]
        if self.selPrgSelected == 1:
            msgByteArray = [self.selPrgSelected,
            self.getObjectBackColor('sliderValue')[0],self.getObjectBackColor('sliderValue')[1],self.getObjectBackColor('sliderValue')[2],
            0,0,0,
            0,0,0,
            self.sliderValue_brightness]
        elif self.selPrgSelected == 2:
            msgByteArray = [self.selPrgSelected,
            self.getObjectBackColor('btnSetClr_1')[0],self.getObjectBackColor('btnSetClr_1')[1],self.getObjectBackColor('btnSetClr_1')[2],
            self.getObjectBackColor('btnSetClr_2')[0],self.getObjectBackColor('btnSetClr_2')[1],self.getObjectBackColor('btnSetClr_2')[2],
            self.getObjectBackColor('btnSetClr_3')[0],self.getObjectBackColor('btnSetClr_3')[1],self.getObjectBackColor('btnSetClr_3')[2],
            self.sliderValue_brightness]
        elif self.selPrgSelected == 3:
            msgByteArray = [self.selPrgSelected,
            0,0,0,
            0,0,0,
            0,0,0,
            self.sliderValue_brightness]

        
        #bArr = bytes(msgByteArray)
        msgByteArray[0] += 48
        #print(bArr)
        #strbArr = "".join(map(chr, msgByteArray))
 
        #print(strbArr)

        return msgByteArray
        #print([sChar.encode() for sChar in strbArr])

async def main(app):
    await asyncio.gather(app.async_run("asyncio"))


if __name__ == "__main__":
    #SayHello().run()
    Logger.setLevel(logging.DEBUG)

    # app running on one thread with two async coroutines
    app = SayHello()
    #app.run()
    asyncio.run(main(app))
