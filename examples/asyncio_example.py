import asyncio

from mpd.asyncio import MPDClient

async def main():
    print("Create MPD client")
    client = MPDClient()
    try:
        await client.connect('localhost', 6600)
    except Exception as e:
        print("Connection failed:", e)
        return

    print("Connected to MPD version", client.mpd_version)

    try:
        status = await client.status()
    except Exception as e:
        print("Status error:", e)
        return
    else:
        print("Status success:", status)

    for x in await client.decoders():
        print("sync decoder:", x)

    async for x in client.decoders():
        print("async decoder:", x)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
