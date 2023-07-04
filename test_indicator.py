import asyncio

from indicator import Indicator

blue_indicator = Indicator(pin=17)

async def blink_indicator(indicator):
    indicator.on()
    asyncio.sleep(3)
    indicator.off()

async def stop_indicator(indicator, timeout):
    asyncio.sleep(timeout)
    indicator.off()


async def main():
    # Blinking indicator
    task_blink_indicator = asyncio.create_task(blink_indicator(blue_indicator))
    task_stop_indicator = asyncio.create_task(stop_indicator(blue_indicator, 20))

    await task_blink_indicator
    await task_stop_indicator
    print ('end')

asyncio.run (main())