from collections import deque

class CacheLine:
    def __init__(self):        
        self.valid = False
        self.tag = None
        self.data = None

class Cache:
    def __init__(self, size=16, block_size=4, associativity=1):
        self.size = size
        self.block_size = block_size
        self.associativity = associativity
        self.num_sets = self.size // (self.block_size * self.associativity)
        self.sets = [deque(maxlen=self.associativity) for _ in range(self.num_sets)]

    def access(self, address, memory):
        set_index = (address // self.block_size) % self.num_sets
        tag = address // (self.block_size * self.num_sets)
        cache_set = self.sets[set_index]
        for line in cache_set:
            if line.valid and line.tag == tag:
                return True
        new_line = CacheLine()
        new_line.valid = True
        new_line.tag = tag
        new_line.data = memory[address]
        cache_set.append(new_line)
        return False