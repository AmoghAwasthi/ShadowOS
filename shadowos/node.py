"""
Distributed node foundation.

Do not implement real networking yet.
First make the local OS simulation stable.

Later this module can use Python sockets to connect
multiple SHADOWOS instances.
"""


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.online = True
        self.process_ids = []

    def add_process(self, pid):
        """Record that a process belongs to this node."""

        self.process_ids.append(pid)

    def fail(self):
        """Simulate node failure."""

        self.online = False
        print(f"[Node] {self.node_id} is OFFLINE.")

    def recover(self):
        """Simulate node recovery."""

        self.online = True
        print(f"[Node] {self.node_id} is ONLINE.")
