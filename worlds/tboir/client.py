from __future__ import annotations
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import os
from queue import Queue
import colorama

import ModuleUpdate
import settings
from worlds.tboir import TboiSettings
ModuleUpdate.update()

import Utils

if __name__ == "__main__":
    Utils.init_logging("Isaac Client", exception_logger="Client")

from CommonClient import gui_enabled, logger, ClientCommandProcessor, \
    CommonContext, server_loop

class IsaacClientCommandProcessor(ClientCommandProcessor):
    def _cmd_resync(self):
        """Manually trigger a resync."""
        self.output(f"Syncing items.")
        self.ctx.syncing = True


class IsaacContext(CommonContext):
    settings: TboiSettings = None

    save_data_path: str = ""
    mod_viable: bool = False
    client_version = Utils.Version(1,0,0)

    class State(Enum):
        DISCONNECTED = 1
        GATHERING_DATA = 2
        CONNECTED = 3

    @dataclass
    class Command:
        type: str
        payload: any

    @dataclass
    class SaveData:
        seed: str
        timestamp: str
        actor: str
        commands: list[IsaacContext.Command]


    command_processor: int = IsaacClientCommandProcessor
    game = "The Binding of Isaac Repentance"
    items_handling = 0b111  # full remote
    current_state = State.DISCONNECTED

    def __init__(self, server_address: str | None, password: str | None):
        super(IsaacContext, self).__init__(server_address, password)
        s = settings.get_settings()
        self.settings = s.tboir_options

    def resolve_paths(self):
        try:
            if not self.settings.game_folder or not self.settings.game_folder.endswith("The Binding of Isaac Rebirth"):
                self.settings.game_folder = None
                self.gui_error("Invalid game directory", "Please select the directory which contains your Binding of Isaac executable.\nUsually located in 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\' called 'The Binding of Isaac Rebirth'.")
                return

            settings.get_settings()["tboir_options"] = self.settings
        except:
            self.gui_error("Invalid game directory", "Please select the directory which contains your Binding of Isaac executable.\nUsually located in 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\' called 'The Binding of Isaac Rebirth'.")
            return

        potential_mod_dirs = [
            name for name in os.listdir(os.path.join(self.settings.game_folder, "mods"))
            if (name.startswith('the archipelago of isaac') or name.startswith('ap_mod')) and os.path.isdir(os.path.join(os.path.join(self.settings.game_folder, "mods"), name))
            ]
        
        if len(potential_mod_dirs) == 0:
            self.gui_error("Mod not found", "The Archipelago of Isaac mod does not seem to be installed. Please subscribe to the mod on the steam workshop.")
            return
        if len(potential_mod_dirs) > 1:
            self.gui_error("Multiple Archipelago mods", "There seem to be multiple Archipelago mods installed.")
            return

        supported_client_file = os.path.join(self.settings.game_folder, "mods", potential_mod_dirs[0], "supported_client")
        if os.path.isfile(supported_client_file):
            with open(supported_client_file, "r", encoding="utf-8") as f:
                v_nums = f.read().split('.')
                v = Utils.Version(int(v_nums[0]),int(v_nums[1]),int(v_nums[2]))
                if v < self.client_version:
                    self.gui_error("Mod to old", "Your Archipelago of Isaac mod seems to be outdated. Please updated it to the newest version.")
                    return
                elif v > self.client_version:
                    self.gui_error("Client to old", "Your Isaac client seems to be outdated. Please download the newest .apworld file.")
                    return
        else:
            self.gui_error("Mod to old", "Your Archipelago of Isaac mod seems to be outdated. Please updated it to the newest version.")
            return
        self.mod_viable = True

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(IsaacContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(IsaacContext, self).connection_closed()
        self.current_state = self.State.DISCONNECTED

    async def shutdown(self):
        await super(IsaacContext, self).shutdown()
    
    def set_data(self, key: str, value: any):
        Utils.async_start(self.send_msgs([
            {"cmd": "Set", "key": key, "want_reply": False, "operations": [{"operation": "replace", "value": value}]}
            ]))

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:
            self.current_state = self.State.GATHERING_DATA
            Utils.async_start(self.send_msgs([
                {"cmd": "Get", "keys": [f"{self.username}_saveslot",
                                        f"{self.username}_run_data",
                                        f"{self.username}_session_data"]}]))
        if cmd in {"Retrieved"}:
            if f"{self.username}_saveslot" in args["keys"]:
                if self.stored_data[f"{self.username}_saveslot"] is None:
                    self.stored_data[f"{self.username}_saveslot"] = 0
                    self.set_data(f"{self.username}_saveslot", self.stored_data[f"{self.username}_saveslot"])
            if f"{self.username}_run_data" in args["keys"]:
                if self.stored_data[f"{self.username}_run_data"] is None:
                    self.stored_data[f"{self.username}_run_data"] = {}
                    self.set_data(f"{self.username}_run_data", self.stored_data[f"{self.username}_run_data"])
            if f"{self.username}_session_data" in args["keys"]:
                if self.stored_data[f"{self.username}_session_data"] is None:
                    self.stored_data[f"{self.username}_session_data"] = {}
                    self.set_data(f"{self.username}_session_data", self.stored_data[f"{self.username}_session_data"])

        if cmd in {"ReceivedItems"}:
            start_index = args["index"]
            if start_index != len(self.items_received):
                for item in args['items']:
                    pass
        if cmd in {"RoomUpdate"}:
            if "checked_locations" in args:
                for ss in self.checked_locations:
                    pass

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class IsaacManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Isaac Client"

        self.ui = IsaacManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    commands_to_be_sent = Queue()

    def process_mod_command(self, c: IsaacContext.Command):
        if c.type == "RequestAll":
            resp = IsaacContext.Command()
            resp.type = "AllData"
            resp.payload = {
                "run_data": self.stored_data[f"{self.username}_run_data"],
                "session_data": self.stored_data[f"{self.username}_session_data"],
                "checked_locations": self.checked_locations,
                "missing_locations": self.missing_locations,
                "received_items": self.items_received,
                "item_names": self.item_names,
                "location_names": self.location_names,
                "player_names": self.player_names,
                "seed": self.seed_name,
                "slot_info": self.slot_info,
                "slot": self.slot
            }
            self.commands_to_be_sent.put(resp)
        else:
            pass

    def poll(self):
        if not os.path.isfile(self.save_data_path): return

        data = json.loads(open(self.save_data_path).read())
        save_data = IsaacContext.SaveData(
            seed=data["seed"],
            timestamp=data["timestamp"],
            actor=data["actor"],
            commands=[IsaacContext.Command(**c) for c in data["commands"]]
        )

        if save_data.actor != "mod": return
        if save_data.seed != "" and save_data.seed != self.seed_name: return

        for c in save_data.commands:
            self.process_mod_command(c)

        new_save_data = IsaacContext.SaveData(
            seed=self.seed_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor="client",
            commands=[self.commands_to_be_sent.get() for _ in range(self.commands_to_be_sent.qsize())]
        )
        with open(self.save_data_path, "w") as f:
            json.dump(asdict(new_save_data), f, indent=2)

async def game_watcher(ctx: IsaacContext):
    while not ctx.exit_event.is_set():
        if not ctx.mod_viable and (not ctx._messagebox or not ctx._messagebox._is_open) and ctx.ui:
            ctx.resolve_paths()

        if ctx.current_state == ctx.State.GATHERING_DATA \
                and ctx.stored_data[f"{ctx.username}_saveslot"] is not None \
                and ctx.stored_data[f"{ctx.username}_session_data"] is not None \
                and ctx.stored_data[f"{ctx.username}_run_data"] is not None:
            while ctx.stored_data[f"{ctx.username}_saveslot"] == 0:
                logger.info('Enter save slot (1-3):')
                try:
                    slot = int(await ctx.console_input())
                    if slot >= 1 and slot <= 3:
                        ctx.stored_data[f"{ctx.username}_saveslot"] = slot
                        ctx.set_data(f"{ctx.username}_saveslot", slot)
                except:
                    pass
            logger.info(f'Connecting to save slot {ctx.stored_data[f"{ctx.username}_saveslot"]}')
            ctx.save_data_path = os.path.join(ctx.settings.game_folder, "data", "the archipelago of isaac", f"save{ctx.stored_data[f"{ctx.username}_saveslot"]}.dat")
            ctx.current_state = ctx.State.CONNECTED
        if ctx.current_state == ctx.State.CONNECTED:
            ctx.poll()
        await asyncio.sleep(0.1)


async def main():
    ctx = IsaacContext(None, None)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()
    progression_watcher = asyncio.create_task(
        game_watcher(ctx), name="IsaacProgressionWatcher")

    await ctx.exit_event.wait()
    ctx.server_address = None

    await progression_watcher

    await ctx.shutdown()
    
if __name__ == '__main__':
    colorama.init()
    asyncio.run(main())
    colorama.deinit()

def launch():
    # use colorama to display colored text highlighting
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()