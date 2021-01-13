import cfg
import random


class Player:
    """Manage player characters, they control ships and own facilities."""
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.kind = 'player'
        self.index = 1

        # behaviours
        self.favouring = None

        self.hangars = []
        self.trades = []
        self.rubine = 0
        self.verdite = 0
        self.ceruliun = 0
        self.mupees = cfg.player_starting_mupees

        self.player_setup()

    def player_setup(self):
        # choose a random hangar to begin in
        self.assign_start_hangar()
        # build starting hangar and bay
        self.build_starter_setup()
        # build starter ship in
        self.build_ship()

    def assign_start_hangar(self):
        # Choose a random hangar from available hangars in all stations.
        choices = []
        for station in self.game.stations:
            for hangar in station.hangars:
                if hangar.owner is None:
                    choices.append(hangar)
        chosen = random.choice(choices)
        chosen.owner = self.name
        self.hangars.append(chosen)

    def build_starter_setup(self):
        # each new player gets one warehouse and one bay to start. The ship comes in the bay.
        self.hangars[0].new_warehouse()
        self.hangars[0].new_bay()

    def build_ship(self):
        for i in self.hangars:
            for j in i.facilities:
                # I have used the occupied attribute as the check here because only bays have it.
                if j.kind == 'bay':
                    if j.occupant is None:
                        j.new_ship()
                        return

    def perform(self, cmd, args):
        # upgrades can cost 'mupees'
        if cmd == '!upgrade':
            self.upgrade(args)
            return
        # builds can cost resources
        if cmd == '!build':
            self.buy(args)
            return
        if cmd == '!set':
            self.set_behaviour(args)
            return
        if cmd == '!hunt':
            self.hunt(args)
            return
        if cmd == 'take':
            self.take_trade(args)
            return
        if cmd == 'list':
            self.init_trade(args)
            return
        if cmd == 'delist':
            self.cancel_trade(args)
            return

    def upgrade(self, args):
        # upgrade syntax: ['facility kind', 'facility_index', 'upgrade_request']
        # facility_kind
        fk = args[0]
        # facility_index
        fi = args[1]
        # upgrade_request
        ur = args[2]
        print('beginning upgrade')
        if fk in cfg.upgrade_values.keys():
            print(f"{fk} found!")
            if ur in cfg.upgrade_values[fk].keys():
                print(f"{ur} found!")
                for h in self.hangars:
                    for f in h.facilities:
                        # if fac kind matches kind and fac index matches index
                        print(f"facility index = {f.index}\n facility kind = {f.kind}")
                        if f.kind == fk and f.index == int(fi):
                            print("found match")
                            if f.occupant is not None:
                                # occupant commands will pertain to bay facilities.
                                if ur == 'miner':
                                    # check for required resources if enough:
                                    # extract resources
                                    f.occupant.miner_lvl += 1
                                    print('miner upgraded')
                                    # else return not enough resources
                                    return
                                elif ur == 'hold':
                                    # check for required resources if enough:
                                    # extract resources
                                    f.occupant.hold_capacity += 1
                                    print('hold upgraded')
                                    # else return not enough resources
                                    return
                                elif ur == 'thrusters':
                                    # check for required resources if enough:
                                    # extract resources
                                    f.occupant.normal_vel += .1
                                    print('thrusters upgraded')
                                    # else return not enough resources
                                    return
                            else:
                                print("No ship in this facility.")
                        else:
                            print("can not find a kind or index match.")
            else:
                print(f"{ur} is not a valid upgrade request.")
        else:
            print(f"{fk} is not a valid facility kind.")

    def set_behaviour(self, args):
        # upgrade syntax: ['facility kind', 'facility_index', 'behaviour']
        # facility_kind
        fk = args[0]
        # facility_index
        fi = args[1]
        # behaviour
        b = args[2]
        print('beginning upgrade')
        if fk in cfg.set_behaviours.keys():
            print(f"{fk} found!")
            if b in cfg.set_behaviours[fk].keys():
                print(f"{b} found!")
                for h in self.hangars:
                    for f in h.facilities:
                        # if fac kind matches kind and fac index matches index
                        print(f"facility index = {f.index}\n facility kind = {f.kind}")
                        if f.kind == fk and f.index == int(fi):
                            print("found match")
                            if f.occupant is not None:
                                # occupant commands will pertain to bay facilities.
                                if b == 'mine':
                                    # check for required resources if enough:
                                    # extract resources
                                    f.occupant.behaviour = 'mine'
                                    print(f'Ship in {fk} {fi} now set to mine.')
                                    # else return not enough resources
                                    return
                            else:
                                print("No ship in this facility.")
                        else:
                            print("can not find a kind or index match.")
            else:
                print(f"{b} is not a valid upgrade request.")
        else:
            print(f"{fk} is not a valid facility kind.")

    def init_trade(self, args):
        # example trade syntax = !list 20 rubine for 300 mupees
        if len(args) != 4:
            print('check trade syntax')
        offer_qty = args[0]
        request_material = args[2]
        request_qty = args[3]
        offer_material = args[1]
        if offer_material in cfg.tradables:
            material_attribute = getattr(self, offer_material)
            if material_attribute >= offer_qty:
                req_list = [0, 0, 0, 0]
                dem_list = [0, 0, 0, 0]
                count = 0
                for i in cfg.tradables:
                    if i == offer_material:
                        req_list[count] = offer_qty
                    if i == request_material:
                        dem_list[count] = request_qty
                    count += 1
                self.game.new_trade(self.name, req_list, dem_list)
            else:
                print(f'Not enough {offer_material} for that trade.')
        else:
            print(f'{offer_material} not a trade commodity.')

    def take_trade(self, game, trade_id):
        pass

    def cancel_trade(self):
        pass

    def hunt(self, args):
        # example args
        pass

    def build(self, args):
        # example args ['warehouse'] ['bay']
        pass

