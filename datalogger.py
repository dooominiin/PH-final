import os 
import sdcard
import time

from machine import Pin, SPI, Timer

class datalogger:
    def __init__(self, input, output, log_periode):
        self.mount()
        names_i = input.get_inputs().keys()
        names_o = output.get_outputs().keys()
        combined_names = list(set(names_i) | set(names_o))
        self.log_data = {}  # Dictionary für die Logdaten
        for key in combined_names:
            self.log_data[key] = 0
        self.filename = "data_log.txt"


        def write_to_log(timer):
            # Prüfe, ob die Logdatei bereits existiert
            file_exists = False
            try:
                with open("sd/" + self.filename, "r"):
                    file_exists = True
            except Exception:
                pass

            if not file_exists:
                try:
                    with open("sd/" + self.filename, "w") as file:
                        # Schreibe die Bezeichnungen in die erste Spalte
                        header = ";".join(self.log_data.keys())
                        file.write(header + "\n")
                except Exception as e:
                    print(e)
                    self.remount()
            for key, i in input.get_inputs().items():
                self.log_data[key] = i
            for key, o in output.get_outputs().items():
                self.log_data[key] = o.value()
            # Schreibe die Werte periodisch in die Logdatei
            values = ";".join(str(data) for data in self.log_data.values())
            if file_exists:
                try:
                    t = time.ticks_ms()
                    with open("sd/" + self.filename, "a") as file:
                        file.write(values + "\n")
                        #print("daten geloggt {}".format(self.log_data["datetime"]))
                    print("speichern benötigt {} s".format(1000*(time.ticks_ms()-t)))
                except Exception as e:
                    print(e)
                    self.remount()

        t = Timer()
        t.init(mode=Timer.PERIODIC, period=log_periode * 1000, callback=write_to_log)

    def mount(self):
        try:
            self.sd = sdcard.SDCard(SPI(0, 40_000_000, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), Pin(17))
            os.mount(self.sd, '/sd') # type: ignore
            print("\nSD Karte erfolgreich verbunden.")
            print(os.listdir('/sd'))
        except Exception as e:
            print(e)

    def remount(self):
        try:
            os.umount(self.sd)
        except Exception as e:
            print(e)
        self.mount()
