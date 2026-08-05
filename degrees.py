class HashMap:
    def __init__(self, size):
        self.size = size
        self.map = [None] * size

    def hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        index = self.hash(key)
        if self.map[index] is None:
            self.map[index] = [(key, value)]
        else:
            for i in range(len(self.map[index])):
                if self.map[index][i][0] == key:
                    self.map[index][i] = (key, value)
                    return
            self.map[index].append((key, value))

    def get(self, key):
        index = self.hash(key)
        if self.map[index] is not None:
            for i in range(len(self.map[index])):
                if self.map[index][i][0] == key:
                    return self.map[index][i][1]
        return -1

    def remove(self, key):
        index = self.hash(key)
        if self.map[index] is not None:
            for i in range(len(self.map[index])):
                if self.map[index][i][0] == key:
                    del self.map[index][i]
                    return
        print("Key not found")

def main():
    hashmap = HashMap(10)
    hashmap.put('apple', 5)
    hashmap.put('banana', 7)
    print(hashmap.get('apple')) # Output: 5
    hashmap.remove('banana')
    print(hashmap.get('banana')) # Output: -1

if __name__ == "__main__":
    main()