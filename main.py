
from minet import *


def run():
    print "K GO"
    net = MinetNet()
    # boiler = net.new_unit(rcp=UnitRcp("Boiler", [Lot("COAL", 1), Lot("WATER", 10)], [Lot("STEAM", 100)]))
    # coal_src = net.new_unit(rcp=UnitRcp("CoalMiner", [], [Lot("COAL", 1)]))
    # water_src = net.new_unit(rcp=UnitRcp("WaterPump", [], [Lot("WATER", 10)]))
    # steam_sink = net.new_unit(rcp=UnitRcp("SteamTurbine", [Lot("STEAM", 100)], []))
    boiler = net.new_unit(rcp_name="Boiler")
    coal_mine = net.new_unit(rcp_name="Coal Mine")
    water_pump = net.new_unit(rcp_name="Water Pump")
    steam_turbine = net.new_unit(rcp_name="Steam Turbine")

    boiler.rx_slots[0].connect_to(coal_mine.tx_slots[0])
    boiler.rx_slots[1].connect_to(water_pump.tx_slots[0])
    boiler.tx_slots[0].connect_to(steam_turbine.rx_slots[0])

    done = False
    while not done:
        net.tick()
        # TODO: set done condition, for now, debug with breakpoint on the while loop

    print "K DONE"


if __name__ == '__main__':
    run()
