#!/usr/bin/env python3
"""
Custom 8x8 Test Environment
Uses the generated winnable map configuration for consistent testing
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from environment import WumpusWorld
from test_map_8x8_winnable import *

class Test8x8WumpusWorld(WumpusWorld):
    """Custom 8x8 Wumpus World with predefined winnable configuration"""
    
    def __init__(self):
        # Initialize with base configuration
        super().__init__(
            size=WORLD_SIZE, 
            num_wumpus=NUM_WUMPUS, 
            pit_probability=0.0  # We'll set pits manually
        )
        
        # Override with our specific configuration
        self._setup_custom_world()
    
    def _setup_custom_world(self):
        """Setup the world with our custom configuration"""
        # Set positions from configuration
        self.pits = set(PITS)
        self.wumpus_positions = set(WUMPUS_POSITIONS)
        self.gold_position = GOLD_POSITION
        
        # Ensure agent starts at correct position
        self.agent_position = START_POSITION
        self.visited_cells = {START_POSITION}
        
        print(f"🗺️  Custom 8x8 Test World Loaded")
        print(f"📍 Agent: {START_POSITION} -> Gold: {GOLD_POSITION}")
        print(f"👹 Wumpus at: {WUMPUS_POSITIONS}")
        print(f"🕳️  Pits at: {PITS}")
    
    def _generate_world(self):
        """Override world generation - we use predefined configuration"""
        # Already set in _setup_custom_world()
        pass
    
    def print_world_map(self):
        """Print a visual representation of the current world"""
        print("\n🗺️  Current World State:")
        
        # Print grid from top to bottom (correct orientation)
        for y in range(WORLD_SIZE, -1, -1):
            row = []
            for x in range(WORLD_SIZE):
                pos = (x, y)
                cell = ". "
                
                if pos == self.agent_position:
                    if self.agent_alive:
                        cell = "🤖 "  # Living agent
                    else:
                        cell = "💀 "  # Dead agent
                elif pos == self.gold_position:
                    if self.agent_has_gold:
                        cell = "📦 "  # Gold taken
                    else:
                        cell = "💰 "  # Gold available
                elif pos in self.pits:
                    cell = "🕳️ "
                elif pos in self.wumpus_positions:
                    cell = "👹 "
                elif pos in self.visited_cells:
                    cell = "✓ "  # Visited safe cell
                
                row.append(cell)
            
            print(f"Y{y}: " + " ".join(f"{cell:2}" for cell in row))
        
        print("    " + " ".join([f"X{i}" for i in range(8)]))
        print()


def test_intelligent_agent():
    """Test the intelligent agent on our custom 8x8 map"""
    print("🧪 Testing Intelligent Agent on Custom 8x8 Map")
    print("=" * 60)
    
    from agent import WumpusAgent
    
    # Create custom world and agent
    world = Test8x8WumpusWorld()
    agent = WumpusAgent(WORLD_SIZE, NUM_WUMPUS)
    
    # Show initial world state
    world.print_world_map()
    
    # Run simulation
    steps = 0
    max_steps = 300
    action_log = []
    
    print("🎮 Starting simulation...")
    print("-" * 40)
    
    while not world.game_over and steps < max_steps:
        # Get current state for logging
        current_pos = world.agent_position
        
        # Get percept and update agent
        percept = world._generate_percepts()
        agent.perceive(percept)
        
        # Choose and execute action
        action = agent.choose_action()
        world.step(action)
        agent.update_position(action, percept)
        
        # Log action
        action_log.append({
            'step': steps + 1,
            'position': current_pos,
            'action': action.value,
            'percept': str(percept) if percept else 'None'
        })
        
        # Print key steps
        #if steps < 10 or steps % 10 == 0 or world.game_over:
        if steps < 50:
            print(f"Step {steps + 1:3d}: {current_pos} -> {action.value}")
            if percept and percept != []:
                print(f"         Percept: {percept}")
            
        steps += 1
    
    # Final results
    final_state = world.get_world_state()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    world.print_world_map()
    
    print(f"🎯 Mission Status:")
    print(f"   Total steps: {steps}")
    print(f"   Final position: {final_state['agent_position']}")
    print(f"   Agent alive: {'✅ Yes' if final_state['agent_alive'] else '❌ No'}")
    print(f"   Has gold: {'✅ Yes' if final_state['agent_has_gold'] else '❌ No'}")
    print(f"   Final score: {final_state['score']}")
    
    # Determine success level
    if final_state['agent_alive'] and final_state['agent_has_gold']:
        success_level = "🏆 COMPLETE SUCCESS"
        success_desc = "Agent retrieved gold and survived!"
    elif final_state['agent_alive']:
        success_level = "🟡 PARTIAL SUCCESS"
        success_desc = "Agent survived but didn't retrieve gold"
    else:
        success_level = "❌ MISSION FAILED"
        success_desc = "Agent died during mission"
        
        # Show where agent died
        death_pos = final_state['agent_position']
        if death_pos in world.pits:
            success_desc += f" (fell into pit at {death_pos})"
        elif death_pos in world.wumpus_positions:
            success_desc += f" (eaten by wumpus at {death_pos})"
    
    print(f"\n{success_level}")
    print(f"   {success_desc}")
    
    # Show path efficiency
    optimal_path_length = 14  # Manhattan distance (0,0) to (7,7) = 14
    if final_state['agent_alive'] and final_state['agent_has_gold']:
        efficiency = (optimal_path_length / steps) * 100
        print(f"   Path efficiency: {efficiency:.1f}% (optimal: {optimal_path_length} steps)")
    
    # Export knowledge base
    agent.export_knowledge_base("knowledge_base.txt")
    
    return final_state['agent_alive'] and final_state['agent_has_gold']


def test_random_agent():
    """Test random agent for comparison"""
    print("\n🎲 Testing Random Agent for Comparison")
    print("=" * 60)
    
    from agent import RandomAgent
    
    # Create world and random agent
    world = Test8x8WumpusWorld()
    agent = RandomAgent(WORLD_SIZE)
    
    # Run simulation
    steps = 0
    max_steps = 100  # Random agent usually dies quickly
    
    while not world.game_over and steps < max_steps:
        percept = world._generate_percepts()
        action = agent.choose_action()
        world.step(action)
        
        steps += 1
    
    final_state = world.get_world_state()
    
    print(f"Random Agent Results:")
    print(f"   Steps: {steps}")
    print(f"   Alive: {'Yes' if final_state['agent_alive'] else 'No'}")
    print(f"   Has Gold: {'Yes' if final_state['agent_has_gold'] else 'No'}")
    print(f"   Score: {final_state['score']}")
    
    return final_state['agent_alive'] and final_state['agent_has_gold']


if __name__ == "__main__":
    print("🗺️  8x8 Wumpus World Test Suite")
    print("Agent at (0,0) → Gold at (7,7)")
    print("=" * 60)
    
    # Test intelligent agent
    intelligent_success = test_intelligent_agent()
    
    # Test random agent
    #random_success = test_random_agent()
    
    # Final comparison
    print("\n" + "=" * 60)
    print("📈 COMPARISON SUMMARY")
    print("=" * 60)
    print(f"Intelligent Agent: {'✅ SUCCESS' if intelligent_success else '❌ FAILED'}")
    #print(f"Random Agent:      {'✅ SUCCESS' if random_success else '❌ FAILED'}")
    
    # if intelligent_success and not random_success:
    #     print("\n🎉 Perfect! Intelligent agent succeeded where random agent failed!")
    #     print("   This demonstrates the effectiveness of logical reasoning.")
    # elif intelligent_success:
    #     print("\n✅ Intelligent agent successfully completed the mission!")
    # else:
    #     print("\n⚠️  Map may be challenging - consider adjusting difficulty.")
