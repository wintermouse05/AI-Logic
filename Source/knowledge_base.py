"""
Knowledge Base and Inference Engine for Wumpus World
This module implements propositional logic inference using forward chaining.
"""

from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass
from environment import Direction, Percept
import itertools

@dataclass
class Proposition:
    """Represents a propositional logic statement"""
    name: str
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return isinstance(other, Proposition) and self.name == other.name

@dataclass 
class Rule:
    """Represents a logical rule (implication)"""
    premises: Set[Proposition]  # Antecedent (if part)
    conclusion: Proposition     # Consequent (then part)
    
    def __str__(self):
        if len(self.premises) == 0:
            return f"⊢ {self.conclusion}"
        elif len(self.premises) == 1:
            return f"{list(self.premises)[0]} → {self.conclusion}"
        else:
            premises_str = " ∧ ".join(str(p) for p in self.premises)
            return f"({premises_str}) → {self.conclusion}"

class KnowledgeBase:
    """Knowledge Base for Wumpus World using Propositional Logic"""
    
    def __init__(self, world_size: int, num_wumpus: int = 2):
        self.world_size = world_size
        self.num_wumpus = num_wumpus
        self.facts: Set[Proposition] = set()  # Known true propositions
        self.rules: List[Rule] = []           # Inference rules
        self.negative_facts: Set[Proposition] = set()  # Known false propositions
        
        # Initialize with basic world knowledge
        self._initialize_world_rules()
    
    def _create_proposition(self, prop_type: str, x: int, y: int) -> Proposition:
        """Create a proposition for a specific cell"""
        return Proposition(f"{prop_type}_{x}_{y}")
    
    def _initialize_world_rules(self):
        """Initialize basic world rules and constraints"""
        
        # Rule 1: Starting cell (0,0) is safe
        self.add_fact(Proposition("Safe_0_0"))
        self.add_negative_fact(Proposition("Pit_0_0"))
        self.add_negative_fact(Proposition("Wumpus_0_0"))
        
        # Rule 2: Breeze rules - if there's a breeze at (x,y), 
        # then at least one adjacent cell has a pit
        for x in range(self.world_size):
            for y in range(self.world_size):
                breeze_prop = self._create_proposition("Breeze", x, y)
                adjacent_pits = []
                
                # Get adjacent cells
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adj_x, adj_y = x + dx, y + dy
                    if self._is_valid_position(adj_x, adj_y):
                        pit_prop = self._create_proposition("Pit", adj_x, adj_y)
                        adjacent_pits.append(pit_prop)
                
                # Breeze → (Pit_adj1 ∨ Pit_adj2 ∨ ... ∨ Pit_adjN)
                # We'll handle disjunction through multiple rules
                if adjacent_pits:
                    for pit_prop in adjacent_pits:
                        # If no breeze and all other adjacent cells are known safe of pits,
                        # then this cell has no pit
                        pass  # Complex disjunctive reasoning handled in inference
        
        # Rule 3: Stench rules - similar to breeze but for wumpus
        for x in range(self.world_size):
            for y in range(self.world_size):
                stench_prop = self._create_proposition("Stench", x, y)
                adjacent_wumpus = []
                
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adj_x, adj_y = x + dx, y + dy
                    if self._is_valid_position(adj_x, adj_y):
                        wumpus_prop = self._create_proposition("Wumpus", adj_x, adj_y)
                        adjacent_wumpus.append(wumpus_prop)
        
        # Rule 4: Safety rules
        # Safe(x,y) ↔ ¬Pit(x,y) ∧ ¬Wumpus(x,y)
        for x in range(self.world_size):
            for y in range(self.world_size):
                safe_prop = self._create_proposition("Safe", x, y)
                pit_prop = self._create_proposition("Pit", x, y)
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                
                # If not pit and not wumpus, then safe
                self.add_rule(Rule(set(), safe_prop))  # Will be handled in inference
                
                # If pit or wumpus, then not safe
                # If safe, then not pit and not wumpus
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within world boundaries"""
        return 0 <= x < self.world_size and 0 <= y < self.world_size
    
    def add_fact(self, fact: Proposition):
        """Add a known fact to the knowledge base"""
        #print(f"[KB] Adding fact: {fact}")
        self.facts.add(fact)
    
    def add_negative_fact(self, fact: Proposition):
        """Add a known negative fact (something that is false)"""
        self.negative_facts.add(fact)
    
    def add_rule(self, rule: Rule):
        """Add an inference rule"""
        self.rules.append(rule)
    
    def is_known_true(self, prop: Proposition) -> bool:
        """Check if proposition is known to be true"""
        return prop in self.facts
    
    def is_known_false(self, prop: Proposition) -> bool:
        """Check if proposition is known to be false"""
        return prop in self.negative_facts
    
    def is_unknown(self, prop: Proposition) -> bool:
        """Check if proposition is unknown"""
        return not self.is_known_true(prop) and not self.is_known_false(prop)
    
    def update_from_percept(self, position: Tuple[int, int], percept: Percept):
        """Update knowledge base based on percept at given position"""
        x, y = position
        
        # Update breeze information
        breeze_prop = self._create_proposition("Breeze", x, y)
        if percept.breeze:
            self.add_fact(breeze_prop)
        else:
            self.add_negative_fact(breeze_prop)
        
        # Update stench information
        stench_prop = self._create_proposition("Stench", x, y)
        if percept.stench:
            self.add_fact(stench_prop)
        else:
            self.add_negative_fact(stench_prop)
        
        # Update glitter information
        glitter_prop = self._create_proposition("Glitter", x, y)
        if percept.glitter:
            self.add_fact(glitter_prop)
            # Gold is at this position
            gold_prop = self._create_proposition("Gold", x, y)
            self.add_fact(gold_prop)
        else:
            self.add_negative_fact(glitter_prop)
        
        # If no breeze, adjacent cells have no pits
        if not percept.breeze:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                adj_x, adj_y = x + dx, y + dy
                if self._is_valid_position(adj_x, adj_y):
                    pit_prop = self._create_proposition("Pit", adj_x, adj_y)
                    self.add_negative_fact(pit_prop)
        
        # If no stench, adjacent cells have no wumpus
        if not percept.stench:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                adj_x, adj_y = x + dx, y + dy
                if self._is_valid_position(adj_x, adj_y):
                    wumpus_prop = self._create_proposition("Wumpus", adj_x, adj_y)
                    self.add_negative_fact(wumpus_prop)
        
        # Current position is safe (agent is there and alive)
        safe_prop = self._create_proposition("Safe", x, y)
        self.add_fact(safe_prop)
        pit_prop = self._create_proposition("Pit", x, y)
        wumpus_prop = self._create_proposition("Wumpus", x, y)
        self.add_negative_fact(pit_prop)
        self.add_negative_fact(wumpus_prop)
    
    def infer_safe_cells(self) -> Set[Tuple[int, int]]:
        """Infer which cells are definitely safe"""
        safe_cells = set()
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                pit_prop = self._create_proposition("Pit", x, y)
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                
                # Cell is safe if we know there's no pit and no wumpus
                if self.is_known_false(pit_prop) and self.is_known_false(wumpus_prop):
                    safe_cells.add((x, y))
        
        return safe_cells
    
    def infer_dangerous_cells(self) -> Set[Tuple[int, int]]:
        """Infer which cells are definitely dangerous"""
        dangerous_cells = set()
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                pit_prop = self._create_proposition("Pit", x, y)
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                safe_prop = self._create_proposition("Safe", x, y)
                
                # Cell is dangerous if we know there's a pit or wumpus
                if self.is_known_true(pit_prop) or self.is_known_true(wumpus_prop):
                    dangerous_cells.add((x, y))
                
                # Cell is also dangerous if we explicitly know it's not safe
                elif self.is_known_false(safe_prop):
                    dangerous_cells.add((x, y))
        
        return dangerous_cells
    
    def infer_wumpus_locations(self) -> Set[Tuple[int, int]]:
        """Infer possible wumpus locations using constraint satisfaction"""
        possible_wumpus = set()
        
        # Find cells where we know there's a wumpus
        for x in range(self.world_size):
            for y in range(self.world_size):
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                if self.is_known_true(wumpus_prop):
                    possible_wumpus.add((x, y))
        
        # Use stench information to constrain wumpus locations
        stench_cells = []
        for x in range(self.world_size):
            for y in range(self.world_size):
                stench_prop = self._create_proposition("Stench", x, y)
                if self.is_known_true(stench_prop):
                    stench_cells.append((x, y))
        
        # For each stench cell, at least one adjacent cell must have a wumpus
        if stench_cells and len(possible_wumpus) < self.num_wumpus:
            possible_wumpus.update(self._solve_wumpus_constraints(stench_cells))
        
        return possible_wumpus
    
    def _solve_wumpus_constraints(self, stench_cells: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Solve wumpus location constraints using model checking"""
        # Get all possible wumpus locations (not known to be safe)
        candidates = []
        for x in range(self.world_size):
            for y in range(self.world_size):
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                if not self.is_known_false(wumpus_prop):
                    candidates.append((x, y))
        
        # Try all combinations of wumpus placements
        definite_wumpus = set()
        
        # Check which cells must have wumpus in all valid models
        for candidate in candidates:
            # Check if this candidate appears in all valid models
            appears_in_all = True
            
            # Generate models without this candidate
            other_candidates = [c for c in candidates if c != candidate]
            if len(other_candidates) >= self.num_wumpus:
                for wumpus_combo in itertools.combinations(other_candidates, self.num_wumpus):
                    if self._is_valid_wumpus_model(set(wumpus_combo), stench_cells):
                        appears_in_all = False
                        break
            
            if appears_in_all:
                definite_wumpus.add(candidate)
        
        return definite_wumpus
    
    def _is_valid_wumpus_model(self, wumpus_positions: Set[Tuple[int, int]], 
                             stench_cells: List[Tuple[int, int]]) -> bool:
        """Check if a wumpus model is consistent with stench observations"""
        for stench_x, stench_y in stench_cells:
            # Check if any adjacent cell has a wumpus
            has_adjacent_wumpus = False
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                adj_x, adj_y = stench_x + dx, stench_y + dy
                if (adj_x, adj_y) in wumpus_positions:
                    has_adjacent_wumpus = True
                    break
            
            if not has_adjacent_wumpus:
                return False
        
        return True
    
    def forward_chain(self) -> bool:
        """Apply forward chaining inference"""
        changed = True
        iterations = 0
        max_iterations = 100  # Prevent infinite loops
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            
            # Apply breeze/stench inference rules
            changed |= self._apply_breeze_rules()
            changed |= self._apply_stench_rules()
            changed |= self._apply_safety_rules()
        
        return iterations < max_iterations
    
    def _apply_breeze_rules(self) -> bool:
        """Apply inference rules related to breeze and pits"""
        changed = False
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                breeze_prop = self._create_proposition("Breeze", x, y)
                
                # Get adjacent cells
                adjacent_cells = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adj_x, adj_y = x + dx, y + dy
                    if self._is_valid_position(adj_x, adj_y):
                        adjacent_cells.append((adj_x, adj_y))
                
                # If we know there's no breeze, all adjacent cells have no pits
                if self.is_known_false(breeze_prop):
                    for adj_x, adj_y in adjacent_cells:
                        pit_prop = self._create_proposition("Pit", adj_x, adj_y)
                        if not self.is_known_false(pit_prop):
                            self.add_negative_fact(pit_prop)
                            changed = True
                
                # If there's a breeze and all but one adjacent cells are known pit-free,
                # then the remaining cell must have a pit
                elif self.is_known_true(breeze_prop):
                    unknown_cells = []
                    known_pit_free_cells = []
                    
                    for adj_x, adj_y in adjacent_cells:
                        pit_prop = self._create_proposition("Pit", adj_x, adj_y)
                        if self.is_unknown(pit_prop):
                            unknown_cells.append((adj_x, adj_y))
                        elif self.is_known_false(pit_prop):
                            known_pit_free_cells.append((adj_x, adj_y))
                    
                    # Only conclude the unknown cell has a pit if:
                    # 1. There's exactly one unknown cell, AND
                    # 2. All other adjacent cells are confirmed pit-free
                    if (len(unknown_cells) == 1 and 
                        len(known_pit_free_cells) == len(adjacent_cells) - 1):
                        
                        adj_x, adj_y = unknown_cells[0]
                        pit_prop = self._create_proposition("Pit", adj_x, adj_y)
                        self.add_fact(pit_prop)
                        changed = True  

                    # Special case: If there are 2 unknown cells and both breeze and stench are present,
                    # we can infer that one cell has a pit and the other has a wumpus
                    elif (len(unknown_cells) == 2 and 
                          len(known_pit_free_cells) == len(adjacent_cells) - 2):
                        
                        stench_prop = self._create_proposition("Stench", x, y)
                        if self.is_known_true(stench_prop):
                            # Both breeze and stench are present, so one unknown cell has pit, other has wumpus
                            # We can't determine which is which without more information, but we know
                            # that these cells are dangerous
                            for adj_x, adj_y in unknown_cells:
                                safe_prop = self._create_proposition("Safe", adj_x, adj_y)
                                if not self.is_known_false(safe_prop):
                                    self.add_negative_fact(safe_prop)
                                    changed = True
                    
        return changed
    
    def _apply_stench_rules(self) -> bool:
        """Apply inference rules related to stench and wumpus"""
        changed = False
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                stench_prop = self._create_proposition("Stench", x, y)
                
                # Get adjacent cells
                adjacent_cells = []
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adj_x, adj_y = x + dx, y + dy
                    if self._is_valid_position(adj_x, adj_y):
                        adjacent_cells.append((adj_x, adj_y))
                
                # If we know there's no stench, all adjacent cells have no wumpus
                if self.is_known_false(stench_prop):
                    for adj_x, adj_y in adjacent_cells:
                        wumpus_prop = self._create_proposition("Wumpus", adj_x, adj_y)
                        if not self.is_known_false(wumpus_prop):
                            self.add_negative_fact(wumpus_prop)
                            changed = True
                
                # If there's a stench and all but one adjacent cells are known wumpus-free,
                # then the remaining cell must have a wumpus
                elif self.is_known_true(stench_prop):
                    unknown_cells = []
                    known_wumpus_free_cells = []
                    
                    for adj_x, adj_y in adjacent_cells:
                        wumpus_prop = self._create_proposition("Wumpus", adj_x, adj_y)
                        if self.is_unknown(wumpus_prop):
                            unknown_cells.append((adj_x, adj_y))
                        elif self.is_known_false(wumpus_prop):
                            known_wumpus_free_cells.append((adj_x, adj_y))
                    
                    # Only conclude the unknown cell has a wumpus if:
                    # 1. There's exactly one unknown cell, AND
                    # 2. All other adjacent cells are confirmed wumpus-free
                    if (len(unknown_cells) == 1 and 
                        len(known_wumpus_free_cells) == len(adjacent_cells) - 1):
                        
                        adj_x, adj_y = unknown_cells[0]
                        wumpus_prop = self._create_proposition("Wumpus", adj_x, adj_y)
                        self.add_fact(wumpus_prop)
                        changed = True
                    
                    # Special case: If there are 2 unknown cells and both stench and breeze are present,
                    # we can infer that one cell has a wumpus and the other has a pit
                    elif (len(unknown_cells) == 2 and 
                          len(known_wumpus_free_cells) == len(adjacent_cells) - 2):
                        
                        breeze_prop = self._create_proposition("Breeze", x, y)
                        if self.is_known_true(breeze_prop):
                            # Both stench and breeze are present, so one unknown cell has wumpus, other has pit
                            # We can't determine which is which without more information, but we know
                            # that these cells are dangerous
                            for adj_x, adj_y in unknown_cells:
                                safe_prop = self._create_proposition("Safe", adj_x, adj_y)
                                if not self.is_known_false(safe_prop):
                                    self.add_negative_fact(safe_prop)
                                    changed = True
                    
        return changed
    
    def _apply_safety_rules(self) -> bool:
        """Apply safety inference rules"""
        changed = False
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                pit_prop = self._create_proposition("Pit", x, y)
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                safe_prop = self._create_proposition("Safe", x, y)
                
                # If no pit and no wumpus, then safe
                if (self.is_known_false(pit_prop) and self.is_known_false(wumpus_prop) 
                    and not self.is_known_true(safe_prop)):
                    self.add_fact(safe_prop)
                    changed = True
                
                # If safe, then no pit and no wumpus
                elif self.is_known_true(safe_prop):
                    if not self.is_known_false(pit_prop):
                        self.add_negative_fact(pit_prop)
                        changed = True
                    if not self.is_known_false(wumpus_prop):
                        self.add_negative_fact(wumpus_prop)
                        changed = True
        
        return changed
    
    def get_knowledge_summary(self) -> Dict:
        """Get summary of current knowledge for debugging/visualization"""
        summary = {
            'facts': [str(f) for f in self.facts],
            'negative_facts': [str(f) for f in self.negative_facts],
            'safe_cells': list(self.infer_safe_cells()),
            'dangerous_cells': list(self.infer_dangerous_cells()),
            'possible_wumpus': list(self.infer_wumpus_locations()),
            'certain_wumpus': list(self.infer_certain_wumpus()),
            'certain_pits': list(self.infer_certain_pits())
        }
        return summary
    
    def infer_certain_wumpus(self) -> Set[Tuple[int, int]]:
        """Get cells where we are certain there is a wumpus"""
        certain_wumpus = set()
        
        # Find cells where we explicitly know there's a wumpus
        for x in range(self.world_size):
            for y in range(self.world_size):
                wumpus_prop = self._create_proposition("Wumpus", x, y)
                if self.is_known_true(wumpus_prop):
                    certain_wumpus.add((x, y))
        
        return certain_wumpus
    
    def infer_certain_pits(self) -> Set[Tuple[int, int]]:
        """Get cells where we are certain there is a pit"""
        certain_pits = set()
        
        # Find cells where we explicitly know there's a pit
        for x in range(self.world_size):
            for y in range(self.world_size):
                pit_prop = self._create_proposition("Pit", x, y)
                if self.is_known_true(pit_prop):
                    certain_pits.add((x, y))
        
        return certain_pits
