# NBTEditor

## Video Demo: [link]()

## Description

This is a Minecraft NBT Formatted File Editor based on [amulet_nbt](https://pypi.org/project/amulet-nbt/).
This editor accepts all NBT files such as files in `.minecraft/saves/world/playerdata`.

What is NBT (Named Binary Tag) Format? [See This](https://minecraft.fandom.com/wiki/NBT_format)

[Github Repo]{}

## How to use

### Install

Run the following command:
`pip3 install -r requirements.txt`

### Running

Run `editor.py` like this:
`python3 editor.py [filename]`

Example:
`python3 editor.py test-player.dat`

After running the command, you will enter a shell-like environment; Here, you can play around and read/modify the file. To start, type `list` into the shell.

#### Commands

`quit` - quit immediately

`enter new-location` - change current location to *old-location+new-location*

`exit [layers]` - exit *layers* layers or 1 layer (default)

`list [location]` - list all tags under *current-location(default) or location*

`value` [location] - get the value of ([location] | current location)

`save filename [compressed=0]` - save opened file to "filename" with compression=compressed (1 or 0)

`del location` - delete location from file

`insert` - insert into current location a tag (other values are prompted)

`as_hex` - represent current value as hexadecimal (Only for IntArrayTag type).
(Note: this is raw UUID, different from standard Minecraft UUID format, only 1st section is the same)

## How it works

I created a class, `editor.NBTWalker` to process the NBT file. Upon creation it only reads the file and saves it to memory. There are 7 functions available.

1. `NBTWalker.exists(self, location)`: returns whether the tag *location* exists.
2. `NBTWalker.get_tag(self, location)`: returns the `amulet_nbt.AbstractBaseTag` tag (meant to be read-only) at *location*. Raises `DoesNotExist` if location does not exist.
3. `NBTWalker.set_tag(self, location, value)`: Sets [location] to be value *only if location exists*. Raises `DoesNotExist` if location does not exist.
4. `NBTWalker.insert_tag(self, location. tagname, tagtype, value)`: Inserts a tag with name *tagname* at location *location* with the type *tagtype* and value *value*. Note: *tagtype* can only be one of `DATA_TYPES[0]`, that is, not a `MutableSequence`.
5. `NBTWalker.create_tag(self, location, tagname, tagtype)`: Same as `insert_tag`, but creates only empty `MutableSequence`s.
6. `NBTWalker.del_tag(self, location)`: Deletes tag at location *location*.
7. `NBTWalker.save(self, filename, compressed=False)`: Saves the whole file to *filename* with compression enabled/disabled.

Variable `location`: Locations are accepted as a string of indexes separated by `.`.

Example: `Inventory.0.tags` (processed as `rootTag["Inventory"][0]["tags"]`)

`Inventory` -> index of CompoundTag under root

`0` -> index of Inventory (Number-based list indexes work the same way as the dict-like CompoundTag)

`tags` -> index of Inventory.0

### Locations

In the shell, Locations start with `root` if it's a absolute position.

In code, the function-accepted locations don't start with `root` and starts with the first tag under the root tag (with type `NamedTag`), for example `location = "EnderChest.0.id"`.

## Development process

### V1

First, I started out with a prototype that could only process the data, that is, no writing.
See commit `9d5be12`.

### V2

Next, I tried using a `TagWalker` class to go through the data, only to find out that it's almost impossible to modify anything. I was still using my own data structures as a wrapper and through multiple layers of data structures it was impossible to change a `amulet_nbt.AbstractBaseTag` and having its change mirrored on the base `amulet_nbt.NamedTag` object. I also determined the usage of this program as a shell-like script.

### V3

Version 3 was implemented without my own layer of data structures, so I'm manipulating the `amulet_nbt.AbstractBaseTag` objects directly. I added a few more commands to the shell: mainly `insert` and `del`.
