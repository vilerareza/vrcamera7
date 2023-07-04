import asyncio

from indicator import Indicator

blue_indicator = Indicator(pin=27)
yellow_indicator = Indicator(pin=22)
indicator_off = False

async def blink_indicator(indicator):
    global indicator_off
    while not indicator_off:
        indicator.on()
        await asyncio.sleep(3)
        indicator.off()
        await asyncio.sleep(3)

async def error_indicator(indicator):
    await asyncio.sleep(5)
    indicator.on()


async def stop_indicator(indicator, timeout):
    global indicator_off
    await asyncio.sleep(timeout)
    indicator_off = True
    indicator.off()


async def main():
    # Blinking indicator
    task_blink_indicator = asyncio.create_task(blink_indicator(blue_indicator))
    task_error_indicator = asyncio.create_task(error_indicator(yellow_indicator))
    task_stop_indicator = asyncio.create_task(stop_indicator(blue_indicator, 20))

    await task_blink_indicator
    await task_stop_indicator
    print ('end')
# 
asyncio.run (main())