from WoWRaidScore.wcl_utils.wcl_util_functions import convert_timestamp
from unidecode import unidecode


class WCLEventTypes(object):
    apply_debuff = "applydebuff"
    apply_debuff_stack = "applydebuffstack"
    remove_debuff = "removedebuff"
    damage = "damage"
    death = "death"
    cast = "cast"
    combatant_info = "combatantinfo"


class WCLRaid(object):
    def __init__(self, data):
        self.start_time = convert_timestamp(data.get("start"))
        self.end_time = convert_timestamp(data.get("end"))
        self.title = data.get("title")
        self.zone = data.get("zone")
        self.language = data.get("lang")


class WCLFight(object):
    def __init__(self, data, zone_id, raid_start_time):
        self.name = data.get("name")
        self.id = data.get("id")
        self.attempt = 0
        self.zone_id = zone_id
        self.boss_id = data.get("boss")
        self.raid_size = data.get("size")
        self.start_time_str = data.get("start_time")
        self.end_time_str = data.get("end_time")
        self.start_time = convert_timestamp(self.start_time_str + raid_start_time)
        self.end_time = convert_timestamp(self.end_time_str + raid_start_time)
        self.difficulty = data.get("difficulty")
        self.kill = data.get("kill")
        self.percent = data.get("bossPercentage", 10000) / 100.0
        self.players = []
        self.enemies = {}

    def set_attempt(self, attempt):
        self.attempt = attempt

    def add_player(self, player):
        self.players.append(player)

    def add_enemy(self, enemy):
        self.enemies[enemy.id] = enemy

    def __str__(self):
        return "<WCLFight {} ({}) - {} ({}%)>".format(self.name, self.boss_id, self.id, self.percent)

    def __repr__(self):
        return self.__str__()


class WCLActor(object):
    def __init__(self, data):
        self.name = data.get("name")
        self.id = data.get("id")
        self.type = data.get("type")
        self.guid = data.get("guid")
        self.fights = [d.get("id") for d in data.get("fights")]

    def __str__(self):
        return "<Actor: {} ({})>".format(self.name, self.id)

    def __repr__(self):
        return self.__str__()


class WCLPlayer(WCLActor):

    def __init__(self, data):
        super(WCLPlayer, self).__init__(data)
        self.server = ""

    def __str__(self):
        return "<Player: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()


class WCLEnemy(WCLActor):
    pass


class WCLPlayerFightInfo(object):
    def __init__(self, data, actor_objs_dict=None):
        self.source = data.get("sourceID")
        self.spec_id = data.get("specID")
        self.speed = data.get("speed", 0)
        self.avoidance = data.get("avoidance", 0)
        self.leech = data.get("leech", 0)
        self.stamina = data.get("stamina")
        self.haste = data.get("hasteMelee")
        self.vers = data.get("versatilityDamageDone")
        self.mastery = data.get("mastery")
        self.crit = data.get("critSpell")

        if actor_objs_dict is not None:
            self.source = actor_objs_dict.get(self.source, self.source)

    @property
    def safe_source(self):
        source_name = self.source
        if source_name is None:
            return "Unknown"
        if not isinstance(source_name, int):
            source_name = unidecode(self.source.name)
        return source_name

    def __str__(self):
        return "<CombatantInfo {} - {}".format(self.safe_source, self.spec_id)


class WCLTargetEvent(object):
    def __init__(self, data, actor_objs_dict=None):
        self.type = data.get("type")
        self.name = data.get("ability", {}).get("name")
        self.timestamp = data.get("timestamp")
        self.source = data.get("sourceID")
        self.target = data.get("targetID")
        self.source_is_friendly = data.get("sourceIsFriendly")
        self.target_is_friendly = data.get("targetIsFriendly")
        if actor_objs_dict is not None:
            self.source = actor_objs_dict.get(self.source, self.source)
            self.target = actor_objs_dict.get(self.target, self.target)

    @property
    def safe_source(self):
        source_name = self.source
        if source_name is None:
            return "Unknown"
        if not isinstance(source_name, int):
            source_name = unidecode(self.source.name)
        return source_name

    @property
    def safe_target(self):
        source_name = self.target
        if source_name is None:
            return "Unknown"
        if not isinstance(source_name, int):
            source_name = unidecode(self.target.name)
        return source_name

    def __str__(self):
        return "<Event {}: {}->{} {}>".format(self.type, self.safe_source, self.safe_target,
                                                 self.timestamp)

    def __repr__(self):
        return self.__str__()


class WCLAbilityEventObj(WCLTargetEvent):
    def __init__(self, data, actor_objs_dict=None):
        super(WCLAbilityEventObj, self).__init__(data, actor_objs_dict)
        self.name = data.get("ability", {}).get("name")
        self.id = data.get("ability", {}).get("guid")

    def __str__(self):
        return "<Event {}: {} {}->{} {}>".format(self.type, self.name, self.safe_source, self.safe_target,
                                                 self.timestamp)


class WCLApplyDebuffEvent(WCLAbilityEventObj):
    def __init__(self, data, actor_objs_dict=None):
        super(WCLAbilityEventObj, self).__init__(data, actor_objs_dict)


class WCLApplyDebuffStackEvent(WCLAbilityEventObj):
    def __init__(self, data, actor_objs_dict=None):
        super(WCLAbilityEventObj, self).__init__(data, actor_objs_dict)
        self.stack = data.get("stack")


class WCLRemoveDebuffEvent(WCLAbilityEventObj):
    pass


class WCLDamageEvent(WCLAbilityEventObj):
    def __init__(self, data, actor_objs_dict=None):
        super(WCLAbilityEventObj, self).__init__(data, actor_objs_dict)
        self.tick = data.get("tick")
        self.point_x = data.get("x")
        self.point_y = data.get("y")
        self.hit_type = data.get("hitType")
        self.damage_total = data.get("amount") + data.get("absorbed")

    def __str__(self):
        return "<WCLDamageEvent{} {} {}->{} for {} damage. ({})>".format(" (tick)" if self.tick else "", self.name,
                                                                         self.safe_source, self.safe_target,
                                                                         self.damage_total, self.timestamp)


class WCLCastEvent(WCLTargetEvent):

    def __init__(self, data, actor_objs_dict=None):
        super(WCLCastEvent, self).__init__(data, actor_objs_dict)
        self.name = data.get("ability", {}).get("name")
        self.point_x = data.get("x")
        self.point_y = data.get("y")

    def __str__(self):
        return "<WCLCastEvent {} {}->{} {}>".format(self.name, self.safe_source, self.safe_target,
                                                    self.timestamp)


class WCLDeathEvent(WCLTargetEvent):
    pass

    def __str__(self):
        return "<WCLDeathEvent {} killed {}>".format(self.safe_source, self.safe_target)
