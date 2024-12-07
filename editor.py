import sys
import amulet_nbt
import warnings
import pprint
from mutf8 import decode_modified_utf8, encode_modified_utf8
warnings.simplefilter("ignore")

class Item():
    def __init__(self, count: int, item_id: str, tags: dict):
        self.count = count
        self.item_id = item_id
        self.tags = {name: obj for name, obj in tags.items()}
        self.enchantments = None
        self.parse_enchantments()
        
    @classmethod
    def from_nbt_tag(cls, tag: amulet_nbt.CompoundTag):
        try:
            tags = dict(tag.get_compound("tag"))
        except:
            try:
                tags = dict(tag.get_compound("Stack").get_compound("tag"))
            except:
                tags = dict()
        if "BlockEntityTag" in tags.keys():
            try:
                bet = list(tags["BlockEntityTag"].get_list("Items"))
            except: pass
            else:
                return ShulkerBox(count=tag.get_byte("Count").py_int,
                item_id=tag.get_string("id").py_str,
                tags=tags, inv=bet)
        if "Inventory" in tags.keys() and tag.get_string("id").py_str.endswith("backpack"):
            bet = list(tags["Inventory"])
            return Backpack(count=tag.get_byte("Count").py_int,
            item_id=tag.get_string("id").py_str,
            tags=tags, inv=bet)
        try:
            stack = tag.get_compound("Stack")
        except KeyError:
            pass
        else:
            return cls(
                count=tag.get_compound("Stack").get_byte("Count").py_int,
                item_id=tag.get_compound("Stack").get_string("id").py_str,
                tags=tags
            )
        return cls(
            count=tag.get_byte("Count").py_int,
            item_id=tag.get_string("id").py_str,
            tags=tags
        )

    def parse_enchantments(self):
        if "Enchantments" in self.tags.keys() or "StoredEnchantments" in self.tags.keys():
            self.enchantments = dict()
        else:
            return
        if "Enchantments" in self.tags.keys():
            for ench in self.tags["Enchantments"].py_list:
                self.enchantments[ench.get_string("id").py_str] = ench.get_short("lvl").py_int
        if "StoredEnchantments" in self.tags.keys():
            for ench in self.tags["StoredEnchantments"].py_list:
                self.enchantments[ench.get_string("id").py_str] = ench.get_short("lvl").py_int

    def __repr__(self):
        return f"{type(self).__name__}(\"{self.item_id}\") x {self.count}"

class InventoryItem(Item):
    def set_slot(self, slot):
        self.slot = slot

class Inventory:
    _slots_ = [
        100, 101, 102, 103
    ] + list(range(32))

    def __init__(self, inv: list):
        self.inv = {}
        for i in inv:
            try:
                slot = i.get_byte("Slot").py_int
            except:
                slot = i.get_int("Slot").py_int
            self.inv[slot] = InventoryItem.from_nbt_tag(i)
            self.inv[slot].set_slot(slot)


    def get_item_by_slot(self, slot):
        return self.inv[slot]

    @classmethod
    def load_from_tag(cls, tag: amulet_nbt.ListTag):
        return cls(list(tag))

    def __repr__(self):
        s = type(self).__name__ + f"(\n\t"
        for b, i in self.inv.items():
            s += str(b) + ": " + str(i) + "\n\t"
        s += ")"
        return s

class EnderChest(Inventory):
    _slots_ = list(range(28))

class ShulkerBox(Inventory, InventoryItem):
    _slots_ = list(range(28))
    def __init__(self, count, item_id, tags, inv):
        Inventory.__init__(self, inv)
        InventoryItem.__init__(self, count, item_id, tags)

class Backpack(ShulkerBox):
    _slots_ = []


class Coord():
    def __init__(self, x, y, z, dimension):
        self.x = x
        self.y = y
        self.z = z
        self.demension = dimension
        self.d = dimension

    def __repr__(self):
        return f"Coord({self.x}, {self.y}, {self.z}, {repr(self.d)})"

class Player():
    def __init__(self, filename="player.dat"):
        data = amulet_nbt.load(
            filename,
            string_decoder=decode_modified_utf8
        )
        self.data = dict(data.compound)

        self.pos = Coord(
            self.data["Pos"][0].py_float, 
            self.data["Pos"][1].py_float, 
            self.data["Pos"][2].py_float, 
            self.data["Dimension"].py_str
            )
        self.health = int(self.data["Health"].py_float)
        self.hunger = self.data["foodLevel"].py_int
        self.saturation = self.data["foodSaturationLevel"].py_float
        self.inventory = Inventory.load_from_tag(self.data["Inventory"])
        self.ender_chest = EnderChest.load_from_tag(self.data["EnderItems"])

    def __repr__(self):
        return f"Player(pos={self.pos}, {self.health}/20HP, {self.hunger}+{self.saturation}/20SATU, inv=\n{self.inventory},\nender_chest=\n{self.ender_chest})"


class NBT:
    def __init__(self, tag: amulet_nbt.AnyNBT):
        self.tag = tag
        self.typeof = type(tag)

    def save(self, filename):
        self.tag.save_to(filename, compressed=False, string_encoder=encode_modified_utf8)

class DataTag(NBT):
    def __init__(self, tag: amulet_nbt.AnyNBT):
        super().__init__(tag)

    @property
    def value(self):
        return self.tag.py_data
    
    @value.setter
    def value(self, value):
        self.tag = self.typeof(value)

    def __repr__(self):
        return self.value
    
class RootTag(NBT):
    def __init__(self, tag: amulet_nbt.NamedTag):
        super().__init__(tag)
    
    @property
    def value(self):
        return self.tag.compound
    

class ListTag(DataTag):
    @property
    def value(self):
        return self.tag.py_data
    
    @value.setter
    def value(self, value):
        self.tag = self.typeof(value)
    
    def __getitem__(self, i):
        return self.tag[i]
    
    def get(self, i=None):
        if i is None:
            return self.tag
        return self.tag[i]
    
    def set(self, i, val):
        v = self.value
        v[i] = val
        self.value = v

    def __repr__(self):
        return repr(self.value)

class CompoundTag(DataTag):
    @property
    def value(self):
        return self.tag.py_data
    
    @value.setter
    def value(self, value):
        self.tag = self.typeof(value)
    
    def __getitem__(self, i):
        return self.tag[i]
    
    def get(self, i=None):
        if i is None:
            return self.tag
        return self.tag[i]
    
    def set(self, i, val):
        v = self.value
        v[i] = val
        self.value = v

    def __repr__(self):
        return repr(dict(self.value))

class IntArrayTag(DataTag):
    @property
    def value(self):
        return list(self.tag.py_data)
    
    def as_hex(self):
        return "-".join(hex(i)[2:] for i in self.value)
    
    @value.setter
    def value(self, value):
        self.tag = self.typeof(value)

    def __repr__(self):
        return self.as_hex()

DATA_TYPES = [
    ([amulet_nbt.ByteTag, amulet_nbt.StringTag, amulet_nbt.IntTag, 
      amulet_nbt.ShortTag, amulet_nbt.IntArrayTag, amulet_nbt.DoubleTag], DataTag),
    ([amulet_nbt.ListTag], ListTag),
    ([amulet_nbt.CompoundTag, amulet_nbt.NamedTag], CompoundTag),
]

class DoesNotExist(Exception): 
    pass


class NBTWalker:
    def __init__(self, filename="player.dat"):
        self.root = amulet_nbt.load(
            filename,
            string_decoder=decode_modified_utf8
        )
        self.filename = filename

    def _process_location(self, location: str):
        location = location.split(".")
        if location[0] == "":
            location = location[1:]
        return [1] + location
        
    def exists(self, location):
        return self._exists(self._process_location(location))
    
    def get_tag(self, location):
        return self._get_tag(self._process_location(location))
    
    def set_tag(self, location, value):
        return self._set_tag(self._process_location(location), value)
    
    def save(self, filename, compressed=False):
        self.root.save_to(filename, compressed=compressed, string_encoder=encode_modified_utf8)
    
    def _set_tag(self, location, value):
        tag = self.root
        if self._exists(location):
            locs = []
            for loc in location:
                print(loc)
                try:
                    tag[loc]
                except TypeError:
                    loc = int(loc)
                tag = tag[loc]
                locs.append(loc)
        else:
            raise DoesNotExist(repr(location))
        typeof = type(tag)
        tag = self.root
        for loc in locs[:-1]:
            print(loc)
            tag = tag[loc]
        tag[locs[-1]] = typeof(value)
        
    def _get_tag(self, location):
        tag = self.root
        if self._exists(location):
            for loc in location:
                try:
                    tag[loc]
                except TypeError:
                    loc = int(loc)
                tag = tag[loc]
            return tag
        else:
            raise DoesNotExist(repr(location))


    def _exists(self, location):
        tag = self.root
        for loc in location:
            try:
                tag[loc]
            except TypeError:
                try:
                    loc = int(loc)
                    tag[loc]
                except:
                    return False
            except:
                return False
            tag = tag[loc]
        return True

def enter(command):
    global location
    if location:
        newlocation = location + "." + command[1]
    else:
        newlocation = command[1]
    if t.exists(location + "." + command[1]):
        location = newlocation
    else:
        print(f"Unknown location: {newlocation}")
        return -1
    
def exit(command):
    global location
    if location == "":
        sys.exit()
    l = location.split(".")
    print(l)
    try:
        num = int(command[1])
    except IndexError:
        num = 0
    except Exception as e:
        print(type(e), e.args[0])
        return -1
    if num > len(l):
        sys.exit()
    l = l[:-num]
    location = ".".join(l)

def do_list_tag(command):
    global location
    tag = t.get_tag(location)
    if type(tag) in DATA_TYPES[1][0]:
        print(f"List[{type(tag.value[0]).__name__}]")
    elif type(tag) in DATA_TYPES[2][0]:
        for i, j in tag.value.items():
            if type(j) in DATA_TYPES[0][0]:
                print("-", i, ":", j.value ,"("+type(j).__name__+")")
            else:
                print("-", i, ":", type(j).__name__)
    elif type(tag) == DataTag:
        print(f"Error: {location[-1]}: is an object")
    else:
        print(f"Error: unknown type {type(tag)}")

t = NBTWalker("player.nbt")

location = ""

while True:
    command = input(f"({t.filename}) "+location+"$ ").split()
    if not command:
        continue
    command[0] = command[0].lower()
    if command[0].startswith("quit"):
        break
    if command[0] == "enter":
        enter(command)
    elif command[0] == "exit":
        exit(command)
    elif command[0] == "value":
        if len(command) == 1:
            print(pprint.pformat(t.get_tag(location).value))
        elif len(command) == 2:
            if enter(["enter", command[1]]) != -1:
                print(pprint.pformat(t.get_tag(location).value))
                print(location, len(command[1].split(".")))
                exit(["exit", len(command[1].split("."))])

    elif command[0] == "list":
        do_list_tag(command)
    elif command[0] == "set":
        pass
    elif command[0] == "save":
        if len(command) == 2:
            t.save(command[1])
        elif len(command) == 3:
            try:   
                t.save(command[1], bool(int(command[2])))
            except Exception as e:
                print(type(e), e.args[0])
        else:
            print("Usage: save `filename` [compressed=0]")
    else:
        print(f"Unknown command: \'{command[0]}\'")

