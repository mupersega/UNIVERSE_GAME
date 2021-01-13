import cfg
import random


class Player:
    """Manage player characters, they control ships and own facilities."""
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.kind = 'player'
        self.index = 1
        self.sub_status = False

        # behaviours
        self.favouring = None

        self.hangars = []
        self.trades = []
        self.unassigned_resources = [0, 0, 0, 0]
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
        if cmd == 'buy':
            self.buy(args)
            return
        if cmd == 'sell':
            self.list(args)
            return
        if cmd == 'cancel':
            self.cancel_sell(args)
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
        if len(args) != 3:
            print('check !set syntax (args)')
        fk = args[0]
        # facility_index
        fi = args[1]
        # behaviour
        b = args[2]
        print('setting behaviour')
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

    def list(self, args):
        # example trade syntax = !list 100 rubine @ 2
        if len(args) != 4:
            print('check !list syntax')
        list_material = args[1].lower()
        try:
            list_qty = int(round(args[0]))
            list_price = int(round(args[3]))
        except:
            print(f'{self.name.title()} price/qty must be a number.')
        if list_material in cfg.tradables:
            # get players current amount of this material
            material_attribute = getattr(self, list_material)
            if material_attribute >= list_qty:
                material_attribute -= list_qty
                self.game.new_trade(self, list_qty, list_material, list_price)
            else:
                print(f'Not enough {list_material} to list that amount.')
        else:
            print(f'{list_material} not a trade commodity.')

    def buy(self, game, trade_id):
        pass

    def cancel_sell(self):
        pass

    def hunt(self, args):
        # example args
        pass

    def build(self, args):
        # example args ['warehouse'] ['bay']
        pass

