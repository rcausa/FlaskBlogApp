class Node:
    def __init__(self, data, next_node):
        self.data = data
        self.next_node = next_node

    
class Queue:
    """
    Creates a queue, using a FILO method (first in, last out).
    (Add to the tail, remove from the head).
    """
    def __init__(self):
        # Track the head and tail of the 'linked list'
        self.head = None
        self.tail = None

    def enqueue(self, data):
        if self.tail is None and self.head is None:
            # empty queue
            self.tail = self.head = Node(data, None)
            return 

        self.tail.next_node = Node(data, None) # point previous tail to new data
        self.tail = self.tail.next_node # chenge the variable holding the tail node
        return
    
    def dequeue(self):
        if self.head is None:
            return None
        removed = self.head
        self.head = self.head.next_node
        if self.head is None:
            # if head points to nothing, i.e. head=tail
            self.tail = None
        return removed