# WiFi PTZ Controller

DIY remote for controlling cameras via visca over ip.
Running on ESP32 microcontroller and micropython. Using arcade buttons from amazon in a self designed 3d printed case.

![Controller Overview](/img/build_06.jpg)

### Features

- Joystick for `pan` and `tilt`
- Two buttons for `zoom in` and `zoom out`
- Five buttons for calling `presets`

### Installation

#### 1. Flashing micropython to ESP32

Detailed instructions:
https://docs.micropython.org/en/latest/esp32/tutorial/intro.html
___
    pip install esptool

Erase ESP's flash 

    esptool.py --port COM4 erase_flash

Download a micropython image:
https://micropython.org/download/#esp32

Write the image

    esptool.py --chip esp32 --port COM4 write_flash -z 0x1000 esp32-20180511-v1.9.4.bin


Replace `COM4` with the port your ESP is connected.
The filename of the image `esp32-20180511-v1.9.4.bin` needs to be replaced by the name of the downloaded image. 

#### 2. Download the repository

Clone the repo or download it manually

    git clone git@github.com:scrtt/wifi_ptz_controller.git

#### 3. Customize the settings

In `src/settings.py` it is necessary to edit:
- `CAMERA_IP_ADDRESS`
- `WIFI_SSID`
- `WIFI_KEY`

#### 4. Upload src files to your ESP

Install ampy https://github.com/scientifichackers/ampy

    pip install adafruit-ampy

In the project root switch to the src folder

    cd src

Copy files to the ESP

    ampy --port COM4 put main.py
    ampy --port COM4 put settings.py
    ampy --port COM4 put visca_over_ip

Restart the ESP and be happy 😎

### 4. Credits

Python VISCA over IP module:
https://github.com/misterhay/VISCA-IP-Controller
