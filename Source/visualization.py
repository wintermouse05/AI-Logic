"""
Visualization Module for Wumpus World
Provides console-based visualization of the game state.
"""

from typing import Dict, Set, Tuple, Optional
from environment import WumpusWorld, Direction
from agent import WumpusAgent, RandomAgent
import os
import time

class WumpusVisualizer:
    """Console-based visualizer for Wumpus World"""
    
    def __init__(self):
        self.symbols = {
            'agent_north': '↑',
            'agent_east': '→',
            'agent_south': '↓',
            'agent_west': '←',
            'wumpus': 'W',
            'pit': 'P',
            'gold': 'G',
            'stench': 'S',
            'breeze': 'B',
            'safe': '.',
            'unknown': '?',
            'visited': '·',
            'wall': '#'
        }
        
        self.colors = {
            'reset': '\033[0m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m'
        }
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_agent_symbol(self, direction: Direction) -> str:
        """Get symbol for agent based on direction"""
        direction_map = {
            Direction.NORTH: 'agent_north',
            Direction.EAST: 'agent_east',
            Direction.SOUTH: 'agent_south',
            Direction.WEST: 'agent_west'
        }
        return self.symbols[direction_map[direction]]
    
    def colorize(self, text: str, color: str) -> str:
        """Add color to text"""
        return f"{self.colors[color]}{text}{self.colors['reset']}"
    
    def display_world(self, world: WumpusWorld, agent=None, show_hidden=False):
        """Display the current world state"""
        state = world.get_world_state()
        size = state['size']
        
        print(f"\n{self.colorize('=== WUMPUS WORLD ===', 'bold')}")
        print(f"Score: {self.colorize(str(state['score']), 'yellow')}")
        print(f"Agent: {state['agent_position']} facing {state['agent_direction'].name}")
        print(f"Arrow: {'Yes' if state['agent_has_arrow'] else 'No'}")
        print(f"Gold: {'Yes' if state['agent_has_gold'] else 'No'}")
        print(f"Actions taken: {state['action_count']}")
        
        if state['last_percept']:
            print(f"Last percept: {state['last_percept']}")
        
        print("\nWorld Map:")
        
        # Create grid display
        for y in range(size - 1, -1, -1):  # Top to bottom
            # Row with coordinates
            row_str = f"{y:2d} "
            
            for x in range(size):
                cell_content = self._get_cell_display(
                    (x, y), state, agent, show_hidden
                )
                row_str += f"[{cell_content}]"
            
            print(row_str)
        
        # Column coordinates
        col_str = "   "
        for x in range(size):
            col_str += f" {x} "
        print(col_str)
        
        # Legend
        self._display_legend(agent)
    
    def _get_cell_display(self, pos: Tuple[int, int], state: Dict, 
                         agent=None, show_hidden=False) -> str:
        """Get display content for a cell"""
        x, y = pos
        cell_str = ""
        
        # Agent position
        if pos == state['agent_position']:
            agent_symbol = self.get_agent_symbol(state['agent_direction'])
            if state['agent_alive']:
                cell_str = self.colorize(agent_symbol, 'blue')
            else:
                cell_str = self.colorize('X', 'red')
        
        # World objects (if showing hidden or if discovered)
        elif show_hidden:
            if pos in state['pits']:
                cell_str = self.colorize(self.symbols['pit'], 'red')
            elif pos in state['wumpus_positions']:
                cell_str = self.colorize(self.symbols['wumpus'], 'magenta')
            elif pos == state['gold_position']:
                cell_str = self.colorize(self.symbols['gold'], 'yellow')
            else:
                cell_str = self.symbols['unknown']
        
        # Agent's knowledge (if agent is provided)
        elif agent and hasattr(agent, 'kb'):
            if pos in agent.kb.infer_safe_cells():
                if pos in state['visited_cells']:
                    cell_str = self.colorize(self.symbols['visited'], 'green')
                else:
                    cell_str = self.colorize(self.symbols['safe'], 'green')
            elif pos in agent.kb.infer_dangerous_cells():
                cell_str = self.colorize('!', 'red')
            else:
                cell_str = self.symbols['unknown']
        
        # Default display for visited/unvisited
        else:
            if pos in state['visited_cells']:
                cell_str = self.symbols['visited']
            else:
                cell_str = self.symbols['unknown']
        
        return cell_str
    
    def _display_legend(self, agent=None):
        """Display legend for symbols"""
        print(f"\n{self.colorize('Legend:', 'bold')}")
        print(f"{self.colorize('↑→↓←', 'blue')} Agent  {self.colorize('!', 'red')} Dangerous")
        print(f"{self.colorize('·', 'green')} Visited {self.colorize('?', 'white')} Unknown")
        print(f"{self.colorize('.', 'green')} Safe    {self.colorize('X', 'red')} Dead Agent")
        
        if agent is None:  # Show actual world objects
            print(f"{self.colorize('W', 'magenta')} Wumpus  {self.colorize('P', 'red')} Pit")
            print(f"{self.colorize('G', 'yellow')} Gold")
    
    def display_agent_knowledge(self, agent):
        """Display agent's knowledge state"""
        if not hasattr(agent, 'kb'):
            return
        
        knowledge = agent.kb.get_knowledge_summary()
        
        print(f"\n{self.colorize('=== AGENT KNOWLEDGE ===', 'bold')}")
        print(f"Safe cells: {len(knowledge['safe_cells'])}")
        print(f"Dangerous cells: {len(knowledge['dangerous_cells'])}")
        print(f"Possible wumpus locations: {knowledge['possible_wumpus']}")
        
        if hasattr(agent, 'gold_position') and agent.gold_position:
            print(f"Known gold location: {self.colorize(str(agent.gold_position), 'yellow')}")
        
        status = agent.get_status()
        if status['current_plan_length'] > 0:
            print(f"Current plan length: {status['current_plan_length']}")
    
    def display_step_by_step(self, world: WumpusWorld, agent, 
                           step_delay: float = 1.0, max_steps: int = 1000):
        """Run simulation with step-by-step visualization"""
        step_count = 0
        
        while not world.game_over and step_count < max_steps:
            self.clear_screen()
            
            # Display current state
            self.display_world(world, agent)
            self.display_agent_knowledge(agent)
            
            print(f"\n{self.colorize(f'Step {step_count + 1}', 'bold')}")
            
            # Get current percept
            current_percept = world._generate_percepts()
            agent.perceive(current_percept)
            
            # Choose and execute action
            action = agent.choose_action()
            print(f"Agent chooses: {self.colorize(action.value, 'cyan')}")
            
            # Execute action in world
            percept = world.step(action)
            
            # Check if wumpus moved and notify agent
            if world.wumpus_moved:
                print(f"🔄 Wumpus movement detected in step {step_count + 1}")
                agent.perceive(percept, wumpus_moved=True)
            else:
                agent.perceive(percept, wumpus_moved=False)
            
            agent.update_position(action, percept)
            
            step_count += 1
            
            # Check for game end conditions
            if world.game_over:
                self.clear_screen()
                self.display_world(world, agent)
                self._display_game_result(world, step_count)
                break
            
            # Wait for next step
            if step_delay > 0:
                time.sleep(step_delay)
            else:
                input("Press Enter for next step...")
        
        if step_count >= max_steps:
            print(f"\n{self.colorize('Simulation stopped: Maximum steps reached', 'yellow')}")
    
    def _display_game_result(self, world: WumpusWorld, steps: int):
        """Display final game result"""
        state = world.get_world_state()
        
        print(f"\n{self.colorize('=== GAME OVER ===', 'bold')}")
        print(f"Steps taken: {steps}")
        print(f"Final score: {self.colorize(str(state['score']), 'yellow')}")
        
        if state['agent_alive']:
            if state['agent_has_gold']:
                print(f"{self.colorize('SUCCESS: Agent escaped with gold!', 'green')}")
            else:
                print(f"{self.colorize('ESCAPED: Agent climbed out safely', 'cyan')}")
        else:
            print(f"{self.colorize('FAILURE: Agent died', 'red')}")
    
    def run_silent_simulation(self, world: WumpusWorld, agent, max_steps: int = 1000) -> Dict:
        """Run simulation without visualization and return results"""
        step_count = 0
        
        while not world.game_over and step_count < max_steps:
            # Get current percept and let agent perceive
            current_percept = world._generate_percepts()
            agent.perceive(current_percept)
            
            # Choose and execute action
            action = agent.choose_action()
            percept = world.step(action)
            
            # Check if wumpus moved and notify agent
            if world.wumpus_moved:
                agent.perceive(percept, wumpus_moved=True)
            else:
                agent.perceive(percept, wumpus_moved=False)
            
            agent.update_position(action, percept)
            
            step_count += 1
        
        state = world.get_world_state()
        
        return {
            'success': state['agent_alive'] and state['agent_has_gold'] and world.game_over,
            'score': state['score'],
            'steps': step_count,
            'agent_alive': state['agent_alive'],
            'has_gold': state['agent_has_gold'],
            'completed': world.game_over
        }


def run_comparison_experiment(num_trials: int = 10, world_size: int = 6, 
                            num_wumpus: int = 2, pit_prob: float = 0.2):
    """Run comparison experiment between intelligent and random agents"""
    visualizer = WumpusVisualizer()
    
    print(f"\n{visualizer.colorize('=== COMPARISON EXPERIMENT ===', 'bold')}")
    print(f"Trials: {num_trials}, World size: {world_size}x{world_size}")
    print(f"Wumpus: {num_wumpus}, Pit probability: {pit_prob}")
    
    # Results storage
    intelligent_results = []
    random_results = []
    
    for trial in range(num_trials):
        print(f"\nTrial {trial + 1}/{num_trials}")
        
        # Test intelligent agent
        world = WumpusWorld(world_size, num_wumpus, pit_prob, seed=trial)
        agent = WumpusAgent(world_size, num_wumpus)
        result = visualizer.run_silent_simulation(world, agent)
        intelligent_results.append(result)
        
        # Test random agent with same world
        world.reset(seed=trial)
        random_agent = RandomAgent(world_size)
        result = visualizer.run_silent_simulation(world, random_agent)
        random_results.append(result)
    
    # Calculate statistics
    def calculate_stats(results):
        successes = sum(1 for r in results if r['success'])
        avg_score = sum(r['score'] for r in results) / len(results)
        avg_steps = sum(r['steps'] for r in results) / len(results)
        survival_rate = sum(1 for r in results if r['agent_alive']) / len(results)
        
        return {
            'success_rate': successes / len(results),
            'avg_score': avg_score,
            'avg_steps': avg_steps,
            'survival_rate': survival_rate
        }
    
    intelligent_stats = calculate_stats(intelligent_results)
    random_stats = calculate_stats(random_results)
    
    # Display results
    print(f"\n{visualizer.colorize('=== RESULTS ===', 'bold')}")
    print(f"\n{visualizer.colorize('Intelligent Agent:', 'green')}")
    print(f"  Success rate: {intelligent_stats['success_rate']:.2%}")
    print(f"  Average score: {intelligent_stats['avg_score']:.1f}")
    print(f"  Average steps: {intelligent_stats['avg_steps']:.1f}")
    print(f"  Survival rate: {intelligent_stats['survival_rate']:.2%}")
    
    print(f"\n{visualizer.colorize('Random Agent:', 'red')}")
    print(f"  Success rate: {random_stats['success_rate']:.2%}")
    print(f"  Average score: {random_stats['avg_score']:.1f}")
    print(f"  Average steps: {random_stats['avg_steps']:.1f}")
    print(f"  Survival rate: {random_stats['survival_rate']:.2%}")
    
    print(f"\n{visualizer.colorize('Improvement:', 'yellow')}")
    print(f"  Success rate: +{(intelligent_stats['success_rate'] - random_stats['success_rate']):.2%}")
    print(f"  Score improvement: +{(intelligent_stats['avg_score'] - random_stats['avg_score']):.1f}")
    
    return intelligent_results, random_results
