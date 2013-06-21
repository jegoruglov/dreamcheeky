#!/usr/bin/python

import time
import usb
import os
import multiprocessing

alarm_p = None
def alarm():
    while 1:
        os.system('play ALARM.WAV')
import pudb
pudb.set_trace()

def action(cur_state, prev_state):
    global alarm_p
    if alarm_p is not None and alarm_p.is_alive():
        alarm_p.terminate()
    if cur_state in lid_closed:
        print 'Safe'
    elif cur_state in button_on:
        print 'FIRE'
        os.system('play rocket_take_off.mp3')
        os.system('play target_destroyed.mp3')
    elif cur_state in lid_opened and prev_state in button_off:
        print 'Warning!!!'
        alarm_p = multiprocessing.Process(target=alarm)
        alarm_p.start()
    elif cur_state in button_off and prev_state in button_on:
        print 'Target destroyed.'
    elif cur_state in lid_opened and prev_state in button_on:
        print "That shouldn't happen"

dev = usb.core.find(idVendor=0x1d34, idProduct=0x000d)
configuration = list(dev)[0]
interface = list(configuration)[0]
endpoint = list(interface)[0]

try:
    dev.detach_kernel_driver(0)
except Exception, e:
    # It may already be unloaded.
    pass

cur_state = None
prev_state = None
waiting_coeff = 0.005

lid_closed = (20, 21)
lid_opened = (22, 23)
button_off = (21, 23)
button_on = (20, 22)

while 1:
    # USB setup packet. I think it's a USB HID SET_REPORT.
    result = dev.ctrl_transfer(bmRequestType=0x21, bRequest= 0x09, wValue= 0x0200, data_or_wLength="\x00\x00\x00\x00\x00\x00\x00\x02", timeout=500)
    try:
        result = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)[0]
        if cur_state is None:
            cur_state = result
            action(cur_state, prev_state)
        if result != cur_state:
            prev_state, cur_state = cur_state, result
            action(cur_state, prev_state)
    except Exception, e:
        # Sometimes this fails. Unsure why.
        pass#print e
    time.sleep(endpoint.bInterval * waiting_coeff) # 10ms
