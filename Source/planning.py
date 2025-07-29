"""
Planning Module for Wumpus World Agent
Implements A* search algorithm for optimal pathfinding considering risk and utility.
"""

import heapq
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass, field
from environment import Direction, Action
from knowledge_base import KnowledgeBase
import math

@dataclass
class Node:
    """Node for A* search"""
    position: Tuple[int, int]
    direction: Direction
    g_cost: float = 0.0  # Cost from start
    h_cost: float = 0.0  # Heuristic cost to goal
    f_cost: float = field(init=False)  # Total cost
    parent: Optional['Node'] = None
    action: Optional[Action] = None
    
    def __post_init__(self):
        self.f_cost = self.g_cost + self.h_cost
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class WumpusPlanner:
    """A* based planner for Wumpus World navigation"""
    
    def __init__(self, world_size: int, kb: KnowledgeBase):
        self.world_size = world_size
        self.kb = kb
        
        # Risk parameters
        self.safe_cost = 1.0
        self.unknown_cost = 10.0  # Higher cost for unknown cells
        self.dangerous_cost = 1000.0  # Very high cost for dangerous cells
        self.turn_cost = 1.0
        
    def _is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within world boundaries"""
        x, y = pos
        return 0 <= x < self.world_size and 0 <= y < self.world_size
    
    def _get_adjacent_positions(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid adjacent positions"""
        x, y = pos
        adjacent = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_pos = (x + dx, y + dy)
            if self._is_valid_position(new_pos):
                adjacent.append(new_pos)
        return adjacent
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _euclidean_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def _get_cell_risk_cost(self, pos: Tuple[int, int]) -> float:
        """Get the risk-adjusted cost of moving to a cell"""
        safe_cells = self.kb.infer_safe_cells()
        dangerous_cells = self.kb.infer_dangerous_cells()
        
        if pos in safe_cells:
            return self.safe_cost
        elif pos in dangerous_cells:
            return self.dangerous_cost
        else:
            # Unknown cell - moderate risk
            return self.unknown_cost
    
    def _get_direction_to_position(self, from_pos: Tuple[int, int], 
                                 to_pos: Tuple[int, int]) -> Optional[Direction]:
        """Get direction needed to move from one position to adjacent position"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        if (dx, dy) == (0, 1):
            return Direction.NORTH
        elif (dx, dy) == (1, 0):
            return Direction.EAST
        elif (dx, dy) == (0, -1):
            return Direction.SOUTH
        elif (dx, dy) == (-1, 0):
            return Direction.WEST
        else:
            return None  # Not adjacent
    
    def _get_actions_to_face_direction(self, current_dir: Direction, 
                                     target_dir: Direction) -> List[Action]:
        """Get actions needed to face target direction"""
        if current_dir == target_dir:
            return []
        
        directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        current_idx = directions.index(current_dir)
        target_idx = directions.index(target_dir)
        
        # Calculate the shortest rotation
        diff = (target_idx - current_idx) % 4
        
        if diff == 1:  # Turn right once
            return [Action.TURN_RIGHT]
        elif diff == 2:  # Turn around (2 rights or 2 lefts)
            return [Action.TURN_RIGHT, Action.TURN_RIGHT]
        elif diff == 3:  # Turn left once (equivalent to 3 rights)
            return [Action.TURN_LEFT]
        else:
            return []
    
    def _reconstruct_path(self, node: Node) -> List[Action]:
        """Reconstruct action sequence from goal node"""
        actions = []
        current = node
        
        while current.parent is not None:
            if current.action:
                actions.append(current.action)
            current = current.parent
        
        actions.reverse()
        return actions
    
    def find_path_to_goal(self, start_pos: Tuple[int, int], start_dir: Direction,
                         goals: List[Tuple[int, int]], 
                         avoid_unknown: bool = False) -> Optional[List[Action]]:
        """
        Find optimal path to any of the goal positions using A*
        
        Args:
            start_pos: Starting position
            start_dir: Starting direction
            goals: List of goal positions
            avoid_unknown: If True, heavily penalize unknown cells
        
        Returns:
            List of actions to reach goal, or None if no path found
        """
        if not goals:
            return None
        
        # Adjust costs based on risk preference
        if avoid_unknown:
            self.unknown_cost = 50.0
        else:
            self.unknown_cost = 10.0
        
        open_set = []
        closed_set = set()
        
        # Create start node
        start_node = Node(
            position=start_pos,
            direction=start_dir,
            g_cost=0.0,
            h_cost=min(self._manhattan_distance(start_pos, goal) for goal in goals)
        )
        
        heapq.heappush(open_set, start_node)
        
        # Track best g_cost for each (position, direction) pair
        best_g_cost = {(start_pos, start_dir): 0.0}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            # Check if we reached a goal
            if current.position in goals:
                return self._reconstruct_path(current)
            
            state_key = (current.position, current.direction)
            if state_key in closed_set:
                continue
            
            closed_set.add(state_key)
            
            # Generate successor states
            successors = self._get_successors(current)
            
            for successor in successors:
                successor_key = (successor.position, successor.direction)
                
                if successor_key in closed_set:
                    continue
                
                # Check if this path to successor is better
                if (successor_key not in best_g_cost or 
                    successor.g_cost < best_g_cost[successor_key]):
                    
                    best_g_cost[successor_key] = successor.g_cost
                    successor.h_cost = min(self._manhattan_distance(successor.position, goal) 
                                         for goal in goals)
                    successor.f_cost = successor.g_cost + successor.h_cost
                    heapq.heappush(open_set, successor)
        
        return None  # No path found
    
    def _get_successors(self, node: Node) -> List[Node]:
        """Generate successor nodes for A* search"""
        successors = []
        
        # Action 1: Move forward
        forward_pos = self._get_forward_position(node.position, node.direction)
        if forward_pos and self._is_valid_position(forward_pos):
            move_cost = self._get_cell_risk_cost(forward_pos)
            successor = Node(
                position=forward_pos,
                direction=node.direction,
                g_cost=node.g_cost + move_cost,
                parent=node,
                action=Action.MOVE_FORWARD
            )
            successors.append(successor)
        
        # Action 2: Turn left
        new_direction = self._turn_left(node.direction)
        successor = Node(
            position=node.position,
            direction=new_direction,
            g_cost=node.g_cost + self.turn_cost,
            parent=node,
            action=Action.TURN_LEFT
        )
        successors.append(successor)
        
        # Action 3: Turn right
        new_direction = self._turn_right(node.direction)
        successor = Node(
            position=node.position,
            direction=new_direction,
            g_cost=node.g_cost + self.turn_cost,
            parent=node,
            action=Action.TURN_RIGHT
        )
        successors.append(successor)
        
        return successors
    
    def _get_forward_position(self, pos: Tuple[int, int], direction: Direction) -> Optional[Tuple[int, int]]:
        """Get position after moving forward in given direction"""
        x, y = pos
        dx, dy = direction.value
        new_pos = (x + dx, y + dy)
        
        if self._is_valid_position(new_pos):
            return new_pos
        return None
    
    def _turn_left(self, direction: Direction) -> Direction:
        """Get direction after turning left"""
        directions = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]
        current_index = directions.index(direction)
        return directions[(current_index + 1) % 4]
    
    def _turn_right(self, direction: Direction) -> Direction:
        """Get direction after turning right"""
        directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        current_index = directions.index(direction)
        return directions[(current_index + 1) % 4]
    
    def find_safe_exploration_targets(self, current_pos: Tuple[int, int], 
                                    visited: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Find safe unvisited cells for exploration"""
        safe_cells = self.kb.infer_safe_cells()
        targets = []
        
        for cell in safe_cells:
            if cell not in visited:
                targets.append(cell)
        
        # Sort by distance from current position
        targets.sort(key=lambda pos: self._manhattan_distance(current_pos, pos))
        return targets
    
    def find_unknown_exploration_targets(self, current_pos: Tuple[int, int],
                                       visited: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Find unknown cells adjacent to safe areas for cautious exploration"""
        safe_cells = self.kb.infer_safe_cells()
        dangerous_cells = self.kb.infer_dangerous_cells()
        targets = []
        
        # Find unknown cells adjacent to safe cells
        for safe_cell in safe_cells:
            for adj_pos in self._get_adjacent_positions(safe_cell):
                if (adj_pos not in visited and 
                    adj_pos not in safe_cells and 
                    adj_pos not in dangerous_cells and
                    adj_pos not in targets):
                    targets.append(adj_pos)
        
        # Sort by distance from current position
        targets.sort(key=lambda pos: self._manhattan_distance(current_pos, pos))
        return targets
    
    def calculate_shooting_utility(self, agent_pos: Tuple[int, int], 
                                 agent_dir: Direction,
                                 wumpus_positions: Set[Tuple[int, int]]) -> float:
        """Calculate utility of shooting in current direction"""
        # Trace shooting path
        x, y = agent_pos
        dx, dy = agent_dir.value
        
        utility = 0.0
        shooting_cost = 10.0  # Cost of shooting
        
        while True:
            x += dx
            y += dy
            if not self._is_valid_position((x, y)):
                break  # Arrow hits wall
            
            if (x, y) in wumpus_positions:
                # Hit a wumpus - positive utility
                utility += 100.0  # Benefit of killing wumpus
                break
        
        return utility - shooting_cost
    
    def plan_gold_retrieval(self, current_pos: Tuple[int, int], 
                          current_dir: Direction,
                          gold_pos: Tuple[int, int]) -> Optional[List[Action]]:
        """Plan path to retrieve gold and return to start"""
        # First, plan path to gold
        path_to_gold = self.find_path_to_goal(current_pos, current_dir, [gold_pos])
        
        if path_to_gold is None:
            return None
        
        # Then plan path from gold back to start
        # Simulate final position and direction after reaching gold
        final_pos = gold_pos
        final_dir = self._simulate_final_direction(current_pos, current_dir, path_to_gold)
        
        path_to_start = self.find_path_to_goal(final_pos, final_dir, [(0, 0)])
        
        if path_to_start is None:
            return None
        
        # Combine paths with grab action
        complete_plan = path_to_gold + [Action.GRAB] + path_to_start + [Action.CLIMB_OUT]
        return complete_plan
    
    def _simulate_final_direction(self, start_pos: Tuple[int, int], 
                                start_dir: Direction, 
                                actions: List[Action]) -> Direction:
        """Simulate final direction after executing action sequence"""
        current_dir = start_dir
        
        for action in actions:
            if action == Action.TURN_LEFT:
                current_dir = self._turn_left(current_dir)
            elif action == Action.TURN_RIGHT:
                current_dir = self._turn_right(current_dir)
        
        return current_dir
