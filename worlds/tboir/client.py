from __future__ import annotations
import asyncio
import colorama

import ModuleUpdate
ModuleUpdate.update()

import Utils

if __name__ == "__main__":
    Utils.init_logging("Isaac Client", exception_logger="Client")

from NetUtils import NetworkItem, ClientStatus
from CommonClient import gui_enabled, logger, get_base_parser, ClientCommandProcessor, \
    CommonContext, server_loop


class IsaacClientCommandProcessor(ClientCommandProcessor):
    def _cmd_resync(self):
        """Manually trigger a resync."""
        self.output(f"Syncing items.")
        self.ctx.syncing = True


class IsaacContext(CommonContext):
    command_processor: int = IsaacClientCommandProcessor
    game = "The Binding of Isaac Repentance"
    items_handling = 0b111  # full remote

    def __init__(self, server_address: str | None, password: str | None):
        super(IsaacContext, self).__init__(server_address, password)

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(IsaacContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(IsaacContext, self).connection_closed()

    async def shutdown(self):
        await super(IsaacContext, self).shutdown()

    def on_package(self, cmd: str, args: dict):
        if cmd in {"Connected"}:
            pass
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


async def game_watcher(ctx: IsaacContext):
    while not ctx.exit_event.is_set():
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