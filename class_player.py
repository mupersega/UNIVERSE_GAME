import random

import cfg


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

        self.entities = []
        self.hangars = []
        self.bays = []
        self.warehouses = []
        self.turrets = []
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

    def assign_start_hangar(self):
        # Choose a random hangar from available hangars in all stations.
        choices = []
        for station in self.game.stations:
            for hangar in station.hangars:
                if hangar.owner is None:
                    choices.append(hangar)
        chosen = random.choice(choices)
        chosen.owner = self
        chosen.update_label()
        self.hangars.append(chosen)

    def build_starter_setup(self):
        # each new player gets one warehouse and one bay to start. The ship comes in the bay.
        self.hangars[0].new_warehouse()
        self.hangars[0].new_bay()
        self.hangars[0].new_turret()
        self.hangars[0].new_turret()

    def perform(self, cmd, sub_status, args):

        # upgrades can cost 'mupees'
        if cmd == '!upgrade':
            self.upgrade(args)
            return
        # builds can cost resources
        if cmd == '!build':
            self.build(sub_status, args)
            return
        if cmd == '!auto':
            self.set_auto(args)
            return
        if cmd == '!cxauto':
            self.cancel_auto(args)
            return
        if cmd == '!set':
            self.set_behaviour(args)
            return
        if cmd == '!hunt':
            self.hunt(args)
            return
        if cmd == '!buy':
            self.buy(args)
            return
        if cmd == '!sell':
            self.list(args)
            return
        if cmd == '!cancel':
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
                            # if f.occupant is not None:
                            # occupant commands will pertain to bay facilities.
                            if ur == 'miner':
                                required = cfg.upgrade_values[fk][ur]
                                available = cfg.tally_resources(self)
                                if f.occupant.miner_lvl < f.occupant.max_miner_lvl:
                                    if cfg.resource_check(required, available):
                                        cfg.withdraw_resources(self, required)
                                        f.occupant.miner_lvl += 1
                                        f.update_bar_lengths()
                                        print('miner upgraded')
                                        return
                                    else:
                                        print("miner upgrade failed")
                                else:
                                    print("Upgrade at max level.")
                                return
                            elif ur == 'hold':
                                required = cfg.upgrade_values[fk][ur]
                                available = cfg.tally_resources(self)
                                if cfg.resource_check(required, available):
                                    cfg.withdraw_resources(self, required)
                                    if f.kind == "warehouse" and f.hold_lvl < f.max_hold_lvl:
                                        f.hold_lvl += 1
                                        f.hold_capacity += cfg.upgrade_amounts[fk]
                                    elif f.kind == "bay" and f.occupant.hold_lvl < f.occupant.max_hold_lvl:
                                        f.occupant.hold_lvl += 1
                                        f.occupant.hold_capacity += cfg.upgrade_amounts[fk]
                                        f.update_bar_lengths()
                                    print('hold upgraded')
                                else:
                                    print("hold upgrade failed")
                                # else return not enough resources
                                return
                            elif ur == 'thrusters':
                                required = cfg.upgrade_values[fk][ur]
                                available = cfg.tally_resources(self)
                                if cfg.resource_check(required, available):
                                    if f.occupant.thrusters_lvl < f.occupant.max_thrusters_lvl:
                                        cfg.withdraw_resources(self, required)
                                        f.occupant.thrusters_lvl += 1
                                        f.occupant.normal_vel += .1
                                        f.update_bar_lengths()
                                    else:
                                        print("Upgrade max lvl")
                                else:
                                    print("thrusters upgrade failed")
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
            print(f"{fk} is not a valid facility.")

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

    def set_auto(self, args):
        print(args)
        if len(args) != 3:
            print("Invalid arg count, check auto upgrade syntax.")
            return
        if args[0] in cfg.upgrade_values.keys():
            if args[2] in cfg.upgrade_values[args[0]].keys():
                for f in self.hangars[0].facilities:
                    if f.kind == args[0] and str(f.index) == args[1]:
                        f.auto = True
                        f.auto_upgrade = args[2]
                        return
                print(f"There is no {args[0]} with an index position of {args[1]}")
            else:
                print(f"{args[2]} is not a valid upgrade type for {args[0]}")
        else:
            print(f"{args[0]} not a valid facility.")

    def process_auto(self):
        for f in self.hangars[0].facilities:
            if f.auto:
                args = [f.kind, f.index, f.auto_upgrade]
                self.upgrade(args)

    def cancel_auto(self, args):
        if len(args) == 2:
            if args[0] in cfg.upgrade_values.keys():
                for f in self.hangars[0].facilities:
                    if f.kind == args[0] and f.index == int(args[1]):
                        f.auto = False
                        f.auto_upgrade = None
                        return
                    print(f"There is no {args[0]} with an index position of {args[1]}")
            else:
                print(f"{args[0]} is not a valid facility.")
        else:
            print("Invalid arg count, check cancel auto syntax.")

    def build(self, sub_status, args):
        # example args ['warehouse'] ['bay']
        # establish build type
        print(args)
        fk = args[0].lower()
        print(f'{self.name}:{sub_status}')
        if sub_status == '1' or self.name in ["dojiwastaken", 'mephistonag']:
            # check to see that max facilities isn't reached
            if len(self.hangars[0].facilities) < cfg.max_facilities:
                # check to see if arg is valid
                if fk in cfg.build_values.keys():
                    if fk == "warehouse":
                        # check for resources
                        required = cfg.build_values[fk]
                        available = cfg.tally_resources(self)
                        if cfg.resource_check(required, available):
                            # withdraw resources
                            cfg.withdraw_resources(self, required)
                            self.hangars[0].new_warehouse()
                        else:
                            print(f'{self.name.title()}: not enough resources to build a {fk}')
                    if fk == "bay":
                        required = cfg.build_values[fk]
                        available = cfg.tally_resources(self)
                        if cfg.resource_check(required, available):
                            # withdraw resources
                            cfg.withdraw_resources(self, required)
                            self.hangars[0].new_bay()
                        else:
                            print(f'{self.name.title()}: not enough resources to build a {fk}')
                else:
                    print(f'{self.name.title()}: {fk.lower()} is not a valid build argument.')
            else:
                print(f'{self.name.title()}: max facilities reached.')
        else:
            print(f'{self.name.title()}: building is for subs only.')
