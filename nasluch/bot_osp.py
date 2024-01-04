#! /bin/env python3

import queue
import subprocess
import sys
import threading
import time
from com.dtmilano.android.viewclient import ViewClient
from com.dtmilano.android.viewclient import ViewNotFoundException

class osp_bot(object):
    def __init__(self):
        self.device, self.serialno = ViewClient.connectToDeviceOrExit(verbose=False)
        self.vc = ViewClient(device=self.device, serialno=self.serialno)

    def open_messenger(self):
        if self.device.isScreenOn() == False:
            print("Screen disabled. Pressing power key.", file=sys.stderr)
            self.device.press('KEYCODE_POWER')
        for _ in range(0, 10):
            print("Pressing back key.", file=sys.stderr)
            self.device.press('KEYCODE_BACK')
            ViewClient.sleep(0.1)
        print("Pressing home key.", file=sys.stderr)
        self.device.press('KEYCODE_HOME')

        ViewClient.sleep(0.3)
        self.device.startActivity(component="com.facebook.orca/.auth.StartScreenActivity")
        ViewClient.sleep(2)
        self.vc.dump()
        self.vc.findViewWithContentDescription("New message").touch()
        ViewClient.sleep(1)
        self.device.type("Podzial Bojowy")
        ViewClient.sleep(2)
        self.vc.dump()
        self.vc.findViewByIdOrRaise("id/no_id/8").touch()
        ViewClient.sleep(1)

    def check_messenger_ready(self):
        if self.device.isScreenOn() == False:
            print("Screen disabled. Presing power key.", file=sys.stderr)
            self.device.press('KEYCODE_POWER')
        # pb_chat = (self.vc.findViewWithContentDescription("Podział Bojowy.") != None)
        # print("Podzial Bojowy {} found".format("" if pb_chat == True else "not"))
        self.vc.dump()
        pb_chat = (self.vc.findViewWithText("Aa") != None)
        print("Chat {}found".format("" if pb_chat == True else "not "), file=sys.stderr)
        if pb_chat == False:
            for _ in range(0, 30):
                self.device.press('DEL')
            self.vc.dump()
            pb_chat = (self.vc.findViewWithText("Aa") != None)

        if pb_chat == True:
            self.vc.findViewWithText("Aa").touch()

        ViewClient.sleep(1)

        kb_shown = self.device.isKeyboardShown()
        print("Keyboart {}shown".format("" if kb_shown == True else "not "), file=sys.stderr)
        return (pb_chat & kb_shown)

    def send_message(self, text):
        self.device.type("[nasluch]: " + text)
        self.vc.dump()
        self.vc.findViewWithContentDescription("Send").touch()

def messenger_func(q):
    ob = osp_bot();
    while True:
        osp_name = q.get()
        while True:
            try:
                if ob.check_messenger_ready() == True:
                    print("Messenger ready", file=sys.stderr)
                    print("Sending: {}".format(osp_name), file=sys.stderr)
                    ob.send_message(osp_name)
                    break
                else:
                    print("Messenger not ready", file=sys.stderr)
                    ob.open_messenger()
            except Exception as e:
                print(e, file=sys.stderr)
                break


def main():
    filename = "/home/jacek/projects/scripts/nasluch/osp.csv"

    patterns = {}

    with open(filename) as f:
        for line in f:
            key, value = line.strip().split(':')
            patterns[int(key)] = value

    q = queue.Queue(maxsize=30)
    mess_thread = threading.Thread(target=messenger_func, args=(q,))
    mess_thread.start()

    while True:
        try:
            inp = input()
            if inp == "":
                continue

            try:
                stqc_code = inp.split()[9]
                int(stqc_code)
            except:
                continue
            else:
                try:
                    message = "Alarm dla " + patterns[int(stqc_code)]
                except:
                    message = "Alarm dla nieznanej jednostki"
                finally:
                    q.put(message)
                    print(message)
                    with open("/home/jacek/nasluch/syreny.txt", 'a') as logfile:
                        logfile.write(inp + "  (" + message + ")\n")
        except EOFError:
            # time.sleep(0.1)
            continue

    mess_thread.join()

main()


