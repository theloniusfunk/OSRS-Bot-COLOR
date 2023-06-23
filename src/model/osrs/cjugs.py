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

class OSRSJugs(OSRSBot):
    def __init__(self):
        bot_title = "cJugs"
        description = "This bot makes wine."
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
        jugs = 0

        while time.time() - start_time < end_time:
            count = 0;
            pink = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)

            
            while api_s.get_inv_item_indices(ids.JUG_OF_WATER) and api_s.get_inv_item_indices(ids.GRAPES):
                if api_s.get_is_inv_full(): #for make wine relying on full inv
                    self.makewine() #make wine
                    jugs += 14;
                    time.sleep(0.7) #needed or will double make wine twice
                    self.mouse.move_to(pink[0].random_point())
                    pag.press("space")
                    while not api_m.get_is_player_idle():
                        time.sleep(random.uniform(0.3, 0.35))
                        print("not idle - making jugs")
                    print("all jugs made")
                else:
                    break
            self.mouse.move_to(pink[0].random_point()) #open bank with pink marker
            self.mouse.click()
            print("deposit all")
            while not imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "DepositAll.png"), self.win.game_view, 0.05):
                time.sleep(random.uniform(0.1, 0.3))
                count += 1;
                print(count)
                if count == 10:
                    break
            if count == 10:
                continue
            else:
                self.__DepositAll()
                time.sleep(random.uniform(0.2, 0.25))
                self.__move_mouse_to_item1()
                self.mouse.click()
                time.sleep(random.uniform(0.198, 0.31))
                self.__move_mouse_to_item2()
                self.mouse.click()
                time.sleep(random.uniform(0.13, 0.312))

            # Escape key out of bank menu
            pag.press("esc")
            print("escape")
            self.mouse.move_to(self.win.inventory_slots[13].random_point())

            
            self.log_msg(f"jugs made: ~{jugs}")   

            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.__logout("Finished.")
    
    def makewine(self):
        self.mouse.move_to(self.win.inventory_slots[13].random_point())
        self.mouse.click()
        time.sleep(random.uniform(0.132, 0.344))
        #ADD RANDOM CHANCE FOR OTHER INV SLOT???????
        self.mouse.move_to(self.win.inventory_slots[14].random_point())
        self.mouse.click()
        time.sleep(random.uniform(0.132, 0.344))
        return True
    def __DepositAll(self):
        DepositAll = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "DepositAll.png"), self.win.game_view, 0.05)
        self.mouse.move_to(DepositAll.random_point())
        self.mouse.click()
        return True
    def __move_mouse_to_item1(self):
        green = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        self.mouse.move_to(green[0].random_point())
        return True
    def __move_mouse_to_item2(self):
        red = self.get_all_tagged_in_rect(self.win.game_view, clr.RED)
        self.mouse.move_to(red[0].random_point())
        return True
