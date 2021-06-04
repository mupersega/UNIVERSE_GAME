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
        self.autos = []
        # self.pause_autos = True
        self.rubine = 0
        self.verdite = 0
        self.ceruliun = 0
        self.mupees = cfg.player_starting_mupees

        self.kills = 0
        self.leaderboard_position = 0

        # Leaderboard element
        self.name_plate = cfg.leaderboard_font.render(self.name[0:15].title(), True, cfg.col.bone)
        self.kills_plate = cfg.leaderboard_font.render(str(self.kills), True, cfg.col.bone)

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
        # self.hangars[0].new_turret()

    def perform(self, cmd, sub_status, args):

        if cmd == '!upgrade':
            self.upgrade(args)
            return
        if cmd == '!build':
            self.build(sub_status, args)
            return
        if cmd == '!auto':
            self.set_auto(args)
            return
        if cmd == '!cxauto':
            self.cancel_auto(args)
            return
        if cmd == '!activate':
            self.activate(args)
            return
        if cmd == '!deactivate':
            self.deactivate(args)
            return
        if cmd == '!load':
            self.load(args)
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
                                        f.auto = False
                                else:
                                    print("Upgrade at max level.")
                                    f.auto = False
                                return
                            elif ur == 'hold':
                                required = cfg.upgrade_values[fk][ur]
                                available = cfg.tally_resources(self)
                                if cfg.resource_check(required, available):
                                    cfg.withdraw_resources(self, required)
                                    if f.kind == "warehouse" and f.hold_lvl < f.max_hold_lvl:
                                        f.hold_lvl += 1
                                        f.hold_capacity += cfg.upgrade_amounts[fk]
                                    else:
                                        print("Upgrade at max level.")
                                        f.auto = False
                                        return
                                    if f.kind == "bay" and f.occupant.hold_lvl < f.occupant.max_hold_lvl:
                                        f.occupant.hold_lvl += 1
                                        f.occupant.hold_capacity += cfg.upgrade_amounts[fk]
                                        f.update_bar_lengths()
                                    else:
                                        print("Upgrade at max level.")
                                        f.auto = False
                                        return
                                    print('hold upgraded')
                                else:
                                    print("hold upgrade failed")
                                    f.auto = False
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
                                        f.auto = False
                                else:
                                    print("thrusters upgrade failed")
                                    f.auto = False
                                return
                        else:
                            print("No ship in this facility.")
                    else:
                        print("can not find a kind or index match.")
            else:
                print(f"{ur} is not a valid upgrade request.")
        else:
            print(f"{fk} is not a valid facility kind.")

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
                        # self.pause_autos = False
                        if f not in self.autos:
                            self.autos.append(f)
                print(f"There is no {args[0]} with an index position of {args[1]}")
            else:
                print(f"{args[2]} is not a valid upgrade type for {args[0]}")
        else:
            print(f"{args[0]} not a valid facility.")

    def process_auto(self):
        for f in self.autos:
            if f.auto:
                args = [f.kind, f.index, f.auto_upgrade]
                self.upgrade(args)

    def unpause_autos(self):
        for i in self.autos:
            i.auto = True

    def cancel_auto(self, args):
        if len(args) == 2:
            if args[0] in cfg.upgrade_values.keys():
                for f in self.hangars[0].facilities:
                    if f.kind == args[0] and f.index == int(args[1]):
                        f.auto = False
                        f.auto_upgrade = None
                        if f in self.autos:
                            self.autos.remove(self)
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
        # check for subscriber or VIP status
        if sub_status == '1' or self.name in ["dojiwastaken", "mephistonag"]:
            # check to see that max facilities isn't reached
            if len(self.hangars[0].facilities) < cfg.max_facilities:
                # check to see if arg is valid
                if fk in cfg.build_values.keys():
                    if fk == "warehouse":
                        # check for resources
                        if cfg.resource_check(cfg.build_values[fk], cfg.tally_resources(self)):
                            # withdraw resources
                            cfg.withdraw_resources(self, cfg.build_values[fk])
                            self.hangars[0].new_warehouse()
                        else:
                            print(f'{self.name.title()}: not enough resources to build a {fk}')
                    if fk == "bay":
                        if cfg.resource_check(cfg.build_values[fk], cfg.tally_resources(self)):
                            # withdraw resources
                            cfg.withdraw_resources(self, cfg.build_values[fk])
                            self.hangars[0].new_bay()
                        else:
                            print(f'{self.name.title()}: not enough resources to build a {fk}')
                    if fk == "turret":
                        if cfg.resource_check(cfg.build_values[fk], cfg.tally_resources(self)):
                            # withdraw resources
                            cfg.withdraw_resources(self, cfg.build_values[fk])
                            self.hangars[0].new_turret()
                        else:
                            print(f'{self.name.title()}: not enough resources to build a {fk}')
                else:
                    print(f'{self.name.title()}: {fk.lower()} is not a valid build argument.')
            else:
                print(f'{self.name.title()}: max facilities reached.')
        else:
            print(f'{self.name.title()}: building is for subs only.')

    def activate(self, args):
        if len(args) == 2:
            if args[0] == 'turret':
                for f in self.hangars[0].facilities:
                    if f.kind == args[0] and f.index == int(args[1]):
                        f.activate()
                        return
                    print(f"There is no {args[0]} with an index position of {args[1]}")
            else:
                print(f"{args[0]} is not a valid facility.")
        else:
            print("Invalid arg count, check cancel auto syntax.")

    def deactivate(self, args):
        if len(args) == 2:
            if args[0] == 'turret':
                for f in self.hangars[0].facilities:
                    if f.kind == args[0] and f.index == int(args[1]):
                        f.deactivate()
                        return
                    print(f"There is no {args[0]} with an index position of {args[1]}")
            else:
                print(f"{args[0]} is not a valid facility.")
        else:
            print("Invalid arg count, check cancel auto syntax.")

    def distribute_resources(self, amt):
        distribute_amt = amt.copy()
        for i, t in enumerate(distribute_amt.copy()):
            qty = t
            for _ in range(qty):
                for h in self.hangars:
                    for f in h.facilities:
                        if f.kind == 'warehouse' and sum(f.ores) < f.hold_capacity:
                            distribute_amt[i] -= 1
                            f.ores[i] += 1
                            break
        print("after")
        print(distribute_amt)
        self.unpause_autos()

    def load(self, args):
        # example args ['turret', '1', 'maul']
        if len(args) == 3:
            if args[0] == "turret":
                for f in self.hangars[0].facilities:
                    print(f.index)
                    if f.kind == args[0] and f.index == int(args[1]):
                        f.load(args[2])
                    print(f"There is no {args[0]} with an index position of {args[1]}")
            else:
                print(f"{args[0]} is not a valid facility.")
        else:
            print("Invalid arg count, check turret load syntax.")