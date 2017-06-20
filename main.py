
class Lot(object):
    def __init__(self, tag, amt):
        self.tag = tag
        self.amt = amt

    def __eq__(self, other):
        return other.tag == self.tag and other.amt == self.amt


class Slot(object):
    """
    Contains a Lot, is part of a Unit
    """
    def __init__(self, flow, tag):
        self.flow = flow
        self.tag = tag
        self.lot = None

        self.src_slots = []
        self.tgt_slots = []


    def take(self):
        if self.lot is not None:
            lot = self.lot
            self.lot = None
            return lot
        return None

    def give(self, lot):
        if self.lot is None:
            self.lot = lot
            return True
        return False

    def connect_to(self, slot):
        if not isinstance(slot, Slot):
            return

        if self.flow == "IN" and slot.flow == "OUT":
            if self not in slot.tgt_slots and slot not in self.src_slots:
                slot.tgt_slots.append(self)
                self.src_slots.append(slot)

        if self.flow == "OUT" and slot.flow == "IN":
            if self not in slot.src_slots and slot not in self.tgt_slots:
                slot.src_slots.append(self)
                self.tgt_slots.append(slot)

    def process(self):



class UnitRcp(object):
    def __init__(self, req_lots, mak_lots):
        self.req_lots = req_lots
        self.mak_lots = mak_lots

    # def add_req_lot(self, lot):
    #     if isinstance(lot, Lot) and lot not in self.req_lots:
    #         self.req_lots.append(lot)
    #
    # def add_mak_lot(self, lot):
    #     if isinstance(lot, Lot) and lot not in self.mak_lots:
    #         self.mak_lots.append(lot)


class Unit(object):
    def __init__(self, cfg):
        self.cfg = cfg if isinstance(cfg, UnitRcp) else None
        self.rx_slots = []
        for tag in self.cfg.req_lots:
            self.rx_slots.append(Slot(tag))

        self.tx_slots = []
        for tag in self.cfg.mak_lots:
            self.tx_slots.append(Slot(tag))

        self.src_idx = 0
        self.tgt_idx = 0

    def tick(self):



def run():
    print "K GO"


if __name__ == '__main__':
    run()
