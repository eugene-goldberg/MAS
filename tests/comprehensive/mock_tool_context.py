"""Mock ToolContext for testing RAG tools."""

class MockToolContext:
    """Mock ToolContext that mimics the real ToolContext for testing."""
    
    def __init__(self):
        self.state = {}
        
    def get_current_corpus(self):
        """Get the current corpus from state."""
        return self.state.get("current_corpus_display_name", "")
        
    def set_current_corpus(self, corpus_name):
        """Set the current corpus in state."""
        self.state["current_corpus_display_name"] = corpus_name
        self.state[f"corpus_exists_{corpus_name}"] = True