# Wumpus World Agent - AI Project Implementation

## Overview
This project implements an intelligent agent for the Wumpus World environment using propositional logic inference and A* pathfinding. The agent uses a knowledge base to reason about the world state and make optimal decisions.

## Features

### Core Components
1. **Environment Simulator** (`environment.py`)
   - Configurable world size (default 8x8)
   - Multiple wumpus support (default 2)
   - Adjustable pit probability (default 0.2)
   - Complete percept system (stench, breeze, glitter, bump, scream)
   - Advanced moving wumpus module

2. **Knowledge Base & Inference Engine** (`knowledge_base.py`)
   - Propositional logic representation
   - Forward chaining inference
   - Handles multiple wumpus and pits
   - Safe/dangerous cell inference

3. **Planning Module** (`planning.py`)
   - A* pathfinding algorithm
   - Risk-aware path planning
   - Optimal action sequence generation

4. **Hybrid Agent** (`agent.py`)
   - Integrates all components
   - Multiple exploration strategies
   - Intelligent shooting decisions
   - Gold retrieval planning

5. **Visualization** (`visualization.py`)
   - Console-based world display
   - Real-time agent knowledge visualization
   - Performance comparison tools

## Installation & Requirements

### Dependencies
```bash
pip install -r requirements.txt
```

### Requirements.txt Contents
No external libraries required - uses only Python standard library.

## Usage

### Basic Demo
```bash
python main.py --mode demo --size 6 --wumpus 2 --delay 1.0
```

### Interactive Mode
```bash
python main.py --mode interactive
```

### Comparison Experiment
```bash
python main.py --mode experiment --trials 20 --size 6
```

### Advanced Settings
```bash
# Enable moving wumpus
python main.py --mode demo --moving-wumpus --size 8

# Show hidden world objects (for debugging)
python main.py --mode demo --show-hidden

# Use random agent baseline
python main.py --mode demo --agent-type random
```

### Command Line Options
- `--mode`: demo, experiment, interactive (default: demo)
- `--size`: World size NxN (default: 6)
- `--wumpus`: Number of wumpus (default: 2)
- `--pit-prob`: Pit probability 0.0-1.0 (default: 0.2)
- `--seed`: Random seed for reproducibility
- `--steps`: Maximum steps (default: 1000)
- `--delay`: Delay between steps in seconds (default: 1.0)
- `--trials`: Number of trials for experiment (default: 10)
- `--moving-wumpus`: Enable moving wumpus (advanced setting)
- `--show-hidden`: Show hidden world objects
- `--agent-type`: intelligent or random (default: intelligent)

## Test Cases

Generate test cases:
```bash
python main.py --create-tests
```

This creates three test scenarios in the `testcases/` folder:
- Small world (4x4, 1 wumpus)
- Medium world (6x6, 2 wumpus)
- Large world (8x8, 3 wumpus)

## Architecture

### Knowledge Base Rules
The agent uses propositional logic with the following key rules:

1. **Breeze Rules**: `Breeze(x,y) ↔ ∃adjacent_cell: Pit(adjacent_cell)`
2. **Stench Rules**: `Stench(x,y) ↔ ∃adjacent_cell: Wumpus(adjacent_cell)`
3. **Safety Rules**: `Safe(x,y) ↔ ¬Pit(x,y) ∧ ¬Wumpus(x,y)`
4. **Initial Conditions**: `Safe(0,0) ∧ ¬Pit(0,0) ∧ ¬Wumpus(0,0)`

### Agent Strategy
1. **Perception**: Update knowledge base with percepts
2. **Inference**: Apply forward chaining to derive new facts
3. **Planning**: Use A* search for optimal pathfinding
4. **Action Selection**: Choose actions based on:
   - Gold retrieval (if known location)
   - Safe exploration
   - Strategic shooting
   - Risk-aware movement

### Exploration Strategies
- **Safe First**: Explore known safe cells before venturing into unknown areas
- **Cautious**: Balanced approach with moderate risk tolerance
- **Aggressive**: Higher risk tolerance for faster exploration

## Performance

### Scoring System
- Move forward: -1
- Turn left/right: -1
- Shoot: -10
- Grab gold: +10
- Climb out with gold: +1000
- Die (pit/wumpus): -1000

### Expected Performance
The intelligent agent typically achieves:
- 70-90% success rate (depending on world complexity)
- Significantly higher scores than random baseline
- Efficient path planning with minimal unnecessary moves

## Advanced Features

### Moving Wumpus Module
- Wumpus move every 5 agent actions
- Movement is random to adjacent valid cells
- Knowledge base updates dynamically
- Adds temporal reasoning challenges

### Risk Assessment
- Cells classified as Safe, Dangerous, or Unknown
- Risk-adjusted pathfinding costs
- Shooting utility calculations
- Conservative vs aggressive exploration modes

## Code Structure
```
Source/
├── main.py              # Main program entry point
├── environment.py       # World simulation
├── knowledge_base.py    # Logic inference engine
├── planning.py          # A* pathfinding
├── agent.py             # Intelligent & random agents
├── visualization.py     # Console visualization
└── testcases/          # Test scenarios
    ├── small_world_config.txt
    ├── medium_world_config.txt
    └── large_world_config.txt
```

## Troubleshooting

### Common Issues
1. **Display Issues**: Ensure terminal supports Unicode characters
2. **Performance**: Reduce world size or visualization delay for faster execution
3. **Memory**: Large worlds (>10x10) may require more memory

### Debug Mode
Use `--show-hidden` to see the actual world state for debugging agent behavior.

## Implementation Notes

### Knowledge Representation
- Propositions: `Type_x_y` format (e.g., `Pit_2_3`, `Safe_1_1`)
- Facts: Known true propositions
- Negative facts: Known false propositions
- Rules: Implication relationships

### Inference Engine
- Forward chaining with iterative rule application
- Constraint satisfaction for wumpus location inference
- Model checking for complex logical relationships

### Planning Algorithm
- A* search with admissible heuristics
- Risk-weighted edge costs
- Multi-goal pathfinding support

This implementation provides a complete solution to the Wumpus World problem with advanced features and comprehensive testing capabilities.
