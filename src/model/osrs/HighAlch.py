import time
import random
import pyautogui as pag

import utilities.game_launcher as launcher
import pathlib

import utilities.ocr as ocr
import utilities.random_util as rd
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSHighAlch(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "High Alch"
        description = "This bot high alchs. use standard magic spellbook and position alch behind spell."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False
        self.AlchCount = 0
  
    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def launch_game(self):
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite_with_settings(self, settings)

    def main_loop(self):
        # Setup API
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()

        exp = 0
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            
            if rd.random_chance(probability=0.002) and self.take_breaks:
                self.take_break(max_seconds=45, fancy=True)

            if exp == 0:
                self.log_msg("Selecting spellbook...")
                self.mouse.move_to(self.win.cp_tabs[6].random_point())
                self.mouse.click()

            self.log_msg("Selecting highalch...")
            if exp == 0:
                self.mouse.move_to(self.win.spellbook_normal[34].random_point())
            self.mouse.click()
            time.sleep(random.uniform(0.21, 0.63))
            if exp == 0:
                self.mouse.move_to(self.win.spellbook_normal[34].random_point())
                #self.mouse.move_to(self.win.inventory_slots[11].random_point())
            self.mouse.click()
            if exp := self.api_m.wait_til_gained_xp("Magic", timeout=5):
                if exp > 0:
                    #Alch Count
                    self.AlchCount += 1
                    #Log Count
                    self.log_msg(f"Alch Count: ~{self.AlchCount}")
                    time.sleep(random.uniform(0.2, 0.46))
                else:
                    self.log_msg(f"exp=: ~{exp}")
                    exp = 0
            else:
                self.set_status(BotStatus.STOPPED)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.set_status(BotStatus.STOPPED)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)