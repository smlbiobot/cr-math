import csv
import pprint

import crapipy

client = crapipy.Client()

pp = pprint.PrettyPrinter(indent=2)

# read data
chest_data = {}
with open('treasure_chests.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        chest_data[row['Name']] = row

arena_data = {}
with open('arenas.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        arena_data[row['Name']] = row

def arena_row_by_id(arena_id):
    """Get arena data by arena int id."""
    for k, v in arena_data.items():
        if v['Arena'] == str(arena_id):
            return v
    return None

def get_prop(data, attr):
    value = data.get(attr)
    if value.isdigit():
        value = int(value)
    return value


class Chest:
    def __init__(self, name, data):
        self.name = name
        self.time_taken_hours = get_prop(data, 'TimeTakenHours')
        self.chest_count_in_chest_cycle = get_prop(data, 'ChestCountInChestCycle')
        self.rare_chance = get_prop(data, 'RareChance')
        self.epic_chance = get_prop(data, 'EpicChance')
        self.legendary_chance = get_prop(data, 'LegendaryChance')
        self.base_min_gold_per_card = get_prop(data, 'MinGoldPerCard')
        self.base_max_gold_per_card = get_prop(data, 'MaxGoldPerCard')
        self.random_spells = get_prop(data, 'RandomSpells')

    def __str__(self):
        out = []
        attrs = ['name', 'time_taken_hours', 'chest_count_in_chest_cycle',
                 'rare_chance', 'epic_chance', 'legendary_chance',
                 'random_spells']
        for attr in attrs:
            out.append("{:<30}{:>10}".format(attr, getattr(self, attr)))
        out.append("{:<10}{:>10}{:>10}{:>10}".format(
            "Arena", "Card Count", "Min Gold", "Max Gold"
        ))
        for arena_id in range(1, 12):
            out.append("Arena {:<4}{:>10,.2f}{:>10,.2f}{:>10,.2f}".format(
                arena_id,
                self.prop_by_arena('random_spells', arena_id),
                self.prop_by_arena('base_min_gold_per_card', arena_id),
                self.prop_by_arena('base_max_gold_per_card', arena_id),
            ))
        # for tup in self.card_count:
        #     out.append("Arena {:<3} {:>10,.2f}".format(tup[0], tup[1]))
        out.append("-" * 40)
        return "\n".join(out)

    @property
    def card_count(self):
        """Show stats based on arena."""
        count = []
        for arena_id in range(1, 12):
            row = arena_row_by_id(arena_id)
            if row is not None:
                count.append((arena_id, self.random_spells * int(row['ChestRewardMultiplier']) / 100))
        return count

    def prop_by_arena(self, prop, arena_id):
        row = arena_row_by_id(arena_id)
        if row is not None:
            return int(row['ChestRewardMultiplier']) / 100 * getattr(self, prop)
        return 0

    @property
    def min_gold_per_card(self):
        out = []
        for arena_id in range(1, 12):
            out.append((arena_id, self.prop_by_arena('base_min_gold_per_card', arena_id)))
        return out

    @property
    def max_gold_per_card(self):
        out = []
        for arena_id in range(1, 12):
            out.append((arena_id, self.prop_by_arena('base_max_gold_per_card', arena_id)))
        return out


chests = []
for name in ['Silver', 'Gold', 'Giant', 'Magic', 'Epic', 'Super', 'Legendary']:
    chest_data_dict = chest_data[name]
    chest_obj = Chest(name, chest_data_dict)
    print(chest_obj)
    chests.append(chest_obj)

chest_cycle = client.get_constants().chest_cycle.order
