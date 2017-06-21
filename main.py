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

    def __eq__(self, other):
        return other.tag == self.tag and other.amt == self.amt

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.tag, self.amt))

    def __repr__(self):
        return ".{} {}.".format(self.tag, self.amt)


class Slot(object):
    """
    Contains a Lot, is part of a Unit
    """

    def __init__(self, unit, tag):
        self.unit = unit if isinstance(unit, Unit) else None
        self.tag = tag
        self.lot = None

        self.flow = "NONE"

        self.src_slots = []
        self.tgt_slots = []

        SlotMgr.add_slot(self)

    def give(self, lot):
        if lot is None or not isinstance(lot, Lot):
            return

        if self.lot is None:
            self.lot = lot
        elif lot.tag == self.lot.tag and lot.amt > 0:
            self.lot.amt += lot.amt

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
                    rx_slot.give(Lot(slot.tag, div_amt))
                # Keep the remaining amount_
                rem_amt = lot.amt % len(slot.tgt_slots)
                slot.give(Lot(slot.tag, rem_amt))


class RxSlot(Slot):
    def __init__(self, unit, rcp):
        super(RxSlot, self).__init__(unit, rcp)
        self.flow = "IN"

    def connect_to(self, slot):
        if isinstance(slot, TxSlot) and self not in slot.tgt_slots and slot not in self.src_slots:
            slot.tgt_slots.append(self)
            self.src_slots.append(slot)
            return True

        return False


class TxSlot(Slot):
    def __init__(self, unit, rcp):
        super(TxSlot, self).__init__(unit, rcp)
        self.flow = "OUT"

    def connect_to(self, slot):
        if isinstance(slot, RxSlot) and self not in slot.src_slots and slot not in self.tgt_slots:
            slot.src_slots.append(self)
            self.tgt_slots.append(slot)
            return True

        return False


class UnitRcp(object):
    def __init__(self, req_lots, mak_lots):
        self.req_lots = req_lots
        self.mak_lots = mak_lots


class Unit(object):
    def __init__(self, rcp):
        self.rcp = rcp if isinstance(rcp, UnitRcp) else None

        self.rx_slots = {}
        for idx, rcp_lot in enumerate(self.rcp.req_lots):
            self.rx_slots[idx] = (RxSlot(self, rcp_lot.tag), rcp_lot)

        self.tx_slots = {}
        for idx, rcp_lot in enumerate(self.rcp.mak_lots):
            self.tx_slots[idx] = (TxSlot(self, rcp_lot.tag), rcp_lot)

    def tick(self, tick):
        # Start by assuming we have all the lots we need to do our recipe
        lots_avbl = True
        # Now if any is insufficient, then lots are not avbl
        for rcp_lot, slot in self.rx_slots.iteritems():
            if slot.lot.amt < rcp_lot.amt:
                lots_avbl = False

        # If we have enough, do our recipe
        if lots_avbl:
            # Nom the rx
            for slot_info in self.rx_slots.itervalues():
                slot_info[0].lot.amt -= slot_info[1].amt

            # Create the tx
            for slot_info in self.tx_slots.itervalues():
                slot_info[0].lot.amt += slot_info[1].amt


def run():
    print "K GO"


if __name__ == '__main__':
    run()
