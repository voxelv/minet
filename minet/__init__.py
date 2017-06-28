
from rcps import rcps


class Lot(object):
    """
    A Lot is a bunch of something. The tag is what kind, and the amt is how many.
    :param tag: The kind of thing
    :param amt: How much of thing
    :type tag: str
    :type amt: int
    """
    def __init__(self, tag, amt):
        self.tag = tag
        self.amt = amt

    def __repr__(self):
        return ".{} {}.".format(self.tag, self.amt)


class LotPool(object):

    def __init__(self):
        """
        A pool for Lot objects
        """
        self.pool = []

    def get(self, tag, amt):
        """
        Gets a lot from the pool, or creates a new one
        if needed.
        :param tag: tag to set the Lot as
        :param amt: amount to set the Lot as
        :return: a Lot
        :rtype: Lot
        """
        if len(self.pool) > 0:
            lot = self.pool.pop()
            lot.__init__(tag, amt)
        else:
            lot = Lot(tag, amt)
        return lot

    def put(self, lot):
        """
        Puts a Lot back
        :param lot:
        :return:
        """
        self.pool.append(lot)


class Slot(object):
    """
    Contains a Lot, is part of a Unit
    """

    def __init__(self, net, unit, tag, rcp_amt):
        """
        Slot initializer
        :param net: the MinetNet for this
        :param unit: parent Unit
        :param tag: tag for the Slot
        :param rcp_amt: recipe amount req or mak
        """
        if not isinstance(net, MinetNet):
            raise TypeError("net is not a MinetNet")
        if not isinstance(unit, Unit):
            raise TypeError("unit is not a Unit")

        self.net = net
        self.unit = unit

        self.tag = tag
        self.lot = None

        self.flow = "INVALID"

        self.rcp_amt = rcp_amt

        # Slot connections
        self.src_slots = []
        self.tgt_slots = []

        self.net.slot_mgr.add_slot(self)

    def give(self, lot):
        if not isinstance(lot, Lot):
            raise TypeError("lot is not a Lot")

        if self.lot is None:
            self.lot = lot

    def take(self):
        if self.lot is not None:
            lot = self.lot
            self.lot = None
            return lot
        return None

    def tick(self, tick):
        pass

    def __repr__(self):
        return "{}[{}]{}".format(
            "->" if self.flow == "IN" else "",
            "_" if self.lot is None else self.lot,
            "->" if self.flow == "OUT" else "")


class SlotMgr(object):

    def __init__(self, net):
        if not isinstance(net, MinetNet):
            raise TypeError("net is not a MinetNet")
        self.net = net

        self.tx_slots = []
        self.rx_slots = []

    def add_slot(self, slot):
        if not isinstance(slot, Slot):
            raise TypeError("slot argument is not a Slot")

        if isinstance(slot, TxSlot) and slot not in self.tx_slots:
            self.tx_slots.append(slot)

        elif isinstance(slot, RxSlot) and slot not in self.rx_slots:
            self.rx_slots.append(slot)

    def tick(self):

        # TX all the TxSlot
        for slot in self.tx_slots:
            # Only if the TxSlot has a lot and amt
            if slot.lot is not None and slot.lot.amt > 0 and len(slot.tgt_slots) > 0:
                # Get the amt
                lot = slot.take()
                # Divvy among the slot targets
                div_amt = int(lot.amt / len(slot.tgt_slots))
                # Give to targets
                for rx_slot in slot.tgt_slots:
                    rx_lot = rx_slot.take()
                    # Create lots if needed
                    if rx_lot is None:
                        rx_lot = self.net.lot_pool.get(slot.tag, 0)
                    # Increment lot amt
                    rx_lot.amt += div_amt
                    # Give the lot to the rx slot
                    rx_slot.give(rx_lot)

                # Keep the remaining amount
                rem_amt = lot.amt % len(slot.tgt_slots)
                # Destroy lots if no longer needed
                if rem_amt > 0:
                    slot.give(self.net.lot_pool.get(slot.tag, rem_amt))
                else:
                    self.net.lot_pool.put(lot)


class RxSlot(Slot):
    def __init__(self, net, unit, rcp, rcp_amt):
        super(RxSlot, self).__init__(net, unit, rcp, rcp_amt)
        self.flow = "IN"

    def connect_to(self, slot):
        if isinstance(slot, TxSlot) and self not in slot.tgt_slots and slot not in self.src_slots:
            slot.tgt_slots.append(self)
            self.src_slots.append(slot)
            return True

        return False


class TxSlot(Slot):
    def __init__(self, net, unit, rcp, rcp_amt):
        super(TxSlot, self).__init__(net, unit, rcp, rcp_amt)
        self.flow = "OUT"

    def connect_to(self, slot):
        if isinstance(slot, RxSlot) and self not in slot.src_slots and slot not in self.tgt_slots:
            slot.src_slots.append(self)
            self.tgt_slots.append(slot)
            return True

        return False


class UnitMgr(object):
    def __init__(self):
        self.units = {}
        self.count = 0

    def add_unit(self, unit):
        if unit not in self.units.itervalues():
            tmp = self.count
            self.count += 1
            self.units[tmp] = unit
            return tmp
        return -1

    def tick(self):
        for unit in self.units.itervalues():
            unit.tick()

    def get_unit(self, idx):
        return self.units.get(idx, None)

    def del_unit(self, idx):
        self.units.pop(idx, None)


class UnitRcp(object):
    def __init__(self, name, req_lots, mak_lots):
        self.name = name
        self.req_lots = req_lots
        self.mak_lots = mak_lots

    def __repr__(self):
        return "{}->{}".format(self.req_lots, self.mak_lots)


class Unit(object):
    def __init__(self, net, rcp):
        if not isinstance(net, MinetNet):
            raise TypeError("net is not a MinetNet")
        if not isinstance(rcp, UnitRcp):
            raise TypeError("rcp is not a UnitRcp")

        self.net = net
        self.rcp = rcp

        self.slots = {}

        count = 0
        for rcp_lot in self.rcp.req_lots:
            self.slots[count] = RxSlot(self.net, self, rcp_lot.tag, rcp_lot.amt)
            count += 1

        for rcp_lot in self.rcp.mak_lots:
            self.slots[count] = TxSlot(self.net, self, rcp_lot.tag, rcp_lot.amt)

    def tick(self):
        # Start by assuming we have all the lots we need to do our recipe
        lots_ready = True
        # Now if any is insufficient, then lots are not ready
        for slot in self.slots.itervalues():
            if slot.flow == "IN" and (slot.lot is None or slot.lot.amt < slot.rcp_amt):
                lots_ready = False

        # If we have enough, do our recipe
        if lots_ready:
            # Nom the rx
            for slot in self.slots.itervalues():
                # Skip TxSlots
                if slot.flow == "OUT":
                    continue

                lot = slot.take()
                lot.amt -= slot.rcp_amt
                if lot.amt > 0:
                    slot.give(lot)
                else:
                    self.net.lot_pool.put(lot)

            # Create the tx
            for slot in self.slots.itervalues():
                # Skip RxSlots
                if slot.flow == "IN":
                    continue
                lot = slot.take()
                if lot is None:
                    lot = self.net.lot_pool.get(slot.tag, 0)
                lot.amt += slot.rcp_amt
                slot.give(lot)

    def __repr__(self):
        return "Unit: ({})".format("_" if self.rcp is None else self.rcp.name)


class MinetNet(object):
    """
    Manages a minet
    """
    NULL_RCP = UnitRcp("", [], [])

    def __init__(self):
        self.lot_pool = LotPool()
        self.unit_mgr = UnitMgr()
        self.slot_mgr = SlotMgr(self)
        self.tick_count = 0

    def new_unit(self, rcp=None, rcp_name=""):
        if rcp is None:
            rcp = self.NULL_RCP

        if rcp_name in rcps:
            req_lots = []
            mak_lots = []
            for req in rcps.get(rcp_name).get("req"):
                req_lots.append(Lot(req[0], req[1]))
            for mak in rcps.get(rcp_name).get("mak"):
                mak_lots.append(Lot(mak[0], mak[1]))
            rcp = UnitRcp(rcp_name, req_lots, mak_lots)

        unit = Unit(self, rcp)
        idx = self.unit_mgr.add_unit(unit)
        return idx

    def tick(self):
        self.slot_mgr.tick()
        self.unit_mgr.tick()
        self.tick_count += 1

    def connect(self, unit1_idx, unit1_slot_idx, unit2_idx, unit2_slot_idx):
        unit1_slot = self.unit_mgr.get_unit(unit1_idx).slots[unit1_slot_idx]
        unit2_slot = self.unit_mgr.get_unit(unit2_idx).slots[unit2_slot_idx]
        unit1_slot.connect_to(unit2_slot)
