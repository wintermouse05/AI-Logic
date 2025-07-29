"""
Wumpus World Pygame GUI Demo
Demonstrates the key features of the pygame interface
"""

import os
import sys

def main():
    print("🏰 Wumpus World - Pygame GUI Demo")
    print("=" * 50)
    
    print("""
🎮 PYGAME GUI FEATURES:

📋 Main Menu:
   • Interactive settings with sliders and checkboxes
   • World size: 4x4 to 10x10
   • Wumpus count: 1-4
   • Pit probability: 10%-50%
   • Agent type: Intelligent vs Random
   • Moving wumpus option
   • Show hidden objects (debug mode)

🎯 Game Interface:
   • Real-time game board visualization
   • Color-coded cells (safe=green, dangerous=red)
   • Agent direction indicators (arrows)
   • Percept symbols (💨=stench, 🌪️=breeze)
   • Gold (💰) and hazard visualization
   • Visited cell tracking

🎛️ Game Controls:
   • Pause/Resume button
   • Single step mode for debugging
   • Reset game
   • Return to menu
   • Speed control slider

📊 Information Panel:
   • Live game statistics
   • Agent knowledge display
   • Safe/dangerous cell counts
   • Current position and status
   • Game log with action history

🧪 Experiment Mode:
   • Performance comparison
   • Intelligent vs Random agent
   • Success rate analysis
   • Statistical results

⌨️ Keyboard Shortcuts:
   • SPACE - Pause/Resume
   • S - Single step (when paused)
   • R - Reset game
   • ESC - Back to menu/quit

🎨 Visual Features:
   • Smooth animations
   • Emoji-based symbols
   • Color-coded feedback
   • Real-time updates
   • Professional UI design

USAGE:
1. Run: python pygame_gui.py
2. Adjust settings on main menu
3. Click 'Start Game' to begin
4. Use controls to manage simulation
5. Try 'Experiment' for AI comparison

The GUI provides an intuitive way to understand how the
intelligent agent reasons about the Wumpus World using
propositional logic and risk-aware pathfinding.
""")
    
    print("\n🚀 To start the GUI:")
    print("cd Source && python pygame_gui.py")
    print("\nOr use the launcher:")
    print("python run_gui.py")

if __name__ == "__main__":
    main()
