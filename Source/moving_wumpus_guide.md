# Moving Wumpus Knowledge Base Guide

This guide explains how to use the enhanced moving wumpus functionality in the knowledge base.

## Overview

When a wumpus moves in the Wumpus World, the agent's knowledge about wumpus locations and stench becomes outdated. The knowledge base provides several functions to handle this scenario by:

1. **Clearing all memory about wumpus possible positions**
2. **Clearing memory about stench and checking again for new stench**

## Available Functions

### 1. `handle_wumpus_movement()`
**Basic handler for moving wumpus scenario**

```python
kb.handle_wumpus_movement()
```

**What it does:**
- Clears all wumpus-related facts and negative facts
- Clears all stench-related facts and negative facts
- Runs inference to update the knowledge base

**When to use:**
- Simple scenarios where you just want to clear wumpus and stench knowledge
- When you don't need to re-perceive the current position

### 2. `handle_moving_wumpus_enhanced(current_position=None)`
**Enhanced handler with additional features**

```python
# Without re-perceiving current position
kb.handle_moving_wumpus_enhanced()

# With re-perceiving current position
kb.handle_moving_wumpus_enhanced(current_position=(1, 1))
```

**What it does:**
- Clears all wumpus-related facts and negative facts
- Clears all stench-related facts and negative facts
- Optionally re-perceives the current position (marks it as safe)
- Runs inference to update the knowledge base

**When to use:**
- When you want to ensure the current position is marked as safe
- When you need more comprehensive handling of the moving wumpus scenario

### 3. `clear_wumpus_and_stench_knowledge()`
**Utility function for custom handling**

```python
kb.clear_wumpus_and_stench_knowledge()
```

**What it does:**
- Clears all wumpus-related facts and negative facts
- Clears all stench-related facts and negative facts
- **Does NOT run inference** (you handle it separately)

**When to use:**
- When you want to clear knowledge but handle inference yourself
- For testing or debugging purposes
- When you need custom logic after clearing knowledge

### 4. `get_wumpus_knowledge_status()`
**Debugging function to check current state**

```python
status = kb.get_wumpus_knowledge_status()
print(f"Wumpus facts: {status['wumpus_facts_count']}")
print(f"Stench facts: {status['stench_facts_count']}")
```

**Returns:**
- Dictionary with counts and details of wumpus and stench knowledge

## Usage Examples

### Example 1: Basic Usage
```python
from knowledge_base import KnowledgeBase

# Create knowledge base
kb = KnowledgeBase(world_size=4, num_wumpus=2)

# Agent detects wumpus movement
kb.handle_wumpus_movement()

# Agent can now re-perceive the world to get updated information
```

### Example 2: Enhanced Usage with Current Position
```python
# Agent is at position (2, 3) when wumpus moves
current_pos = (2, 3)
kb.handle_moving_wumpus_enhanced(current_position=current_pos)

# The current position is automatically marked as safe
# Agent should now re-perceive to get updated stench information
```

### Example 3: Custom Handling
```python
# Clear knowledge manually
kb.clear_wumpus_and_stench_knowledge()

# Add custom logic here
# ...

# Run inference when ready
kb.forward_chain()

# Update with fresh percepts
fresh_percept = Percept(breeze=False, stench=True, glitter=False, scream=False)
kb.update_from_percept((1, 1), fresh_percept)
```

### Example 4: Integration with Agent
```python
class Agent:
    def __init__(self):
        self.kb = KnowledgeBase(world_size=4, num_wumpus=2)
        self.position = (0, 0)
    
    def detect_wumpus_movement(self):
        """Called when agent detects wumpus has moved"""
        # Use enhanced handler with current position
        self.kb.handle_moving_wumpus_enhanced(current_position=self.position)
        
        # Re-perceive current position to get updated stench
        percept = self.environment.get_percept(self.position)
        self.kb.update_from_percept(self.position, percept)
```

## What Gets Cleared

### Wumpus Knowledge
- All `Wumpus_x_y` facts (known wumpus locations)
- All `Wumpus_x_y` negative facts (known safe locations from wumpus perspective)

### Stench Knowledge
- All `Stench_x_y` facts (known stench locations)
- All `Stench_x_y` negative facts (known no-stench locations)

## What Stays Intact

- **Pit knowledge**: Breeze and pit-related facts remain unchanged
- **Gold knowledge**: Glitter and gold-related facts remain unchanged
- **Safe cells**: Cells known to be safe from pits remain marked as safe
- **Agent position**: Current position is marked as safe (no pit, no wumpus)

## Best Practices

1. **Always re-perceive after clearing**: After calling any of these functions, the agent should re-perceive the current position to get updated stench information.

2. **Use enhanced handler when possible**: The enhanced handler provides more comprehensive handling and is generally the best choice.

3. **Check knowledge status**: Use `get_wumpus_knowledge_status()` to verify that knowledge has been cleared properly.

4. **Run inference**: All handlers automatically run inference, but if using the utility function, remember to call `forward_chain()` manually.

## Testing

Run the test script to see the functions in action:

```bash
python test_moving_wumpus.py
```

This will demonstrate all the functions and show their effects on the knowledge base.

## Troubleshooting

### Issue: Knowledge not being cleared
- Check that you're calling the function correctly
- Verify the function completed without errors
- Use `get_wumpus_knowledge_status()` to check the current state

### Issue: Agent getting confused after wumpus movement
- Make sure you're re-perceiving the current position after clearing knowledge
- Verify that the current position is marked as safe
- Check that inference has been run to propagate new knowledge

### Issue: Performance problems
- The functions are designed to be efficient, but clearing large knowledge bases can take time
- Consider using the utility function if you need more control over the process
