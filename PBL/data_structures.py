"""
data_structures.py
Core data structures: Hash Table and Linked List
"""

class Node:
    """Linked List Node for collision handling in hash table"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    """Hash Table implementation for O(1) indexing"""
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * size
        
    def _hash(self, key):
        """Hash function using Python's built-in hash"""
        return hash(str(key)) % self.size
    
    def insert(self, key, value):
        """Insert key-value pair with chaining for collision handling"""
        index = self._hash(key)
        if self.table[index] is None:
            self.table[index] = Node(key, value)
        else:
            current = self.table[index]
            while current:
                if current.key == key:
                    current.value = value
                    return
                if current.next is None:
                    break
                current = current.next
            current.next = Node(key, value)
    
    def get(self, key):
        """Retrieve value by key"""
        index = self._hash(key)
        current = self.table[index]
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None
    
    def delete(self, key):
        """Delete key-value pair"""
        index = self._hash(key)
        current = self.table[index]
        prev = None
        
        while current:
            if current.key == key:
                if prev:
                    prev.next = current.next
                else:
                    self.table[index] = current.next
                return True
            prev = current
            current = current.next
        return False