"""
Hybrid Wumpus World Agent
Integrates knowledge base, inference engine, and planning module.
"""

from typing import List, Tuple, Optional, Set
from environment import WumpusWorld, Action, Direction, Percept
from knowledge_base import KnowledgeBase, Proposition
from planning import WumpusPlanner
import random

class WumpusAgent:
    """Intelligent agent for Wumpus World using logic and planning"""
    
    def __init__(self, world_size: int = 8, num_wumpus: int = 2):
        self.world_size = world_size
        self.num_wumpus = num_wumpus
        
        # Initialize components
        self.kb = KnowledgeBase(world_size, num_wumpus)
        self.planner = WumpusPlanner(world_size, self.kb)
        
        # Agent state
        self.position = (0, 0)
        self.direction = Direction.EAST
        self.has_arrow = True
        self.has_gold = False
        self.visited_cells = {(0, 0)}
        self.action_history = []
        self.gold_position = None
        self.plan = []  # Current action plan
        
        # Strategy parameters
        self.exploration_strategy = "safe_first"  # "safe_first", "cautious", "aggressive"
        self.risk_tolerance = 0.3
        
    def perceive(self, percept: Percept):
        """Process percept and update knowledge base"""
        # Update knowledge base with current percept
        self.kb.update_from_percept(self.position, percept)
        
        # Run inference to derive new knowledge
        self.kb.forward_chain()
        
        # Check for gold discovery
        if percept.glitter and not self.has_gold:
            self.gold_position = self.position
            print(f"🏆 Gold discovered at {self.position}!")
        
        # Log important discoveries
        if percept.stench and not any(action.get('stench') for action in self.action_history[-3:] if isinstance(action, dict)):
            print(f"⚠️ Stench detected at {self.position}")
        
        if percept.breeze and not any(action.get('breeze') for action in self.action_history[-3:] if isinstance(action, dict)):
            print(f"💨 Breeze detected at {self.position}")
    
    def choose_action(self) -> Action:
        """Choose next action based on current knowledge and strategy"""
        
        # If we have a plan, continue executing it
        if self.plan:
            action = self.plan.pop(0)
            print(f"🎯 Executing planned action: {action.value}")
            return action
        
        # Check if we have gold and are at start - climb out
        if self.has_gold and self.position == (0, 0):
            print("🎉 Mission accomplished! Climbing out with gold.")
            return Action.CLIMB_OUT
        
        # If we found gold, plan retrieval
        if self.gold_position and not self.has_gold and self.position == self.gold_position:
            print("📦 Grabbing gold...")
            return Action.GRAB
        
        # If we have gold, plan return to start
        if self.has_gold:
            print("🏃 Planning return to start...")
            return_plan = self.planner.find_path_to_goal(
                self.position, self.direction, [(0, 0)]
            )
            if return_plan:
                self.plan = return_plan + [Action.CLIMB_OUT]
                return self.plan.pop(0)
        
        # If we know gold location, plan to get it
        if self.gold_position and not self.has_gold:
            print(f"🗺️ Planning path to gold at {self.gold_position}...")
            gold_plan = self.planner.find_path_to_goal(
                self.position, self.direction, [self.gold_position]
            )
            if gold_plan:
                self.plan = gold_plan + [Action.GRAB]
                return self.plan.pop(0)
        
        # Consider shooting if we have arrow and can hit wumpus
        if self.has_arrow:
            shoot_action = self._consider_shooting()
            if shoot_action:
                return shoot_action
        
        # Exploration strategy
        next_action = self._choose_exploration_action()
        if next_action:
            return next_action
        
        # Fallback: random safe action
        return self._choose_safe_random_action()
    
    def _consider_shooting(self) -> Optional[Action]:
        """Consider whether to shoot based on wumpus inference"""
        wumpus_locations = self.kb.infer_wumpus_locations()
        
        if not wumpus_locations:
            return None
        
        # Calculate utility of shooting in current direction
        utility = self.planner.calculate_shooting_utility(
            self.position, self.direction, wumpus_locations
        )
        
        # Shoot if utility is positive and high enough
        if utility > 50.0:  # Threshold for shooting
            print(f"🏹 Shooting arrow! Expected utility: {utility:.1f}")
            return Action.SHOOT
        
        # Consider turning to face a wumpus
        for wumpus_pos in wumpus_locations:
            # Check if wumpus is in line with current position
            if self._is_in_line_of_fire(wumpus_pos):
                # Turn to face the wumpus
                required_dir = self._get_direction_to_target(wumpus_pos)
                if required_dir and required_dir != self.direction:
                    turn_actions = self._get_turn_actions(required_dir)
                    if turn_actions:
                        print(f"🎯 Turning to face wumpus at {wumpus_pos}")
                        self.plan = turn_actions + [Action.SHOOT]
                        return self.plan.pop(0)
        
        return None
    
    def _is_in_line_of_fire(self, target_pos: Tuple[int, int]) -> bool:
        """Check if target is in line with current position"""
        x1, y1 = self.position
        x2, y2 = target_pos
        
        # Check if on same row or column
        return x1 == x2 or y1 == y2
    
    def _get_direction_to_target(self, target_pos: Tuple[int, int]) -> Optional[Direction]:
        """Get direction to face target position"""
        x1, y1 = self.position
        x2, y2 = target_pos
        
        if x1 == x2:  # Same column
            if y2 > y1:
                return Direction.NORTH
            elif y2 < y1:
                return Direction.SOUTH
        elif y1 == y2:  # Same row
            if x2 > x1:
                return Direction.EAST
            elif x2 < x1:
                return Direction.WEST
        
        return None
    
    def _get_turn_actions(self, target_dir: Direction) -> List[Action]:
        """Get actions to turn to target direction"""
        return self.planner._get_actions_to_face_direction(self.direction, target_dir)
    
    def _choose_exploration_action(self) -> Optional[Action]:
        """Choose exploration action based on strategy"""
        
        if self.exploration_strategy == "safe_first":
            return self._safe_first_exploration()
        elif self.exploration_strategy == "cautious":
            return self._cautious_exploration()
        elif self.exploration_strategy == "aggressive":
            return self._aggressive_exploration()
        
        return None
    
    def _safe_first_exploration(self) -> Optional[Action]:
        """Explore safe cells first, then carefully venture into unknown"""
        
        # First, try to visit known safe cells
        safe_targets = self.planner.find_safe_exploration_targets(
            self.position, self.visited_cells
        )
        
        if safe_targets:
            print(f"🛡️ Moving to safe cell: {safe_targets[0]}")
            path = self.planner.find_path_to_goal(
                self.position, self.direction, safe_targets[:3]
            )
            if path:
                self.plan = path
                return self.plan.pop(0)
        
        # If no safe cells, carefully explore unknown cells
        unknown_targets = self.planner.find_unknown_exploration_targets(
            self.position, self.visited_cells
        )
        
        if unknown_targets:
            print(f"🔍 Cautiously exploring unknown cell: {unknown_targets[0]}")
            path = self.planner.find_path_to_goal(
                self.position, self.direction, unknown_targets[:2],
                avoid_unknown=True
            )
            if path:
                self.plan = path
                return self.plan.pop(0)
        
        return None
    
    def _cautious_exploration(self) -> Optional[Action]:
        """Balanced exploration avoiding high-risk areas"""
        # Similar to safe_first but with different risk parameters
        self.planner.unknown_cost = 15.0
        return self._safe_first_exploration()
    
    def _aggressive_exploration(self) -> Optional[Action]:
        """More aggressive exploration accepting higher risk"""
        self.planner.unknown_cost = 5.0
        
        # Include more exploration targets
        safe_targets = self.planner.find_safe_exploration_targets(
            self.position, self.visited_cells
        )
        unknown_targets = self.planner.find_unknown_exploration_targets(
            self.position, self.visited_cells
        )
        
        all_targets = safe_targets + unknown_targets
        
        if all_targets:
            path = self.planner.find_path_to_goal(
                self.position, self.direction, all_targets[:5]
            )
            if path:
                self.plan = path
                return self.plan.pop(0)
        
        return None
    
    def _choose_safe_random_action(self) -> Action:
        """Choose a random safe action as fallback"""
        safe_actions = [Action.TURN_LEFT, Action.TURN_RIGHT]
        
        # Check if forward movement is safe
        forward_pos = self._get_forward_position()
        if forward_pos and forward_pos in self.kb.infer_safe_cells():
            safe_actions.append(Action.MOVE_FORWARD)
        
        return random.choice(safe_actions)
    
    def _get_forward_position(self) -> Optional[Tuple[int, int]]:
        """Get position if moving forward"""
        x, y = self.position
        dx, dy = self.direction.value
        new_pos = (x + dx, y + dy)
        
        if 0 <= new_pos[0] < self.world_size and 0 <= new_pos[1] < self.world_size:
            return new_pos
        return None
    
    def update_position(self, action: Action, percept: Percept):
        """Update agent's internal state after action"""
        # Record action in history
        self.action_history.append({
            'action': action,
            'position': self.position,
            'direction': self.direction,
            'percept': str(percept),
            'stench': percept.stench,
            'breeze': percept.breeze
        })
        
        # Update position and direction based on action
        if action == Action.MOVE_FORWARD and not percept.bump:
            x, y = self.position
            dx, dy = self.direction.value
            new_position = (x + dx, y + dy)
            if 0 <= new_position[0] < self.world_size and 0 <= new_position[1] < self.world_size:
                self.position = new_position
                self.visited_cells.add(self.position)
        
        elif action == Action.TURN_LEFT:
            directions = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]
            current_index = directions.index(self.direction)
            self.direction = directions[(current_index + 1) % 4]
        
        elif action == Action.TURN_RIGHT:
            directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
            current_index = directions.index(self.direction)
            self.direction = directions[(current_index + 1) % 4]
        
        elif action == Action.GRAB:
            if percept.glitter or (self.gold_position and self.position == self.gold_position):
                self.has_gold = True
                print("✨ Gold acquired!")
        
        elif action == Action.SHOOT:
            self.has_arrow = False
            if percept.scream:
                print("💀 Wumpus killed!")
    
    def get_status(self) -> dict:
        """Get current agent status for debugging"""
        return {
            'position': self.position,
            'direction': self.direction.name,
            'has_arrow': self.has_arrow,
            'has_gold': self.has_gold,
            'visited_cells': len(self.visited_cells),
            'gold_position': self.gold_position,
            'current_plan_length': len(self.plan),
            'knowledge_summary': self.kb.get_knowledge_summary()
        }


class RandomAgent:
    """Random agent baseline for comparison"""
    
    def __init__(self, world_size: int = 8):
        self.world_size = world_size
        self.position = (0, 0)
        self.direction = Direction.EAST
        self.has_arrow = True
        self.has_gold = False
        self.visited_cells = {(0, 0)}
    
    def perceive(self, percept: Percept):
        """Random agent doesn't learn from percepts"""
        if percept.glitter:
            print("Random agent found gold!")
    
    def choose_action(self) -> Action:
        """Choose random action"""
        if self.has_gold and self.position == (0, 0):
            return Action.CLIMB_OUT
        
        # Random action selection with some bias
        actions = [Action.MOVE_FORWARD, Action.TURN_LEFT, Action.TURN_RIGHT]
        
        # Small chance to grab or shoot
        if random.random() < 0.1:
            actions.append(Action.GRAB)
        
        if self.has_arrow and random.random() < 0.05:
            actions.append(Action.SHOOT)
        
        return random.choice(actions)
    
    def update_position(self, action: Action, percept: Percept):
        """Update random agent state"""
        if action == Action.MOVE_FORWARD and not percept.bump:
            x, y = self.position
            dx, dy = self.direction.value
            new_position = (x + dx, y + dy)
            if 0 <= new_position[0] < self.world_size and 0 <= new_position[1] < self.world_size:
                self.position = new_position
                self.visited_cells.add(self.position)
        
        elif action == Action.TURN_LEFT:
            directions = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]
            current_index = directions.index(self.direction)
            self.direction = directions[(current_index + 1) % 4]
        
        elif action == Action.TURN_RIGHT:
            directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
            current_index = directions.index(self.direction)
            self.direction = directions[(current_index + 1) % 4]
        
        elif action == Action.GRAB and percept.glitter:
            self.has_gold = True
        
        elif action == Action.SHOOT:
            self.has_arrow = False
    
    def get_status(self) -> dict:
        """Get random agent status"""
        return {
            'position': self.position,
            'direction': self.direction.name,
            'has_arrow': self.has_arrow,
            'has_gold': self.has_gold,
            'visited_cells': len(self.visited_cells)
        }
