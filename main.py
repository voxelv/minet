from math import floor


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


class Slot(object):
    """
    Contains a Lot, is part of a Unit
    """

    def __init__(self, unit, tag, rcp_amt):
        self.unit = unit if isinstance(unit, Unit) else None
        self.tag = tag
        self.lot = None

        self.flow = "NONE"

        self.rcp_amt = rcp_amt

        self.src_slots = []
        self.tgt_slots = []

        SlotMgr.add_slot(self)

    def give(self, lot):
        if lot is None or not isinstance(lot, Lot):
            return

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
    tx_slots = []
    rx_slots = []
    on_tick = 0

    @staticmethod
    def add_slot(slot):
        if not isinstance(slot, Slot):
            return

        if isinstance(slot, TxSlot) and slot not in SlotMgr.tx_slots:
            SlotMgr.tx_slots.append(slot)

        elif isinstance(slot, RxSlot) and slot not in SlotMgr.rx_slots:
            SlotMgr.rx_slots.append(slot)

    @staticmethod
    def tick(tick):
        SlotMgr.on_tick = tick

        # TX all the TxSlot
        for slot in SlotMgr.tx_slots:
            # Only if the TxSlot has a lot and amt
            if slot.lot is not None and slot.lot.amt > 0:
                # Get the amt
                lot = slot.take()
                # Divvy among the slot targets
                div_amt = int(floor(lot.amt / len(slot.tgt_slots)))
                # Give to targets
                for rx_slot in slot.tgt_slots:
                    rx_lot = rx_slot.take()
                    # Create lots if needed
                    if rx_lot is None:
                        rx_lot = Lot(slot.tag, 0)
                    # Increment lot amt
                    rx_lot.amt += div_amt
                    # Give the lot to the rx slot
                    rx_slot.give(rx_lot)

                # Keep the remaining amount
                rem_amt = lot.amt % len(slot.tgt_slots)
                # Destroy lots if no longer needed
                if rem_amt > 0:
                    slot.give(Lot(slot.tag, rem_amt))


class RxSlot(Slot):
    def __init__(self, unit, rcp, rcp_amt):
        super(RxSlot, self).__init__(unit, rcp, rcp_amt)
        self.flow = "IN"

    def connect_to(self, slot):
        if isinstance(slot, TxSlot) and self not in slot.tgt_slots and slot not in self.src_slots:
            slot.tgt_slots.append(self)
            self.src_slots.append(slot)
            return True

        return False


class TxSlot(Slot):
    def __init__(self, unit, rcp, rcp_amt):
        super(TxSlot, self).__init__(unit, rcp, rcp_amt)
        self.flow = "OUT"

    def connect_to(self, slot):
        if isinstance(slot, RxSlot) and self not in slot.src_slots and slot not in self.tgt_slots:
            slot.src_slots.append(self)
            self.tgt_slots.append(slot)
            return True

        return False


class UnitMgr(object):
    units = []

    @staticmethod
    def add_unit(unit):
        if unit not in UnitMgr.units:
            UnitMgr.units.append(unit)

    @staticmethod
    def tick(tick):
        for unit in UnitMgr.units:
            unit.tick(tick)


class UnitRcp(object):
    def __init__(self, req_lots, mak_lots):
        self.req_lots = req_lots
        self.mak_lots = mak_lots

    def __repr__(self):
        return "{}->{}".format(self.req_lots, self.mak_lots)


class Unit(object):
    def __init__(self, rcp):
        self.rcp = rcp if isinstance(rcp, UnitRcp) else None

        self.rx_slots = []
        for rcp_lot in self.rcp.req_lots:
            self.rx_slots.append(RxSlot(self, rcp_lot.tag, rcp_lot.amt))

        self.tx_slots = []
        for rcp_lot in self.rcp.mak_lots:
            self.tx_slots.append(TxSlot(self, rcp_lot.tag, rcp_lot.amt))

        UnitMgr.add_unit(self)

    def tick(self, tick):
        # Start by assuming we have all the lots we need to do our recipe
        lots_avbl = True
        # Now if any is insufficient, then lots are not avbl
        for slot in self.rx_slots:
            if slot.lot is None:
                return

            if slot.lot.amt < slot.rcp_amt:
                lots_avbl = False

        # If we have enough, do our recipe
        if lots_avbl:
            # Nom the rx
            for slot in self.rx_slots:
                lot = slot.take()
                lot.amt -= slot.rcp_amt
                if lot.amt > 0:
                    slot.give(lot)

            # Create the tx
            for slot in self.tx_slots:
                lot = slot.take()
                if lot is None:
                    lot = Lot(slot.tag, 0)
                lot.amt += slot.rcp_amt
                slot.give(lot)

    def __repr__(self):
        return "Unit: {}->{}".format(self.rcp.req_lots, self.rcp.mak_lots)


def run():
    print "K GO"
    boiler = Unit(UnitRcp([Lot("COAL", 1), Lot("WATER", 10)], [Lot("STEAM", 100)]))
    coal_src = Unit(UnitRcp([], [Lot("COAL", 2)]))
    water_src = Unit(UnitRcp([], [Lot("WATER", 10)]))
    steam_sink = Unit(UnitRcp([Lot("STEAM", 100)], []))

    boiler.rx_slots[0].connect_to(coal_src.tx_slots[0])
    boiler.rx_slots[1].connect_to(water_src.tx_slots[0])
    boiler.tx_slots[0].connect_to(steam_sink.rx_slots[0])

    tick = 0
    done = False
    while not done:
        SlotMgr.tick(tick)
        UnitMgr.tick(tick)
        tick += 1

    print "K DONE"


if __name__ == '__main__':
    run()
