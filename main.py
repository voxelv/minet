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


class LotPool(object):
    pool = []

    @staticmethod
    def get(tag, amt):
        if len(LotPool.pool) > 0:
            lot = LotPool.pool.pop()
            lot.__init__(tag, amt)
        else:
            lot = Lot(tag, amt)
        return lot

    @staticmethod
    def put(lot):
        LotPool.pool.append(lot)


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

    @staticmethod
    def add_slot(slot):
        if not isinstance(slot, Slot):
            return

        if isinstance(slot, TxSlot) and slot not in SlotMgr.tx_slots:
            SlotMgr.tx_slots.append(slot)

        elif isinstance(slot, RxSlot) and slot not in SlotMgr.rx_slots:
            SlotMgr.rx_slots.append(slot)

    @staticmethod
    def tick():

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
                        rx_lot = LotPool.get(slot.tag, 0)
                    # Increment lot amt
                    rx_lot.amt += div_amt
                    # Give the lot to the rx slot
                    rx_slot.give(rx_lot)

                # Keep the remaining amount
                rem_amt = lot.amt % len(slot.tgt_slots)
                # Destroy lots if no longer needed
                if rem_amt > 0:
                    slot.give(LotPool.get(slot.tag, rem_amt))
                else:
                    LotPool.put(lot)


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
    def tick():
        for unit in UnitMgr.units:
            unit.tick()


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

    def tick(self):
        # Start by assuming we have all the lots we need to do our recipe
        lots_ready = True
        # Now if any is insufficient, then lots are not ready
        for slot in self.rx_slots:
            if slot.lot is None:
                return

            if slot.lot.amt < slot.rcp_amt:
                lots_ready = False

        # If we have enough, do our recipe
        if lots_ready:
            # Nom the rx
            for slot in self.rx_slots:
                lot = slot.take()
                lot.amt -= slot.rcp_amt
                if lot.amt > 0:
                    slot.give(lot)
                else:
                    LotPool.put(lot)

            # Create the tx
            for slot in self.tx_slots:
                lot = slot.take()
                if lot is None:
                    lot = LotPool.get(slot.tag, 0)
                lot.amt += slot.rcp_amt
                slot.give(lot)

    def __repr__(self):
        return "Unit: {}->{}".format(self.rcp.req_lots, self.rcp.mak_lots)


def run():
    print "K GO"
    boiler = Unit(UnitRcp([Lot("COAL", 1), Lot("WATER", 10)], [Lot("STEAM", 100)]))
    coal_src = Unit(UnitRcp([], [Lot("COAL", 1)]))
    water_src = Unit(UnitRcp([], [Lot("WATER", 10)]))
    steam_sink = Unit(UnitRcp([Lot("STEAM", 100)], []))

    boiler.rx_slots[0].connect_to(coal_src.tx_slots[0])
    boiler.rx_slots[1].connect_to(water_src.tx_slots[0])
    boiler.tx_slots[0].connect_to(steam_sink.rx_slots[0])

    done = False
    while not done:
        SlotMgr.tick()
        UnitMgr.tick()

        # TODO: set done condition, for now, debug with breakpoint on the while loop

    print "K DONE"


if __name__ == '__main__':
    run()
