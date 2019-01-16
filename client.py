#!/usr/bin/env python

import asyncio
import websockets
import json

import op

from secret import TOKEN


class Bot():
    def __init__(self):
        self.interval = None
        self.sequence = None
        self.session_id = None

        self.auth = {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "disco",
                    "$device": "disco"
                },
                "compress": False,
                "large_threshold": 250,
                "shard": [1, 10],
                "presence": {
                    "game": {
                        "name": "with handpicked bugs",
                        "type": 0
                    },
                    "status": "dnd",
                    "since": 91879201,
                    "afk": False
                }
            }

        asyncio.run(self.main())
        # asyncio.get_event_loop().run_until_complete(self.hello())
        # print(self.opcode(1, self.sequence))

    async def main(self):
        async with websockets.connect(
                'wss://gateway.discord.gg/?v=6&encoding=json') \
                as self.websocket:
            await self.hello()
            if self.interval is None:
                print("Hello failed, exiting")
                return
            await asyncio.gather(self.heartbeat(), self.receive())
            # while self.interval is not None:
            #     pass

    async def receive(self):
        print("Entering receive")
        async for message in self.websocket:
            print("<", message)
            data = json.loads(message)
            if data["op"] == op.DISPATCH:
                if data["t"] == "READY":
                    self.session_id = data["d"]["session_id"]
                    print("Got session ID:", self.session_id)

    async def send(self, opcode, payload):
        data = self.opcode(opcode, payload)
        print(">", data)
        await self.websocket.send(data)

    async def heartbeat(self):
        print("Entering heartbeat")
        while self.interval is not None:
            print("Sending a heartbeat")
            await self.send(op.HEARTBEAT, self.sequence)
            await asyncio.sleep(self.interval)

    async def hello(self):
        await self.send(op.IDENTIFY, self.auth)
        print(f"hello > auth")

        ret = await self.websocket.recv()
        print(f"hello < {ret}")

        data = json.loads(ret)
        opcode = data["op"]
        if opcode != 10:
            print("Unexpected reply")
            print(ret)
            return
        self.interval = (data["d"]["heartbeat_interval"] - 2000) / 1000
        # self.interval = 5
        print("interval:", self.interval)

    def opcode(self, opcode: int, payload) -> str:
        data = {
            "op": opcode,
            "d": payload
        }
        return json.dumps(data)


if __name__ == "__main__":
    Bot()
