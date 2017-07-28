
from minet import MinetNet
import rcps


def run():
    print "K GO"
    net = MinetNet()

    boiler = net.new_unit(rcp_name="Boiler")
    coal_mine = net.new_unit(rcp_name="Coal Mine")
    water_pump = net.new_unit(rcp_name="Water Pump")
    steam_turbine = net.new_unit(rcp_name="Steam Turbine")

    gook_fabs = []
    for i in range(rcps.rcps["Steam Turbine"]["mak"][0][1] / rcps.rcps["Gook Fabricator"]["req"][0][1]):
        gook_fab = net.new_unit(rcp_name="Gook Fabricator")
        gook_fabs.append(gook_fab)
        net.connect(gook_fab, 0, steam_turbine, 1)

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
        u = net.unit_mgr.get_unit(44)
        print u.slots[1].lot.amt if u.slots[1].lot is not None else ""

    print "K DONE"


if __name__ == '__main__':
    run()
