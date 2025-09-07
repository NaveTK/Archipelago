from dataclasses import dataclass

from Options import DefaultOnToggle, OptionCounter, OptionSet, Toggle, Range, PerGameCommonOptions


class ForceLategame(DefaultOnToggle):
    """
    TODO: ForceLategame
    """
    display_name = "Force Lategame to be late"

class WinCollectsMissedLocations(DefaultOnToggle):
    """
    TODO: WinCollectsMissedLocations
    """
    display_name = "Win collects missed locations"

class FortunesAreHints(DefaultOnToggle):
    """
    TODO: FortunesAreHints
    """
    display_name = "Fornues are Hints"

class Goals(OptionSet):
    """
    TODO: Goals
    """
    display_name = "Goals"

    valid_keys = frozenset({
        "Mom",
        "Mom's Heart",
        "Isaac",
        "Satan",
        "Blue Baby",
        "The Lamb",
        "Mega Satan",
        "Boss Rush",
        "Hush",
        "Beast",
        "Mother",
        "Delirium"
    })
    default = frozenset({"Mega Satan", "Beast", "Mother", "Delirium"})

class ExcludeAreas(OptionSet):
    """
    TODO: Excluded areas
    """
    display_name = "Excluded areas"

    valid_keys = frozenset({"The Void", "Ascend", "Alt Path", "Timed Areas"})
    default = frozenset({})

class AdditionalItemLocations(Range):
    """
    TODO: AdditionalItemLocations
    """
    display_name = "Additional Item Locations"
    range_start = 0
    range_end = 300
    default = 100

class ItemLocationStep(Range):
    """
    TODO: ItemLocationStep
    """
    display_name = "Item Location Step"
    range_start = 1
    range_end = 5
    default = 3

class AdditionalBossRewards(DefaultOnToggle):
    """
    TODO: AdditionalBossRewards
    """
    display_name = "Additional Boss Rewards"

class ScatterPreviousItems(DefaultOnToggle):
    """
    TODO: ScatterPreviousItems
    """
    display_name = "Scatter Previous Items"

class JunkPercentage(Range):
    """
    TODO: JunkPercentage
    """
    display_name = "Junk Percentage"
    range_start = 0
    range_end = 100
    default = 85

class TrapPercentage(Range):
    """
    TODO: TrapPercentage
    """
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 10

class ItemWeights(OptionCounter):
    """Specify the distribution of items that should be placed into the pool.

    If you don't want a specific type of items, set the weight to zero.
    """
    display_name = "Item Weights"
    valid_keys = frozenset({
        "Angel Deal Item",
        "Boss Item",
        "Curse Room Item",
        "Devil Deal Item",
        "Golden Chest Item",
        "Library Item",
        "Planetarium Item",
        "Red Chest Item",
        "Secret Room Item",
        "Shop Item",
        "Treasure Room Item"
    })
    min = 0
    default = {
        "Angel Deal Item": 6,
        "Boss Item": 12,
        "Curse Room Item": 4,
        "Devil Deal Item": 6,
        "Golden Chest Item": 8,
        "Library Item": 1,
        "Planetarium Item": 1,
        "Red Chest Item": 1,
        "Secret Room Item": 8,
        "Shop Item": 15,
        "Treasure Room Item": 15
    }

class RetainItemsPercentage(Range):
    """
    TODO: RetainItemsPercentage
    """
    display_name = "Retain Items percentage"
    range_start = 0
    range_end = 100
    default = 30

class JunkWeights(OptionCounter):
    """Specify the distribution of junk that should be placed into the pool.

    If you don't want a specific type of junk, set the weight to zero.
    """
    display_name = "Junk Weights"
    valid_keys = frozenset({
        "Random Bomb",
        "Random Card",
        "Random Chest",
        "Random Coin",
        "Random Heart",
        "Random Key",
        "Random Pill",
        "Random Trinket"
    })
    min = 0
    default = {
        "Random Bomb": 5,
        "Random Card": 3,
        "Random Chest": 2,
        "Random Coin": 6,
        "Random Heart": 5,
        "Random Key": 5,
        "Random Pill": 3,
        "Random Trinket": 1
    }

class RetainJunkPercentage(Range):
    """
    TODO: RetainJunkPercentage
    """
    display_name = "Retain Junk percentage"
    range_start = 0
    range_end = 100
    default = 10

class TrapWeights(OptionCounter):
    """Specify the distribution of traps that should be placed into the pool.

    If you don't want a specific type of trap, set the weight to zero.
    """
    display_name = "Trap Weights"
    valid_keys = frozenset({
        "Curse Trap",
        "Paralysis Trap",
        "Retro Vision Trap",
        "Teleport Trap",
        "Troll Bomb Trap",
        "Wavy Cap Trap"
    })
    min = 0
    default = {
        "Curse Trap": 20,
        "Paralysis Trap": 20,
        "Retro Vision Trap": 20,
        "Teleport Trap": 20,
        "Troll Bomb Trap": 20,
        "Wavy Cap Trap": 20
    }

class DeathLink(Toggle):
    """
    TODO: DeathLink
    """
    display_name = "Death Link"

class OneUps(Range):
    """
    TODO: OneUps
    """
    display_name = "1-UPs"
    range_start = 0
    range_end = 10
    default = 3

class RetainOneUpsPercentage(Range):
    """
    TODO: RetainOneUpsPercentage
    """
    display_name = "Retain 1-UPs percentage"
    range_start = 0
    range_end = 100
    default = 100
    
@dataclass
class TboiOptions(PerGameCommonOptions):
    goals: Goals
    excluded_areas: ExcludeAreas
    force_lategame: ForceLategame
    win_collects_missed_locations: WinCollectsMissedLocations
    scatter_previous_items: ScatterPreviousItems
    additional_boss_rewards: AdditionalBossRewards
    fortunes_are_hints: FortunesAreHints
    additional_item_locations: AdditionalItemLocations
    item_location_step: ItemLocationStep
    item_weights: ItemWeights
    retain_items_percentage: RetainItemsPercentage
    junk_percentage: JunkPercentage
    junk_weights: JunkWeights
    retain_junk_percentage: RetainJunkPercentage
    trap_percentage: TrapPercentage
    trap_weights: TrapWeights
    deathlink: DeathLink
    one_ups: OneUps
    retain_one_ups_percentage: RetainOneUpsPercentage