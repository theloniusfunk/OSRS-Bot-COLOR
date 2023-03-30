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

class OSRSMiningTpower(OSRSBot):
    def __init__(self):
        bot_title = "cMiningTpower"
        description = "This bot mines."
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
        mined = 0

        while time.time() - start_time < end_time:

            while not api_s.get_is_inv_full():
                pink = self.get_nearest_tag(clr.PINK) 
                yellow = self.get_nearest_tag(clr.YELLOW)
                cyan = self.get_nearest_tag(clr.CYAN)
                gate1 = 0;
                if pink:
                    print("pink up")
                    rock = self.get_all_tagged_in_rect(self.win.game_view, clr.WHITE)
                    check = 2;
                    gate1 = 1;
                elif yellow:
                    print("yellow up")
                    rock = self.get_all_tagged_in_rect(self.win.game_view, clr.RED)
                    check = 3;
                    gate1=1;
                elif cyan:
                    print("cyan up")
                    rock = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
                    check = 1;
                    gate1=1;     
                if gate1 == 1:
                    self.mouse.move_to(rock[0].random_point())
                    self.mouse.click()
                    print("click")
                    timeout = 0;
                    gate2 = 0;
                    gatesingle = 0;
                
                if check == 2: #mined pink(white) check yellow(red)
                    temp_move = self.get_all_tagged_in_rect(self.win.game_view, clr.RED)
                    self.mouse.move_to(temp_move[0].random_point())
                    gatesingle += 0;
                    if gatesingle >= 2:
                        occupied_slots = api_s.get_inv_item_indices(ids.IRON_ORE)
                        self.drop(occupied_slots[:1])
                        gatesingle = 0;
                    print("move yellow")
                    while self.get_nearest_tag(clr.PINK):
                        time.sleep(0.05)
                        timeout += 1;
                        if timeout == 50: #5 second
                            print("break")
                            break
                        if gate2 == 0:
                            gate2 = 1;
                            print("mining")
                elif check== 3: #mined yellow(red) check cyan(green)
                    temp_move = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
                    self.mouse.move_to(temp_move[0].random_point())
                    gatesingle += 0;
                    if gatesingle >= 2:
                        occupied_slots = api_s.get_inv_item_indices(ids.IRON_ORE)
                        self.drop(occupied_slots[:1])
                        gatesingle = 0;
                    print("move green")
                    while self.get_nearest_tag(clr.YELLOW):
                        time.sleep(0.05)
                        timeout += 1;
                        if timeout == 50: #1 second
                            print("break")
                            break
                        if gate2 == 0:
                            gate2 = 1;
                            print("mining")
                elif check== 1: #mined cyan(green) check pink(white)
                    temp_move = self.get_all_tagged_in_rect(self.win.game_view, clr.WHITE)
                    self.mouse.move_to(temp_move[0].random_point())
                    gatesingle += 0;
                    if gatesingle >= 2:
                        occupied_slots = api_s.get_inv_item_indices(ids.IRON_ORE)
                        self.drop(occupied_slots[:1])
                        gatesingle = 0;
                    print("move white")
                    while self.get_nearest_tag(clr.CYAN):
                        time.sleep(0.05)
                        timeout += 1;
                        if timeout == 50: #1 second
                            print("break")
                            break
                        if gate2 == 0:
                            gate2 = 1;
                            print("mining")
                
                print("idle")

            else:
                self.drop_all()
                time.sleep(0.5)
                if occupied_slots := api_s.get_inv_item_indices(ids.IRON_ORE):
                    self.drop(occupied_slots[:])
                mined += 28
                self.log_msg(f"Rocks mined: ~{mined}")   

            self.update_progress((time.time() - start_time) / end_time)
        self.update_progress(1)
        self.__logout("Finished.")