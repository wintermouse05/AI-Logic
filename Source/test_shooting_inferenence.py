#!/usr/bin/env python3
"""
Test script to verify shooting inference logic in the knowledge base.
This tests the scenario where:
1. Agent faces a cell and perceives stench
2. Agent shoots at that cell and gets a scream
3. Stench percept disappears in next move
4. Knowledge base should infer the target cell is safe
"""

from knowledge_base import KnowledgeBase
from environment import Direction, Percept
from agent import WumpusAgent

def test_shooting_inference():
    """Test the shooting inference logic"""
    print("🧪 Testing shooting inference logic...")
    
    # Create a small world (4x4) with 1 wumpus
    world_size = 4
    num_wumpus = 1
    
    # Create knowledge base
    kb = KnowledgeBase(world_size, num_wumpus)
    
    # Create agent
    agent = WumpusAgent(world_size, num_wumpus)
    
    print(f"📍 Agent starts at {agent.position} facing {agent.direction}")
    
    # Simulate agent perceiving stench at position (0,0) facing east
    # This means there's a wumpus at (1,0)
    stench_percept = Percept(stench=True, breeze=False, glitter=False, bump=False, scream=False)
    print(f"👃 Agent perceives: {stench_percept}")
    
    # Update knowledge base with stench percept
    kb.update_from_percept(agent.position, stench_percept)
    print("📚 Knowledge base updated with stench percept")
    
    # Check what the KB knows about adjacent cells
    print("\n🔍 Knowledge before shooting:")
    summary = kb.get_knowledge_summary()
    print(f"   Facts: {summary['facts'][:5]}...")  # Show first 5 facts
    print(f"   Safe cells: {summary['safe_cells']}")
    print(f"   Dangerous cells: {summary['dangerous_cells']}")
    
    # Simulate shooting east (towards cell (1,0))
    print(f"\n🏹 Agent shoots {agent.direction} from {agent.position}")
    
    # Use the new shooting inference method
    kb.handle_shooting_result(
        agent.position, 
        agent.direction, 
        scream_heard=True,  # Wumpus killed
        stench_disappeared=False  # Stench hasn't disappeared yet
    )
    
    print("📚 Knowledge base updated after shooting (scream heard)")
    
    # Check knowledge after shooting
    print("\n🔍 Knowledge after shooting (scream heard):")
    summary = kb.get_knowledge_summary()
    print(f"   Facts: {summary['facts'][:5]}...")
    print(f"   Safe cells: {summary['safe_cells']}")
    print(f"   Dangerous cells: {summary['dangerous_cells']}")
    
    # Now simulate stench disappearing
    print(f"\n👃 Agent perceives stench disappeared at {agent.position}")
    no_stench_percept = Percept(stench=False, breeze=False, glitter=False, bump=False, scream=False)
    
    # Update knowledge base with no stench percept
    kb.update_from_percept(agent.position, no_stench_percept)
    
    # Use shooting inference method with stench disappeared
    kb.handle_shooting_result(
        agent.position, 
        agent.direction, 
        scream_heard=True,  # Wumpus was killed
        stench_disappeared=True  # Stench disappeared
    )
    
    print("📚 Knowledge base updated after stench disappeared")
    
    # Check final knowledge
    print("\n🔍 Final knowledge after stench disappeared:")
    summary = kb.get_knowledge_summary()
    print(f"   Facts: {summary['facts'][:5]}...")
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

def test_agent_integration():
    """Test the agent's integration with the new shooting logic"""
    print("\n🧪 Testing agent integration...")
    
    world_size = 4
    num_wumpus = 1
    agent = WumpusAgent(world_size, num_wumpus)
    
    # Simulate the complete scenario
    print(f"📍 Agent at {agent.position} facing {agent.direction}")
    
    # Step 1: Perceive stench
    stench_percept = Percept(stench=True, breeze=False, glitter=False, bump=False, scream=False)
    print(f"👃 Step 1: Agent perceives {stench_percept}")
    agent.perceive(stench_percept)
    
    # Step 2: Shoot
    print(f"🏹 Step 2: Agent shoots {agent.direction}")
    agent.execute_action("shoot")
    
    # Step 3: Perceive no stench (stench disappeared)
    no_stench_percept = Percept(stench=False, breeze=False, glitter=False, bump=False, scream=False)
    print(f"👃 Step 3: Agent perceives {no_stench_percept}")
    agent.perceive(no_stench_percept)
    
    # Check final knowledge
    summary = agent.kb.get_knowledge_summary()
    target_cell = (1, 0)
    
    print(f"\n🔍 Final agent knowledge:")
    print(f"   Safe cells: {summary['safe_cells']}")
    print(f"   Dangerous cells: {summary['dangerous_cells']}")
    
    if target_cell in summary['safe_cells']:
        print(f"✅ SUCCESS: Agent correctly infers {target_cell} is safe!")
    else:
        print(f"❌ FAILURE: Agent does not infer {target_cell} is safe")
    
    return target_cell in summary['safe_cells']

if __name__ == "__main__":
    print("🚀 Starting shooting inference tests...\n")
    
    # Test 1: Direct knowledge base usage
    test1_passed = test_shooting_inference()
    
    # Test 2: Agent integration
    test2_passed = test_agent_integration()
    
    print(f"\n📊 Test Results:")
    print(f"   Test 1 (Direct KB): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Test 2 (Agent): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The shooting inference logic is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the implementation.")