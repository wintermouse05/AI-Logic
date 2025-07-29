# Wumpus World AI Project

An intelligent agent for the classic Wumpus World problem, featuring propositional logic-based reasoning and risk-aware pathfinding with a modern pygame GUI.

## Overview

This project implements a complete Wumpus World environment with an intelligent agent that uses logical reasoning to navigate safely while hunting for gold. The agent combines propositional logic, forward chaining inference, and A* search to make optimal decisions.

## Features

### Core Components
- **Complete Wumpus World Environment**: Dynamic world with pits, wumpuses, gold, and moving wumpus support
- **Intelligent Agent**: Uses propositional logic and forward chaining for reasoning
- **Knowledge Base**: Maintains and infers facts about the world state
- **Risk-Aware Planning**: A* pathfinding with risk-weighted costs
- **Modern Pygame GUI**: Interactive graphical interface with real-time visualization
- **Console Visualization**: Text-based game display with agent comparison
- **Performance Analysis**: Built-in experiment framework

### Advanced Features
- Moving wumpus with unpredictable behavior
- Constraint satisfaction for efficient reasoning
- Multi-goal pathfinding (explore, hunt, escape)
- Dynamic risk assessment
- Interactive GUI with game controls and settings
- Real-time agent knowledge visualization
- Comprehensive logging and statistics

## Quick Start

### Prerequisites
- Python 3.6+
- pygame (for GUI interface)

### Installation
```bash
# Install pygame for the GUI
pip install pygame

# Or if using the project's virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install pygame
```

### Running the Game

#### 🎮 Pygame GUI (Recommended)
```bash
# Launch the interactive graphical interface
python run_gui.py

# Or run directly from Source directory
cd Source
python pygame_gui.py
```

**GUI Features:**
- 🎯 Interactive game board with visual feedback
- ⚙️ Adjustable settings (world size, difficulty, agent type)
- 🧠 Real-time agent knowledge display
- 📊 Built-in performance experiments
- ⏸️ Pause/step controls for debugging
- 📝 Live game log with action history
- 🎨 Color-coded safe/dangerous cell visualization
- 🏆 Game over screens with detailed statistics

**GUI Controls:**
- `SPACE` - Pause/Resume game
- `S` - Single step (when paused)
- `R` - Reset current game
- `ESC` - Back to main menu
- Mouse - Interact with settings and controls

#### 💻 Console Interface
```bash
cd Source

# Interactive mode with menu
python main.py

# Quick demo
python main.py --demo

# Run performance experiments
python main.py --experiment
```

## Project Structure

```
wumpus-world/
├── Source/                     # Main source code
│   ├── environment.py         # Wumpus World environment
│   ├── knowledge_base.py      # Propositional logic KB
│   ├── planning.py            # A* pathfinding
│   ├── agent.py               # Intelligent & Random agents
│   ├── visualization.py       # Console visualization
│   ├── main.py                # CLI interface
│   ├── pygame_gui.py          # Modern GUI interface
│   └── gui.py                 # Tkinter GUI (backup)
├── run_gui.py                 # GUI launcher
├── Report.md                  # Detailed project report
└── README.md                  # This file
```

## Game Settings

The pygame GUI allows you to customize:

- **World Size**: 4x4 to 10x10 grid
- **Wumpus Count**: 1-4 wumpuses
- **Pit Probability**: 0.1 to 0.5 chance per cell
- **Agent Type**: Intelligent (logic-based) or Random
- **Moving Wumpus**: Enable unpredictable wumpus movement
- **Show Hidden**: Reveal all objects (debug mode)
- **Speed**: Simulation speed control

## Agent Comparison

### Intelligent Agent
- **Logic**: Propositional reasoning with forward chaining
- **Planning**: Risk-aware A* pathfinding
- **Knowledge**: Maintains comprehensive world model
- **Performance**: ~20% success rate, high survival rate
- **Strategy**: Cautious exploration, strategic planning

### Random Agent
- **Logic**: Random action selection
- **Planning**: No pathfinding
- **Knowledge**: No world model
- **Performance**: ~0% success rate, low survival
- **Strategy**: Pure randomness

## Technical Implementation

### Propositional Logic
- Wumpus and pit location inference
- Safe cell identification
- Constraint satisfaction
- Forward chaining algorithm

### A* Search Algorithm
- Risk-weighted pathfinding
- Multiple goal handling
- Dynamic cost calculation
- Safe route optimization

### Knowledge Base
- Fact storage and retrieval
- Rule-based inference
- Incremental learning
- Contradiction detection

## Performance Results

Based on 100-trial experiments:

| Agent Type | Success Rate | Avg Score | Survival Rate |
|------------|-------------|-----------|---------------|
| Intelligent| 20%         | 245       | 40%           |
| Random     | 0%          | -973      | 5%            |

## Development Notes

This project demonstrates:
- AI reasoning under uncertainty
- Logical inference systems
- Risk-aware planning algorithms
- Game AI development
- Python GUI programming
- Performance analysis and visualization

## Troubleshooting

### Common Issues

1. **Pygame not found**
   ```bash
   pip install pygame
   ```

2. **Import errors**
   - Make sure you're in the correct directory
   - Use `python run_gui.py` from the project root

3. **Performance issues**
   - Reduce world size for faster simulation
   - Use lower wumpus counts for simpler worlds

### System Requirements
- Python 3.6+
- pygame 2.0+
- ~50MB disk space
- Graphical display for GUI

## License

This project is for educational purposes as part of an AI course assignment.

## Author

Completed as part of CS AI coursework - Wumpus World reasoning and planning project.
