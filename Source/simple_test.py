#!/usr/bin/env python3
"""
Simple test for shooting inference logic
"""

from knowledge_base import KnowledgeBase
from environment import Direction

def test_shooting_inference():
    """Test the shooting inference logic"""
    print("🧪 Testing shooting inference logic...")
    
    # Create a small world (4x4) with 1 wumpus
    world_size = 4
    num_wumpus = 1
    
    # Create knowledge base
    kb = KnowledgeBase(world_size, num_wumpus)
    
    print(f"📍 Testing from position (0,0) facing {Direction.EAST}")
    
    # Simulate shooting east (towards cell (1,0))
    agent_position = (0, 0)
    agent_direction = Direction.EAST
    
    # Use the new shooting inference method
    kb.handle_shooting_result(
        agent_position, 
        agent_direction, 
        scream_heard=True,  # Wumpus killed
        stench_disappeared=True  # Stench disappeared
    )
    
    print("📚 Knowledge base updated after shooting")
    
    # Check knowledge after shooting
    summary = kb.get_knowledge_summary()
    print(f"   Safe cells: {summary['safe_cells']}")
    print(f"   Dangerous cells: {summary['dangerous_cells']}")
    
    # Check if cell (1,0) is now marked as safe
    target_cell = (1, 0)  # Cell the agent was facing
    if target_cell in summary['safe_cells']:
        print(f"✅ SUCCESS: Cell {target_cell} is now marked as safe!")
    else:
        print(f"❌ FAILURE: Cell {target_cell} is not marked as safe")
        print(f"   Current safe cells: {summary['safe_cells']}")
    
    # Check if wumpus at (1,0) is marked as false
    wumpus_prop = kb._create_proposition("Wumpus", 1, 0)
    if kb.is_known_false(wumpus_prop):
        print(f"✅ SUCCESS: Wumpus at {target_cell} is correctly marked as false!")
    else:
        print(f"❌ FAILURE: Wumpus at {target_cell} is not marked as false")
    
    return target_cell in summary['safe_cells']

if __name__ == "__main__":
    print("🚀 Starting simple shooting inference test...\n")
    
    try:
        test_passed = test_shooting_inference()
        if test_passed:
            print("\n🎉 Test passed! The shooting inference logic is working correctly.")
        else:
            print("\n💥 Test failed. Check the implementation.")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()