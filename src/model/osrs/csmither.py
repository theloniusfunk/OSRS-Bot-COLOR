import time
import random
import pyautogui as pag
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

import utilities.api.item_ids as ids
import utilities.imagesearch as imsearch
import utilities.ocr as ocr
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class OSRSSmither(OSRSBot):
    def __init__(self):
        bot_title = "cSmith"
        description = "This bot smiths. Position your character near the banks at Var and press Play."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
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

    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        gate = 0;

        while time.time() - start_time < end_time:
            
            # Clicks on Furnace
            while api_s.get_inv_item_indices(ids.STEEL_BAR):
                    self.__move_mouse_to_anvil()
                    self.walkrun(10) #10 energy or higher
                    #running to anvil
                    while not api_m.get_is_player_idle():
                        time.sleep(1)
                        print("not idle - running")
                    print("idle - at anvil")
                    pag.press("space")
                    gate = 0;
                    while not api_m.get_is_player_idle():
                        time.sleep(2)
                        print("not idle - smithing")
                    print("idle")

            if gate == 0:
                print("Go to Bank")
                self.take_break(max_seconds=1)
                cyan_tile = self.get_nearest_tag(clr.CYAN)
                self.mouse.move_to(cyan_tile.random_point())
                self.walkrun(10) #10 energy or higher
                    #running to bank
                while not api_m.get_is_player_idle():
                    time.sleep(1)
                    print("not idle - running")
                print("idle - at bank")

            if DepositAll:= imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "DepositAll.png"), self.win.game_view, 0.05):
                if api_s.get_inv():
                    print("deposit all")
                    self.mouse.move_to(DepositAll.random_point())
                    self.mouse.click()
                    self.take_break(max_seconds=1)
            
            #Fill inventory with bar1
            self.__move_mouse_to_bar_1()
            self.mouse.click()
            time.sleep(random.uniform(0.85, 1.24))

            # Escape key out of bank menu
            if gate == 0:
                pag.press("esc")
                print("escape")
                gate = 1;
            time.sleep(random.uniform(0.21, 0.31))

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __move_mouse_to_anvil(self):
        anvil = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
        self.mouse.move_to(anvil[0].random_point())

        if not self.mouseover_text(contains=["Smelt"] + ["Furnace"], color=[clr.OFF_WHITE, clr.OFF_CYAN]):
            self.mouse.move_to(anvil[0].random_point())
        return True

    def __move_mouse_to_bar_1(self):
        bank_bar = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        self.mouse.move_to(bank_bar[0].random_point())
        return True
    
    def walkrun(self, energy):
        if self.get_run_energy() > energy:
                    pag.keyDown("ctrl")
                    time.sleep(random.uniform(0.132, 0.344))
                    self.mouse.click()
                    time.sleep(random.uniform(0.135, 0.333))
                    pag.keyUp("ctrl")
        else:
            self.mouse.click()
        return True