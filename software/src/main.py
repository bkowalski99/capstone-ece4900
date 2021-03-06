# main.py

# imports
import time
import struct
import ubluetooth as bluetooth
from machine import I2C
from imu import MPU6050
from micropython import const
from ble_advertising import advertising_payload

# constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

# functions


def bt_irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        # A central has connected to this peripheral.
        conn_handle, addr_type, addr = data
        connections.add(conn_handle)
        ble.gap_advertise(None)
        print('[bluetooth] device connected')
    elif event == _IRQ_CENTRAL_DISCONNECT:
        # A central has disconnected from this peripheral.
        conn_handle, addr_type, addr = data
        connections.remove(conn_handle)
        ble.gap_advertise(500000)
        print('[bluetooth] device disconnected')
    else:
        print('[bluetooth] received event {}'.format(event))


# entrypoint
i2c = I2C(0)
imu = MPU6050(i2c)
ble = bluetooth.BLE()
ble.active(True)
ble.irq(bt_irq)
ble.config(gap_name='Bosu')

# configure the services that will be advertised
ACCEL_UUID = bluetooth.UUID('7ED5A5BC-8013-4753-B199-0A364D52E5DE')
ACCEL_CHAR = (bluetooth.UUID('F477FD95-41F0-4C73-9093-5DA7DC624DF0'),
              bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
ACCEL_SERVICE = (ACCEL_UUID, (ACCEL_CHAR,),)
SERVICES = (ACCEL_SERVICE,)

((accel,),) = ble.gatts_register_services(SERVICES)

connections = set()

# this advertising payload can't be too long
payload = advertising_payload(name='Bosu Ballers')
ble.gap_advertise(500000, adv_data=payload)

while True:
    for conn in connections:
        xyz = imu.accel.xyz
        ble.gatts_notify(conn, accel, struct.pack('<fff', *xyz))
    time.sleep_ms(100)
