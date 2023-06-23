import time
import random
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import pyautogui as pag
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
import utilities.imagesearch as imsearch

from typing import List, Union

class OSRSFiremaking(OSRSBot):
    def __init__(self):
        bot_title = "cFiremaking"
        description = "This bot makes fire."
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
        fire = 0
        count = 1
        yellow = 1
        red = 0
        exp = 0

        while time.time() - start_time < end_time:
            ashes = 0;
            # if no logs in inventory go bank
            while not api_s.get_inv_item_indices(ids.logs): 
                if api_s.get_inv_item_indices(ids.ASHES):
                    ashes = 1 
                    print("ASHES")
                cyan = self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN)
                self.mouse.move_to(cyan[0].random_point()) #open bank with cyan marker             
                self.mouse.click()
                while not api_m.get_is_player_idle():
                        time.sleep(random.uniform(0.3, 0.35))
                        print("not idle - walking to bank")
                print("at bank")
                if ashes == 1:
                    self.__DepositAll()
                    time.sleep(random.uniform(0.2, 0.25))
                #Get Logs
                pink = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
                self.mouse.move_to(pink[0].random_point())
                self.mouse.click()
                time.sleep(random.uniform(0.1, 0.2))
                pag.press("esc")
                print("escape")
                count = 1
                time.sleep(random.uniform(0.4, 0.5))
            
            #check if you have logs in inv
            while api_s.get_inv_item_indices(ids.logs):
                if red == 1:
                    red = self.get_all_tagged_in_rect(self.win.game_view, clr.RED)
                    self.mouse.move_to(red[0].random_point())
                    self.mouse.click() #ADD CTRL RUN HERE? HOW IS RUN ENERGY?
                    red = 0
                    yellow = 1
                elif yellow == 1:
                    yellow = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
                    self.mouse.move_to(yellow[0].random_point())
                    self.mouse.click() #ADD CTRL RUN HERE? HOW IS RUN ENERGY?
                    red = 1
                    yellow = 0
                #start_tile, count = (self.red(), 1) if count == 0 else (self.yellow(), 0)
                #self.mouse.move_to(start_tile.random_point())
                #self.mouse.click() #ADD CTRL RUN HERE? HOW IS RUN ENERGY?
                #time.sleep(random.uniform(0.2, 0.25))
                while not api_m.get_is_player_idle():
                    time.sleep(0.05)
                    #time.sleep(random.uniform(0.2, 0.25))
                
                # if code reaches here then starting tile and will start to burn logs
                Tinder = api_s.get_inv_item_indices(ids.TINDERBOX)
                while api_s.get_inv_item_indices(ids.logs):
                    Logs = api_s.get_inv_item_indices(ids.logs)
                    if count == 1:
                        self.clicktinder(Tinder)
                        self.movelogs(Logs,modifier=0)
                        self.mouse.click()
                        #if exp := api_m.wait_til_gained_xp("Firemaking", timeout=5):
                        #    if exp > 0:
                        #        fire += 1
                        #        self.log_msg(f"fires made: ~{fire}")
                        fire += 1
                        self.log_msg(f"fires made: ~{fire}")
                        count += 1
                    elif count == 27:
                        self.clicktinder(Tinder)
                        self.movelogs(Logs,modifier=0)
                        count += 1
                        if exp := api_m.wait_til_gained_xp("Firemaking", timeout=5):
                            if exp > 0:
                                self.mouse.click()
                                fire += 1
                                self.log_msg(f"fires made: ~{fire}")
                    elif count < 27:
                        self.clicktinder(Tinder)
                        self.movelogs(Logs, modifier=1)
                        count += 1
                        if exp := api_m.wait_til_gained_xp("Firemaking", timeout=5):
                            if exp > 0:
                                self.mouse.click()
                                fire += 1
                                self.log_msg(f"fires made: ~{fire}")
                
                    if exp < 0:
                        self.log_msg(f"exp=: ~{exp}")
                        exp = 0
                        break

            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.__logout("Finished.")
    
    def clicktinder(self,Tinder):
        self.mouse.move_to(self.win.inventory_slots[Tinder[0]].random_point())
        self.mouse.click()
    
    def movelogs(self, Logs, modifier):
        self.mouse.move_to(self.win.inventory_slots[Logs[0+modifier]].random_point())

    def leftclick_two_items(self, item1, item2, lowerbound, upperbound):

        for x, y in zip(item1, item2):
            self.mouse.move_to(self.win.inventory_slots[x].random_point())
            self.mouse.click()
            #time.sleep(random.uniform(lowerbound, upperbound))
            self.mouse.move_to(self.win.inventory_slots[y].random_point())
            self.mouse.click()
            #time.sleep(random.uniform(lowerbound, upperbound))
