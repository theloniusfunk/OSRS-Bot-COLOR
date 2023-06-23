import time
import random
import pyautogui as pag

import utilities.game_launcher as launcher
import pathlib

import utilities.ocr as ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSAddyRock(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Addy Rock"
        description = "This bot mines Addy Ore from the Mining Guild and Banks. Position your character at Falador South Bank, with Empty Inventory."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False
        self.Trips = 0
        self.Ore = 0

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
        gate1 = 0
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            # self.mouse.move_to(self.win.cp_tabs[3].random_point())
            # self.mouse.click()

            #inv empty and at bank
            if not self.api_s.get_inv_item_indices(ids.ADAMANTITE_ORE) and self.get_nearest_tag(clr.CYAN):
                self.__identify_guild_ladder()
                self.mouse.click()
                # self.walkrun(20) #20 energy or higher
                while not self.api_m.get_is_player_idle():
                    time.sleep(random.uniform(0.5, 0.75))
                    print("not idle - running")
            
            #mining
            while not self.api_s.get_is_inv_full():
                pink = self.get_nearest_tag(clr.PINK) 
                yellow = self.get_nearest_tag(clr.YELLOW)
                if pink:
                    print("pink up")
                    rock = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
                    gate1 = 1
                    check = 1
                elif yellow:
                    print("yellow up")
                    rock = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
                    check = 2
                    gate1= 1
                elif not pink and not yellow:
                    time.sleep(0.5)
                    # self.mouse.move_to(self.win.cp_tabs[10].random_point())
                    # self.mouse.click()
                    pag.press("left") #switch world
                    time.sleep(random.uniform(8, 11))
                    gate1 = 0

                if gate1 == 1:
                    self.mouse.move_to(rock[0].random_point())
                    self.mouse.click()
                    print("click")
                    # timeout = 0;
                if gate1 == 1:
                    if check == 1: #mined pink check yellow
                        while self.get_nearest_tag(clr.PINK):
                            time.sleep(0.5)
                            # timeout += 1;
                            # if timeout == 50: #5 second
                            #     print("break")
                            #     break
                            print("running or mining pink")
                    elif check == 2: #mined yellow check pink
                        while self.get_nearest_tag(clr.YELLOW):
                            time.sleep(0.5)
                            # timeout += 1;
                            # if timeout == 50: #1 second
                            #     print("break")
                            #     break
                            print("running or mining yellow")
                
            #inv full go to bank
            if self.api_s.get_is_inv_full() and not self.get_nearest_tag(clr.CYAN):
                print("go to bank - climb ladder")
                #Click ladder to go back up
                self.__identify_guild_ladder()
                self.mouse.click()
                # self.walkrun(40) #40 energy or higher
                
                while not self.api_m.get_is_player_idle():
                    time.sleep(random.uniform(0.5, 0.75))
                    print("not idle - running")
                    while not self.api_m.get_player_position() in [(3021, 3339, 0)]:
                        time.sleep(random.uniform(0.1, 0.2))
                    print("at top of ladder")

                time.sleep(random.uniform(0.34, 0.38))

            #walk to bank
            if self.api_s.get_is_inv_full():
                print("go to bank")
                self.__identify_bank_booth()
                self.mouse.click()
                # self.walkrun(80) #80 energy or higher              

                while not self.api_m.get_is_player_idle():
                    time.sleep(random.uniform(0.5, 0.75))
                    print("not idle - walking")
  
                if imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "DepositAll.png"), self.win.game_view, 0.05):
                    print("deposit all")
                    self.__DepositAll()
                    time.sleep(random.uniform(0.15, 0.2))
                    pag.press("esc")
                    print("escape")
                time.sleep(random.uniform(0.2, 0.4))
                
                #Acknowledge Trip and Amount of Ore Mined
                self.Trips += 1
                self.Ore += 28

                #Log Trip and Ore Mined
                self.log_msg(f"Trip: {self.Trips}. Total Ore Mined: ~{self.Ore}")

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.set_status(BotStatus.STOPPED)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
      
    def __identify_guild_ladder(self):
        ladder = self.get_all_tagged_in_rect(self.win.game_view, clr.WHITE)
        #while not self.mouseover_text(contains=["Ladder"], color=[clr.OFF_CYAN]):
        self.mouse.move_to(ladder[0].random_point())
        return True

    def __identify_bank_booth(self):
        cyan_tile = self.get_nearest_tag(clr.CYAN)
        print(cyan_tile)
        self.mouse.move_to(cyan_tile.random_point())
        """        
        bank_booth = self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN)
        print(bank_booth)
        self.mouse.move_to(bank_booth[0].random_point())"""
        return True
    
    def __DepositAll(self):
        DepositAll = imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("bank", "DepositAll.png"), self.win.game_view, 0.05)
        self.mouse.move_to(DepositAll.random_point())
        self.mouse.click()
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