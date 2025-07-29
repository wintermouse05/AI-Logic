#!/usr/bin/env python3
"""
Test Map Generator for 8x8 Wumpus World
Creates a guaranteed winnable map with agent at (0,0) and gold at (7,7)
"""

import sys
import os
import random
from typing import Set, Tuple, List, Optional

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class WinningMapGenerator:
    """Generate 8x8 Wumpus World maps that are guaranteed to be winnable"""
    
    def __init__(self, size: int = 8):
        self.size = size
        self.start_pos = (0, 0)  # Bottom-left
        self.gold_pos = (7, 7)   # Top-right
        self.pits = set()
        self.wumpus_positions = set()
        
    def generate_winning_map(self, num_wumpus: int = 2, num_pits: int = 8) -> dict:
        """Generate a map with guaranteed safe path from start to gold"""
        
        # First, establish a guaranteed safe path
        safe_path = self._create_safe_path()
        
        # Place wumpus strategically (not on safe path)
        self._place_wumpus_safely(num_wumpus, safe_path)
        
        # Place pits strategically (not on safe path)
        self._place_pits_safely(num_pits, safe_path)
        
        # Verify the map is still winnable
        if not self._verify_winnable():
            # Fallback to minimal safe configuration
            self._create_minimal_safe_map(num_wumpus, num_pits)
        
        return self._get_map_config()
    
    def _create_safe_path(self) -> Set[Tuple[int, int]]:
        """Create a guaranteed safe path from start to gold"""
        # Create an L-shaped path: right then up
        safe_path = set()
        
        # Horizontal path from (0,0) to (7,0)
        for x in range(8):
            safe_path.add((x, 0))
        
        # Vertical path from (7,0) to (7,7)
        for y in range(8):
            safe_path.add((7, y))
        
        # Add some alternative paths for robustness
        # Secondary path: up then right (along edges)
        for y in range(4):  # Go up to middle
            safe_path.add((0, y))
        for x in range(4):  # Go right partially
            safe_path.add((x, 3))
        
        return safe_path
    
    def _place_wumpus_safely(self, num_wumpus: int, safe_path: Set[Tuple[int, int]]):
        """Place wumpus away from safe path"""
        self.wumpus_positions = set()
        
        # Get all positions not on safe path and not adjacent to safe path
        available_positions = []
        
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if pos not in safe_path and not self._adjacent_to_safe_path(pos, safe_path):
                    available_positions.append(pos)
        
        # Place wumpus in strategic positions
        if len(available_positions) >= num_wumpus:
            # Prefer corners and areas away from both start and goal
            strategic_positions = [
                pos for pos in available_positions 
                if self._manhattan_distance(pos, self.start_pos) > 3 and 
                   self._manhattan_distance(pos, self.gold_pos) > 3
            ]
            
            if len(strategic_positions) >= num_wumpus:
                self.wumpus_positions = set(random.sample(strategic_positions, num_wumpus))
            else:
                self.wumpus_positions = set(random.sample(available_positions, min(num_wumpus, len(available_positions))))
        
        # If we can't place all wumpus safely, place them in corners
        if len(self.wumpus_positions) < num_wumpus:
            corner_positions = [(1, 6), (6, 1), (2, 5), (5, 2)]  # Safe corners
            for pos in corner_positions:
                if len(self.wumpus_positions) >= num_wumpus:
                    break
                if pos not in safe_path:
                    self.wumpus_positions.add(pos)
    
    def _place_pits_safely(self, num_pits: int, safe_path: Set[Tuple[int, int]]):
        """Place pits away from safe path"""
        self.pits = set()
        
        # Get available positions (not on safe path, not wumpus, not adjacent to safe path)
        available_positions = []
        
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if (pos not in safe_path and 
                    pos not in self.wumpus_positions and
                    not self._adjacent_to_safe_path(pos, safe_path)):
                    available_positions.append(pos)
        
        # Place pits randomly in safe positions
        if available_positions:
            num_to_place = min(num_pits, len(available_positions))
            self.pits = set(random.sample(available_positions, num_to_place))
    
    def _adjacent_to_safe_path(self, pos: Tuple[int, int], safe_path: Set[Tuple[int, int]]) -> bool:
        """Check if position is adjacent to any safe path cell"""
        x, y = pos
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adj_x, adj_y = x + dx, y + dy
            if 0 <= adj_x < self.size and 0 <= adj_y < self.size:
                if (adj_x, adj_y) in safe_path:
                    return True
        return False
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _verify_winnable(self) -> bool:
        """Verify there's still a safe path from start to gold using BFS"""
        visited = {self.start_pos}
        queue = [self.start_pos]
        
        while queue:
            x, y = queue.pop(0)
            
            if (x, y) == self.gold_pos:
                return True
            
            # Check all adjacent cells
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if not (0 <= nx < self.size and 0 <= ny < self.size):
                    continue
                
                # Skip if already visited
                if (nx, ny) in visited:
                    continue
                
                # Skip dangerous cells
                if (nx, ny) in self.pits or (nx, ny) in self.wumpus_positions:
                    continue
                
                visited.add((nx, ny))
                queue.append((nx, ny))
        
        return False
    
    def _create_minimal_safe_map(self, num_wumpus: int, num_pits: int):
        """Create a minimal safe map as fallback"""
        self.pits = {(2, 2), (4, 4), (1, 5), (5, 1), (3, 6)}  # Strategic pit placement
        
        # Place wumpus in safe locations
        wumpus_candidates = [(2, 5), (5, 2)]
        self.wumpus_positions = set(wumpus_candidates[:num_wumpus])
    
    def _get_map_config(self) -> dict:
        """Get the complete map configuration"""
        return {
            'size': self.size,
            'start_position': self.start_pos,
            'gold_position': self.gold_pos,
            'pits': list(self.pits),
            'wumpus_positions': list(self.wumpus_positions),
            'num_wumpus': len(self.wumpus_positions),
            'num_pits': len(self.pits)
        }
    
    def print_map(self, config: dict):
        """Print a visual representation of the map"""
        print(f"\n🗺️  Generated 8x8 Wumpus World Map")
        print(f"📍 Agent starts at: {config['start_position']} (bottom-left)")
        print(f"💰 Gold located at: {config['gold_position']} (top-right)")
        print(f"👹 Wumpus count: {config['num_wumpus']}")
        print(f"🕳️  Pit count: {config['num_pits']}")
        print()
        
        # Create visual grid (flipped for correct orientation)
        for y in range(7, -1, -1):  # Start from top row
            row = []
            for x in range(8):
                pos = (x, y)
                cell = "."
                
                if pos == config['start_position']:
                    cell = "S"  # Start
                elif pos == config['gold_position']:
                    cell = "G"  # Gold
                elif pos in config['pits']:
                    cell = "P"  # Pit
                elif pos in config['wumpus_positions']:
                    cell = "W"  # Wumpus
                
                row.append(cell)
            
            print(f"Y{y}: " + " ".join(row))
        
        print("    " + " ".join([f"X{i}" for i in range(8)]))
        print("\nLegend: S=Start, G=Gold, W=Wumpus, P=Pit, .=Empty")
    
    def save_map_config(self, config: dict, filename: str):
        """Save map configuration to file"""
        with open(filename, 'w') as f:
            f.write("# 8x8 Wumpus World Test Configuration\n")
            f.write("# Generated with guaranteed winnable path\n")
            f.write(f"# Agent: {config['start_position']} -> Gold: {config['gold_position']}\n\n")
            
            f.write(f"WORLD_SIZE = {config['size']}\n")
            f.write(f"START_POSITION = {config['start_position']}\n")
            f.write(f"GOLD_POSITION = {config['gold_position']}\n")
            f.write(f"PITS = {config['pits']}\n")
            f.write(f"WUMPUS_POSITIONS = {config['wumpus_positions']}\n")
            f.write(f"NUM_WUMPUS = {config['num_wumpus']}\n")
            f.write(f"NUM_PITS = {config['num_pits']}\n")
        
        print(f"💾 Map configuration saved to: {filename}")


def create_custom_environment_with_config(config: dict):
    """Create a custom environment instance with the generated configuration"""
    
    # Import here to avoid circular imports
    from environment import WumpusWorld
    
    class CustomWumpusWorld(WumpusWorld):
        def __init__(self):
            # Initialize with config parameters
            super().__init__(
                size=config['size'], 
                num_wumpus=config['num_wumpus'], 
                pit_probability=0.0  # We'll set pits manually
            )
            
            # Override generated world with our custom configuration
            self.pits = set(config['pits'])
            self.wumpus_positions = set(config['wumpus_positions'])
            self.gold_position = config['gold_position']
            
            # Ensure agent starts at correct position
            self.agent_position = config['start_position']
            self.visited_cells = {config['start_position']}
    
    return CustomWumpusWorld


def test_generated_map(config: dict):
    """Test the generated map with the intelligent agent"""
    print("\n🧪 Testing generated map with intelligent agent...")
    
    try:
        from agent import WumpusAgent
        
        # Create custom environment
        CustomWumpusWorld = create_custom_environment_with_config(config)
        world = CustomWumpusWorld()
        
        # Create intelligent agent
        agent = WumpusAgent(config['size'], config['num_wumpus'])
        
        # Run simulation
        steps = 0
        max_steps = 200
        
        while not world.game_over and steps < max_steps:
            # Get percept and update agent
            percept = world._generate_percepts()
            agent.perceive(percept)
            
            # Choose and execute action
            action = agent.choose_action()
            world.step(action)
            agent.update_position(action, percept)
            
            steps += 1
        
        # Report results
        final_state = world.get_world_state()
        
        print(f"\n📊 Test Results:")
        print(f"  Steps taken: {steps}")
        print(f"  Final position: {final_state['agent_position']}")
        print(f"  Agent alive: {final_state['agent_alive']}")
        print(f"  Has gold: {final_state['agent_has_gold']}")
        print(f"  Final score: {final_state['score']}")
        
        if final_state['agent_alive'] and final_state['agent_has_gold']:
            print("  🏆 SUCCESS: Agent completed the mission!")
            return True
        elif final_state['agent_alive']:
            print("  🟡 PARTIAL: Agent survived but didn't get gold")
            return False
        else:
            print("  ❌ FAILURE: Agent died")
            return False
            
    except Exception as e:
        print(f"❌ Error testing map: {e}")
        return False


def main():
    """Generate and test a winning 8x8 map"""
    print("🎮 8x8 Wumpus World Map Generator")
    print("=" * 50)
    
    # Create generator
    generator = WinningMapGenerator(size=8)
    
    # Generate multiple maps and pick the best one
    best_config = None
    best_score = -float('inf')
    
    for attempt in range(5):
        print(f"\nGenerating map attempt {attempt + 1}/5...")
        
        config = generator.generate_winning_map(num_wumpus=2, num_pits=8)
        
        # Quick evaluation - prefer maps with reasonable paths
        score = 0
        if len(config['pits']) >= 6:  # Good number of pits
            score += 10
        if len(config['wumpus_positions']) == 2:  # Right number of wumpus
            score += 10
        
        if score > best_score:
            best_score = score
            best_config = config
    
    if best_config:
        print(f"\n✅ Best map generated (score: {best_score})")
        
        # Print the map
        generator.print_map(best_config)
        
        # Save configuration
        config_filename = "test_map_8x8_winnable.py"
        generator.save_map_config(best_config, config_filename)
        
        # Test the map
        success = test_generated_map(best_config)
        
        if success:
            print("\n🎉 Generated map is confirmed winnable!")
        else:
            print("\n⚠️  Map may be challenging but should still be winnable")
        
        print(f"\n💡 To use this map, import the configuration from: {config_filename}")
        
        return best_config
    else:
        print("❌ Failed to generate a suitable map")
        return None


if __name__ == "__main__":
    main()
