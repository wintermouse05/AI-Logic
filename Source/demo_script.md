# Demo Video Script - Wumpus World Agent

## Demo Overview (10 minutes max)

### 1. Introduction (1 minute)
"Welcome to our Wumpus World Agent demonstration. This project implements an intelligent agent that uses propositional logic and A* pathfinding to navigate a dangerous world, find gold, and return safely."

**Show project structure:**
```bash
tree Source/
```

### 2. Environment Simulator Demo (2 minutes)
"First, let's see the environment simulator in action with a basic demo."

**Command:**
```bash
python main.py --mode demo --size 4 --delay 1.0 --show-hidden
```

**Explain while running:**
- Grid layout with coordinates
- Agent symbol and direction
- Hidden objects (pits, wumpus, gold) when shown
- Percept system (stench, breeze, glitter)
- Scoring system

### 3. Knowledge Base and Inference (2 minutes)
"Now let's see how the agent builds knowledge and makes inferences."

**Command:**
```bash
python main.py --mode demo --size 6 --delay 1.5
```

**Point out during execution:**
- How agent perceives stench/breeze
- Knowledge base updates in real-time
- Safe vs dangerous cell classification
- Forward chaining inference in action
- Strategic decision making

### 4. Planning and Pathfinding (1.5 minutes)
"Watch how the agent uses A* search for optimal pathfinding."

**Show when agent plans paths:**
- Path to safe exploration targets
- Risk-aware pathfinding (avoiding dangerous areas)
- Gold retrieval planning
- Return journey to start position

### 5. Advanced Features Demo (1.5 minutes)
**Moving Wumpus:**
```bash
python main.py --mode demo --size 6 --moving-wumpus --delay 1.0
```

**Explain:**
- Wumpus movement every 5 actions
- Knowledge base adaptation
- Dynamic reasoning under uncertainty

### 6. Performance Comparison (2 minutes)
"Let's compare our intelligent agent with a random baseline."

**Command:**
```bash
python main.py --mode experiment --trials 5 --size 4
```

**Highlight results:**
- Success rate comparison
- Score improvement
- Survival rate differences
- Strategic vs random behavior

### 7. System Architecture (1 minute)
**Show code structure briefly:**
- Environment simulator (`environment.py`)
- Knowledge base (`knowledge_base.py`) 
- Planning module (`planning.py`)
- Hybrid agent (`agent.py`)
- Visualization (`visualization.py`)

**Key implementation points:**
- Propositional logic representation
- Forward chaining inference
- A* search with risk costs
- Integration of all components

## Demo Commands Summary

### Basic Demo
```bash
python main.py --mode demo --size 6 --delay 1.0
```

### Show Hidden Objects (for explanation)
```bash
python main.py --mode demo --size 4 --show-hidden --delay 1.5
```

### Moving Wumpus Demo
```bash
python main.py --mode demo --size 6 --moving-wumpus --delay 1.0
```

### Performance Experiment
```bash
python main.py --mode experiment --trials 5 --size 4
```

### Interactive Mode
```bash
python main.py --mode interactive
```

## Key Points to Emphasize

### Technical Achievements
1. **Complete Knowledge-Based System**: Full propositional logic implementation
2. **Forward Chaining Inference**: Automatic knowledge derivation
3. **Optimal Planning**: A* search with risk-aware costs
4. **Advanced Features**: Moving wumpus handling
5. **Performance**: Significant improvement over random baseline

### Problem-Solving Approach
1. **Logical Reasoning**: Uses percepts to build world model
2. **Uncertainty Handling**: Distinguishes safe, dangerous, and unknown areas
3. **Risk Management**: Balances exploration with safety
4. **Strategic Planning**: Optimal pathfinding for gold retrieval

### System Design
1. **Modular Architecture**: Clean separation of concerns
2. **Extensible Design**: Easy to add new features
3. **Comprehensive Testing**: Multiple test scenarios
4. **Real-time Visualization**: Clear demonstration of agent behavior

## Conclusion Points
- Successfully implements all project requirements
- Demonstrates significant performance improvement
- Handles advanced scenarios (moving wumpus)
- Provides comprehensive evaluation framework
- Ready for practical deployment and further research

## Troubleshooting Tips
- If agent dies quickly: World may have difficult pit configuration
- If visualization is too fast: Increase --delay parameter
- If display issues: Ensure terminal supports Unicode characters
- For debugging: Use --show-hidden to see actual world state
