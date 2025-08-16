#!/usr/bin/env python3
"""
Test script for moving wumpus functionality in the knowledge base.
This demonstrates how to use the enhanced wumpus movement handlers.
"""

from knowledge_base import KnowledgeBase
from environment import Percept

def test_moving_wumpus_functionality():
    """Test the moving wumpus functionality"""
    print("🧪 Testing Moving Wumpus Functionality")
    print("=" * 50)
    
    # Create a knowledge base for a 4x4 world
    kb = KnowledgeBase(world_size=4, num_wumpus=2)
    
    # Simulate some initial knowledge
    print("\n1. Initial knowledge base setup...")
    
    # Add some percepts to build up knowledge
    percept1 = Percept(breeze=True, stench=True, glitter=False, scream=False)
    kb.update_from_percept((1, 1), percept1)
    
    percept2 = Percept(breeze=False, stench=False, glitter=False, scream=False)
    kb.update_from_percept((0, 1), percept2)
    
    # Show initial state
    print("Initial knowledge status:")
    status = kb.get_wumpus_knowledge_status()
    print(f"  Wumpus facts: {status['wumpus_facts_count']}")
    print(f"  Stench facts: {status['stench_facts_count']}")
    print(f"  Safe cells: {kb.infer_safe_cells()}")
    print(f"  Possible wumpus locations: {kb.infer_wumpus_locations()}")
    
    # Test the basic moving wumpus handler
    print("\n2. Testing basic moving wumpus handler...")
    kb.handle_wumpus_movement()
    
    print("After basic handler:")
    status = kb.get_wumpus_knowledge_status()
    print(f"  Wumpus facts: {status['wumpus_facts_count']}")
    print(f"  Stench facts: {status['stench_facts_count']}")
    print(f"  Safe cells: {kb.infer_safe_cells()}")
    print(f"  Possible wumpus locations: {kb.infer_wumpus_locations()}")
    
    # Add some knowledge back
    print("\n3. Adding some knowledge back...")
    percept3 = Percept(breeze=True, stench=False, glitter=False, scream=False)
    kb.update_from_percept((2, 2), percept3)
    
    # Test the enhanced moving wumpus handler
    print("\n4. Testing enhanced moving wumpus handler...")
    kb.handle_moving_wumpus_enhanced(current_position=(2, 2))
    
    print("After enhanced handler:")
    status = kb.get_wumpus_knowledge_status()
    print(f"  Wumpus facts: {status['wumpus_facts_count']}")
    print(f"  Stench facts: {status['stench_facts_count']}")
    print(f"  Safe cells: {kb.infer_safe_cells()}")
    print(f"  Possible wumpus locations: {kb.infer_wumpus_locations()}")
    
    # Test the utility function
    print("\n5. Testing utility function...")
    kb.clear_wumpus_and_stench_knowledge()
    
    print("After utility function:")
    status = kb.get_wumpus_knowledge_status()
    print(f"  Wumpus facts: {status['wumpus_facts_count']}")
    print(f"  Stench facts: {status['stench_facts_count']}")
    
    print("\n✅ Moving wumpus functionality test completed!")

def test_integration_with_agent():
    """Test how this would integrate with an agent"""
    print("\n🔗 Testing Integration with Agent")
    print("=" * 50)
    
    kb = KnowledgeBase(world_size=4, num_wumpus=2)
    
    # Simulate agent discovering wumpus movement
    print("Agent detects wumpus movement...")
    
    # Method 1: Use the basic handler
    print("Using basic handler:")
    kb.handle_wumpus_movement()
    
    # Method 2: Use the enhanced handler with current position
    print("Using enhanced handler with current position:")
    kb.handle_moving_wumpus_enhanced(current_position=(1, 1))
    
    # Method 3: Use utility function for custom handling
    print("Using utility function for custom handling:")
    kb.clear_wumpus_and_stench_knowledge()
    # Agent can then call update_from_percept() to get fresh information
    fresh_percept = Percept(breeze=False, stench=True, glitter=False, scream=False)
    kb.update_from_percept((1, 1), fresh_percept)
    
    print("✅ Integration test completed!")

if __name__ == "__main__":
    test_moving_wumpus_functionality()
    test_integration_with_agent()
