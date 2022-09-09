import network
from machine import Pin, reset
from time import sleep

from visca_over_ip import Camera
from settings import Settings


class ControlPanel:
    def __init__(self, camera):
        self.buttons = []
        self.cam_is_moving = False
        self.camera = camera

    def check_and_execute_buttons(self):
        for button in self.buttons:
            if button.is_pressed():
                if not self.cam_is_moving:
                    button.action()
                self.cam_is_moving = True
                return
        if self.cam_is_moving:
            self.stop_cam()

    def add_button(self, button):
        button.camera = self.camera
        self.buttons.append(button)

    def stop_cam(self):
        self.camera.pantilt(0, 0)
        self.camera.zoom(0)
        self.cam_is_moving = False
        print('Stop!')


class Button:
    def __init__(self, pin, pull_up=True):
        self.pin = pin
        self._pull_up = pull_up

    def action(self):
        pass

    def is_pressed(self):
        return self.pin.value() != self._pull_up


class PresetButton(Button):
    def __init__(self, pin, preset):
        super().__init__(pin)
        self.preset = preset
        self.camera = None

    def action(self):
        print('Preset fired!')
        self.camera.recall_preset(preset_num=self.preset)
        sleep(1.5)


class ZoomButton(Button):
    def __init__(self, pin, zoom_in=True):
        super().__init__(pin)
        self.camera = None
        self.zoom_speed = Settings.ZOOM_SPEED
        if not zoom_in:
            self.zoom_speed *= -1

    def action(self):
        self.camera.zoom(self.zoom_speed)
        print('Zoom Action fired!')


class Joystick:
    def __init__(self, up_btn, right_btn, down_btn, left_btn):
        self.up_btn = up_btn
        self.right_btn = right_btn
        self.down_btn = down_btn
        self.left_btn = left_btn
        self.pan_speed = 0
        self.tilt_speed = 0
        self.speed = Settings.PANTILT_SPEED
        self.camera = None

    def _set_speeds(self):
        self.tilt_speed = 0
        self.pan_speed = 0

        if not self.up_btn.pin.value():
            self.tilt_speed = self.speed * -1
        if not self.right_btn.pin.value():
            self.pan_speed = self.speed
        if not self.down_btn.pin.value():
            self.tilt_speed = self.speed
        if not self.left_btn.pin.value():
            self.pan_speed = self.speed * -1

        if Settings.INVERT_PAN:
            self.pan_speed *= -1
        if Settings.INVERT_TILT:
            self.tilt_speed *= -1

    def is_pressed(self):
        self._set_speeds()
        return self.tilt_speed != 0 or self.pan_speed != 0

    def action(self):
        self.camera.pantilt(self.pan_speed, self.tilt_speed)
        print('Joystick Action fired!')


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(Settings.WIFI_SSID, Settings.WIFI_KEY)
        while not sta_if.isconnected():
            pass
        print('connected')


def init_cam_and_panel():

    cam = Camera(Settings.CAMERA_IP_ADDRESS)
    up_button = Button(Pin(26, Pin.IN, Pin.PULL_UP))
    right_button = Button(Pin(14, Pin.IN, Pin.PULL_UP))
    down_button = Button(Pin(27, Pin.IN, Pin.PULL_UP))
    left_button = Button(Pin(12, Pin.IN, Pin.PULL_UP))

    joystick = Joystick(up_button, right_button, down_button, left_button)
    zoom_in_btn = ZoomButton(Pin(18, Pin.IN, Pin.PULL_UP), zoom_in=True)
    zoom_out_btn = ZoomButton(Pin(19, Pin.IN, Pin.PULL_UP), zoom_in=False)

    preset_btn_1 = PresetButton(Pin(15, Pin.IN, Pin.PULL_UP), Settings.PRESET_ID_1)
    preset_btn_2 = PresetButton(Pin(2, Pin.IN, Pin.PULL_UP), Settings.PRESET_ID_2)
    preset_btn_3 = PresetButton(Pin(0, Pin.IN, Pin.PULL_UP), Settings.PRESET_ID_3)
    preset_btn_4 = PresetButton(Pin(4, Pin.IN, Pin.PULL_UP), Settings.PRESET_ID_4)
    preset_btn_5 = PresetButton(Pin(5, Pin.IN, Pin.PULL_UP), Settings.PRESET_ID_5)

    ctrl = ControlPanel(cam)
    ctrl.add_button(joystick)
    ctrl.add_button(zoom_in_btn)
    ctrl.add_button(zoom_out_btn)
    ctrl.add_button(preset_btn_1)
    ctrl.add_button(preset_btn_2)
    ctrl.add_button(preset_btn_3)
    ctrl.add_button(preset_btn_4)
    ctrl.add_button(preset_btn_5)

    return ctrl


if __name__ == '__main__':
    try:
        # Initialize WiFi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        do_connect()

        # Initialize camera and Panel
        panel = init_cam_and_panel()
        while True:
            do_connect()
            panel.check_and_execute_buttons()
            print('sleep')
            sleep(0.1)

    except:
        sleep(5)
        reset()

