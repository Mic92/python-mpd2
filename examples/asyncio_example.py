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

    withalbumart = await client.albumart("ji/intro.mp3")
    print("albumart:",withalbumart)
    nocoverfile = await client.readpicture("nocoverfile/intro.mp3")
    print("readpicture:",nocoverfile)
    notfound = await client.readpicture("nocover/file.mp3")
    print("readpicture, no data",notfound)

    try:
        status = await client.status()
    except Exception as e:
        print("Status error:", e)
        return
    else:
        print("Status success:", status)

    print(list(await client.commands()))

    import time
    start = time.time()
    for x in await client.listall():
        print("sync:", x)
        print("Time to first sync:", time.time() - start)
        break

    start = time.time()
    async for x in client.listall():
        print("async:", x)
        print("Time to first async:", time.time() - start)
        break

    try:
        await client.addid()
    except Exception as e:
        print("An erroneous command, as expected, raised:", e)

    try:
        async for x in client.plchangesposid():
            print("Why does this work?")
    except Exception as e:
        print("An erroneous asynchronously looped command, as expected, raised:", e)

    i = 0
    async for subsystem in client.idle():
        print("Idle change in", subsystem)
        i += 1
        if i > 5:
            print("Enough changes, quitting")
            break

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
