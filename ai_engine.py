"""
ai_engine.py - Core AI implementation for CodeFix

This module implements semantic similarity search using sentence transformers
to find relevant bug solutions based on user descriptions.
"""

import json
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from models import BugReport, BugSolution


class BugSolutionAI:
    """
    AI engine for finding bug solutions using semantic similarity search.
    
    This class loads a pre-trained sentence transformer model and uses it to
    find the most similar bug examples from our knowledge base.
    """
    
    def __init__(self):
        """Initialize the AI engine with model and examples."""
        self.model = None
        self.examples = []
        self.example_embeddings = None
        self.model_loaded = False
        
        # Load examples and prepare embeddings
        self._load_examples()
        self._load_model()
        self._prepare_embeddings()
    
    def _load_examples(self):
        """Load bug examples from data/examples.json."""
        examples_path = Path("data/examples.json")
        if examples_path.exists():
            with open(examples_path, 'r') as f:
                self.examples = json.load(f)
        else:
            # Fallback to default examples if file doesn't exist
            self.examples = self._get_default_examples()
    
    def _get_default_examples(self) -> List[Dict[str, Any]]:
        """Return default React bug examples if no examples.json exists."""
        return [
            {
                "title": "Fix React State Mutation",
                "description": "React component not updating when state changes. Direct mutation of state objects/arrays doesn't trigger re-renders.",
                "solution": "React doesn't detect direct state mutations. You need to create new objects/arrays to trigger re-renders. Use the spread operator or create new instances.",
                "code_example": "// ❌ Direct mutation\ntodos.push(item);\nsetTodos(todos);\n\n// ✅ New array\nsetTodos([...todos, item]);",
                "source": "React Documentation - State Updates",
                "tags": ["react", "state", "mutation", "hooks"],
                "keywords": ["state", "update", "mutation", "re-render", "useState"]
            },
            {
                "title": "Fix useEffect Infinite Loop",
                "description": "useEffect hook running infinitely, causing performance issues and potential crashes.",
                "solution": "useEffect runs when dependencies change. If you're setting state inside useEffect without proper dependencies, it can create infinite loops. Add missing dependencies or use useCallback/useMemo.",
                "code_example": "// ❌ Infinite loop\nuseEffect(() => {\n  setCount(count + 1);\n}, []);\n\n// ✅ Proper dependency\nuseEffect(() => {\n  setCount(prev => prev + 1);\n}, []);",
                "source": "React Hooks Documentation",
                "tags": ["react", "useEffect", "hooks", "infinite-loop"],
                "keywords": ["useEffect", "infinite", "loop", "dependency", "hooks"]
            },
            {
                "title": "Fix Event Handler Binding",
                "description": "Event handlers not working properly, especially in loops or when passing functions as props.",
                "solution": "Event handlers need proper binding or should be defined as arrow functions to preserve 'this' context. Use arrow functions or bind methods properly.",
                "code_example": "// ❌ Loses context\n<button onClick={this.handleClick}>Click</button>\n\n// ✅ Arrow function preserves context\n<button onClick={() => this.handleClick()}>Click</button>",
                "source": "React Event Handling Documentation",
                "tags": ["react", "events", "binding", "handlers"],
                "keywords": ["event", "handler", "binding", "onClick", "context"]
            }
        ]
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            print("Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_loaded = True
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.model_loaded = False
    
    def _prepare_embeddings(self):
        """Generate embeddings for all examples and save them."""
        if not self.model_loaded or not self.examples:
            return
        
        try:
            # Generate embeddings for example descriptions
            example_texts = [example['description'] for example in self.examples]
            embeddings = self.model.encode(example_texts)
            
            # Save embeddings for future use
            embeddings_path = Path("data/embeddings.npy")
            embeddings_path.parent.mkdir(exist_ok=True)
            np.save(embeddings_path, embeddings)
            
            self.example_embeddings = embeddings
            print(f"✅ Generated embeddings for {len(self.examples)} examples")
            
        except Exception as e:
            print(f"❌ Failed to generate embeddings: {e}")
            self.example_embeddings = None
    
    def find_solution(self, bug_report: BugReport) -> Optional[BugSolution]:
        """
        Find the best matching solution for a bug report.
        
        Args:
            bug_report: The bug report to analyze
            
        Returns:
            BugSolution if confident match found, None otherwise
        """
        if not self.model_loaded or self.example_embeddings is None:
            return None
        
        try:
            # Generate embedding for the bug description
            bug_embedding = self.model.encode([bug_report.description])
            
            # Calculate similarity with all examples
            similarities = cosine_similarity(bug_embedding, self.example_embeddings)
            similarity_scores = similarities[0]
            
            # Find best match
            best_match_idx = np.argmax(similarity_scores)
            best_similarity = similarity_scores[best_match_idx]
            
            # Calculate confidence
            confidence = self._calculate_confidence(best_similarity, bug_report)
            
            # Return solution if confidence is above threshold
            if confidence > 0.5:
                return self._format_solution(
                    self.examples[best_match_idx], 
                    confidence, 
                    best_similarity
                )
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error finding solution: {e}")
            return None
    
    def _calculate_confidence(self, similarity_score: float, bug_report: BugReport) -> float:
        """
        Calculate confidence score based on similarity and other factors.
        
        Args:
            similarity_score: Raw similarity score (0-1)
            bug_report: The bug report being analyzed
            
        Returns:
            Confidence score (0-1)
        """
        # Start with base similarity score
        base_confidence = float(similarity_score)
        
        # Apply sigmoid-like transformation to spread scores
        adjusted_confidence = 1 / (1 + np.exp(-10 * (base_confidence - 0.5)))
        
        # Ensure confidence is between 0 and 1
        return min(max(adjusted_confidence, 0.0), 1.0)
    
    def _format_solution(self, example: Dict[str, Any], confidence: float, similarity_score: float) -> BugSolution:
        """
        Format an example into a BugSolution response.
        
        Args:
            example: The matched example from our knowledge base
            confidence: Calculated confidence score
            similarity_score: Raw similarity score
            
        Returns:
            Formatted BugSolution
        """
        return BugSolution(
            title=example['title'],
            solution=example['solution'],
            code_example=example['code_example'],
            source=example['source'],
            confidence=confidence,
            tags=example.get('tags', []),
            similarity_score=similarity_score
        )
    
    def update_embeddings(self):
        """Regenerate embeddings for all examples."""
        if self.model_loaded:
            self._prepare_embeddings()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Get all loaded examples."""
        return self.examples
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model and system status."""
        return {
            "model_loaded": self.model_loaded,
            "examples_count": len(self.examples),
            "embeddings_ready": self.example_embeddings is not None,
            "model_name": "all-MiniLM-L6-v2" if self.model else None
        }
