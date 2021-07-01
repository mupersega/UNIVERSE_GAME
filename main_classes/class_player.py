import random

from utility_classes import cfg


class Player:
    """Manage player characters, they control ships and own facilities."""
    def __init__(self, game, name, start_hangar):
        self.game = game
        self.name = name
        self.start_hangar = start_hangar
        self.kind = 'player'
        self.index = 1
        self.sub_status = False
        self.max_facilities = cfg.default_max_facilities

        # behaviours
        self.favouring = None

        self.entities = []
        self.hangars = []
        self.bays = []
        self.warehouses = []
        self.turrets = []
        self.autos = []

        # Target management
        self.kill_priority = 0

        self.favour = 0
        self.total_favour = 0
        self.rubine = 0
        self.verdite = 0
        self.ceruliun = 0
        # Current trade broken down into offering and ask
        self.mupees = cfg.player_starting_mupees

        self.kills = 0
        self.leaderboard_position = 0

        # Leaderboard element
        self.name_plate = cfg.leaderboard_font.render(self.name[0:15].title(), True, cfg.col.p_one)
        self.kills_plate = cfg.leaderboard_font.render(str(self.kills), True, cfg.col.p_one)

        self.player_setup()

    def player_setup(self):
        # choose a random hangar to begin in
        self.assign_start_hangar()
        # build starting hangar and bay
        self.build_starter_setup()

    def assign_start_hangar(self):
        # If player chose a start position, assign them to that hangar.
        if self.start_hangar:
            st = int(self.start_hangar.split('.')[0])
            h = int(self.start_hangar.split('.')[1])
            chosen = self.game.stations[st].hangars[h]
        # Else choose a random hangar from available hangars in all stations.
        else:
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
        if cmd == '!list':
            self.list_trade(args)
        if cmd == '!trade':
            self.take_trade(args)
        if cmd == '!cxtrade':
            self.game.market.clear_player_trade(self.name)
        if cmd == '!tribute':
            self.tribute(args)

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
            self.max_facilities = 7
            # check to see that max facilities isn't reached
        if len(self.hangars[0].facilities) < self.max_facilities:
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

    def list_trade(self, args):
        # I.E. # !trade 30 rubine for 5 ceruliun # #
        # Catch all the things - arg number - quantities - mineral types - max listable amount.
        if len(args) != 5:
            print("Incorrect number of args, check list_trade syntax.")
            return
        offer_mineral = args[1]
        ask_mineral = args[4]
        # Check if qty listed is not able to be converted to integer. (Thus probably incorrect syntax)
        try:
            offer_qty = int(args[0])
            ask_qty = int(args[3])
        except:
            print(f"Trade syntax incorrect offer {args[0]} ask {args[3]}.")
            return
        # Check if minerals are spelt correctly and in mineral list.
        if offer_mineral in cfg.mineral_name_list:
            if ask_mineral in cfg.mineral_name_list:
                if offer_qty <= cfg.max_trade_amt:
                    self.game.market.new_trade(self,
                                               [offer_mineral, offer_qty],
                                               [ask_mineral, ask_qty])
                else:
                    print(f"Offer - {offer_qty} - is above the max trade amount.")
            else:
                print(f"Ask mineral - {ask_mineral.upper()} - not valid.")
        else:
            print(f"Offer mineral - {offer_mineral.upper()} - not valid.")

    def take_trade(self, args):
        self.game.market.finalize_trade(self, args[0])

    def tribute(self, args):
        """Tribute will take a percent of total resource of a specified resource and gift it for a return of favour."""
        allowed_amounts = ["all", "half"]
        amt = args[0].lower()
        mineral = args[1].lower()
        # Check all args validity.
        if amt in allowed_amounts:
            if mineral in cfg.mineral_name_list:
                # Calculate the amount to remove dependant on amt.
                total = cfg.tally_resources(self)
                # Get amount available of specific mineral from total.
                mineral_available = total[cfg.mineral_name_list.index(mineral)]
                # Apply dispatch amount, dispatch_amount list corresponds to allowed_amounts list.
                dispatch_amount = [1, .5]
                mineral_dispatch_amount = int(mineral_available * dispatch_amount[allowed_amounts.index(amt)])
                # Return new mineral list with dispatch amount, and withdraw those resources.
                mineral_list = cfg.return_mineral_list(mineral, mineral_dispatch_amount)
                cfg.withdraw_resources(self, mineral_list)
                # Payout favour.
                self.distribute_favour(cfg.convert_mineral_to_favour(mineral_list))
            else:
                print(f'{mineral.title()} is not a valid mineral type {self.name.title()}.')
        else:
            print(f'{amt} is not a valid amount to tribute {self.name.title()}.')

    def distribute_favour(self, amt):
        self.favour += amt
        self.tribute += amt
        self.total_favour += amt
