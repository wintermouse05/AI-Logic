"""
Wumpus World Environment Simulator
This module implements the environment for the Wumpus World problem.
"""

import random
import copy
from enum import Enum
from typing import List, Tuple, Dict, Set, Optional

class Direction(Enum):
    NORTH = (0, 1)
    EAST = (1, 0)
    SOUTH = (0, -1)
    WEST = (-1, 0)

class Action(Enum):
    MOVE_FORWARD = "move_forward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    GRAB = "grab"
    SHOOT = "shoot"
    CLIMB_OUT = "climb_out"

class Percept:
    def __init__(self, stench=False, breeze=False, glitter=False, bump=False, scream=False):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream
    
    def __str__(self):
        percepts = []
        if self.stench: percepts.append("Stench")
        if self.breeze: percepts.append("Breeze")
        if self.glitter: percepts.append("Glitter")
        if self.bump: percepts.append("Bump")
        if self.scream: percepts.append("Scream")
        return f"[{', '.join(percepts) if percepts else 'None'}]"

class WumpusWorld:
    def __init__(self, size=8, num_wumpus=2, pit_probability=0.2, seed=None):
        self.size = size
        self.num_wumpus = num_wumpus
        self.pit_probability = pit_probability
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
        
        # Initialize world state
        self.pits = set()
        self.wumpus_positions = set()
        self.gold_position = None
        self.agent_position = (0, 0)
        self.agent_direction = Direction.EAST
        self.agent_has_arrow = True
        self.agent_has_gold = False
        self.agent_alive = True
        self.game_over = False
        self.score = 0
        self.action_count = 0
        self.moving_wumpus = False  # For advanced setting
        self.wumpus_moved = False  # Track if wumpus moved in last step
        
        # Generate world
        self._generate_world()
        
        # For visualization and tracking
        self.visited_cells = {(0, 0)}
        self.last_percept = None
        self.action_log = []
    
    def _generate_world(self):
        """Generate pits, wumpus, and gold positions ensuring a winnable path"""
        max_attempts = 100
        for attempt in range(max_attempts):
            self.pits = set()
            self.wumpus_positions = set()
            
            all_positions = [(x, y) for x in range(self.size) for y in range(self.size)]
            
            # Remove starting position (0,0) from possible dangerous positions
            safe_positions = all_positions.copy()
            safe_positions.remove((0, 0))
            
            # Generate pits with reduced probability to ensure more safe paths
            # Determine number of pits based on pit_probability and total positions
            num_pits = int(self.pit_probability * len(safe_positions))
            # Randomly select pit positions (excluding (0,0))
            if num_pits > 0:
                self.pits = set(random.sample(safe_positions, min(num_pits, len(safe_positions))))
            else:
                self.pits = set()
            
            # Remove pit positions from available positions for wumpus and gold
            available_positions = [pos for pos in safe_positions if pos not in self.pits]
            
            # Place wumpus
            if len(available_positions) >= self.num_wumpus:
                self.wumpus_positions = set(random.sample(available_positions, self.num_wumpus))
                available_positions = [pos for pos in available_positions if pos not in self.wumpus_positions]
            
            # Place gold (can be at starting position, but prefer reachable positions)
            gold_positions = [pos for pos in all_positions if pos not in self.pits and pos not in self.wumpus_positions]
            if gold_positions:
                self.gold_position = random.choice(gold_positions)
            
            # Check if there's a safe path to gold using BFS
            if self._has_safe_path_to_gold():
                return  # Valid world generated
        
        # If we can't generate a valid world after max_attempts, create a minimal safe world
        self._generate_minimal_safe_world()
    
    def _has_safe_path_to_gold(self):
        """Check if there's a safe path from (0,0) to gold using BFS"""
        if not self.gold_position:
            return False
            
        start = (0, 0)
        target = self.gold_position
        
        if start == target:
            return True
        
        visited = {start}
        queue = [start]
        
        while queue:
            x, y = queue.pop(0)
            
            # Check all adjacent cells (4-directional movement)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if not (0 <= nx < self.size and 0 <= ny < self.size):
                    continue
                
                # Skip if already visited
                if (nx, ny) in visited:
                    continue
                
                # Check if this is the target (gold) - gold position should be reachable
                if (nx, ny) == target:
                    # Target is reachable if it's not in a pit or with a wumpus
                    if (nx, ny) not in self.pits and (nx, ny) not in self.wumpus_positions:
                        return True
                    continue  # Target is blocked, keep searching
                
                # Skip dangerous cells (pits and wumpus positions)
                if (nx, ny) in self.pits or (nx, ny) in self.wumpus_positions:
                    continue
                
                # Add safe cell to queue for further exploration
                visited.add((nx, ny))
                queue.append((nx, ny))
        
        return False
    
    # def _generate_minimal_safe_world(self):
    #     """Generate a minimal safe world that's always winnable"""
    #     print("Generating minimal safe world (backup)...")
        
    #     self.pits = set()
    #     self.wumpus_positions = set()
        
    #     # Create a simple path pattern
    #     if self.size >= 4:
    #         # Place wumpus in a safe corner, away from main path
    #         self.wumpus_positions = {(self.size - 1, self.size - 1)}
            
    #         # Place gold in an accessible location
    #         self.gold_position = (2, 0) if self.size > 2 else (1, 0)
            
    #         # Add one or two pits in safe locations that don't block the path
    #         if self.size >= 4:
    #             # Add pit that doesn't block path to gold
    #             self.pits = {(1, 2)} if self.size > 3 else set()
        
    #     elif self.size == 3:
    #         # For 3x3 world
    #         self.wumpus_positions = {(2, 2)}
    #         self.gold_position = (1, 0)
    #         self.pits = {(0, 2)}  # One pit that doesn't block path
        
    #     else:
    #         # For very small worlds (2x2), keep it minimal
    #         self.wumpus_positions = {(1, 1)}
    #         self.gold_position = (1, 0)
    #         self.pits = set()  # No pits in tiny worlds
    
    def _is_valid_position(self, pos):
        """Check if position is within world boundaries"""
        x, y = pos
        return 0 <= x < self.size and 0 <= y < self.size
    
    def _get_adjacent_positions(self, pos):
        """Get valid adjacent positions"""
        x, y = pos
        adjacent = []
        for direction in Direction:
            dx, dy = direction.value
            new_pos = (x + dx, y + dy)
            if self._is_valid_position(new_pos):
                adjacent.append(new_pos)
        return adjacent
    
    def _generate_percepts(self):
        """Generate percepts for current agent position"""
        stench = any(wumpus in self._get_adjacent_positions(self.agent_position) 
                    for wumpus in self.wumpus_positions)
        breeze = any(pit in self._get_adjacent_positions(self.agent_position) 
                    for pit in self.pits)
        glitter = self.agent_position == self.gold_position and not self.agent_has_gold
        
        return Percept(stench=stench, breeze=breeze, glitter=glitter)
    
    def _turn_left(self):
        """Turn agent left"""
        directions = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]
        current_index = directions.index(self.agent_direction)
        self.agent_direction = directions[(current_index + 1) % 4]
    
    def _turn_right(self):
        """Turn agent right"""
        directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        current_index = directions.index(self.agent_direction)
        self.agent_direction = directions[(current_index + 1) % 4]
    
    def _move_forward(self):
        """Move agent forward in current direction"""
        dx, dy = self.agent_direction.value
        new_x = self.agent_position[0] + dx
        new_y = self.agent_position[1] + dy
        new_position = (new_x, new_y)
        
        if self._is_valid_position(new_position):
            self.agent_position = new_position
            self.visited_cells.add(new_position)
            return False  # No bump
        else:
            return True  # Bump into wall
    
    def _shoot_arrow(self):
        """Shoot arrow in current direction"""
        if not self.agent_has_arrow:
            return False  # No arrow to shoot
        
        self.agent_has_arrow = False
        self.score -= 10  # Shooting cost
        
        # Trace arrow path
        x, y = self.agent_position
        dx, dy = self.agent_direction.value
        
        while True:
            x += dx
            y += dy
            if not self._is_valid_position((x, y)):
                break  # Arrow hits wall
            
            # Check if arrow hits wumpus
            if (x, y) in self.wumpus_positions:
                self.wumpus_positions.remove((x, y))
                return True  # Wumpus killed, scream
        
        return False  # Arrow missed
    
    def _check_death(self):
        """Check if agent dies from pit or wumpus"""
        if self.agent_position in self.pits:
            self.agent_alive = False
            self.score -= 1000
            self.game_over = True
            return True
        
        if self.agent_position in self.wumpus_positions:
            self.agent_alive = False
            self.score -= 1000
            self.game_over = True
            return True
        
        return False
    
    def _move_wumpus(self):
        """Move all wumpus after every 5 agent actions (advanced setting)"""
        if not self.moving_wumpus:
            return
        
        old_wumpus_positions = self.wumpus_positions.copy()
        new_wumpus_positions = set()
        
        for wumpus_pos in self.wumpus_positions:
            adjacent_positions = self._get_adjacent_positions(wumpus_pos)
            # Filter out positions with pits, walls, or other wumpus
            valid_moves = [pos for pos in adjacent_positions 
                          if pos not in self.pits and pos not in new_wumpus_positions]
            
            if valid_moves:
                new_pos = random.choice(valid_moves)
                new_wumpus_positions.add(new_pos)
            else:
                new_wumpus_positions.add(wumpus_pos)  # Stay in place
        
        self.wumpus_positions = new_wumpus_positions
        
        # Check if wumpus actually moved
        if old_wumpus_positions != self.wumpus_positions:
            print(f"🔄 Wumpus moved from {old_wumpus_positions} to {self.wumpus_positions}")
            self.wumpus_moved = True
        else:
            self.wumpus_moved = False
        
        # Check if wumpus moved into agent's position (agent dies)
        if self.agent_position in self.wumpus_positions:
            self.agent_alive = False
            self.score -= 1000
            self.game_over = True
    
    def step(self, action: Action):
        """Execute action and return percept"""
        if self.game_over or not self.agent_alive:
            return self._generate_percepts()
        
        # Reset wumpus movement flag at start of step
        self.wumpus_moved = False
        
        # Log action
        self.action_log.append({
            'action': action,
            'position': self.agent_position,
            'direction': self.agent_direction,
            'score_before': self.score
        })
        
        percept = Percept()
        
        # Execute action
        if action == Action.MOVE_FORWARD:
            bump = self._move_forward()
            percept.bump = bump
            self.score -= 1
            if not bump:
                self._check_death()
        
        elif action == Action.TURN_LEFT:
            self._turn_left()
            self.score -= 1
        
        elif action == Action.TURN_RIGHT:
            self._turn_right()
            self.score -= 1
        
        elif action == Action.GRAB:
            if self.agent_position == self.gold_position and not self.agent_has_gold:
                self.agent_has_gold = True
                self.score += 10
        
        elif action == Action.SHOOT:
            scream = self._shoot_arrow()
            percept.scream = scream
        
        elif action == Action.CLIMB_OUT:
            if self.agent_position == (0, 0):
                if self.agent_has_gold:
                    self.score += 1000
                self.game_over = True
        
        # Increment action count
        self.action_count += 1
        
        # Move wumpus every 5 actions (advanced setting)
        if self.moving_wumpus and self.action_count % 5 == 0:
            self._move_wumpus()
            if not self.agent_alive:  # Agent killed by moving wumpus
                percept = self._generate_percepts()
                self.last_percept = percept
                return percept
        
        # Generate remaining percepts
        if self.agent_alive:
            environment_percept = self._generate_percepts()
            percept.stench = environment_percept.stench
            percept.breeze = environment_percept.breeze
            percept.glitter = environment_percept.glitter
        
        self.last_percept = percept
        return percept
    
    def enable_moving_wumpus(self):
        """Enable moving wumpus for advanced setting"""
        self.moving_wumpus = True
    
    def get_world_state(self):
        """Get current world state for visualization"""
        return {
            'size': self.size,
            'agent_position': self.agent_position,
            'agent_direction': self.agent_direction,
            'agent_has_arrow': self.agent_has_arrow,
            'agent_has_gold': self.agent_has_gold,
            'agent_alive': self.agent_alive,
            'pits': self.pits,
            'wumpus_positions': self.wumpus_positions,
            'gold_position': self.gold_position,
            'visited_cells': self.visited_cells,
            'score': self.score,
            'game_over': self.game_over,
            'last_percept': self.last_percept,
            'action_count': self.action_count
        }
    
    def reset(self, seed=None, preserve_agent_learning=True):
        """Reset world to initial state
        
        Args:
            seed: Optional random seed for reproducible worlds
            preserve_agent_learning: Whether to preserve agent's strategic learning
        """
        if seed is not None:
            self.seed = seed
            random.seed(seed)
        
        # Reset world state
        self.pits = set()
        self.wumpus_positions = set()
        self.gold_position = None
        self.agent_position = (0, 0)
        self.agent_direction = Direction.EAST
        self.agent_has_arrow = True
        self.agent_has_gold = False
        self.agent_alive = True
        self.game_over = False
        self.score = 0
        self.action_count = 0
        self.wumpus_moved = False  # Reset wumpus movement flag
        self.visited_cells = {(0, 0)}  # Clear all colored cells
        self.last_percept = None
        self.action_log = []
        
        # Generate new world layout
        self._generate_world()
        
        # Return information about the reset
        return {
            'preserve_learning': preserve_agent_learning,
            'new_world_generated': True,
            'start_position': (0, 0)
        }
