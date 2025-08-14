"""
GUI Interface for Wumpus World using tkinter
Provides a graphical interface for the Wumpus World game with real-time visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import Optional, Dict, Tuple
import queue
import json

from environment import WumpusWorld, Direction, Action
from agent import WumpusAgent, RandomAgent
from visualization import WumpusVisualizer

class WumpusWorldGUI:
    """GUI application for Wumpus World"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wumpus World - AI Agent")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Game state
        self.world = None
        self.agent = None
        self.simulation_running = False
        self.simulation_thread = None
        self.step_delay = 1.0
        
        # GUI components
        self.canvas = None
        self.cell_size = 60
        self.info_text = None
        self.log_text = None
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        self.setup_gui()
        self.setup_styles()
        
        # Start message processing
        self.root.after(100, self.process_messages)
    
    def setup_styles(self):
        """Setup custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2b2b2b', foreground='white')
        style.configure('Info.TLabel', font=('Arial', 10), background='#2b2b2b', foreground='white')
        style.configure('Custom.TButton', font=('Arial', 10))
        style.configure('Custom.TFrame', background='#2b2b2b')
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏰 Wumpus World - AI Agent", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Top controls
        self.setup_controls(main_frame)
        
        # Main content area
        content_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel - Game board
        left_frame = ttk.Frame(content_frame, style='Custom.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_game_board(left_frame)
        
        # Right panel - Information and controls
        right_frame = ttk.Frame(content_frame, style='Custom.TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.setup_info_panel(right_frame)
    
    def setup_controls(self, parent):
        """Setup control buttons and settings"""
        controls_frame = ttk.Frame(parent, style='Custom.TFrame')
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Settings row 1
        settings_frame1 = ttk.Frame(controls_frame, style='Custom.TFrame')
        settings_frame1.pack(fill=tk.X, pady=2)
        
        ttk.Label(settings_frame1, text="World Size:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value="6")
        size_combo = ttk.Combobox(settings_frame1, textvariable=self.size_var, values=["4", "6", "8", "10"], width=5)
        size_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(settings_frame1, text="Wumpus Count:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.wumpus_var = tk.StringVar(value="2")
        wumpus_combo = ttk.Combobox(settings_frame1, textvariable=self.wumpus_var, values=["1", "2", "3", "4"], width=5)
        wumpus_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(settings_frame1, text="Pit Prob:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.pit_var = tk.StringVar(value="0.2")
        pit_combo = ttk.Combobox(settings_frame1, textvariable=self.pit_var, values=["0.1", "0.2", "0.3", "0.4"], width=5)
        pit_combo.pack(side=tk.LEFT)
        
        # Settings row 2
        settings_frame2 = ttk.Frame(controls_frame, style='Custom.TFrame')
        settings_frame2.pack(fill=tk.X, pady=2)
        
        ttk.Label(settings_frame2, text="Agent Type:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.agent_var = tk.StringVar(value="Intelligent")
        agent_combo = ttk.Combobox(settings_frame2, textvariable=self.agent_var, values=["Intelligent", "Random"], width=10)
        agent_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(settings_frame2, text="Speed:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(settings_frame2, textvariable=self.speed_var, values=["Slow", "Normal", "Fast", "Very Fast"], width=10)
        speed_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Moving wumpus checkbox
        self.moving_wumpus_var = tk.BooleanVar()
        moving_check = ttk.Checkbutton(settings_frame2, text="Moving Wumpus", variable=self.moving_wumpus_var)
        moving_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # Show hidden checkbox
        self.show_hidden_var = tk.BooleanVar()
        hidden_check = ttk.Checkbutton(settings_frame2, text="Show Hidden", variable=self.show_hidden_var)
        hidden_check.pack(side=tk.LEFT)
        
        # Control buttons
        buttons_frame = ttk.Frame(controls_frame, style='Custom.TFrame')
        buttons_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(buttons_frame, text="🎮 Start Game", command=self.start_game, style='Custom.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_button = ttk.Button(buttons_frame, text="⏸️ Pause", command=self.pause_game, style='Custom.TButton', state='disabled')
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.step_button = ttk.Button(buttons_frame, text="➡️ Step", command=self.step_game, style='Custom.TButton', state='disabled')
        self.step_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_button = ttk.Button(buttons_frame, text="🔄 Reset", command=self.reset_game, style='Custom.TButton')
        self.reset_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.experiment_button = ttk.Button(buttons_frame, text="🧪 Experiment", command=self.run_experiment, style='Custom.TButton')
        self.experiment_button.pack(side=tk.LEFT)
    
    def setup_game_board(self, parent):
        """Setup the game board canvas"""
        board_frame = ttk.Frame(parent, style='Custom.TFrame')
        board_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for the game board
        self.canvas = tk.Canvas(board_frame, bg='#1e1e1e', highlightthickness=1, highlightcolor='#555555')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Legend
        legend_frame = ttk.Frame(board_frame, style='Custom.TFrame')
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(legend_frame, text="Legend:", style='Title.TLabel').pack(anchor=tk.W)
        
        legend_text = """
🤖 Agent    🏰 Wumpus    🕳️ Pit    ✨ Gold    💨 Breeze    👃 Stench
🟢 Safe     🔴 Dangerous  ⚪ Unknown  👀 Visited  🎯 Target
        """
        ttk.Label(legend_frame, text=legend_text.strip(), style='Info.TLabel').pack(anchor=tk.W)
    
    def setup_info_panel(self, parent):
        """Setup the information panel"""
        info_frame = ttk.Frame(parent, style='Custom.TFrame')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game information
        ttk.Label(info_frame, text="Game Information", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, width=35, height=15, 
                                                  bg='#1e1e1e', fg='white', font=('Consolas', 9))
        self.info_text.pack(fill=tk.X, pady=(0, 10))
        
        # Game log
        ttk.Label(info_frame, text="Game Log", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(info_frame, width=35, height=20,
                                                 bg='#1e1e1e', fg='#00ff00', font=('Consolas', 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear log button
        clear_button = ttk.Button(info_frame, text="Clear Log", command=self.clear_log, style='Custom.TButton')
        clear_button.pack(pady=(5, 0))
    
    def get_speed_delay(self):
        """Get delay based on speed setting"""
        speed_map = {
            "Slow": 2.0,
            "Normal": 1.0,
            "Fast": 0.5,
            "Very Fast": 0.1
        }
        return speed_map.get(self.speed_var.get(), 1.0)
    
    def start_game(self):
        """Start a new game"""
        if self.simulation_running:
            return
        
        try:
            # Get settings
            size = int(self.size_var.get())
            wumpus_count = int(self.wumpus_var.get())
            pit_prob = float(self.pit_var.get())
            
            # Create world and agent
            self.world = WumpusWorld(size, wumpus_count, pit_prob)
            
            if self.moving_wumpus_var.get():
                self.world.enable_moving_wumpus()
                self.log_message("🔄 Moving wumpus enabled!")
            
            if self.agent_var.get() == "Intelligent":
                self.agent = WumpusAgent(size, wumpus_count)
                self.log_message("🧠 Intelligent agent selected")
            else:
                self.agent = RandomAgent(size)
                self.log_message("🎲 Random agent selected")
            
            # Update canvas size
            self.cell_size = min(60, 600 // size)
            
            # Start simulation
            self.simulation_running = True
            self.step_delay = self.get_speed_delay()
            
            # Update button states
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            self.step_button.config(state='disabled')
            
            # Start simulation thread
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            
            self.log_message(f"🎮 Game started! World: {size}x{size}, Wumpus: {wumpus_count}, Pit prob: {pit_prob}")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid settings: {e}")
    
    def pause_game(self):
        """Pause/resume the game"""
        if self.simulation_running:
            self.simulation_running = False
            self.pause_button.config(text="▶️ Resume")
            self.step_button.config(state='normal')
            self.log_message("⏸️ Game paused")
        else:
            self.simulation_running = True
            self.pause_button.config(text="⏸️ Pause")
            self.step_button.config(state='disabled')
            
            # Resume simulation
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            self.log_message("▶️ Game resumed")
    
    def step_game(self):
        """Execute one step of the game"""
        if self.world and self.agent and not self.world.game_over:
            self.execute_step()
    
    def reset_game(self):
        """Reset the game"""
        self.simulation_running = False
        self.world = None
        self.agent = None
        
        # Update button states
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled', text="⏸️ Pause")
        self.step_button.config(state='disabled')
        
        # Clear displays
        self.canvas.delete("all")
        self.update_info_display()
        self.log_message("🔄 Game reset")
    
    def simulation_loop(self):
        """Main simulation loop (runs in separate thread)"""
        step_count = 0
        max_steps = 1000
        
        while self.simulation_running and self.world and not self.world.game_over and step_count < max_steps:
            self.execute_step()
            step_count += 1
            time.sleep(self.step_delay)
        
        # Game ended
        if self.world and self.world.game_over:
            self.message_queue.put(("game_over", step_count))
        elif step_count >= max_steps:
            self.message_queue.put(("max_steps", step_count))
    
    def execute_step(self):
        """Execute one step of the simulation"""
        if not self.world or not self.agent:
            return
        
        # Get current percept
        current_percept = self.world._generate_percepts()
        self.agent.perceive(current_percept)
        
        # Choose action
        action = self.agent.choose_action()
        
        # Execute action
        percept = self.world.step(action)
        self.agent.update_position(action, percept)
        
        # Update display
        self.message_queue.put(("update", {
            "action": action.value,
            "percept": str(percept),
            "step": len(self.world.action_log)
        }))
    
    def process_messages(self):
        """Process messages from simulation thread"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "update":
                    self.update_display()
                    self.log_message(f"Step {data['step']}: {data['action']} -> {data['percept']}")
                
                elif message_type == "game_over":
                    self.simulation_running = False
                    self.update_display()
                    self.show_game_result(data)
                
                elif message_type == "max_steps":
                    self.simulation_running = False
                    self.log_message(f"⏰ Game stopped: Maximum steps ({data}) reached")
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def update_display(self):
        """Update the visual display"""
        if not self.world:
            return
        
        self.draw_world()
        self.update_info_display()
    
    def draw_world(self):
        """Draw the world on the canvas"""
        self.canvas.delete("all")
        
        if not self.world:
            return
        
        state = self.world.get_world_state()
        size = state['size']
        
        # Calculate canvas size
        canvas_size = size * self.cell_size
        self.canvas.config(width=canvas_size, height=canvas_size)
        
        # Draw grid
        for i in range(size + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, canvas_size, fill='#555555', width=1)
            y = i * self.cell_size
            self.canvas.create_line(0, y, canvas_size, y, fill='#555555', width=1)
        
        # Draw cells
        for x in range(size):
            for y in range(size):
                self.draw_cell(x, y, state)
        
        # Draw coordinates
        for i in range(size):
            # X coordinates (bottom)
            self.canvas.create_text(i * self.cell_size + self.cell_size // 2, 
                                  canvas_size + 10, text=str(i), fill='white', font=('Arial', 8))
            # Y coordinates (left)
            self.canvas.create_text(-10, (size - 1 - i) * self.cell_size + self.cell_size // 2, 
                                  text=str(i), fill='white', font=('Arial', 8))
    
    def draw_cell(self, x: int, y: int, state: Dict):
        """Draw a single cell"""
        # Convert to canvas coordinates (flip Y axis)
        canvas_x = x * self.cell_size
        canvas_y = (state['size'] - 1 - y) * self.cell_size
        
        cell_center_x = canvas_x + self.cell_size // 2
        cell_center_y = canvas_y + self.cell_size // 2
        
        pos = (x, y)
        
        # Background color based on knowledge
        bg_color = '#1e1e1e'  # Default dark
        
        if hasattr(self.agent, 'kb'):
            safe_cells = self.agent.kb.infer_safe_cells()
            dangerous_cells = self.agent.kb.infer_dangerous_cells()
            
            if pos in safe_cells:
                bg_color = '#0d2818' if pos in state['visited_cells'] else '#0a1f0a'  # Dark green
            elif pos in dangerous_cells:
                bg_color = '#2d0a0a'  # Dark red
        
        # Draw cell background
        self.canvas.create_rectangle(canvas_x + 1, canvas_y + 1, 
                                   canvas_x + self.cell_size - 1, 
                                   canvas_y + self.cell_size - 1,
                                   fill=bg_color, outline='#555555')
        
        # Draw world objects (if showing hidden or discovered)
        symbols = []
        
        if self.show_hidden_var.get():
            # Show actual world state
            if pos in state['pits']:
                symbols.append(('🕳️', '#ff4444'))
            if pos in state['wumpus_positions']:
                symbols.append(('🏰', '#8a2be2'))
            if pos == state['gold_position']:
                symbols.append(('✨', '#ffd700'))
        else:
            # Show agent's knowledge
            if hasattr(self.agent, 'gold_position') and pos == self.agent.gold_position:
                symbols.append(('✨', '#ffd700'))
        
        # Show percepts for visited cells
        if pos in state['visited_cells'] and not self.show_hidden_var.get():
            if hasattr(self.agent, 'kb'):
                # Check knowledge base for percepts
                breeze_prop = f"Breeze_{x}_{y}"
                stench_prop = f"Stench_{x}_{y}"
                
                if any(fact.name == breeze_prop for fact in self.agent.kb.facts):
                    symbols.append(('💨', '#87ceeb'))
                if any(fact.name == stench_prop for fact in self.agent.kb.facts):
                    symbols.append(('👃', '#90ee90'))
        
        # Draw symbols
        if len(symbols) == 1:
            symbol, color = symbols[0]
            self.canvas.create_text(cell_center_x, cell_center_y, text=symbol, 
                                  fill=color, font=('Arial', 16))
        elif len(symbols) > 1:
            # Multiple symbols - arrange them
            for i, (symbol, color) in enumerate(symbols[:4]):  # Max 4 symbols
                offset_x = (i % 2 - 0.5) * 10
                offset_y = (i // 2 - 0.5) * 10
                self.canvas.create_text(cell_center_x + offset_x, cell_center_y + offset_y, 
                                      text=symbol, fill=color, font=('Arial', 12))
        
        # Draw agent
        if pos == state['agent_position']:
            if state['agent_alive']:
                # Agent direction arrows
                agent_symbols = {
                    Direction.NORTH: '⬆️',
                    Direction.EAST: '➡️',
                    Direction.SOUTH: '⬇️',
                    Direction.WEST: '⬅️'
                }
                agent_symbol = agent_symbols.get(state['agent_direction'], '🤖')
                self.canvas.create_text(cell_center_x, cell_center_y - 15, text=agent_symbol, 
                                      fill='#00bfff', font=('Arial', 16))
            else:
                self.canvas.create_text(cell_center_x, cell_center_y, text='💀', 
                                      fill='#ff0000', font=('Arial', 16))
        
        # Draw visited indicator
        if pos in state['visited_cells'] and pos != state['agent_position']:
            self.canvas.create_oval(canvas_x + 2, canvas_y + 2, 
                                  canvas_x + 8, canvas_y + 8,
                                  fill='#4444ff', outline='')
    
    def update_info_display(self):
        """Update the information display"""
        self.info_text.delete(1.0, tk.END)
        
        if not self.world:
            self.info_text.insert(tk.END, "No game running\n")
            return
        
        state = self.world.get_world_state()
        
        # Basic game info
        info = f"""Game Status: {'Running' if not state['game_over'] else 'Finished'}
Score: {state['score']}
Agent Position: {state['agent_position']}
Agent Direction: {state['agent_direction'].name}
Agent Alive: {'Yes' if state['agent_alive'] else 'No'}
Has Arrow: {'Yes' if state['agent_has_arrow'] else 'No'}
Has Gold: {'Yes' if state['agent_has_gold'] else 'No'}
Actions Taken: {state['action_count']}

"""
        
        # Agent knowledge (if intelligent agent)
        if hasattr(self.agent, 'kb'):
            knowledge = self.agent.kb.get_knowledge_summary()
            info += f"""Agent Knowledge:
Safe Cells: {len(knowledge['safe_cells'])}
Dangerous Cells: {len(knowledge['dangerous_cells'])}
Possible Wumpus: {knowledge['possible_wumpus']}

"""
            
            if hasattr(self.agent, 'gold_position') and self.agent.gold_position:
                info += f"Known Gold Location: {self.agent.gold_position}\n"
            
            status = self.agent.get_status()
            if status['current_plan_length'] > 0:
                info += f"Current Plan Length: {status['current_plan_length']}\n"
        
        # Last percept
        if state['last_percept']:
            info += f"\nLast Percept: {state['last_percept']}\n"
        
        self.info_text.insert(tk.END, info)
    
    def show_game_result(self, steps):
        """Show game result dialog"""
        if not self.world:
            return
        
        state = self.world.get_world_state()
        
        if state['agent_alive']:
            if state['agent_has_gold']:
                result = "🎉 SUCCESS!\nAgent escaped with gold!"
                title = "Victory!"
            else:
                result = "🚪 Agent climbed out safely\n(but without gold)"
                title = "Safe Exit"
        else:
            result = "💀 FAILURE!\nAgent died"
            title = "Game Over"
        
        result += f"\n\nFinal Score: {state['score']}\nSteps Taken: {steps}"
        
        messagebox.showinfo(title, result)
        
        # Update button states
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled', text="⏸️ Pause")
        self.step_button.config(state='disabled')
    
    def run_experiment(self):
        """Run comparison experiment"""
        try:
            # Get settings
            size = int(self.size_var.get())
            wumpus_count = int(self.wumpus_var.get())
            pit_prob = float(self.pit_var.get())
            
            # Run experiment in separate thread
            def experiment_thread():
                from visualization import run_comparison_experiment
                
                self.log_message("🧪 Starting comparison experiment...")
                self.message_queue.put(("log", "Running 10 trials..."))
                
                intelligent_results, random_results = run_comparison_experiment(
                    num_trials=10, world_size=size, num_wumpus=wumpus_count, pit_prob=pit_prob
                )
                
                # Calculate statistics
                def calc_stats(results):
                    successes = sum(1 for r in results if r['success'])
                    return {
                        'success_rate': successes / len(results),
                        'avg_score': sum(r['score'] for r in results) / len(results),
                        'survival_rate': sum(1 for r in results if r['agent_alive']) / len(results)
                    }
                
                intelligent_stats = calc_stats(intelligent_results)
                random_stats = calc_stats(random_results)
                
                # Show results
                result_msg = f"""🧪 Experiment Results (10 trials each)

🧠 Intelligent Agent:
  Success Rate: {intelligent_stats['success_rate']:.1%}
  Average Score: {intelligent_stats['avg_score']:.1f}
  Survival Rate: {intelligent_stats['survival_rate']:.1%}

🎲 Random Agent:
  Success Rate: {random_stats['success_rate']:.1%}
  Average Score: {random_stats['avg_score']:.1f}
  Survival Rate: {random_stats['survival_rate']:.1%}

📈 Improvement:
  Success Rate: +{(intelligent_stats['success_rate'] - random_stats['success_rate']):.1%}
  Score Improvement: +{(intelligent_stats['avg_score'] - random_stats['avg_score']):.1f}
"""
                
                self.message_queue.put(("experiment_done", result_msg))
            
            # Start experiment thread
            exp_thread = threading.Thread(target=experiment_thread, daemon=True)
            exp_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid settings: {e}")
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
    
    def run(self):
        """Start the GUI application"""
        # Handle experiment results
        def check_experiment_results():
            try:
                while True:
                    message_type, data = self.message_queue.get_nowait()
                    if message_type == "experiment_done":
                        messagebox.showinfo("Experiment Results", data)
                        self.log_message("🧪 Experiment completed!")
                    elif message_type == "log":
                        self.log_message(data)
            except queue.Empty:
                pass
            
            self.root.after(1000, check_experiment_results)
        
        self.root.after(1000, check_experiment_results)
        self.root.mainloop()


def main():
    """Main function to start the GUI"""
    app = WumpusWorldGUI()
    app.run()


if __name__ == "__main__":
    main()
