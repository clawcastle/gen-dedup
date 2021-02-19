class Nodes:
    nodes = ["storagenode_1:3001", "storagenode_2:3002", "storagenode_3:3003"]
    count = 1

    def get_next_storage_node(self):
        index = (self.count % len(self.nodes)) - 1
        self.count += 1
        return self.nodes[index]