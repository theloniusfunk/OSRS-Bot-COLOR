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
        
        #self.log_msg("Selecting inventory...")
        #self.mouse.move_to(self.win.cp_tabs[3].random_point())
        #self.mouse.click()

        self.logs = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        
        
        while time.time() - start_time < end_time:
            # 5% chance to take a break between clicks
            if rd.random_chance(probability=0.05) and self.take_breaks:
                self.take_break(max_seconds=15)

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
                #self.take_break(max_seconds=1)


                #slots = api_s.get_inv_item_indices(ids.logs)
                #self.mouse.move_to(self.win.inventory_slots[0].random_point)
                #pag.keyDown("Shift")
                #time.sleep(0.3)
                #pag.click()
                #time.sleep(0.3)
                #pag.keyUp("Shift")
                #pag.press('esc')
                #time.sleep(2) 
                #while api_s.get_is_inv_full():
                 #   print("75")
                  #  cyan_tile = self.get_nearest_tag(clr.CYAN)
                   # print(cyan_tile)
                    # While we cannot see the blue tile, move camera around
                 #   ...
                   #failed_bank_searches += 1
                   #if failed_bank_searches >= 10:
                       # Can't find bank, abort
                    #  self.stop()
                 # If the code makes it here, that means we've found the blue tile
                 # Probably don't need to check the mouseover as your char will be stationary,
                 # can if u want tho.                
                 # # Click if the mouseover text assures us we're clicking the bank
                 #if not self.mouseover_text(contains="Bank"):
                 #   continue
                 #failed_bank_searches = 0
                
                   # self.mouse.move_to(cyan_tile.random_point())
                    #pag.click()
                    #time.sleep(2) 

                    #while not api_m.get_is_player_idle():
                    # While player is running to the bank, wait
                     #   time.sleep(1)
                      #  print("not idle")
                    # If the code makes it here, assume player has opened the bank.
                    #slots = api_s.get_inv_item_indices(ids.logs)
                    #print(slots)
                    #STOPPED HERE
                    #self.mouse.move_to(self.win.inventory_slots[0].random_point)
                    #pag.keyDown("Shift")
                    #pag.click()
                    #pag.keyUp("Shift")
                    #rd.sleep_random(1.5,2)
                    
                    #pag.press('esc')
                    #time.sleep(2) 
                    #rd.sleep_random(1.5,2) 
                
                #slots = api_s.get_inv_item_indices(ids.logs)
                #if not slots:
                 #   # There are no logs in your inventory, wtf?
                #    self.stop()
                #self.mouse.move_to(slots[0].random_point())
                # Shift click any log to deposit all
                #pag.keyDown("Shift")
                #self.mouse.click()
                #pag.keyUp("Shift")
                #time.sleep(1) # give it a sec to register
                #pag.keyDown("ESC") # close bank
                #time.sleep(0.2)
                #pag.keyUp("ESC")
                #time.sleep(0.5) # give it a sec to close the bank UI



            # If our mouse isn't hovering over a tree, and we can't find another tree...
            #if not self.mouseover_text(contains="Chop") and not self.__move_mouse_to_nearest_tree():
            #    failed_searches += 1
            #    if failed_searches % 10 == 0:
            #        self.log_msg("Searching for trees...")
            #    if failed_searches > 60:
            #        # If we've been searching for a whole minute...
            #        self.__logout("No tagged trees found. Logging out.")
            #        return
            #    time.sleep(1)
            #    continue
            #failed_searches = 0  # If code got here, a tree was found

            # If not cutting, click tree

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
                    if not self.mouseover_text(contains="Chop"):
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
            #notidle = 1
            #time.sleep(3)





           # # Click if the mouseover text assures us we're clicking a tree
           # if not self.mouseover_text(contains="Chop"):
           #     continue
           # self.mouse.click()
           # time.sleep(0.5)

            # While the player is chopping (or moving), wait
           # while not api_m.get_is_player_idle():
           #     # Every second there is a 10% chance to move the mouse to the next tree
           #     if rd.random_chance(probability=0.10):
           #         self.__move_mouse_to_nearest_tree(next_nearest=True)
           #     time.sleep(1)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")




    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)

    def __move_mouse_to_nearest_tree(self, next_nearest=False):
        """
        Locates the nearest tree and moves the mouse to it. This code is used multiple times in this script,
        so it's been abstracted into a function.
        Args:
            next_nearest: If True, will move the mouse to the second nearest tree. If False, will move the mouse to the
                          nearest tree.
            mouseSpeed: The speed at which the mouse will move to the tree. See MouseUtil for options.
        Returns:
            True if success, False otherwise.
        """
        trees = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
        tree = None
        if not trees:
            return False
        # If we are looking for the next nearest tree, we need to make sure trees has at least 2 elements
        if next_nearest and len(trees) < 2:
            return False
        trees = sorted(trees, key=RuneLiteObject.distance_from_rect_center)
        tree = trees[1] if next_nearest else trees[0]
        if next_nearest:
            self.mouse.move_to(tree.random_point(), mouseSpeed="slow", knotsCount=2)
        else:
            self.mouse.move_to(tree.random_point())
        return True

        #def __drop_logs(self, api_s: StatusSocket):
        
         #   """Private function for dropping logs. This code is used in multiple places, so it's been abstracted.
          #  Since we made the `api` and `logs` variables assigned to `self`, we can access them from this function.
           # """
            #slots = api_s.get_inv_item_indices(ids.logs)
            #self.drop(slots)
            #self.logs += len(slots)
            #self.log_msg(f"Logs cut: ~{self.logs}")
            #time.sleep(1) 