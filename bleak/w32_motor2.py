import asyncio
import logging
import uuid

from bleak import discover, BleakClient, BleakScanner, BleakError

from binascii import hexlify

devices_dict = {}
devices_list = []
receive_data = []

device = None

#To discover BLE devices nearby 
async def scan():
    dev = await discover()
    for i in range(0,len(dev)):
        #Print the devices discovered
        print("[" + str(i) + "]",'',dev[i].address,'',dev[i].name,'',dev[i].metadata["uuids"])
        #Put devices information into list
        devices_dict[dev[i].address] = []
        devices_dict[dev[i].address].append(dev[i].name)
        devices_dict[dev[i].address].append(dev[i].metadata["uuids"])
        devices_list.append(dev[i].address)
        if dev[i].name == "w32 ControlHub":
            print("found hub:", dev[i])
            global device
            print("setting device to", dev[i].address)
            device = dev[i].address
    print('device:', device)
    if device == None:
        print('device not found')

#An easy notify function, just print the recieve data
def notification_handler(sender, data):
    print(', '.join('{:02x}'.format(x) for x in data))

def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

async def run(address, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        import sys

        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)
    
    # address = "44D5602F-186F-4228-B934-D91B61574A78"
    global device
    device = await BleakScanner.find_device_by_address(address, timeout=20.0)
    if not device:
        raise BleakError(f"A device with address {address} could not be found.")

    async with BleakClient(address, disconnected_callback=handle_disconnect) as client:
    # async with device as client:
        x = client.is_connected
        log.info("Connected: {0}".format(x))


        #Characteristic uuid
        rw_charac = "d9d9e9e1-aa4e-4797-8151-cb41cedaf2ad" # w32
        # rw_charac = "f8e49401-16f2-457e-8426-0fbce4eac6dc" # w33

        await client.start_notify(rw_charac, notification_handler)
        loop = asyncio.get_event_loop()

        addresses=  ["140202FE75BC", 
                    "140202FE75BC", 
                    "140202CB134A", 
                    "140202BC1D3A", 
                    "140202B7AC51", 
                    "140202B49C32", 
                    "140202BD0D1B", 
                    "140202BD0D1B", 
                    "140202897BCC", 
                    "140202897BCC", 
                    "140200FF03FF", 
                    "140202007B6D", 
                    "1402020F8A82", 
                    "140202897BCC"]
        for x in addresses:
            data = bytearray.fromhex(bytes(x, 'utf-8').decode('utf-8'))
            print(data)
            await client.write_gatt_char(rw_charac, data, response=True)
            await asyncio.sleep(0.05)

        await client.stop_notify(rw_charac)



if __name__ == "__main__":
    # print("Scanning for peripherals...")
    # # Build an event loop
    # loop = asyncio.get_event_loop()
    # # Run the discover event
    # loop.run_until_complete(scan())

    # global device
    address = "44D5602F-186F-4228-B934-D91B61574A78" # W32
    # address = "6D46D478-28F6-4877-A7F7-B8BB008E89E2" # W33

    # global device
    # device = await BleakScanner.find_device_by_address(address, timeout=20.0)

    #Run notify event
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(run(address, True))
    # asyncio.run(show_disconnect_handling())
    exit()
