import time

import pyautogui as pag
import utilities.random_util as rd
import utilities.api.item_ids as ids
import utilities.imagesearch as imsearch
#import utilities.window as win

import utilities.color as clr
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.status_socket import StatusSocket
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.geometry import Point, RuneLiteObject



class OSRSFishCook(OSRSBot):
    def __init__(self):
        title = "FishCook"
        description = "This bot fishes and cooks"
        super().__init__(bot_title=title, description=description)
        self.running_time = 50
        self.protect_slots = 1

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_slider_option("protect_slots", "When dropping, protect first x slots:", 0, 4)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "protect_slots":
                self.protect_slots = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.log_msg(f"Protecting first {self.protect_slots} slots when dropping inventory.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # API setup
        api_s = StatusSocket()
        api_m = MorgHTTPSocket()
        fished = 0
        Raw_trout = ids.RAW_TROUT
        Raw_salmon = ids.RAW_SALMON
        failed_searches = 0
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # Check if inventory is full; cook specific raw fish; drop all but protected
            if api_s.get_is_inv_full():
                self.take_break(max_seconds=3)
                #while raw fish exists (declare id above)
                while api_s.get_inv_item_indices(Raw_trout) or api_s.get_inv_item_indices(Raw_salmon):
                    #move mouse to cook fire (PINK)
                    fire = self.get_nearest_tag(clr.PINK)
                    self.mouse.move_to(fire.random_point())
                    pag.click()
                    self.take_break(max_seconds=1) 
                    while not api_m.get_is_player_idle():
                        time.sleep(1)
                        print("not idle - running")
                    print("idle - fire") 
                    pag.press("space")
                    #search for specific fish to cook 
                    #if Cook_Trout:= imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("items", "Cook_Trout.png"), self.win.chat, 0.05):
                     #   print("cook trout")
                     #   self.mouse.move_to(Cook_Trout.random_point())
                     #   pag.click()
                    while not api_m.get_is_player_idle():
                        time.sleep(1)
                        print("not idle - cooking")
                    print("idle") 
                    #if not idle
                self.take_break(max_seconds=2)   
                self.drop_all(skip_slots=list(range(self.protect_slots)))
                fished += 28 - self.protect_slots
                self.log_msg(f"Fishes fished: ~{fished}")
            # If not fishing, click fishing spot
            while not self.is_player_doing_action("Fishing"):
                self.take_break(max_seconds=1)
                fishingspot = self.get_nearest_tag(clr.CYAN)
                if fishingspot is None:
                    failed_searches += 1
                    self.take_break(max_seconds=2)
                    if failed_searches > 10:
                        self.log_msg("Failed to find fishing spot.")
                        self.set_status(BotStatus.STOPPED)
                        return
                else:
                    self.log_msg("Clicking fishing spot...")
                    self.mouse.move_to(fishingspot.random_point())
                    pag.click()
                    self.take_break(max_seconds=1)
                    break
             
            while not api_m.get_is_player_idle():
                time.sleep(1)
                print("not idle")
            print("idle")    
            self.take_break(max_seconds=3)

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)