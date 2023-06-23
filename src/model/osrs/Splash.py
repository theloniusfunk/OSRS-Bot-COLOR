import shutil
import time
from pathlib import Path

import utilities.api.item_ids as item_ids
import utilities.color as clr
import utilities.game_launcher as launcher
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class Splash(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Splash"
        description = (
            "This bot kills NPCs. Position your character near some NPCs and highlight them. After setting this bot's options, please launch RuneLite with the"
            " button on the right."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: int = 1
        self.loot_items: str = ""
        self.hp_threshold: int = 0

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("loot_items", "Loot items (requires re-launch):", "E.g., Coins, Dragon bones")
        self.options_builder.add_slider_option("hp_threshold", "Low HP threshold (0-100)?", 0, 100)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "loot_items":
                self.loot_items = options[option]
            elif option == "hp_threshold":
                self.hp_threshold = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return

        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f'Loot items: {self.loot_items or "None"}.')
        self.log_msg(f"Bot will eat when HP is below: {self.hp_threshold}.")
        self.log_msg("Options set successfully. Please launch RuneLite with the button on the right to apply settings.")

        self.options_set = True

    def launch_game(self):
        if launcher.is_program_running("RuneLite"):
            self.log_msg("RuneLite is already running. Please close it and try again.")
            return
        # Make a copy of the default settings and save locally
        src = launcher.runelite_settings_folder.joinpath("osrs_settings.properties")
        dst = Path(__file__).parent.joinpath("custom_settings.properties")
        shutil.copy(str(src), str(dst))
        # Modify the highlight list
        loot_items = self.capitalize_loot_list(self.loot_items, to_list=False)
        with dst.open() as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("grounditems.highlightedItems="):
                lines[i] = f"grounditems.highlightedItems={loot_items}\n"
        with dst.open("w") as f:
            f.writelines(lines)
        # Launch the game
        launcher.launch_runelite_with_settings(self, dst)

    def main_loop(self):
        self.log_msg("WARNING: This script is for testing and may not be safe for personal use. Please modify it to suit your needs.")

        # Setup API
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()

        self.toggle_auto_retaliate(True)

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        counter = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            counter += 1
            time.sleep(1)
            if counter == 725:
                Green = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
                self.mouse.move_to(Green[0].random_point())
                self.mouse.click()
            if self.get_hp() < self.hp_threshold:
                self.__eat(api_status)
                counter = 0
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __eat(self, api: StatusSocket):
        self.log_msg("HP is low.")
        food_slots = api.get_inv_item_indices(item_ids.all_food)
        if len(food_slots) == 0:
            self.log_msg("No food found. Pls tell me what to do...")
            self.set_status(BotStatus.STOPPED)
            return
        self.log_msg("Eating food...")
        self.mouse.move_to(self.win.inventory_slots[food_slots[0]].random_point())
        self.mouse.click()

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)