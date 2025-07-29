"""
Main program for Wumpus World simulation
Provides command-line interface for running simulations and experiments.
"""

import argparse
import sys
from environment import WumpusWorld
from agent import WumpusAgent, RandomAgent
from visualization import WumpusVisualizer, run_comparison_experiment

def main():
    parser = argparse.ArgumentParser(description='Wumpus World Simulation')
    parser.add_argument('--mode', choices=['demo', 'experiment', 'interactive', 'gui'], 
                       default='demo', help='Simulation mode')
    parser.add_argument('--size', type=int, default=6, help='World size (default: 6)')
    parser.add_argument('--wumpus', type=int, default=2, help='Number of wumpus (default: 2)')
    parser.add_argument('--pit-prob', type=float, default=0.2, help='Pit probability (default: 0.2)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--steps', type=int, default=1000, help='Maximum steps (default: 1000)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between steps in seconds (default: 1.0)')
    parser.add_argument('--trials', type=int, default=10, help='Number of trials for experiment (default: 10)')
    parser.add_argument('--moving-wumpus', action='store_true', help='Enable moving wumpus (advanced setting)')
    parser.add_argument('--show-hidden', action='store_true', help='Show hidden world objects')
    parser.add_argument('--agent-type', choices=['intelligent', 'random'], default='intelligent',
                       help='Type of agent to use')
    
    args = parser.parse_args()
    
    if args.mode == 'demo':
        run_demo(args)
    elif args.mode == 'experiment':
        run_experiment(args)
    elif args.mode == 'interactive':
        run_interactive(args)
    elif args.mode == 'gui':
        run_gui(args)

def run_demo(args):
    """Run a single demonstration"""
    print("=== Wumpus World Demo ===")
    print(f"World size: {args.size}x{args.size}")
    print(f"Wumpus count: {args.wumpus}")
    print(f"Pit probability: {args.pit_prob}")
    if args.moving_wumpus:
        print("Moving wumpus: ENABLED")
    
    # Create world and agent
    world = WumpusWorld(args.size, args.wumpus, args.pit_prob, args.seed)
    
    if args.moving_wumpus:
        world.enable_moving_wumpus()
        print("Advanced setting: Moving wumpus enabled!")
    
    if args.agent_type == 'intelligent':
        agent = WumpusAgent(args.size, args.wumpus)
        print("Using intelligent agent with knowledge base and planning")
    else:
        agent = RandomAgent(args.size)
        print("Using random agent baseline")
    
    # Create visualizer and run simulation
    visualizer = WumpusVisualizer()
    
    if args.show_hidden:
        print("Showing hidden world objects for debugging")
    
    print("\nStarting simulation...")
    print("Press Ctrl+C to stop\n")
    
    try:
        visualizer.display_step_by_step(
            world, agent, step_delay=args.delay, max_steps=args.steps
        )
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")

def run_experiment(args):
    """Run comparison experiment"""
    print("=== Wumpus World Experiment ===")
    print(f"Comparing intelligent vs random agents")
    
    intelligent_results, random_results = run_comparison_experiment(
        num_trials=args.trials,
        world_size=args.size,
        num_wumpus=args.wumpus,
        pit_prob=args.pit_prob
    )
    
    # Save results to file
    with open('experiment_results.txt', 'w') as f:
        f.write("Wumpus World Experiment Results\n")
        f.write(f"Trials: {args.trials}\n")
        f.write(f"World size: {args.size}x{args.size}\n")
        f.write(f"Wumpus: {args.wumpus}, Pit probability: {args.pit_prob}\n\n")
        
        f.write("Intelligent Agent Results:\n")
        for i, result in enumerate(intelligent_results):
            f.write(f"Trial {i+1}: Score={result['score']}, Steps={result['steps']}, "
                   f"Success={result['success']}, Alive={result['agent_alive']}\n")
        
        f.write("\nRandom Agent Results:\n")
        for i, result in enumerate(random_results):
            f.write(f"Trial {i+1}: Score={result['score']}, Steps={result['steps']}, "
                   f"Success={result['success']}, Alive={result['agent_alive']}\n")
    
    print(f"\nDetailed results saved to 'experiment_results.txt'")

def run_interactive(args):
    """Run interactive simulation"""
    print("=== Interactive Wumpus World ===")
    print("Commands: demo, new, experiment, quit")
    
    visualizer = WumpusVisualizer()
    
    while True:
        command = input("\nEnter command: ").strip().lower()
        
        if command == 'quit':
            break
        elif command == 'demo':
            world = WumpusWorld(args.size, args.wumpus, args.pit_prob)
            agent = WumpusAgent(args.size, args.wumpus)
            
            print("Starting demo (press Enter for each step)...")
            visualizer.display_step_by_step(world, agent, step_delay=0)
            
        elif command == 'new':
            try:
                size = int(input("World size (default 6): ") or "6")
                wumpus = int(input("Number of wumpus (default 2): ") or "2")
                pit_prob = float(input("Pit probability (default 0.2): ") or "0.2")
                
                world = WumpusWorld(size, wumpus, pit_prob)
                agent = WumpusAgent(size, wumpus)
                
                print("Created new world. Use 'demo' to run simulation.")
                
            except ValueError:
                print("Invalid input. Please enter numbers.")
                
        elif command == 'experiment':
            try:
                trials = int(input("Number of trials (default 10): ") or "10")
                run_comparison_experiment(trials, args.size, args.wumpus, args.pit_prob)
            except ValueError:
                print("Invalid input. Please enter a number.")
                
        else:
            print("Unknown command. Available: demo, new, experiment, quit")

def run_gui(args):
    """Run GUI version"""
    try:
        from gui import WumpusWorldGUI
        print("🎮 Starting Wumpus World GUI...")
        app = WumpusWorldGUI()
        app.run()
    except ImportError as e:
        print(f"Error: GUI dependencies not available: {e}")
        print("Make sure tkinter is installed (usually comes with Python)")
    except Exception as e:
        print(f"Error starting GUI: {e}")

def create_test_cases():
    """Create test cases for submission"""
    print("Creating test cases...")
    
    test_configs = [
        {'size': 4, 'wumpus': 1, 'pit_prob': 0.1, 'seed': 42, 'name': 'small_world'},
        {'size': 6, 'wumpus': 2, 'pit_prob': 0.2, 'seed': 123, 'name': 'medium_world'},
        {'size': 8, 'wumpus': 3, 'pit_prob': 0.25, 'seed': 456, 'name': 'large_world'}
    ]
    
    for config in test_configs:
        print(f"Creating test case: {config['name']}")
        
        # Create world
        world = WumpusWorld(config['size'], config['wumpus'], config['pit_prob'], config['seed'])
        agent = WumpusAgent(config['size'], config['wumpus'])
        visualizer = WumpusVisualizer()
        
        # Run simulation and save results
        result = visualizer.run_silent_simulation(world, agent)
        
        # Save configuration and result
        with open(f"testcases/{config['name']}_config.txt", 'w') as f:
            f.write(f"World Configuration: {config['name']}\n")
            f.write(f"Size: {config['size']}x{config['size']}\n")
            f.write(f"Wumpus count: {config['wumpus']}\n")
            f.write(f"Pit probability: {config['pit_prob']}\n")
            f.write(f"Random seed: {config['seed']}\n\n")
            
            f.write("World State:\n")
            state = world.get_world_state()
            f.write(f"Pits: {list(state['pits'])}\n")
            f.write(f"Wumpus positions: {list(state['wumpus_positions'])}\n")
            f.write(f"Gold position: {state['gold_position']}\n\n")
            
            f.write("Result:\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Score: {result['score']}\n")
            f.write(f"Steps: {result['steps']}\n")
            f.write(f"Agent alive: {result['agent_alive']}\n")
        
        print(f"Test case {config['name']}: Score={result['score']}, Success={result['success']}")

if __name__ == "__main__":
    # Check if we should create test cases
    if len(sys.argv) > 1 and sys.argv[1] == '--create-tests':
        create_test_cases()
    else:
        main()
