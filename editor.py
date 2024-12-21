import sys
import amulet_nbt
import warnings
import pprint
import itertools
from mutf8 import decode_modified_utf8, encode_modified_utf8
warnings.simplefilter("ignore")



DATA_TYPES = [
    (amulet_nbt.ByteTag, amulet_nbt.StringTag, amulet_nbt.IntTag, amulet_nbt.LongTag, 
      amulet_nbt.ShortTag, amulet_nbt.IntArrayTag, amulet_nbt.DoubleTag, amulet_nbt.ByteArrayTag),
    (amulet_nbt.ListTag,),
    (amulet_nbt.CompoundTag, amulet_nbt.NamedTag),
]

INPUT_DATA_TYPES = {i: j for i, j in zip(
    range(len(list(itertools.chain(*DATA_TYPES)))-1), list(itertools.chain(*DATA_TYPES))[:-1]
    )}

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

    def insert_tag(self, location, tagname, tagtype, value):
        return self._insert_tag(self._process_location(location), tagname, tagtype, value)
    
    def create_tag(self, location, tagname, tagtype):
        return self._create_tag(self._process_location(location), tagname, tagtype)
    
    def save(self, filename, compressed=False):
        self.root.save_to(filename, compressed=compressed, string_encoder=encode_modified_utf8)

    def del_tag(self, location):
        return self._del_tag(self._process_location(location))
    
    def _del_tag(self, location):
        tag = self.root
        if self._exists(location):
            locs = []
            for loc in location:
                try:
                    tag[loc]
                except TypeError:
                    loc = int(loc)
                tag = tag[loc]
                locs.append(loc)
        else:
            raise DoesNotExist(repr(location))
        tag = self.root
        for loc in locs[:-1]:  # I found out how to modify nested MutableSequence from an idea gotten from https://yiyan.baidu.com/
            tag = tag[loc]     # Other similar methods below used the same idea
        del tag[locs[-1]]
    
    def _set_tag(self, location, value):
        tag = self.root
        if self._exists(location):
            locs = []
            for loc in location:
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
            tag = tag[loc]
        tag[locs[-1]] = typeof(value)

    def _insert_tag(self, location, tagname, tagtype, value):
        tag = self.root
        if self._exists(location):
            locs = []
            for loc in location:
                try:
                    tag[loc]
                except TypeError:
                    loc = int(loc)
                tag = tag[loc]
                locs.append(loc)
        else:
            raise DoesNotExist(repr(location))
        tag = self.root
        for loc in locs:
            tag = tag[loc]
        tag[tagname] = tagtype(value)

    def _create_tag(self, location, tagname, tagtype):
        tag = self.root
        if self._exists(location):
            locs = []
            for loc in location:
                try:
                    tag[loc]
                except TypeError:
                    loc = int(loc)
                tag = tag[loc]
                locs.append(loc)
        else:
            raise DoesNotExist(repr(location))
        tag = self.root
        for loc in locs:
            tag = tag[loc]
        if tagname is None:
            tag.append(tagtype.create())
        else:
            tag[tagname] = tagtype.create()

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
        newlocation = location + "." + " ".join(command[1:])
    else:
        newlocation = command[1]
    if command[1].startswith("root."):
        newlocation = ".".join(command[1].split(".")[1:])
    if t.exists(newlocation):
        location = newlocation
    else:
        print(f"Unknown location: {newlocation}")
        return -1
    
def exit(command):
    global location
    if location == "":
        sys.exit()
    l = location.split(".")
    try:
        num = int(command[1])
    except IndexError:
        num = 1
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
    if type(tag) in DATA_TYPES[1]:
        all_types = set(type(t).__name__ for t in tag.value)
        print(f"List[{', '.join(all_types)}][0:{len(tag)-1}]")
    elif type(tag) in DATA_TYPES[2]:
        for i, j in tag.value.items():
            if type(j) in DATA_TYPES[0]:
                print("-", i, ":", j.value ,"("+type(j).__name__+")")
            else:
                print("-", i, ":", type(j).__name__)
        if len(tag.value) == 0:
            print("Empty!")
    elif type(tag) in DATA_TYPES[0]:
        print(f"Error: {location[-1]}: is an object")
    else:
        print(f"Error: unknown type {type(tag)}")

if len(sys.argv) != 2:
    import os.path
    print(f"Usage: {os.path.basename(__file__)} filename")
    sys.exit(1)

filename = sys.argv[1]

t = NBTWalker(filename)
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
                if command[1].startswith("root."):
                    exit(["exit", len(command[1].split("."))-1])
                else:
                    exit(["exit", len(command[1].split("."))])

    elif command[0] == "list":
        do_list_tag(command)
    elif command[0] == "set":
        if len(command) == 2:
            # set . value
            t.set_tag(location, command[1])
        elif len(command) == 3:
            # set location value
            if command[1].startswith("root."):
                command[1] = command[1].split(".")[1:]
            else:
                command[1] = location + "." + command[1]
            t.set_tag(command[1], command[2])

    elif command[0] == "del":
        if len(command) == 2:
            if command[1].startswith("root."):
                t.del_tag(command[1][5:])
            else:
                t.del_tag(location + "." + command[1])

    # TODO: add ability to add ListTag and CompoundTag
    elif command[0] == "insert":
        # insert into data structure, too many args, ask for them
        typeof = INPUT_DATA_TYPES[int(input("Type of data: \n"+"\n".join(
            str(i)+": "+j.__name__ for i, j in INPUT_DATA_TYPES.items()) + "\n-> "
            ))]
        if typeof in DATA_TYPES[0]:
            name = input("Tag name: ")
            val = input("Value: ")
            t.insert_tag(location, name, typeof, val)
        else:
            if type(t.get_tag(location)) in DATA_TYPES[2]:
                name = input("Tag name: ")
                t.create_tag(location, name, typeof)
            else:
                name = str(len(t.get_tag(location)))
                t.create_tag(location, None, typeof)

        print("Created tag", location + "." + name)

    # TODO: add as_hex command
    elif command[0] == "as_hex":
        cur = t.get_tag(location)
        if isinstance(cur, amulet_nbt.IntArrayTag):
            print("-".join(hex(i)[2:] for i in cur.py_data))
    
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

    elif command[0] == "help":
        print("""
Commands:
quit - quit immediately
enter [tag] - enter [tag]
exit [layers] - exit [layers] layers or 1 layer (default)
list [location] - list all tags under ([location] | current location)
value [location] - get the value of ([location] | current location)
save filename [compressed=0] - save opened file to "filename" with compression=compressed
del [location] - delete location from file
insert - insert into current location a tag (other values are prompted)
as_hex - represent current value as hexadecimal     
        (Note: this is raw UUID, different from standard Minecraft UUID format, only 1st section is the same)
""")
    else:
        print(f"Unknown command: \'{command[0]}\'")

