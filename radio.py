# -*- coding: utf8 -*-

import ast
import asyncio
import sys
import time

from rda5807m import Rda5807m


class Radio:

    def __init__(self):
        self.device = Rda5807m(1)

        self.commands = {
            "on": {"call": self.device.on, "help": "power on device"},
            "off": {"call": self.device.off, "help": "power off device"},
            "^": {"call": self.device.set_bass, "value": True, "help": "bass boost"},
            "v": {"call": self.device.set_bass, "value": False, "help": "normal bass"},
            "1": {"call": self.device.set_mute, "value": True, "help": "mute"},
            "0": {"call": self.device.set_mute, "value": False, "help": "unmute"},
            "s": {"call": self.device.set_stereo, "value": True, "help": "stereo"},
            "m": {"call": self.device.set_stereo, "value": False, "help": "mono"},
            "v": {"call": self.set_volume, "type": int, "help": "set volume"},
            "+": {"call": self.set_volume_plus, "help": "increase volume"},
            "-": {"call": self.set_volume_moins, "help": "decrease volume"},
            "f": {"call": self.set_frequency, "type": float, "help": "set frequency"},
            ">": {"call": self.device.set_seek, "value": True, "help": "seek up"},
            "<": {"call": self.device.set_seek, "value": False, "help": "seek down"},
            "d": {"call": self.set_deemphasis, "type": int, "help": "de-emphasize"},
            "i": {"call": self.get_infos, "help": "get infos"},
            "h": {"call": self.help, "help": "help"},
            "q": {"call": self.quit, "help": "quit"},
        }

        self.volume = 7  # default volume set in rda5807m.py

    def initialize(self):
        try:
            self.device.init_chip()
        except:
            print("problem while initializing")
            loop.stop()
        time.sleep(0.2)

    def print_prompt(self):
        print(">> ", end="", flush=True)

    def got_stdin_data(self):
        input_string = sys.stdin.readline().strip('\n')
        if input_string != "":
            self.parse_command(input_string)
        self.print_prompt()

    def quit(self):
        loop.stop()

    def help(self):
        for k, v in self.commands.items():
            print("%s : %s" % (k, v["help"]))

    def parse_command(self, entry):
        parts = entry.split('=')
        command = parts[0]
        if command in self.commands:
            params = self.commands[command]
            call = params["call"]
            if len(parts) == 1:
                if "value" in params:
                    value = params["value"]
                    call(value)
                else:
                    call()
            elif len(parts) == 2:
                value = ast.literal_eval(parts[1])
                if "type" in params:
                    type_ = params["type"]
                    if type(value) == type_:
                        call(value)
                    else:
                        print("bad value type")
                else:
                    print("invalid syntax")
            else:
                print("invalid syntax")
        else:
            print("command not found")

    def set_volume(self, volume):
        if not 0 <= volume <= 15:
            print("bad volume value (0-15)")
            return
        self.volume = volume
        self.device.set_volume(volume)

    def set_volume_moins(self):
        if self.volume == 0:
            return
        self.volume -= 1
        print("volume: %d" % (self.volume,))
        self.device.set_volume(self.volume)

    def set_volume_plus(self):
        if self.volume == 15:
            return
        self.volume += 1
        print("volume: %d" % (self.volume,))
        self.device.set_volume(self.volume)

    def set_frequency(self, frequency):
        if not 76 <= frequency <= 107.5:
            print("bad frequency value (76-107.5)")
        frequency = int(frequency * 10)
        self.device.set_frequency(frequency)

    def set_deemphasis(self, deemphasis):
        if deemphasis not in [50, 75]:
            print("bad de-emphasis value (50, 75)")
        self.device.set_deemphasis(deemphasis)

    def get_infos(self):
        infos = self.device.get_infos()
        print(infos)

    def poll_rds(self):
        self.device.process_rds()
        loop.call_later(0.1, self.poll_rds)

    def close(self):
        self.device.close()


radio = Radio()
radio.initialize()
radio.help()
radio.print_prompt()

loop = asyncio.get_event_loop()
loop.add_reader(sys.stdin, radio.got_stdin_data)
loop.call_later(1, radio.poll_rds)
loop.run_forever()

radio.close()
