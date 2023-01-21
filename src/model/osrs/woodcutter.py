import time

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


class OSRSWoodcutter(OSRSBot):
    def __init__(self):
        bot_title = "Woodcutter"
        description = "This bot power-chops wood. Position your character near some trees, tag them, and press the play button."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 50
        self.take_breaks = True

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
        
        self.logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        
        
        while time.time() - start_time < end_time:
            # 5% chance to take a break between tree searches
            if rd.random_chance(probability=0.05) and self.take_breaks:
                self.take_break(max_seconds=30, fancy=True)

                """ # 2% chance to drop logs early
                if rd.random_chance(probability=0.02):
                self.__drop_logs(api_s)

                # If inventory is full, drop logs
                if api_s.get_is_inv_full():
                self.__drop_logs(api_s) """
            
            print("check if inv full")
            # If inventory is full, go bank
            if api_s.get_is_inv_full():
                print("inv full")
                self.take_break(max_seconds=3)
                cyan_tile = self.get_nearest_tag(clr.CYAN)
                self.mouse.move_to(cyan_tile.random_point())
                pag.click()

                #running to bank
                while not api_m.get_is_player_idle():
                    time.sleep(0.5)
                    print("not idle - running")
                print("idle - at bank")    
                #self.take_break(max_seconds=1)

                if DepositAll:= imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "DepositAll.png"), self.win.game_view, 0.05):
                    print("deposit all")
                    self.mouse.move_to(DepositAll.random_point())
                    self.mouse.click()
                    self.take_break(max_seconds=1)
                    print("close bank")
                    pag.press('esc')
                    time.sleep(0.1)

            while not self.is_player_doing_action("Woodcutting"):
                #self.take_break(max_seconds=1)
                tree = self.get_nearest_tag(clr.PINK)
                if tree is None:
                    failed_searches += 1
                    self.log_msg("Failed to find tree.")
                    time.sleep(1)
                    if failed_searches > 30:
                        self.__logout("No tagged trees found. Logging out.")
                        return
                    break
                else:
                    print("move to!")
                    self.mouse.move_to(tree.random_point())
                    if not self.mouseover_text(contains="Chop", color=clr.OFF_WHITE):
                        print("No Chop")
                        time.sleep(1)
                        break
                    self.log_msg("Clicking tree...")
                    print("click!")
                    pag.click()
                    time.sleep(1)
                    failed_searches = 0
                    break
             
            while not api_m.get_is_player_idle():
                time.sleep(1)
                print("not idle")
            print("idle")    
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")


    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)