from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BigObject():
    Name: str = ""
    DisplayName: str = ""
    Description: str = ""
    Price: Optional[int] = 0
    Fragility: Optional[int] = 0
    CanBePlacedIndoors: Optional[bool] = True
    CanBePlacedOutdoors: Optional[bool] = False
    IsLamp: Optional[bool] = False
    Texture: Optional[str] = ""
    SpriteIndex: Optional[int] = 0
    ContextTags: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "SpriteIndex"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
            elif k == "CanBePlacedIndoors" and not v:
                outDict[k] == v
        return outDict


@dataclass
class Buff():
    Duration: int = 0
    Id: str = ""
    FarmingLevel: Optional[int] = 0
    FishingLevel: Optional[int] = 0
    ForagingLevel: Optional[int] = 0
    LuckLevel: Optional[int] = 0
    MiningLevel: Optional[int] = 0
    Attack: Optional[int] = 0
    Defense: Optional[int] = 0
    MagnetRadius: Optional[int] = 0
    MaxStamina: Optional[int] = 0

    def to_dict(self):
        outDict = {"Duration": 0,
                   "IsDebuff": False,
                   "CustomAttributes": {}}
        for k, v in self.__dict__.items():
            if k in ["Id", "Duration"]:
                outDict[k] = v
            else:
                if v:
                    outDict["CustomAttributes"][k] = v
                if v < 0:
                    outDict["IsDebuff"] = True
        return outDict


@dataclass
class Crop():
    Seasons: list = field(default_factory=lambda: [])
    DaysInPhase: list = field(default_factory=lambda: [])
    HarvestItemID: str = ""
    Texture: str = ""
    SpriteIndex: int = 0
    RegrowDays: Optional[int] = -1
    IsRaised: Optional[bool] = False
    IsPaddyCrop: Optional[bool] = False
    NeedsWatering: Optional[bool] = True
    HarvestMethod: Optional[str] = "Grab"
    HarvestMinStack: Optional[int] = 1
    HarvestMaxStack: Optional[int] = 1
    HarvestMinQuality: Optional[int] = 0
    HarvestMaxQuality: Optional[int] = 0
    HarvestMaxIncreasePerFarmingLevel: Optional[int] = 0
    ExtraHarvestChance: Optional[int] = 0
    TintColors: Optional[list] = field(default_factory=lambda: [])
    CountForMonoculture: Optional[bool] = False
    CountForPolyculture: Optional[bool] = False
    PlantableLocationRules: Optional[dict] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Seasons", "DaysInPhase", "HarvestItemID", "Texture", "SpriteIndex"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class FruitTree():
    DisplayName: str = ""
    Seasons: list = field(default_factory=lambda: [])
    Fruit: list = field(default_factory=lambda: [])
    Texture: str = ""
    TextureSpriteRow: int = 0
    PlantableLocationRule: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["DisplayName", "Seasons", "Fruit", "Texture",
                         "TextureSpriteRow"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class MeleeWeapon():
    Name: str = ""
    DisplayName: str = ""
    Description: str = ""
    Type: int = 0
    Texture: str = ""
    SpriteIndex: int = 0
    MinDamage: int = 0
    MaxDamage: int = 0
    CanBeLostOnDeath: bool = True
    Knockback: Optional[float] = 0.0
    Speed: Optional[int] = 0
    Precision: Optional[int] = 0
    Defense: Optional[int] = 0
    AreaOfEffect: Optional[int] = 0
    CritChance: Optional[float] = 0.0
    CritMultiplier: Optional[float] = 0.0
    MineBaseLevel: Optional[int] = -1
    MineMinLevel: Optional[int] = -1
    Projectiles: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "Type", "Texture",
                         "SpriteIndex", "MinDamage", "MaxDamage", "CanBeLostOnDeath"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class SVObject():
    Name: str = ""
    DisplayName: str = ""
    Description: str = ""
    Type: str = ""
    Category: int = 0
    Price: int = 0
    Texture: str = ""
    SpriteIndex: int = 0
    Edibility: Optional[int] = -1
    IsDrink: Optional[bool] = False
    GeodeDrops: Optional[list] = field(default_factory=lambda: [])
    Buffs: Optional[list] = field(default_factory=lambda: [])
    ArtifactSpotChances: Optional[dict] = field(default_factory=lambda: {})
    ContextTags: Optional[list] = field(default_factory=lambda: [])
    ExcludeFromRandomSale: Optional[bool] = False
    ExcludeFromFishingCollection: Optional[bool] = False
    ExcludeFromShippingCollection: Optional[bool] = False

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "Type",
                         "Category", "Price", "Texture", "SpriteIndex"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class Rule():
    ProducerQualifiedItemId: str = ""
    InputIdentifier: str = ""
    OutputIdentifier: str = ""
    OutputTranslationKey: str = ""
    MinutesUntilReady: int = 0
    Sounds: list = field(default_factory=lambda: [])
    AdditionalFuel: Optional[dict] = field(default_factory=lambda: {})
    AdditionalOutputs: Optional[list] = field(default_factory=lambda: [])
    DelayedSounds: Optional[list] = field(default_factory=lambda: [])
    ExcludeIdentifiers: Optional[list] = field(default_factory=lambda: [])
    FuelIdentifier: Optional[str] = ""
    FuelStack: Optional[int] = 0
    InputPriceBased: Optional[bool] = False
    InputStack: Optional[int] = 1
    KeepInputQuality: Optional[bool] = False
    OutputPriceMultiplier: Optional[float] = 1.0
    OutputQuality: Optional[int] = 0
    OutputStack: Optional[int] = 1
    OutputMaxStack: Optional[int] = 1
    PlacingAnimation: Optional[str] = ""
    PlacingAnimationColorName: Optional[str] = "White"

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["ProducerQualifiedItemId", "InputIdentifier",
                         "OutputIdentifier", "OutputTranslationKey"
                         "MinutesUntilReady", "Sounds"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or (k not in ["OutputPriceMultiplier", "PlacingAnimationColorName", "OutputStack", "InputStack", "OutputMaxStack"] and v) or (k == "OutputPriceMultiplier" and v != 1.0) or (k == "PlacingAnimationColorName" and v != "White") or (k in ["InputStack", "OutputStack", "OutputMaxStack"] and v != 1):
                outDict[k] = v
        return outDict


@dataclass
class PConfig():
    """ProducersConfig for PFM"""
    ProducerQualifiedItemId: str = ""
    AlternateFrameProducing: bool = False
    AlternateFrameWhenReady: bool = False
    DisableBouncingAnimationWhileWorking: Optional[bool] = False
    LightSource: Optional[dict] = field(default_factory=lambda: {})
    NoInputStartMode: Optional[str] = None
    ProducingAnimation: Optional[dict] = field(default_factory=lambda: {})
    ReadyAnimation: Optional[dict] = field(default_factory=lambda: {})

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["ProducerQualifiedItemId", "AlternateFrameProducing",
                         "AlternateFrameWhenReady"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class Shop():
    Items: list = field(default_factory=lambda: [])
    SalableItemTags: Optional[list] = field(default_factory=lambda: [])
    Owners: Optional[list] = field(default_factory=lambda: [])
    Currency: Optional[int] = 0  # 0: Money, 1: Star tokens, 2: Qi coins, 4: Qi Gems
    ApplyProfitMargins: Optional[bool] = None
    StackSizeVisibility: Optional[str] = ""  # Show, Hide, ShowIfMultiple
    OpenSound: Optional[str] = ""
    PurchaseSound: Optional[str] = ""
    purchaseRepeatSound: Optional[str] = ""
    PriceModifiers: Optional[list] = field(default_factory=lambda: [])
    PriceModifierMode: Optional[str] = ""
    VisualTheme: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        for k, v in self.__dict__.items():
            if k == "Items" or (k == "ApplyProfitMargins" and v is not None) or (k not in ["Items", "ApplyProfitMargins"] and v):
                outDict[k] = v
        return outDict


@dataclass
class Inventory():
    ID: Optional[str] = ""
    ItemId: Optional[str] = ""
    RandomItemId: Optional[list] = field(default_factory=lambda: [])
    Condition: Optional[str] = ""
    PerItemCondition: Optional[str] = ""
    MaxItems: Optional[int] = 0
    IsRecipe: Optional[bool] = False
    Quality: Optional[int] = 0
    MinStack: Optional[int] = 0
    MaxStack: Optional[int] = 0
    Price: Optional[int] = 0
    TradeItemId: Optional[str] = ""  # Qualified or Unqualified
    TradeItemAmount: Optional[int] = 0
    ApplyProfitMargins: Optional[bool] = None
    IgnoreShopPriceModifiers: Optional[bool] = False
    AvailableStockModifiers: Optional[list] = field(default_factory=lambda: [])
    OptionalPriceModifiers: Optional[list] = field(default_factory=lambda: [])
    AvailableStockModifierMode: Optional[str] = ""
    PriceModifiers: Optional[list] = field(default_factory=lambda: [])
    PriceModifierMode: Optional[str] = ""
    AvoidRepeat: Optional[bool] = False
    UseObjectDataPrice: Optional[bool] = False
    AvailableStock: Optional[int] = 0
    AvailableStockLimit: Optional[str] = ""  # Global, Player, None (str)
    PerItemCondition: Optional[str] = ""
    ActionsOnPurchase: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        requiredFields = ["Id", "ItemId", "RandomItemId"]
        for k, v in self.__dict__.items():
            if v:
                outDict[k] = v
        if not any(x in outDict for x in requiredFields):
            raise Exception("Error with creating Inventory Item: No ID specified.")
        else:
            return outDict


@dataclass
class OreNode():
    SpriteIndex: int = 0
    Texture: str = ""
    Health: int = 0
    Sound: str = ""
    ItemDropped: str = ""
    Tool: str = ""
    Exp: int = 0
    Skill: str = "mining"
    MineSpawns: list = field(default_factory=lambda: [])
    ExtraItems: Optional[list] = field(default_factory=lambda: [])
    MinDrops: Optional[int] = 1
    MaxDrops: Optional[int] = 1
    Debris: Optional[str] = ""
    BreakingSound: Optional[str] = ""
    MinToolLevel: Optional[int] = ""

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["SpriteIndex", "Texture", "Health", "Sound",
                         "ItemDropped", "Tool", "MinDrops", "MaxDrops",
                         "MineSpawns", "Exp", "Skill"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class CPRule():
    """Output Rules for a Content Patcher Machine"""
    Id: str = ""
    Triggers: list = field(default_factory=lambda: [])
    UseFirstValidOutput: bool = False
    OutputItem: list = field(default_factory=lambda: [])
    MinutesUntilReady: int = -1
    DaysUntilReady: int = -1
    RecalculateOnCollect: bool = False

    def to_dict(self):
        outDict = {}
        for k, v in self.__dict__.items():
            outDict[k] = v
        return outDict
