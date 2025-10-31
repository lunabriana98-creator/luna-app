"""
LUNA COHERENCE FRAMEWORK - Production Version
Ψ² + Δ² = Ω² | Created by: Briana Luna
"""

import re
from typing import Tuple
from dataclasses import dataclass
from enum import Enum

class ProcessingState(Enum):
    PSI = "chaos"
    DELTA = "transform"
    OMEGA = "coherent"

@dataclass
class CoherenceMetrics:
    psi_score: float
    delta_score: float
    omega_score: float
    geometric_conservation: float
    coherence_efficiency: float
    state: ProcessingState
    
    def __str__(self):
        return f"""
Ψ (Chaos):         {self.psi_score:.3f}
Δ (Transform):     {self.delta_score:.3f}  
Ω (Coherence):     {self.omega_score:.3f}
Conservation:      {self.geometric_conservation:.3f}
Efficiency:        {self.coherence_efficiency:.3f}
State:             {self.state.value}
"""
    
    def to_dict(self):
        """For API responses"""
        return {
            "psi": self.psi_score,
            "delta": self.delta_score,
            "omega": self.omega_score,
            "conservation": self.geometric_conservation,
            "efficiency": self.coherence_efficiency,
            "state": self.state.value
        }

class ChaosDetector:
    # Compiled patterns = 10x faster
    HEDGING = re.compile(r'\b(maybe|perhaps|possibly|might|could|probably|likely|I think|I believe|I guess|I suppose|seems like|kind of|sort of|somewhat|rather|fairly)\b', re.IGNORECASE)
    UNCERTAINTY = re.compile(r'\b(unclear|ambiguous|uncertain|confused|unsure|unknown|don\'t know|can\'t tell|hard to say|difficult to determine|question|doubt|wonder)\b', re.IGNORECASE)
    
    def detect_chaos(self, text: str) -> float:
        if not text:
            return 0.0
        words = len(text.split())
        if words == 0:
            return 0.0
        
        hedging = len(self.HEDGING.findall(text))
        uncertainty = len(self.UNCERTAINTY.findall(text))
        questions = text.count('?') * 2
        
        chaos_markers = hedging + uncertainty + questions
        normalized = (chaos_markers / words) * 100
        return min(normalized / 20.0, 1.0)

class TransformationEngine:
    # Pre-compiled transformations
    TRANSFORMS = [
        (re.compile(r'\bI think that\b', re.I), ''),
        (re.compile(r'\bI believe that\b', re.I), ''),
        (re.compile(r'\b(perhaps|maybe|possibly)\b', re.I), ''),
        (re.compile(r'\b(kind|sort) of\b', re.I), ''),
        (re.compile(r'\bmight be\b', re.I), 'is'),
        (re.compile(r'\bcould be\b', re.I), 'is'),
        (re.compile(r'\bseems to be\b', re.I), 'is'),
        (re.compile(r'\bappears to be\b', re.I), 'is'),
        (re.compile(r'\b(is |are )?unclear\b', re.I), 'shows'),
        (re.compile(r'\bambiguous\b', re.I), 'clear'),
    ]
    
    def __init__(self):
        self.chaos_detector = ChaosDetector()
    
    def optimize_transform(self, input_text: str) -> Tuple[str, float]:
        if not input_text:
            return input_text, 0.0
        
        initial_chaos = self.chaos_detector.detect_chaos(input_text)
        result = input_text
        
        # Apply all transforms in one pass
        for pattern, replacement in self.TRANSFORMS:
            result = pattern.sub(replacement, result)
        
        # Clean whitespace
        result = re.sub(r'\s+', ' ', result).strip()
        
        final_chaos = self.chaos_detector.detect_chaos(result)
        chaos_reduction = initial_chaos - final_chaos
        delta_score = max(0.0, min(1.0, chaos_reduction / max(initial_chaos, 0.1)))
        
        return result, delta_score

class LunaFramework:
    """Main API - Single class for easy integration"""
    
    def __init__(self):
        self.chaos_detector = ChaosDetector()
        self.transformer = TransformationEngine()
    
    def process(self, text: str) -> Tuple[str, CoherenceMetrics]:
        """Transform text and return metrics"""
        psi_score = self.chaos_detector.detect_chaos(text)
        transformed, delta_score = self.transformer.optimize_transform(text)
        
        # Calculate coherence
        final_chaos = self.chaos_detector.detect_chaos(transformed)
        omega_score = 1.0 - final_chaos
        
        # Geometric validation
        psi_sq = psi_score ** 2
        delta_sq = delta_score ** 2
        omega_sq = omega_score ** 2
        
        expected = psi_sq + delta_sq
        conservation = 1.0 - abs(omega_sq - expected)
        efficiency = omega_sq / max(psi_sq + delta_sq, 0.01)
        
        # Determine state
        if psi_score > 0.6:
            state = ProcessingState.PSI
        elif delta_score > 0.3:
            state = ProcessingState.DELTA
        else:
            state = ProcessingState.OMEGA
        
        metrics = CoherenceMetrics(
            psi_score=psi_score,
            delta_score=delta_score,
            omega_score=omega_score,
            geometric_conservation=conservation,
            coherence_efficiency=efficiency,
            state=state
        )
        
        return transformed, metrics
    
    def quick_score(self, text: str) -> float:
        """Fast chaos scoring for batch processing"""
        return self.chaos_detector.detect_chaos(text)


# Simple demo
if __name__ == "__main__":
    framework = LunaFramework()
    
    test = "I think maybe this could possibly be interesting, perhaps."
    result, metrics = framework.process(test)
    
    print("INPUT:", test)
    print("OUTPUT:", result)
    print(metrics)
