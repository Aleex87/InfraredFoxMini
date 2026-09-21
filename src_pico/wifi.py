import network
import time
import ujson


def connect_wifi():
    # Load WiFi credentials
    with open("wifi_credentials.json", "r") as file:
        credentials = ujson.load(file)

    wifi_ssid = credentials["WIFI_SSID"]
    wifi_password = credentials["WIFI_PASSWORD"]

    wlan = network.WLAN(network.STA_IF)

    # Activate WiFi interface
    if not wlan.active():
        wlan.active(True)
        time.sleep(1)

    # If already connected, do not reconnect
    if wlan.isconnected():
        print("WiFi already connected!")
        print("Pico IP:", wlan.ifconfig()[0])
        return wlan

    print("Connecting to WiFi...")
    wlan.connect(wifi_ssid, wifi_password)

    timeout = 30

    while not wlan.isconnected() and timeout > 0:
        print("Connecting to WiFi, please wait...", "Status:", wlan.status())

        time.sleep(1)
        timeout -= 1

    if not wlan.isconnected():
        print("WiFi status:", wlan.status())
        raise RuntimeError("Could not connect to WiFi")

    print("WiFi connected!")
    print("Pico IP:", wlan.ifconfig()[0])

    return wlan
