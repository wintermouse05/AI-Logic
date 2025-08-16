"""
Pygame GUI for Wumpus World
A modern, interactive graphical interface for the Wumpus World game.
"""

import pygame
import pygame.mixer
import sys
import threading
import time
import queue
import os
from typing import Dict, Tuple, Optional, List
from enum import Enum

# Add current directory to path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from environment import WumpusWorld, Direction, Action
from agent import WumpusAgent, RandomAgent
from visualization import run_comparison_experiment
from models.character_loader import get_agent_sprite, get_wumpus_sprite, get_gold_sprite, get_hole_sprite

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Colors
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    DARK_YELLOW = (139, 139, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    BROWN = (139, 69, 19)
    DARK_GREEN = (0, 100, 0)
    DARK_RED = (139, 0, 0)
    GOLD = (255, 215, 0)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    EXPERIMENT = 5

class WumpusWorldPygameGUI:
    """Pygame-based GUI for Wumpus World"""
    
    def __init__(self):
        # Screen dimensions
        self.WINDOW_WIDTH = 1400
        self.WINDOW_HEIGHT = 900
        self.BOARD_SIZE = 600
        self.SIDEBAR_WIDTH = 300
        self.HEADER_HEIGHT = 100
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("")  # Xóa tiêu đề
        self.clock = pygame.time.Clock()
        
        # Load background images
        self.menu_background = None
        self.game_background = None
        self.load_backgrounds()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Game state
        self.state = GameState.MENU
        self.world = None
        self.agent = None
        self.simulation_running = False
        self.simulation_thread = None
        self.step_delay = 1.0
        
        # Settings
        self.world_size = 6
        self.wumpus_count = 2
        self.pit_probability = 0.2
        self.agent_type = "Intelligent"
        self.moving_wumpus = False
        self.show_hidden = False
        self.speed = "Normal"
        
        # UI elements
        self.buttons = {}
        self.sliders = {}
        self.checkboxes = {}
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        # Game log
        self.game_log = []
        self.max_log_entries = 20
        
        # Animation
        self.animation_frame = 0
        
        self.setup_ui_elements()
    
    def load_backgrounds(self):
        """Load and scale background images"""
        try:
            # Load menu background (thumbnail.png)
            menu_bg_path = os.path.join(current_dir, "background", "thumbnail.png")
            if os.path.exists(menu_bg_path):
                menu_bg = pygame.image.load(menu_bg_path)
                # Scale to fit screen while maintaining aspect ratio
                self.menu_background = pygame.transform.scale(menu_bg, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
                print("Menu background loaded successfully")
            else:
                print("Menu background not found")
                
            # Load game background (background.png)
            game_bg_path = os.path.join(current_dir, "background", "background.png")
            if os.path.exists(game_bg_path):
                game_bg = pygame.image.load(game_bg_path)
                # Scale to fit screen while maintaining aspect ratio
                self.game_background = pygame.transform.scale(game_bg, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
                print("Game background loaded successfully")
            else:
                print("Game background not found")
                
        except Exception as e:
            print(f"Error loading backgrounds: {e}")
            self.menu_background = None
            self.game_background = None
    
    def setup_ui_elements(self):
        """Setup UI buttons and controls"""
        button_width = 120
        button_height = 40
        
        # Main menu buttons - moved down and centered
        center_x = self.WINDOW_WIDTH // 2
        button_gap = 30  # khoảng cách giữa các nút
        total_width = button_width * 3 + button_gap * 2
        left_x = center_x - total_width // 2
        self.buttons['start'] = pygame.Rect(left_x, 550, button_width, button_height)
        self.buttons['experiment'] = pygame.Rect(left_x + button_width + button_gap, 550, button_width, button_height)
        self.buttons['quit'] = pygame.Rect(left_x + (button_width + button_gap) * 2, 550, button_width, button_height)
            
        # Game control buttons
        self.buttons['pause'] = pygame.Rect(50, 150, button_width, button_height)
        self.buttons['step'] = pygame.Rect(180, 150, button_width, button_height)
        self.buttons['reset'] = pygame.Rect(310, 150, button_width, button_height)
        self.buttons['full_reset'] = pygame.Rect(440, 150, button_width, button_height)
        self.buttons['menu'] = pygame.Rect(570, 150, button_width, button_height)
        
        # Settings sliders (x, y, width, height, min_val, max_val, current_val)
        self.sliders['world_size'] = {
            'rect': pygame.Rect(200, 250, 150, 20),
            'min': 4, 'max': 10, 'value': 6, 'label': 'World Size'
        }
        self.sliders['wumpus_count'] = {
            'rect': pygame.Rect(200, 290, 150, 20),
            'min': 1, 'max': 8, 'value': 2, 'label': 'Wumpus Count'
        }
        self.sliders['pit_prob'] = {
            'rect': pygame.Rect(200, 330, 150, 20),
            'min': 0.1, 'max': 0.5, 'value': 0.2, 'label': 'Pit Probability'
        }
        self.sliders['speed'] = {
            'rect': pygame.Rect(200, 370, 150, 20),
            'min': 0.1, 'max': 3.0, 'value': 1.0, 'label': 'Speed'
        }
        
        # Checkboxes
        self.checkboxes['intelligent'] = {
            'rect': pygame.Rect(200, 410, 20, 20),
            'checked': True, 'label': 'Intelligent Agent'
        }
        self.checkboxes['moving_wumpus'] = {
            'rect': pygame.Rect(200, 440, 20, 20),
            'checked': False, 'label': 'Moving Wumpus'
        }
        self.checkboxes['show_hidden'] = {
            'rect': pygame.Rect(200, 470, 20, 20),
            'checked': False, 'label': 'Show Hidden Objects'
        }
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                    else:
                        return False
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.PLAYING:
                        self.toggle_pause()
                elif event.key == pygame.K_s:
                    if self.state == GameState.PAUSED:
                        self.step_game()
                elif event.key == pygame.K_r:
                    if self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
                        self.reset_game()
                elif event.key == pygame.K_f:  # F for "Forget" - complete reset
                    if self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
                        self.complete_reset_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button held
                    self.handle_mouse_drag(event.pos)
        
        return True
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        if self.state == GameState.MENU:
            if self.buttons['start'].collidepoint(pos):
                self.start_game()
            elif self.buttons['experiment'].collidepoint(pos):
                self.run_experiment()
            elif self.buttons['quit'].collidepoint(pos):
                pygame.quit()
                sys.exit()
    
            # Handle checkbox clicks
            for name, checkbox in self.checkboxes.items():
                if checkbox['rect'].collidepoint(pos):
                    checkbox['checked'] = not checkbox['checked']
                    self.update_settings_from_ui()
        
        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            if self.buttons['pause'].collidepoint(pos):
                self.toggle_pause()
            elif self.buttons['step'].collidepoint(pos):
                if self.state == GameState.PAUSED:
                    self.step_game()
            elif self.buttons['reset'].collidepoint(pos):
                self.reset_game()
            elif self.buttons['full_reset'].collidepoint(pos):
                self.complete_reset_game()
            elif self.buttons['menu'].collidepoint(pos):
                self.state = GameState.MENU
                self.simulation_running = False
        
        elif self.state == GameState.GAME_OVER:
            if self.buttons['reset'].collidepoint(pos):
                self.reset_game()
            elif self.buttons['menu'].collidepoint(pos):
                self.state = GameState.MENU
            # Add area for complete reset in game over screen
            complete_reset_rect = pygame.Rect(570, 150, 120, 40)  # Next to other buttons
            if complete_reset_rect.collidepoint(pos):
                self.complete_reset_game()
    
    def handle_mouse_drag(self, pos):
        """Handle mouse drag for sliders"""
        if self.state == GameState.MENU:
            for name, slider in self.sliders.items():
                if slider['rect'].collidepoint(pos):
                    # Calculate slider value based on mouse position
                    relative_x = pos[0] - slider['rect'].x
                    slider_width = slider['rect'].width
                    ratio = max(0, min(1, relative_x / slider_width))
                    
                    value_range = slider['max'] - slider['min']
                    slider['value'] = slider['min'] + ratio * value_range
                    
                    # Round appropriately
                    if name in ['world_size', 'wumpus_count']:
                        slider['value'] = int(slider['value'])
                    else:
                        slider['value'] = round(slider['value'], 2)
                    
                    self.update_settings_from_ui()
    
    def update_settings_from_ui(self):
        """Update game settings from UI elements"""
        self.world_size = self.sliders['world_size']['value']
        self.wumpus_count = self.sliders['wumpus_count']['value']
        self.pit_probability = self.sliders['pit_prob']['value']
        self.step_delay = 3.1 - self.sliders['speed']['value']  # Invert for intuitive speed
        
        self.agent_type = "Intelligent" if self.checkboxes['intelligent']['checked'] else "Random"
        self.moving_wumpus = self.checkboxes['moving_wumpus']['checked']
        self.show_hidden = self.checkboxes['show_hidden']['checked']
    
    def start_game(self):
        """Start a new game"""
        self.update_settings_from_ui()
        
        # Create world and agent
        self.world = WumpusWorld(self.world_size, self.wumpus_count, self.pit_probability)
        
        if self.moving_wumpus:
            self.world.enable_moving_wumpus()
            self.add_log_message("Moving wumpus enabled!")
        
        if self.agent_type == "Intelligent":
            self.agent = WumpusAgent(self.world_size, self.wumpus_count)
            self.add_log_message("Intelligent agent selected")
        else:
            self.agent = RandomAgent(self.world_size)
            self.add_log_message("Random agent selected")
        
        self.state = GameState.PLAYING
        self.simulation_running = True
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        self.add_log_message(f"Game started! {self.world_size}x{self.world_size} world")
        self.add_log_message("Agent starts at position (0,0) - bottom-left corner")
        self.add_log_message("World generated with guaranteed winnable path to gold!")
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == GameState.PLAYING:
            self.simulation_running = False
            self.state = GameState.PAUSED
            self.add_log_message("⏸Game paused")
        elif self.state == GameState.PAUSED:
            self.simulation_running = True
            self.state = GameState.PLAYING
            # Resume simulation
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            self.add_log_message("Game resumed")
    
    def step_game(self):
        """Execute one step"""
        if self.world and self.agent and not self.world.game_over:
            self.execute_step()
    
    def reset_game(self):
        """Smart reset - if lost, replay same world; if won, generate new world"""
        self.simulation_running = False
        
        if self.world and self.agent:
            # Check game result using world state
            state = self.world.get_world_state()
            
            # Agent won if: alive + has gold + successfully escaped (at start position)
            game_won = (state['agent_alive'] and 
                       state['agent_has_gold'] and 
                       state['agent_position'] == (0, 0) and
                       state['game_over'])
            
            # Agent lost if: died OR game over without winning
            game_lost = (not state['agent_alive'] or 
                        (state['game_over'] and not game_won))
            
            if game_lost:
                # Agent LOST - replay SAME WORLD
                # Save current world configuration before any reset
                saved_pits = set(self.world.pits)
                saved_wumpus = set(self.world.wumpus_positions)  
                saved_gold = self.world.gold_position
                saved_visited = set(self.world.visited_cells)
                
                # Check where agent died and mark that position as dangerous
                death_position = state['agent_position']
                died_from_pit = death_position in saved_pits
                died_from_wumpus = death_position in saved_wumpus
                
                # Only reset agent position and state, keep world layout
                self.world.agent_position = (0, 0)
                self.world.agent_direction = Direction.EAST
                self.world.agent_has_arrow = True
                self.world.agent_has_gold = False
                self.world.agent_alive = True
                self.world.game_over = False
                self.world.score = 0
                self.world.action_count = 0
                self.world.last_percept = None
                self.world.action_log = []
                
                # Keep world layout and visited cells (keep colors!)
                self.world.pits = saved_pits
                self.world.wumpus_positions = saved_wumpus
                self.world.gold_position = saved_gold
                self.world.visited_cells = saved_visited  # Keep all colored cells!
                
                # Reset agent position but preserve knowledge
                if hasattr(self.agent, 'reset_for_new_world'):
                    # Only reset position/direction, keep all learning
                    self.agent.position = (0, 0)
                    self.agent.direction = Direction.EAST
                    self.agent.has_arrow = True
                    self.agent.has_gold = False
                    self.agent.plan = []
                    # DON'T reset knowledge base - keep all learning!
                    
                    # Mark death position as dangerous in knowledge base
                    agent_kb = getattr(self.agent, 'kb', None)
                    if agent_kb:
                        if died_from_pit:
                            # Add definitive knowledge that this cell has a pit
                            pit_prop_name = f"Pit_{death_position[0]}_{death_position[1]}"
                            from knowledge_base import Proposition
                            agent_kb.add_fact(Proposition(pit_prop_name))
                            self.add_log_message(f"Agent died by falling into pit at {death_position}")
                            self.add_log_message(f"Mark {death_position} as deadly pit!")
                        elif died_from_wumpus:
                            # Add definitive knowledge that this cell has a wumpus
                            wumpus_prop_name = f"Wumpus_{death_position[0]}_{death_position[1]}"
                            from knowledge_base import Proposition
                            agent_kb.add_fact(Proposition(wumpus_prop_name))
                            self.add_log_message(f"Agent died by being eaten by Wumpus at {death_position}")
                            self.add_log_message(f"Mark {death_position} as deadly Wumpus!")
                        
                        # Run inference to update knowledge
                        agent_kb.forward_chain()

                self.add_log_message("Smart reset: LOST - Replay the same world!")
                self.add_log_message("Preserve: pit/wumpus/gold positions, cell colors, knowledge base")
                self.add_log_message("Agent returns to (0,0), try again!")
                
            else:
                # Agent WON or manual reset - generate completely NEW world
                reset_info = self.world.reset()
                
                # Reset agent for new world but preserve learning
                if hasattr(self.agent, 'reset_for_new_world'):
                    self.agent.reset_for_new_world(preserve_learning=True)
                    self.add_log_message("Smart reset: WON! Create new world, preserve knowledge base")
                else:
                    self.add_log_message("Smart reset: New world has been created")

                self.add_log_message(f"New {self.world_size}x{self.world_size} world has been created")
                self.add_log_message("Starting new challenge with old experience!")

            # Reset GUI state and restart simulation
            self.state = GameState.PLAYING
            self.simulation_running = True
            
            # Start new simulation thread
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            self.add_log_message("Game is automatic started")

        else:
            self.add_log_message("No active game to reset")
    
    def complete_reset_game(self):
        """Complete reset - new world and clear all agent learning"""
        self.simulation_running = False
        
        if self.world and self.agent:
            # Reset world (generates new map, clears visited cells)
            reset_info = self.world.reset()
            
            # Complete agent reset (forgets all learning)
            if hasattr(self.agent, 'reset_for_new_world'):
                self.agent.reset_for_new_world(preserve_learning=False)
                self.add_log_message("Full reset: Clear all knowledge base")
            else:
                self.add_log_message("Full reset: Reset agent fully")
            
            # Reset GUI state and restart simulation
            self.state = GameState.PLAYING
            self.simulation_running = True
            
            # Start new simulation thread
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            
            self.add_log_message("New world + No knowledge base!")
            self.add_log_message("Agent started from scratch")
            self.add_log_message("Game is automatically started")

        else:
            self.add_log_message("No active game to reset")
    
    def simulation_loop(self):
        """Main simulation loop (runs in separate thread)"""
        step_count = 0
        max_steps = 1000
        
        while (self.simulation_running and self.world and 
               not self.world.game_over and step_count < max_steps):
            self.execute_step()
            step_count += 1
            time.sleep(self.step_delay)
        
        # Game ended
        if self.world and self.world.game_over:
            self.message_queue.put(("game_over", step_count))
        elif step_count >= max_steps:
            self.message_queue.put(("max_steps", step_count))
    
    def execute_step(self):
        """Execute one simulation step"""
        if not self.world or not self.agent:
            return
        
        # Get current percept
        current_percept = self.world._generate_percepts()
        self.agent.perceive(current_percept)
        
        # Choose action
        action = self.agent.choose_action()
        
        # Execute action
        percept = self.world.step(action)
        
        # Check if wumpus moved and notify agent
        if self.world.wumpus_moved:
            self.agent.perceive(percept, wumpus_moved=True)
        else:
            self.agent.perceive(percept, wumpus_moved=False)
        
        self.agent.update_position(action, percept)
        
        # Queue update message
        self.message_queue.put(("step", {
            "action": action.value,
            "percept": str(percept),
            "step_count": len(self.world.action_log)
        }))
    
    def process_messages(self):
        """Process messages from simulation thread"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "step":
                    self.add_log_message(f"Step {data['step_count']}: {data['action']}")
                    if data['percept'] != "[None]":
                        self.add_log_message(f"  Percept: {data['percept']}")
                    
                    # Check if agent died this step
                    if self.world and not self.world.agent_alive:
                        agent_pos = self.world.agent_position
                        if agent_pos in self.world.pits:
                            self.add_log_message(f"Agent fell into pit at {agent_pos}!")
                        elif agent_pos in self.world.wumpus_positions:
                            self.add_log_message(f"Agent eaten by wumpus at {agent_pos}!")
                
                elif message_type == "game_over":
                    self.simulation_running = False
                    self.state = GameState.GAME_OVER
                    self.add_log_message(f"Game over after {data} steps")
                
                elif message_type == "max_steps":
                    self.simulation_running = False
                    self.add_log_message(f"Max steps ({data}) reached")
                
                elif message_type == "experiment_result":
                    self.add_log_message("🧪 Experiment completed!")
                    self.add_log_message(data)
                
        except queue.Empty:
            pass
    
    def run_experiment(self):
        """Run performance comparison experiment"""
        self.state = GameState.EXPERIMENT
        self.add_log_message("🧪 Starting experiment...")
        
        def experiment_thread():
            try:
                intelligent_results, random_results = run_comparison_experiment(
                    num_trials=5, world_size=self.world_size, 
                    num_wumpus=self.wumpus_count, pit_prob=self.pit_probability
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
                
                result_msg = (f"Intelligent: {intelligent_stats['success_rate']:.0%} success, "
                             f"{intelligent_stats['avg_score']:.0f} avg score | "
                             f"Random: {random_stats['success_rate']:.0%} success, "
                             f"{random_stats['avg_score']:.0f} avg score")
                
                self.message_queue.put(("experiment_result", result_msg))
                
            except Exception as e:
                self.message_queue.put(("experiment_result", f"Experiment failed: {e}"))
            
            # Return to menu
            self.state = GameState.MENU
        
        threading.Thread(target=experiment_thread, daemon=True).start()
    
    def add_log_message(self, message):
        """Add message to game log"""
        self.game_log.append(message)
        if len(self.game_log) > self.max_log_entries:
            self.game_log.pop(0)
    
    def draw_menu(self):
        """Draw the main menu"""
        # Draw menu background first
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill(Colors.BLACK)  # Fallback
        
        # Add semi-transparent overlay for better text readability
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(120)  # Semi-transparent
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
    # Xóa tiêu đề
        
        # Settings panel
        settings_x = 50
        settings_y = 200
        
        # Draw sliders
        for name, slider in self.sliders.items():
            # Render label and value
            label = self.font_medium.render(f"{slider['label']}: {slider['value']}", True, Colors.WHITE)
            # Đặt label bên trái slider, căn giữa theo chiều dọc slider
            label_y = slider['rect'].y + (slider['rect'].height // 2) - (label.get_height() // 2)
            self.screen.blit(label, (slider['rect'].x - label.get_width() - 10, label_y))

            # Slider background
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, slider['rect'])

            # Slider handle
            ratio = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            handle_x = slider['rect'].x + ratio * slider['rect'].width
            handle_rect = pygame.Rect(handle_x - 5, slider['rect'].y - 2, 10, slider['rect'].height + 4)
            pygame.draw.rect(self.screen, Colors.WHITE, handle_rect)
        
        # Draw checkboxes
        for name, checkbox in self.checkboxes.items():
            # Checkbox
            pygame.draw.rect(self.screen, Colors.WHITE, checkbox['rect'], 2)
            if checkbox['checked']:
                pygame.draw.line(self.screen, Colors.GREEN, 
                               (checkbox['rect'].x + 3, checkbox['rect'].y + 10),
                               (checkbox['rect'].x + 8, checkbox['rect'].y + 15), 3)
                pygame.draw.line(self.screen, Colors.GREEN,
                               (checkbox['rect'].x + 8, checkbox['rect'].y + 15),
                               (checkbox['rect'].x + 17, checkbox['rect'].y + 5), 3)
            
            # Label
            label = self.font_medium.render(checkbox['label'], True, Colors.WHITE)
            self.screen.blit(label, (checkbox['rect'].x + 30, checkbox['rect'].y))
        
        # Menu buttons
        self.draw_button(self.buttons['start'], "Start Game", Colors.GREEN)
        self.draw_button(self.buttons['experiment'], "Experiment", Colors.BLUE)
        self.draw_button(self.buttons['quit'], "Quit", Colors.RED)
        
        # Instructions
        instructions = [
            "Controls:",
            "SPACE - Pause/Resume",
            "S - Step (when paused)",
            "R - Smart Reset (preserve learning)",
            "F - Full Reset (forget learning)",
            "ESC - Back to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, Colors.LIGHT_GRAY)
            self.screen.blit(text, (settings_x + 400, 250 + i * 20))
    
    def draw_game(self):
        """Draw the game screen"""
        # Draw game background first
        if self.game_background:
            self.screen.blit(self.game_background, (0, 0))
        else:
            self.screen.fill(Colors.BLACK)  # Fallback
        
        # Add semi-transparent overlay for better visibility
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(80)  # Light overlay to make UI elements more visible
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if not self.world:
            return
        
        # Draw control buttons
        button_color = Colors.ORANGE if self.state == GameState.PAUSED else Colors.BLUE
        pause_text = "Resume" if self.state == GameState.PAUSED else "Pause"
        self.draw_button(self.buttons['pause'], pause_text, button_color)
        self.draw_button(self.buttons['step'], "Step", Colors.CYAN if self.state == GameState.PAUSED else Colors.GRAY)
        self.draw_button(self.buttons['reset'], "Smart Reset", Colors.YELLOW)
        self.draw_button(self.buttons['full_reset'], "Full Reset", Colors.ORANGE)
        self.draw_button(self.buttons['menu'], "Menu", Colors.PURPLE)
        
        # Draw game board
        board_x = 50
        board_y = 200
        self.draw_world(board_x, board_y)
        
        # Draw information panel
        info_x = board_x + self.BOARD_SIZE + 20
        info_y = board_y
        self.draw_info_panel(info_x, info_y)
    
    def draw_world(self, x, y):
        """Draw the game world"""
        if not self.world:
            return
        
        state = self.world.get_world_state()
        size = state['size']
        cell_size = self.BOARD_SIZE // size
        
        # Draw grid background
        for row in range(size):
            for col in range(size):
                cell_x = x + col * cell_size
                cell_y = y + (size - 1 - row) * cell_size  # Flip Y coordinate
                cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                
                # Cell background color
                bg_color = Colors.DARK_GRAY
                pos = (col, row)
                
                # Agent's current position gets special coloring
                if pos == state['agent_position']:
                    if state['agent_alive']:
                        bg_color = Colors.GREEN  # Bright green for living agent
                    else:
                        bg_color = Colors.DARK_RED  # Dark red for dead agent
                elif hasattr(self.agent, 'kb'):
                    safe_cells = self.agent.kb.infer_safe_cells()
                    dangerous_cells = self.agent.kb.infer_dangerous_cells()
                    knowledge = self.agent.kb.get_knowledge_summary()
                    certain_wumpus = knowledge.get('certain_wumpus', set())
                    certain_pits = knowledge.get('certain_pits', set())
                    possible_wumpus = knowledge.get('possible_wumpus', set())
                    possible_pits = knowledge.get('possible_pits', set())
                    
                    # Priority 1: Certain dangerous cells (confirmed wumpus or pit) - RED
                    if pos in certain_wumpus or pos in certain_pits:
                        bg_color = Colors.DARK_RED
                    # Priority 2: Safe cells - GREEN variants
                    elif pos in safe_cells:
                        bg_color = Colors.DARK_GREEN if pos in state['visited_cells'] else (0, 50, 0)
                    # Priority 3: Possible dangerous cells (has warning signs) - YELLOW
                    elif pos in possible_wumpus or pos in possible_pits or pos in dangerous_cells:
                        bg_color = Colors.DARK_YELLOW  # Dark yellow for suspected danger
                    # Priority 4: Visited cells with percepts (stench/breeze detected) - YELLOW
                    elif pos in state['visited_cells'] and hasattr(self.agent, 'kb'):
                        stench_prop = f"Stench_{pos[0]}_{pos[1]}"
                        breeze_prop = f"Breeze_{pos[0]}_{pos[1]}"
                        if any(fact.name == stench_prop for fact in self.agent.kb.facts) or \
                           any(fact.name == breeze_prop for fact in self.agent.kb.facts):
                            bg_color = Colors.DARK_YELLOW  # Dark yellow for warning signs
                    # Priority 5: Adjacent to cells with percepts - YELLOW for potential danger
                    elif hasattr(self.agent, 'kb'):
                        # Check if this cell is adjacent to any cell with stench/breeze
                        adjacent_to_danger = False
                        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            adj_pos = (pos[0] + dx, pos[1] + dy)
                            if adj_pos in state['visited_cells']:
                                stench_prop = f"Stench_{adj_pos[0]}_{adj_pos[1]}"
                                breeze_prop = f"Breeze_{adj_pos[0]}_{adj_pos[1]}"
                                if any(fact.name == stench_prop for fact in self.agent.kb.facts) or \
                                   any(fact.name == breeze_prop for fact in self.agent.kb.facts):
                                    adjacent_to_danger = True
                                    break
                        if adjacent_to_danger and pos not in safe_cells:
                            bg_color = Colors.DARK_YELLOW  # Yellow for potential danger
                
                pygame.draw.rect(self.screen, bg_color, cell_rect)
                pygame.draw.rect(self.screen, Colors.WHITE, cell_rect, 1)
                
                # Draw cell contents
                self.draw_cell_contents(cell_x, cell_y, cell_size, pos, state)
    
    def draw_cell_contents(self, cell_x, cell_y, cell_size, pos, state):
        """Draw contents of a single cell"""
        center_x = cell_x + cell_size // 2
        center_y = cell_y + cell_size // 2
        
        symbols = []
        
        # Show hidden objects if enabled
        if self.show_hidden:
            # Draw pit/hole sprite
            if pos in state['pits']:
                hole_sprite = get_hole_sprite(cell_size - 10)
                if hole_sprite:
                    sprite_rect = hole_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(hole_sprite, sprite_rect)
                else:
                    symbols.append(("🕳️", Colors.BROWN))
            
            # Draw wumpus sprite
            if pos in state['wumpus_positions']:
                wumpus_sprite = get_wumpus_sprite(cell_size - 10)
                if wumpus_sprite:
                    sprite_rect = wumpus_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(wumpus_sprite, sprite_rect)
                else:
                    symbols.append(("👹", Colors.RED))
            
            # Draw gold sprite
            if pos == state['gold_position']:
                gold_sprite = get_gold_sprite(cell_size - 10)
                if gold_sprite:
                    sprite_rect = gold_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(gold_sprite, sprite_rect)
                else:
                    symbols.append(("💰", Colors.GOLD))
        else:
            # Show discovered gold sprite
            if hasattr(self.agent, 'gold_position') and pos == self.agent.gold_position:
                gold_sprite = get_gold_sprite(cell_size - 10)
                if gold_sprite:
                    sprite_rect = gold_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(gold_sprite, sprite_rect)
                else:
                    symbols.append(("💰", Colors.GOLD))
        
        # Show confirmed wumpus and holes based on agent's logical inference
        if hasattr(self.agent, 'kb') and not self.show_hidden:
            knowledge = self.agent.kb.get_knowledge_summary()
            
            # Show wumpus sprite if agent is certain this cell has a wumpus
            if pos in knowledge.get('certain_wumpus', set()):
                wumpus_sprite = get_wumpus_sprite(cell_size - 10)
                if wumpus_sprite:
                    sprite_rect = wumpus_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(wumpus_sprite, sprite_rect)
                else:
                    symbols.append(("👹", Colors.RED))
            
            # Show hole sprite if agent is certain this cell has a pit
            if pos in knowledge.get('certain_pits', set()):
                hole_sprite = get_hole_sprite(cell_size - 10)
                if hole_sprite:
                    sprite_rect = hole_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(hole_sprite, sprite_rect)
                else:
                    symbols.append(("🕳️", Colors.BROWN))
        

        
        # Draw symbols
        if len(symbols) == 1:
            self.draw_emoji_text(symbols[0][0], center_x, center_y, 24)
        elif len(symbols) > 1:
            # Arrange multiple symbols
            for i, (symbol, color) in enumerate(symbols[:4]):
                offset_x = (i % 2 - 0.5) * 15
                offset_y = (i // 2 - 0.5) * 15
                self.draw_emoji_text(symbol, center_x + offset_x, center_y + offset_y, 18)
        
        # Always draw agent sprite when agent is in this position (PRIORITY - draw last/on top)
        if pos == state['agent_position']:
            if state['agent_alive']:
                # Vẽ agent theo hướng
                direction = state['agent_direction']
                if direction == Direction.NORTH:
                    agent_sprite = get_agent_sprite(cell_size - 8, 'up.png')
                elif direction == Direction.SOUTH:
                    agent_sprite = get_agent_sprite(cell_size - 8, 'down.png')
                elif direction == Direction.WEST:
                    agent_sprite = get_agent_sprite(cell_size - 8, 'left.png')
                elif direction == Direction.EAST:
                    agent_sprite = get_agent_sprite(cell_size - 8, 'right.png')
                else:
                    agent_sprite = get_agent_sprite(cell_size - 8)
                if agent_sprite:
                    sprite_rect = agent_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(agent_sprite, sprite_rect)
                else:
                    # Fallback to direction symbols if sprite fails
                    direction_symbols = {
                        Direction.NORTH: "⬆️",
                        Direction.EAST: "➡️", 
                        Direction.SOUTH: "⬇️",
                        Direction.WEST: "⬅️"
                    }
                    agent_symbol = direction_symbols.get(state['agent_direction'], "🤖")
                    self.draw_emoji_text(agent_symbol, center_x, center_y, 24)
            else:
                # Hiển thị Death_skull.png vừa với ô
                from models.character_loader import get_death_skull_sprite
                death_sprite = get_death_skull_sprite(cell_size - 8)
                if death_sprite:
                    sprite_rect = death_sprite.get_rect(center=(center_x, center_y))
                    self.screen.blit(death_sprite, sprite_rect)
                else:
                    self.draw_emoji_text("💀", center_x, center_y, 32)
                # Add red overlay to indicate death
                overlay = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                pygame.draw.circle(overlay, (255, 0, 0, 100), (cell_size // 2, cell_size // 2), cell_size // 3, 3)
                self.screen.blit(overlay, (cell_x, cell_y))

    
    def draw_emoji_text(self, text, x, y, size):
        """Draw text (including emojis) centered at position"""
        font = pygame.font.Font(None, size)
        surface = font.render(text, True, Colors.WHITE)
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)
    
    def draw_info_panel(self, x, y):
        """Draw information panel"""
        if not self.world:
            return
        
        state = self.world.get_world_state()
        
        # Game status
        info_lines = [
            f"Status: {'Running' if not state['game_over'] else 'Finished'}",
            f"Score: {state['score']}",
            f"Position: {state['agent_position']}",
            f"Direction: {state['agent_direction'].name}",
            f"Alive: {'Yes' if state['agent_alive'] else 'No'}",
            f"Arrow: {'Yes' if state['agent_has_arrow'] else 'No'}",
            f"Gold: {'Yes' if state['agent_has_gold'] else 'No'}",
            f"Actions: {state['action_count']}",
            "",
        ]
        
        # Agent knowledge
        if hasattr(self.agent, 'kb'):
            knowledge = self.agent.kb.get_knowledge_summary()
            info_lines.extend([
                "Agent Knowledge:",
                f"  Safe cells: {len(knowledge['safe_cells'])}",
                f"  Dangerous: {len(knowledge['dangerous_cells'])}",
                f"  Possible wumpus: {len(knowledge['possible_wumpus'])}",
                "",
            ])
            
            if hasattr(self.agent, 'gold_position') and self.agent.gold_position:
                info_lines.append(f"Gold location: {self.agent.gold_position}")
        
        # Agent learning status
        if hasattr(self.agent, 'games_played'):
            info_lines.extend([
                "Learning Status:",
                f"  Games played: {self.agent.games_played}",
                f"  Strategy: {self.agent.exploration_strategy}",
                f"  Caution level: {getattr(self.agent, 'adaptive_caution', 0.3):.2f}",
                f"  Successes: {len(getattr(self.agent, 'successful_strategies', []))}",
                "",
            ])
        
        # Draw info text
        for i, line in enumerate(info_lines):
            text = self.font_small.render(line, True, Colors.WHITE)
            self.screen.blit(text, (x, y + i * 20))
        
        # Draw game log
        log_y = y + len(info_lines) * 20 + 20
        log_title = self.font_medium.render("Game Log:", True, Colors.WHITE)
        self.screen.blit(log_title, (x, log_y))
        
        for i, message in enumerate(self.game_log[-15:]):  # Show last 15 messages
            color = Colors.GREEN if "🎮" in message or "🏁" in message else Colors.LIGHT_GRAY
            text = self.font_small.render(message, True, color)
            self.screen.blit(text, (x, log_y + 25 + i * 16))
    
    def draw_button(self, rect, text, color):
        """Draw a button"""
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, Colors.WHITE, rect, 2)
        
        text_surface = self.font_medium.render(text, True, Colors.BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_experiment_screen(self):
        """Draw experiment screen"""
        # Draw game background
        if self.game_background:
            self.screen.blit(self.game_background, (0, 0))
        else:
            self.screen.fill(Colors.BLACK)
        
        # Add overlay for better text visibility
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("🧪 Running Experiment...", True, Colors.WHITE)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Animated progress indicator
        self.animation_frame += 1
        dots = "." * ((self.animation_frame // 30) % 4)
        progress_text = self.font_medium.render(f"Comparing agents{dots}", True, Colors.LIGHT_GRAY)
        progress_rect = progress_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.screen.blit(progress_text, progress_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_game()  # Draw game state
        
        # Overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if not self.world:
            return
        
        state = self.world.get_world_state()
        
        # Game over text
        if state['agent_alive']:
            if state['agent_has_gold']:
                title = "SUCCESS!"
                subtitle = "Agent escaped with gold!"
                color = Colors.GREEN
            else:
                title = "ESCAPED"
                subtitle = "Agent climbed out safely"
                color = Colors.BLUE
        else:
            title = "GAME OVER"
            subtitle = "Agent died"
            color = Colors.RED
        
        title_surface = self.font_large.render(title, True, color)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(title_surface, title_rect)
        
        subtitle_surface = self.font_medium.render(subtitle, True, Colors.WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        score_text = f"Final Score: {state['score']}"
        score_surface = self.font_medium.render(score_text, True, Colors.WHITE)
        score_rect = score_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 40))
        self.screen.blit(score_surface, score_rect)
        
        # Instructions
        instruction = "R - Smart Reset (keep learning) | F - Full Reset (forget all) | ESC - Menu"
        instruction_surface = self.font_small.render(instruction, True, Colors.LIGHT_GRAY)
        instruction_rect = instruction_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 80))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Process messages from simulation thread
            self.process_messages()
            
            # Draw based on current state
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state in [GameState.PLAYING, GameState.PAUSED]:
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.EXPERIMENT:
                self.draw_experiment_screen()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        # Cleanup
        pygame.quit()

def main():
    """Main function to start the pygame GUI"""
    try:
        # Kiểm tra file nhạc và báo lỗi chi tiết
        music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music.wav")
        if not os.path.exists(music_path):
            print(f"Error: File music.wav not found at {music_path}")
        else:
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                print("Background music started successfully.")
            except Exception as e:
                print(f"Error loading or playing music.wav: {e}")
        gui = WumpusWorldPygameGUI()
        gui.run()
    except Exception as e:
        print(f"Error starting Pygame GUI: {e}")
        print("Make sure pygame is installed: pip install pygame")

if __name__ == "__main__":
    main()
