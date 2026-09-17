from secrets import WIFI_SSID, WIFI_PASSWORD
import network , time



def connect_wifi():
    wlan= network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        print("Connecting to wifi, please wait..")
        time.sleep(2)
    print("Woho Wifi connected!")
    print("Pico ip:", wlan.ifconfig()[0])

    return wlan
    


