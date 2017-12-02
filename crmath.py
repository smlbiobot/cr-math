import csv
import pprint

import crapipy
import json
from collections import Counter

client = crapipy.Client()

pp = pprint.PrettyPrinter(indent=2)

# read data
chest_data = {}
with open('data/treasure_chests.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        chest_data[row['Name']] = row

arena_data = {}
with open('data/arenas.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        arena_data[row['Name']] = row

with open('data/chest_order.json') as f:
    chest_order = json.load(f)['MainCycle']

print(chest_order)

chest_counter = Counter(chest_order).most_common()

def arena_row_by_id(arena_id):
    """Get arena data by arena int id."""
    for k, v in arena_data.items():
        if v['Arena'] == str(arena_id):
            return v
    return None

def get_prop(data, attr):
    value = data.get(attr)
    if not value:
        return 0
    if value.isdigit():
        value = int(value)
    return value

gem_per_hour = 6


class Chest:
    def __init__(self, name, data):
        self.name = name
        self.time_taken_hours = get_prop(data, 'TimeTakenHours')
        self.chest_count_in_chest_cycle = get_prop(data, 'ChestCountInChestCycle')
        self.rare_chance = get_prop(data, 'RareChance')
        self.epic_chance = get_prop(data, 'EpicChance')
        self.legendary_chance = get_prop(data, 'LegendaryChance')
        self.min_gold_per_card = get_prop(data, 'MinGoldPerCard')
        self.max_gold_per_card = get_prop(data, 'MaxGoldPerCard')
        self.random_spells = get_prop(data, 'RandomSpells')

    def __str__(self):
        out = []
        attrs = ['name', 'time_taken_hours', 'chest_count_in_chest_cycle', 'count_per_cycle',
                 'rare_chance', 'epic_chance', 'legendary_chance',
                 'random_spells']
        for attr in attrs:
            out.append("{:<30}{:>10}".format(attr, getattr(self, attr)))

        columns = [
            "Arena", "Cards", "Min Gold", "Max Gold", "Avg Gold",
            "Commons", "Rares", "Epics", "Leggies", "Card Worth", "Value",
            "Cycle Value", "Cycle hrs", "Cycle Gems"]
        out.append(("{:>14}" * len(columns)).format(*columns))
        for arena_id in range(1, 13):
            out.append(("{:>14,.4f}" * len(columns)).format(
                arena_id,
                self.card_count_by_arena(arena_id),
                self.min_gold_by_arena(arena_id),
                self.max_gold_by_arena(arena_id),
                self.avg_gold_by_arena(arena_id),
                self.common_count_by_arena(arena_id),
                self.rare_count_by_arena(arena_id),
                self.epic_count_by_arena(arena_id),
                self.legendary_count_by_arena(arena_id),
                self.card_worth(arena_id),
                self.chest_value(arena_id),
                self.value_in_cycle(arena_id),
                self.time_in_cycle,
                self.gem_in_cycle
            ))

        out.append("-" * 80)
        return "\n".join(out)

    def prop_by_arena(self, prop, arena_id):
        row = arena_row_by_id(arena_id)
        if row is not None:
            return int(row['ChestRewardMultiplier']) / 100 * getattr(self, prop)
        return 0

    def card_count_by_arena(self, arena_id):
        if self.name == 'Legendary':
            return 1
        if self.name == 'Epic':
            if arena_id < 9:
                return int(chest_data['Epic_Arena{}'.format(arena_id)]['RandomSpells'])
            return 20
        row = arena_row_by_id(arena_id)
        if row is not None:
            return int(row['ChestRewardMultiplier']) / 100 * getattr(self, "random_spells")
        return 0

    def rare_count_by_arena(self, arena_id):
        chance = self.rare_chance
        if chance == 0:
            return 0
        return 1 / chance * self.card_count_by_arena(arena_id)

    def epic_count_by_arena(self, arena_id):
        chance = self.epic_chance
        if chance == 0:
            return 0
        return 1 / chance * self.card_count_by_arena(arena_id)

    def legendary_count_by_arena(self, arena_id):
        chance = self.legendary_chance
        if chance == 0:
            return 0
        return 1 / chance * self.card_count_by_arena(arena_id)

    def common_count_by_arena(self, arena_id):
        return (
            self.card_count_by_arena(arena_id) -
            self.rare_count_by_arena(arena_id) -
            self.epic_count_by_arena(arena_id) -
            self.legendary_count_by_arena(arena_id))

    def card_worth(self, arena_id):
        """Total card worth."""
        return (
            self.common_count_by_arena(arena_id) * 1 +
            self.rare_count_by_arena(arena_id) * 5 +
            self.epic_count_by_arena(arena_id) * 500 +
            self.legendary_count_by_arena(arena_id) * 20000
        )

    def min_gold_by_arena(self, arena_id):
        return self.min_gold_per_card * self.card_count_by_arena(arena_id)

    def max_gold_by_arena(self, arena_id):
        return self.max_gold_per_card * self.card_count_by_arena(arena_id)

    def avg_gold_by_arena(self, arena_id):
        return (self.min_gold_by_arena(arena_id) + self.max_gold_by_arena(arena_id)) / 2

    def chest_value(self, arena_id):
        return self.card_worth(arena_id) + self.avg_gold_by_arena(arena_id)

    def value_in_cycle(self, arena_id):
        return self.chest_value(arena_id) * self.count_per_cycle

    @property
    def time_in_cycle(self):
        return self.count_per_cycle * self.time_taken_hours

    @property
    def gem_in_cycle(self):
        return self.time_in_cycle * gem_per_hour * 1.0

    @property
    def count_per_cycle(self):
        # regular chest
        for k, count in chest_counter:
            if k == self.name:
                return count
        # special chest
        if self.name in ['Super', 'Epic', 'Legendary']:
            return 1/500 * 240
        return 0



out = []

out.append('-' * 80)
out.append('Chest Cycle')
chest_counter = Counter(chest_order).most_common()
for k, count in chest_counter:
    out.append('{:<10}{:>5}'.format(k, count))
out.append('-' * 80)




chests = {}
for name in ['Free','Silver', 'Gold', 'Star', 'Magic', 'Giant', 'Epic', 'Super', 'Legendary']:
    chest_data_dict = chest_data[name]
    chest_obj = Chest(name, chest_data_dict)
    out.append(chest_obj.__str__())
    chests[name] = chest_obj
    
out.append("Total hrs in cycle")



for arena_id in range(2, 12):
    o = {
        "arena": arena_id,
        "total_hours": 0,
        "total_value": 0,
        "total_gems": 0
    }

    for name in ['Silver', 'Gold', 'Magic', 'Giant', 'Epic', 'Super', 'Legendary']:
        chest = chests[name]
        o["total_value"] += chest.value_in_cycle(arena_id)
        o["total_gems"] += chest.gem_in_cycle
        o["total_hours"] += chest.time_in_cycle

    o["value_per_gem"] = o["total_value"] / o["total_gems"]
    out.append("-" * 80)
    out.append(
        "Arena {arena}\n"
        "Total Hours: {total_hours}\n"
        "Total Gems:  {total_gems}\n"
        "Total Value: {total_value}\n"
        "Value per gem {value_per_gem}".format(**o)
    )



print('\n'.join(out))

with open('out.txt', 'w') as f:
    f.write('\n'.join(out))
