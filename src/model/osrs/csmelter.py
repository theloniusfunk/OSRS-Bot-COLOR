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


class OSRSSmelter(OSRSBot):
    def __init__(self):
        bot_title = "cSmelter"
        description = "This bot Smelts iron bars and takes advantage of Rings of Forging. Position your character near the banks at Edgeville and press Play."
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

        keyboard = KeyboardController()
        mouse = MouseController()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            
            # Clicks on Furnace
            while api_s.get_inv_item_indices(ids.IRON_ORE):
                if result := ocr.find_text("Ring of Forging", self.win.chat, ocr.PLAIN_12, clr.PURPLE):
                    print("Ring MELTED")
                    break
                else: 
                    self.__move_mouse_to_furnace()
                    self.mouse.click()
                    self.take_break(max_seconds=1) 
                    #running to furnace
                    while not api_m.get_is_player_idle():
                        time.sleep(1)
                        print("not idle - running")
                    print("idle - at furnace")
                    pag.press("space")
                    while not api_m.get_is_player_idle():
                        time.sleep(2)
                        print("not idle - smelting")
                    print("idle")

            print("Go to Bank")
            self.take_break(max_seconds=3)
            cyan_tile = self.get_nearest_tag(clr.CYAN)
            self.mouse.move_to(cyan_tile.random_point())
            self.mouse.click()
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
            
            #If Ring of Rorging melted. Equip a new one
            if result := ocr.find_text("Ring of Forging", self.win.chat, ocr.PLAIN_12, clr.PURPLE):
                print("line 100")
                self.__withdraw_rof()
                time.sleep(random.uniform(0.19, 0.36))
                self.__equip_rof()
                time.sleep(random.uniform(0.5, 1))

                     
            # Check to make sure it was equiped, if not, equip again
            while not api_s.get_player_equipment():
                print("no equipment")
                self.__withdraw_rof()
                time.sleep(random.uniform(0.19, 0.36))
                self.__equip_rof()
                self.take_break(max_seconds=2)
                
            
            #Fill inventory with ore1
            self.__move_mouse_to_ore_1()
            self.mouse.click()
            time.sleep(random.uniform(0.85, 1.24))

            """#Fill inventory with ore2
            self.__move_mouse_to_ore_2()
            pag.keyDown("shift")
            self.mouse.click()
            pag.keyUp("shift")
            time.sleep(random.uniform(0.85, 1.24))
            """

            """
            #Check you have a full inventory of iron ore, if not, try again
            if not self.api_s.get_is_inv_full():
                self.__move_mouse_to_ore_1()
                self.mouse.click()
                time.sleep(random.uniform(0.32, 0.5))
            """
            # Escape key out of bank menu
            pag.press("esc")
            time.sleep(random.uniform(0.68, 1.12))

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")
    """
    def __move_mouse_to_bank(self):
        banks = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
        self.mouse.move_to(banks[0].random_point())

        if not self.mouseover_text(contains=["Bank"] + ["Bank Booth"], color=[clr.OFF_WHITE, clr.OFF_CYAN]):
            self.mouse.move_to(banks[0].random_point())
        return True
    """
    def __move_mouse_to_furnace(self):
        furnace = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
        self.mouse.move_to(furnace[0].random_point())

        if not self.mouseover_text(contains=["Smelt"] + ["Furnace"], color=[clr.OFF_WHITE, clr.OFF_CYAN]):
            self.mouse.move_to(furnace[0].random_point())
        return True
    """
    def __deposit_inventory(self):
        deposit = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank_deposit_all.png"), self.win.game_view)
        if deposit is None:
            print("Cannot Find Deposit Box")
        self.mouse.move_to(deposit.random_point())
        return True
    """
    def __move_mouse_to_ore_1(self):
        iron_ore = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        self.mouse.move_to(iron_ore[0].random_point())
        return True
    
    def __move_mouse_to_ore_2(self):
        iron_ore = self.get_all_tagged_in_rect(self.win.game_view, clr.RED)
        self.mouse.move_to(iron_ore[0].random_point())
        return True

    def __withdraw_rof(self):
        rof = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
        self.mouse.move_to(rof[0].random_point())
        self.mouse.click()
        return True

    def __equip_rof(self):
        rof = self.mouse.move_to(self.win.inventory_slots[0].random_point())
        pag.keyDown("shift")
        self.mouse.click()
        pag.keyUp("shift")
        return True

    """def __anti_ban(self):
        self.mouse.move_to(self.win.cp_tabs[1].random_point())
        self.mouse.click()
        time.sleep(random.uniform(0.69, 1.56))
        self.mouse.move_to(self.win.inventory_slots[7].random_point())
        time.sleep(random.uniform(2.69, 5.56))
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()


    def __anti_ban2(self):
        self.mouse.move_to(self.win.cp_tabs[4].random_point())
        self.mouse.click()
        time.sleep(random.uniform(1, 2.56))
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()"""