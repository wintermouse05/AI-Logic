
# Wumpus World Agent

This project is an intelligent agent for the Wumpus World puzzle, featuring a graphical user interface (GUI) built with Python and Pygame. The agent uses propositional logic and A* search to solve the puzzle, find gold, and escape safely.


# Wumpus World Agent

This project is a Wumpus World puzzle solver with a graphical user interface (GUI) built using Python and Pygame. It allows you to configure the world, select agent strategies, and solve the puzzle using propositional logic and A* search.

## Features
- Visual interface for playing and solving Wumpus World puzzles
- Multiple built-in world configurations
- Supports intelligent and random agent strategies
- Advanced moving wumpus module
- Animated agent actions and percept visualization
- Experiment framework for performance comparison

## Requirements
- Python 3.7 or higher
- `pygame` library

## How to Run
1. Open a terminal or command prompt.
2. Navigate to the Source directory:
	```bash
	cd 2312171_23127188_23127249_23127382\Source
	```
3. Run the game:
	```bash
	python pygame_gui.py
	```
4. If you want to run the game in console:
	```bash
	python main.py
	```	

## Project Structure
- `main.py` — Entry point for the GUI and simulation
- `agent.py` — Intelligent and random agent logic
- `environment.py` — World simulation and percepts
- `knowledge_base.py` — Logic inference engine
- `planning.py` — A* pathfinding and risk assessment
- `pygame_gui.py` — Pygame GUI implementation
- `models/`, `background/` — Asset files for GUI
- `testcases/` — Sample world configurations

## Notes
- All logic and planning modules are implemented in Python
- The GUI provides real-time visualization of agent knowledge and actions
