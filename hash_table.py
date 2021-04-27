class Node:
    def __init__(self, data=None, next_node=None):
        self.data = data
        self.next_node = next_node

class Data:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class HashTable:
    def __init__(self, table_size):
        self.table_size = table_size
        self.hash_table = [None] * table_size

    def custom_hash(self, key):
        hash_value = 0
        # for char in key string, create a unique value to index by
        for i in key:
            hash_value += ord(i)
            hash_value = (hash_value * ord(i)) % self.table_size
        return hash_value
    
    def add_key_value(self, key, value):
        """ Instead of traversing a list, a hash makes
            it more likely to find an empty place to put your item.
            Otherwise, traverse the list/linked list.

            Store new key,value pair in hash_table.
            Store as new node if doesn't exist, otherwise, add to 
            the linked list at the hash index.
        """
        hashed_key = self.custom_hash(key)
        if self.hash_table[hashed_key] is None:
            self.hash_table[hashed_key] = Node(Data(key, value), None)
        else:
            node = self.hash_table[hashed_key] # 'head' of the linked list
            while node.next_node: # traverse to end
                node = node.next_node
            # new last node has our data, points to None
            node.next_node = Node(Data(key, value), None)

    def get_value(self, key):
        # Get value given a key from hash_table
        hashed_key = self.custom_hash(key)
        if self.hash_table[hashed_key] is not None:
            # if find a linked list of values/one value at this key
            node = self.hash_table[hashed_key]
            if node.next_node is None:
                # if no other values at this key
                return node.data.value
            while node.next_node:
                # otherwise traverse linked list
                # while loop doesn't check condition of last node
                if key == node.data.key:
                    return node.data.value
                node = node.next_node
            if key == node.data.key:
                # check the final node as well
                return node.data.value
        return None

    def print_table(self):
        print("{")
        for i, val in enumerate(self.hash_table):
            if val is not None:
                llist_string = ""
                node = val
                if node.next_node:
                    # if has a next node, i.e. next_node is not None
                    while node.next_node:
                        # add all nodes in linked list
                        llist_string += (
                            str(node.data.key) + " : " + str(node.data.value) + " --> "
                        )
                        node = node.next_node
                    # add last node, pointing to None
                    llist_string += (
                        str(node.data.key) + " : " + str(node.data.value) + " --> None"
                    )
                    print(f"    [{i}] {llist_string}")
                else:
                    print(f"    [{i}] {val.data.key} : {val.data.value}")
            else:
                print(f"    [{i}] {val}")
        print("}")
            

# ht = HashTable(4)
# ht.add_key_value('hi', 'there')
# ht.add_key_value('hi', 'there')
# ht.add_key_value('hi', 'there')
# ht.add_key_value('fflo', 'there')
# ht.print_table()
