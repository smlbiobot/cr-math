import crapipy

client = crapipy.Client()


class Chest:
    def __init__(self,
                 name=None, time=None, gems=None, cards=None, rares=None, epics=None, legendaries=None,
                 min_gold=0, max_gold=0):
        self.name = name
        self.time = time
        self.gems = gems
        self.cards = cards
        self.rares = rares
        self.epics = epics
        self.legendaries = legendaries
        self.min_gold = min_gold
        self.max_gold = max_gold

    @property
    def commons(self):
        return self.cards - self.rares - self.epics - self.legendaries


chests = [
    Chest(
        name='Silver',
        time=3,
        gems=18,
        cards=13,
        rares=1 + 0.083333,
        epics=0.026,
        legendaries=0.00085,
        min_gold=65,
        max_gold=91
    ),
    Chest(
        name='Gold',
        time=8,
        gems=48,
        cards=41,
        rares=4 + 0.1,
        epics=0.14386,
        legendaries=0.00468,
        min_gold=205,
        max_gold=287
    ),
    Chest(
        name='Magic',
        time=12,
        gems=72,
        cards=123,
        rares=24 + 0.6,
        epics=4 + 0.1,
        legendaries=0.13325,
        min_gold=1200,
        max_gold=1200
    ),
    Chest(
        name='Giant',
        time=12,
        gems=72,
        cards=287,
        rares=57 + 0.4,
        epics=0.574,
        legendaries=0.01866,
        min_gold=860,
        max_gold=860
    )
]
chest_cycle = client.get_constants().chest_cycle.order
total_time = 0
total_gems = 0
total_commons = 0
total_epics = 0
total_rares = 0
total_legendaries = 0
total_min_gold = 0
total_max_gold = 0
for cycle in chest_cycle:
    for chest in chests:
        if chest.name == cycle:
            total_time += chest.time
            total_gems += chest.gems
            total_commons += chest.commons
            total_rares += chest.rares
            total_epics += chest.epics
            total_legendaries += chest.legendaries
            total_min_gold += chest.min_gold
            total_max_gold += chest.max_gold

print(chest_cycle)
print(
    "time:        {:>10,.2f} hrs\n"
    "gems:        {:>10,.2f}\n"
    "commons:     {:>10,.2f}\n"
    "rares:       {:>10,.2f}\n"
    "epics:       {:>10,.2f}\n"
    "legendaries: {:>10,.2f}\n"
    "min gold:    {:>10,.2f}\n"
    "max gold:    {:>10,.2f}".format(
        total_time,
        total_gems,
        total_commons,
        total_rares,
        total_epics,
        total_legendaries,
        total_min_gold,
        total_max_gold
    )
)
print(
    "min gold per gem: {:>10,.2f}\n"
    "max gold per gem: {:>10,.2f}\n".format(
        total_min_gold / total_gems,
        total_max_gold / total_gems
    )
)
