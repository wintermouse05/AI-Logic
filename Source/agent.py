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
        
        # Agent state (gets reset with new map)
        self.position = (0, 0)
        self.direction = Direction.EAST
        self.has_arrow = True
        self.has_gold = False
        self.visited_cells = {(0, 0)}
        self.action_history = []
        self.gold_position = None
        self.plan = []  # Current action plan
        
        # Strategy parameters (preserved across resets - agent gets smarter)
        self.exploration_strategy = "safe_first"  # "safe_first", "cautious", "aggressive"
        self.risk_tolerance = 0.3
        
        # Learning parameters (improve over time)
        self.games_played = 0
        self.successful_strategies = []  # Track what worked
        self.failed_patterns = []       # Remember what failed
        self.adaptive_caution = 0.3     # Starts cautious, adapts over time
        
        # Track percepts for inference
        self.previous_percepts = {}  # Store previous percepts by position
        self.last_shooting_position = None  # Track where we last shot from
        self.last_shooting_direction = None  # Track direction we last shot
    
    def perceive(self, percept: Percept):
        """Process percept and update knowledge base"""
        # Store current percept for comparison
        current_percept_key = (self.position, percept.stench, percept.breeze, percept.glitter)
        
        # Check for stench disappearance after shooting
        stench_disappeared = False
        if (self.last_shooting_position and 
            self.last_shooting_position == self.position and
            self.last_shooting_direction):
            
            # Check if stench disappeared from previous percept
            prev_key = self.previous_percepts.get(self.position)
            if prev_key and prev_key[1] and not percept.stench:  # Had stench before, no stench now
                stench_disappeared = True
                print(f"👃 Stench disappeared at {self.position} after shooting!")
        
        # Update knowledge base with current percept
        self.kb.update_from_percept(self.position, percept)
        
        # If we just shot and stench disappeared, update knowledge base accordingly
        if stench_disappeared and self.last_shooting_position and self.last_shooting_direction:
            self.kb.handle_shooting_result(
                self.last_shooting_position, 
                self.last_shooting_direction, 
                True,  # We know a scream was heard (stench disappeared)
                stench_disappeared
            )
            # Clear shooting tracking
            self.last_shooting_position = None
            self.last_shooting_direction = None
        
        # Store current percept for next comparison
        self.previous_percepts[self.position] = current_percept_key
        
        # Run inference
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
        
        # Exploration strategy - try to find safe paths first
        next_action = self._choose_exploration_action()
        if next_action:
            return next_action
        
        # Try to find alternative paths around wumpus
        alternative_action = self._find_alternative_path()
        if alternative_action:
            return alternative_action
        
        # Consider shooting ONLY as absolute last resort
        if self.has_arrow:
            shoot_action = self._consider_shooting()
            if shoot_action:
                return shoot_action
        
        # Fallback: random safe action
        return self._choose_safe_random_action()
    
    def _consider_shooting(self) -> Optional[Action]:
        """Shoot wumpus when blocking critical paths or when no safe moves available"""
        if not self.has_arrow:
            return None
            
        wumpus_locations = self.kb.infer_wumpus_locations()
        if not wumpus_locations:
            return None
        
        # Strategy 1: Shoot if wumpus is blocking our only path to gold
        if self.gold_position and not self.has_gold:
            if self._is_wumpus_blocking_only_path_to_gold(wumpus_locations):
                print("🎯 Shooting wumpus blocking path to gold!")
                return self._execute_strategic_shot(wumpus_locations)
        
        # Strategy 2: Shoot if wumpus is blocking our only path to escape (when we have gold)
        if self.has_gold and self.position != (0, 0):
            if self._is_wumpus_blocking_only_escape_path(wumpus_locations):
                print("🎯 Shooting wumpus blocking escape path!")
                return self._execute_strategic_shot(wumpus_locations)
        
        # Strategy 3: Shoot if we're completely trapped by wumpus with no safe moves
        if self._is_completely_trapped_by_wumpus(wumpus_locations):
            print("🎯 Shooting wumpus - completely trapped!")
            return self._execute_strategic_shot(wumpus_locations)
        
        # Strategy 4: NEW - Shoot if no safe exploration options and no alternative paths
        if self._should_shoot_for_progress(wumpus_locations):
            print("🎯 Shooting wumpus - no safe alternatives for progress!")
            return self._execute_strategic_shot(wumpus_locations)
        
        # Otherwise, DON'T shoot - find alternative paths or wait
        return None
    
    def _is_wumpus_blocking_only_path_to_gold(self, wumpus_locations: Set[Tuple[int, int]]) -> bool:
        """Check if wumpus is blocking the ONLY safe path to gold"""
        if not self.gold_position:
            return False
        
        # Try to find ANY safe path to gold that doesn't require killing wumpus
        safe_cells = self.kb.infer_safe_cells()
        
        # Use BFS to see if we can reach gold through safe cells only
        visited = {self.position}
        queue = [self.position]
        
        while queue:
            current = queue.pop(0)
            
            if current == self.gold_position:
                return False  # Found safe path, no need to shoot
            
            # Check adjacent cells
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                
                if (0 <= nx < self.world_size and 0 <= ny < self.world_size and 
                    next_pos not in visited):
                    
                    # If it's the gold position, we can reach it if it's not with a wumpus
                    if next_pos == self.gold_position:
                        if next_pos not in wumpus_locations:
                            return False  # Safe path to gold exists
                    
                    # Add to queue if it's definitely safe
                    elif next_pos in safe_cells:
                        visited.add(next_pos)
                        queue.append(next_pos)
        
        # No safe path found - wumpus might be blocking
        print("🚫 Wumpus blocking only path to gold!")
        return True
    
    def _is_wumpus_blocking_only_escape_path(self, wumpus_locations: Set[Tuple[int, int]]) -> bool:
        """Check if wumpus is blocking the ONLY safe path back to (0,0)"""
        if not self.has_gold:
            return False
        
        # Try to find ANY safe path back to start
        safe_cells = self.kb.infer_safe_cells()
        safe_cells.add((0, 0))  # Start is always safe
        
        visited = {self.position}
        queue = [self.position]
        
        while queue:
            current = queue.pop(0)
            
            if current == (0, 0):
                return False  # Found safe escape path
            
            # Check adjacent cells
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                next_pos = (nx, ny)
                
                if (0 <= nx < self.world_size and 0 <= ny < self.world_size and 
                    next_pos not in visited and next_pos in safe_cells):
                    visited.add(next_pos)
                    queue.append(next_pos)
        
        print("🚫 Wumpus blocking only escape path!")
        return True
    
    def _is_completely_trapped_by_wumpus(self, wumpus_locations: Set[Tuple[int, int]]) -> bool:
        """Check if agent is completely surrounded by wumpus with no safe moves"""
        adjacent_positions = []
        x, y = self.position
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.world_size and 0 <= ny < self.world_size:
                adjacent_positions.append((nx, ny))
        
        safe_cells = self.kb.infer_safe_cells()
        
        # Check if ALL adjacent cells are either wumpus or dangerous
        for adj_pos in adjacent_positions:
            if adj_pos in safe_cells or adj_pos not in wumpus_locations:
                return False  # Found at least one safe adjacent cell
        
        print("🚫 Completely trapped by wumpus!")
        return True
    
    def _should_shoot_for_progress(self, wumpus_locations: Set[Tuple[int, int]]) -> bool:
        """Check if shooting is necessary to make progress when no safe options exist"""
        # Check if we have any safe exploration targets
        safe_targets = self.planner.find_safe_exploration_targets(
            self.position, self.visited_cells
        )
        
        # Check if we have any unknown exploration targets that might be safe
        unknown_targets = self.planner.find_unknown_exploration_targets(
            self.position, self.visited_cells
        )
        
        # If we have safe targets or unknown targets, don't shoot yet
        if safe_targets or unknown_targets:
            return False
        
        # Check if shooting a wumpus would open up new exploration possibilities
        for wumpus_pos in wumpus_locations:
            if self._is_in_line_of_fire(wumpus_pos):
                # If we can shoot this wumpus, check if it would help us progress
                # This is a simplified check - if wumpus is adjacent to unexplored areas
                x, y = wumpus_pos
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    adj_x, adj_y = x + dx, y + dy
                    if (self._is_valid_position(adj_x, adj_y) and 
                        (adj_x, adj_y) not in self.visited_cells):
                        # Shooting this wumpus might open up unexplored areas
                        return True
        
        return False
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is valid within world boundaries"""
        return 0 <= x < self.world_size and 0 <= y < self.world_size
    
    def _execute_strategic_shot(self, wumpus_locations: Set[Tuple[int, int]]) -> Optional[Action]:
        """Execute strategic shot at blocking wumpus"""
        # Find the best wumpus to shoot (closest to our path)
        target_wumpus = None
        min_distance = float('inf')
        
        for wumpus_pos in wumpus_locations:
            if self._is_in_line_of_fire(wumpus_pos):
                # Calculate distance to this wumpus
                distance = abs(wumpus_pos[0] - self.position[0]) + abs(wumpus_pos[1] - self.position[1])
                if distance < min_distance:
                    min_distance = distance
                    target_wumpus = wumpus_pos
        
        if target_wumpus:
            required_dir = self._get_direction_to_target(target_wumpus)
            if required_dir == self.direction:
                print(f"🎯 STRATEGIC SHOT at blocking wumpus {target_wumpus} (last resort!)")
                return Action.SHOOT
            elif required_dir:
                turn_actions = self._get_turn_actions(required_dir)
                if turn_actions:
                    print(f"🎯 Turning for strategic shot at {target_wumpus}")
                    self.plan = turn_actions + [Action.SHOOT]
                    return self.plan.pop(0)
        
        return None
    
    def _find_alternative_path(self) -> Optional[Action]:
        """Try to find alternative paths around wumpus before shooting"""
        
        # If we know where gold is, try to find alternative routes
        if self.gold_position and not self.has_gold:
            return self._find_detour_to_gold()
        
        # If we have gold, try alternative escape routes
        if self.has_gold and self.position != (0, 0):
            return self._find_detour_to_escape()
        
        # Try exploring safe unknown areas to discover new paths
        return self._explore_for_new_paths()
    
    def _find_detour_to_gold(self) -> Optional[Action]:
        """Find a detour route to gold that avoids known wumpus"""
        safe_cells = self.kb.infer_safe_cells()
        wumpus_locations = self.kb.infer_wumpus_locations()
        
        # Look for safe cells that might lead to alternative paths
        for safe_cell in safe_cells:
            if safe_cell not in self.visited_cells:
                # Try to reach this unexplored safe cell
                path = self.planner.find_path_to_goal(
                    self.position, self.direction, [safe_cell],
                    avoid_unknown=False  # Allow some risk for detours
                )
                if path:
                    print(f"🔄 Taking detour to {safe_cell} to avoid wumpus")
                    self.plan = path
                    return self.plan.pop(0)
        
        return None
    
    def _find_detour_to_escape(self) -> Optional[Action]:
        """Find alternative escape route when carrying gold"""
        safe_cells = self.kb.infer_safe_cells()
        safe_cells.add((0, 0))  # Start is always safe
        
        # Look for safe cells that might provide alternative escape routes
        for safe_cell in safe_cells:
            if safe_cell not in self.visited_cells:
                # Check if this cell might provide a path to escape
                path = self.planner.find_path_to_goal(
                    self.position, self.direction, [safe_cell]
                )
                if path:
                    print(f"🔄 Taking escape detour via {safe_cell}")
                    self.plan = path
                    return self.plan.pop(0)
        
        return None
    
    def _explore_for_new_paths(self) -> Optional[Action]:
        """Explore unknown but potentially safe areas to find new paths"""
        
        # Look for unknown cells adjacent to safe cells
        safe_cells = self.kb.infer_safe_cells()
        unknown_cells = set()
        
        for safe_cell in safe_cells:
            x, y = safe_cell
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.world_size and 0 <= ny < self.world_size):
                    unknown_pos = (nx, ny)
                    if (unknown_pos not in safe_cells and 
                        unknown_pos not in self.kb.infer_dangerous_cells() and
                        unknown_pos not in self.visited_cells):
                        unknown_cells.add(unknown_pos)
        
        # Try to explore the closest unknown cell
        if unknown_cells:
            closest_unknown = min(unknown_cells, 
                                key=lambda pos: abs(pos[0] - self.position[0]) + abs(pos[1] - self.position[1]))
            
            path = self.planner.find_path_to_goal(
                self.position, self.direction, [closest_unknown],
                avoid_unknown=True  # Be cautious approaching unknown areas
            )
            if path:
                print(f"🔍 Exploring unknown area {closest_unknown} for new paths")
                self.plan = path
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
        """Choose a random safe action as fallback, or take calculated risk if no safe options"""
        safe_actions = [Action.TURN_LEFT, Action.TURN_RIGHT]
        
        # Check if forward movement is safe
        forward_pos = self._get_forward_position()
        if forward_pos and forward_pos in self.kb.infer_safe_cells():
            safe_actions.append(Action.MOVE_FORWARD)
        
        # If we have safe actions, use them
        if len(safe_actions) > 2 or self.kb.infer_safe_cells():  # More than just turning
            return random.choice(safe_actions)
        
        # If no safe moves and we have arrow, consider shooting as last resort
        if self.has_arrow:
            wumpus_locations = self.kb.infer_wumpus_locations()
            if wumpus_locations:
                for wumpus_pos in wumpus_locations:
                    if self._is_in_line_of_fire(wumpus_pos):
                        # We can shoot a wumpus - this might be better than turning forever
                        required_dir = self._get_direction_to_target(wumpus_pos)
                        if required_dir == self.direction:
                            print("🎯 DESPERATE SHOT - no safe moves available!")
                            return Action.SHOOT
                        elif required_dir:
                            # Turn towards wumpus for next shot opportunity
                            turn_actions = self._get_turn_actions(required_dir)
                            if turn_actions:
                                print(f"🎯 Turning for desperate shot at wumpus {wumpus_pos}")
                                self.plan = turn_actions + [Action.SHOOT]
                                return self.plan.pop(0)
        
        # Last resort - just turn (agent will keep turning until something changes)
        return random.choice([Action.TURN_LEFT, Action.TURN_RIGHT])
    
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
            # Track shooting position and direction for stench disappearance detection
            self.last_shooting_position = self.position
            self.last_shooting_direction = self.direction
            
            if percept.scream:
                print("💀 Wumpus killed!")
                # Update knowledge base: wumpus is dead, cell is now safe
                self._update_knowledge_after_wumpus_kill()
    
    def _update_knowledge_after_wumpus_kill(self):
        """Update knowledge base after killing a wumpus"""
        # Find which wumpus was killed (the one in line of fire)
        killed_wumpus_pos = None
        
        # Check all positions in the line of fire
        x, y = self.position
        dx, dy = self.direction.value
        
        # Check each cell in the shooting direction until we hit a wall
        current_x, current_y = x + dx, y + dy
        while (0 <= current_x < self.world_size and 0 <= current_y < self.world_size):
            check_pos = (current_x, current_y)
            
            # Check if there was a wumpus at this position
            wumpus_prop = self.kb._create_proposition("Wumpus", current_x, current_y)
            if self.kb.is_known_true(wumpus_prop):
                killed_wumpus_pos = check_pos
                break
                
            # Move to next position in line of fire
            current_x += dx
            current_y += dy
        
        if killed_wumpus_pos:
            print(f"🎯 Wumpus eliminated at {killed_wumpus_pos}")
            
            # Use the knowledge base method to properly eliminate the wumpus
            self.kb.eliminate_wumpus(killed_wumpus_pos)
            
            # Plan to advance into the cleared cell so we continue exploring
            fx, fy = self.position[0] + dx, self.position[1] + dy
            if (fx, fy) == killed_wumpus_pos:
                # Immediate forward step reaches the cleared cell
                self.plan = [Action.MOVE_FORWARD]
                print(f"➡️ Advancing into cleared cell {killed_wumpus_pos}")
            else:
                # Plan a path directly to the cleared wumpus cell
                path_to_cleared = self.planner.find_path_to_goal(
                    self.position, self.direction, [killed_wumpus_pos],
                )
                if path_to_cleared:
                    self.plan = path_to_cleared
                    print(f"🧭 Planning path into cleared cell {killed_wumpus_pos}")
            
            # Clear any outdated plans that were avoiding this area
            if self.plan:
                print("🔄 Replanning due to wumpus elimination...")
                # keep the new plan we just set
        else:
            print("🤔 Heard scream but couldn't identify which wumpus was killed")
    
    def reset_for_new_world(self, preserve_learning=True):
        """Reset agent for new world while optionally preserving learned strategies"""
        
        # Always reset world-specific knowledge
        self.position = (0, 0)
        self.direction = Direction.EAST
        self.has_arrow = True
        self.has_gold = False
        self.visited_cells = {(0, 0)}
        self.gold_position = None
        self.plan = []
        
        # Reset percept tracking
        self.previous_percepts = {}
        self.last_shooting_position = None
        self.last_shooting_direction = None
        
        # Reset knowledge base (forget about dangerous cells in old world)
        self.kb = KnowledgeBase(self.world_size, self.num_wumpus)
        self.planner = WumpusPlanner(self.world_size, self.kb)
        
        if preserve_learning:
            # Preserve and improve strategic knowledge
            self.games_played += 1
            
            # Analyze previous game performance to improve strategy
            self._analyze_game_performance()
            
            # Adapt strategy based on experience
            self._adapt_strategy()
            
            print(f"🧠 Agent reset for game #{self.games_played + 1} - Learning preserved!")
            print(f"🎯 Current strategy: {self.exploration_strategy}, Caution level: {self.adaptive_caution:.2f}")
        else:
            # Complete reset - agent forgets everything
            self.games_played = 0
            self.successful_strategies = []
            self.failed_patterns = []
            self.adaptive_caution = 0.3
            self.exploration_strategy = "safe_first"
            print("🔄 Complete agent reset - All learning cleared!")
    
    def _analyze_game_performance(self):
        """Analyze last game to learn successful patterns"""
        if not self.action_history:
            return
        
        # Analyze action patterns that led to success/failure
        total_actions = len(self.action_history)
        exploration_actions = sum(1 for a in self.action_history if a['action'] in [Action.MOVE_FORWARD])
        caution_actions = sum(1 for a in self.action_history if a['action'] in [Action.TURN_LEFT, Action.TURN_RIGHT])
        shooting_actions = sum(1 for a in self.action_history if a['action'] == Action.SHOOT)
        
        game_stats = {
            'total_actions': total_actions,
            'exploration_ratio': exploration_actions / max(total_actions, 1),
            'caution_ratio': caution_actions / max(total_actions, 1),
            'shooting_actions': shooting_actions,
            'found_gold': self.has_gold,
            'survived': len([a for a in self.action_history if a.get('percept', '') != 'Dead']),
            'strategy_used': self.exploration_strategy
        }
        
        # Track successful patterns
        if self.has_gold:
            self.successful_strategies.append(game_stats)
            if shooting_actions == 0:
                print(f"🎯 EXCELLENT: Won without shooting! Score bonus preserved.")
            else:
                print(f"📈 Successful strategy recorded: {self.exploration_strategy} (shots: {shooting_actions})")
        else:
            self.failed_patterns.append(game_stats)
            if shooting_actions > 0:
                print(f"⚠️ Shot {shooting_actions} times but still failed - consider avoiding shooting")
        
        # Clear action history for new game
        self.action_history = []
    
    def _adapt_strategy(self):
        """Adapt exploration strategy based on experience"""
        if self.games_played < 2:
            return  # Need some experience first
        
        # Analyze success rates of different strategies
        if self.successful_strategies:
            # Calculate success rate for each strategy
            strategy_success = {}
            for strategy_data in self.successful_strategies:
                strategy = strategy_data['strategy_used']
                strategy_success[strategy] = strategy_success.get(strategy, 0) + 1
            
            # Find most successful strategy
            best_strategy = max(strategy_success.keys(), key=lambda x: strategy_success[x])
            
            # Gradually shift towards successful strategies
            if best_strategy != self.exploration_strategy:
                if self.games_played > 3:  # Only change after gaining some experience
                    self.exploration_strategy = best_strategy
                    print(f"🎯 Strategy adapted to: {best_strategy}")
        
        # Adapt caution level based on success/failure patterns
        success_rate = len(self.successful_strategies) / max(self.games_played, 1)
        
        if success_rate > 0.7:
            # High success rate - can be more aggressive
            self.adaptive_caution = max(0.1, self.adaptive_caution - 0.05)
            if self.games_played > 5 and self.exploration_strategy == "safe_first":
                self.exploration_strategy = "cautious"
        elif success_rate < 0.3:
            # Low success rate - be more cautious
            self.adaptive_caution = min(0.8, self.adaptive_caution + 0.1)
            self.exploration_strategy = "safe_first"
        
        # Update planner risk parameters
        self.risk_tolerance = self.adaptive_caution
        if hasattr(self.planner, 'unknown_cost'):
            self.planner.unknown_cost = 10.0 + (self.adaptive_caution * 20.0)
    
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

    def export_knowledge_base(self, file_path: str):
        """Export the agent's current knowledge base summary to a text file."""
        summary = self.kb.get_knowledge_summary()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Knowledge Base Summary\n")
            f.write("======================\n\n")
            for key, value in summary.items():
                f.write(f"{key}:\n")
                if isinstance(value, list):
                    for item in value:
                        f.write(f"  {item}\n")
                else:
                    f.write(f"  {value}\n")
                f.write("\n")

                
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