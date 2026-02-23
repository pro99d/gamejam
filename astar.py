# example realisation of A* algorhitm
class BFS:
    def __init__(self, init_state, target, actions, goal_test) -> None:
        self.frontier = [Node(init_state, None, 0, 0)]
        self.actions = actions 
        self.target = target
        self.visited = set()
        if goal_test:
            self.is_goal = goal_test
    def is_goal(self, node: Node):
        return node.state == self.target

    def repeat(self):
        if not self.frontier:
            raise ValueError("No solution found!")
        node = self.frontier.pop(0)
        if self.is_goal(node):
            return node
        self.visited.add(node)
        for action in self.actions(node):
            if action not in self.visited and action not in self.frontier:
                self.frontier.append(
                    Node(action, node, action, node.path_cost+1)
                )
class Astar(BFS):
    def __init__(self, init_state, target, actions, goal_test, finish) -> None:
        self.finish = finish
        super().__init__(init_state, target, actions, goal_test)
    def h(self, state):
        x, y = map(int, state.split("x"))
        return abs(self.finish[0]-x)+abs(self.finish[1]-y)

    def get_node(self):
        return min(map(lambda x: x.path_cost+self.h(x.state), self.frontier))

    def repeat(self):
        if not self.frontier:
            raise ValueError("No solution found!")
        
        node = self.get_node()
        if self.is_goal(node):
            return node
        self.visited.add(node)
        for action in self.actions(node):
            if action not in self.visited and action not in self.frontier:
                self.frontier.append(
                    Node(action, node, action, node.path_cost+1)
                )

