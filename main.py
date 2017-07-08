
from minet import MinetNet


def run():
    print "K GO"
    net = MinetNet()

    boiler = net.new_unit(rcp_name="Boiler")
    coal_mine = net.new_unit(rcp_name="Coal Mine")
    water_pump = net.new_unit(rcp_name="Water Pump")
    steam_turbine = net.new_unit(rcp_name="Steam Turbine")

    net.connect(boiler, 0, coal_mine, 0)
    net.connect(boiler, 1, water_pump, 0)
    net.connect(boiler, 2, steam_turbine, 0)

    done = False
    while not done:
        net.tick()
        """ TODO: 
            set done condition.
            for now, debug with breakpoint on the while loop otherwise the loop runs quite fast
            and there's no interesting output...
        """

    print "K DONE"


if __name__ == '__main__':
    run()
