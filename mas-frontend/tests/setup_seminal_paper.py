#!/usr/bin/env python3
"""
Setup seminal paper corpus for academic research testing
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.core.mas_client import MASClient
from app.core.config import settings

# Classic transformer paper abstract as our seminal paper
TRANSFORMER_PAPER = """
Title: Attention Is All You Need
Authors: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin
Year: 2017

Abstract:
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature. We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.

Key Contributions:
1. Introduced the Transformer architecture based solely on attention mechanisms
2. Eliminated the need for recurrence and convolutions in sequence transduction
3. Achieved state-of-the-art results on machine translation benchmarks
4. Demonstrated superior parallelizability and training efficiency
5. Showed generalization to other NLP tasks beyond translation

This paper revolutionized natural language processing and became the foundation for models like BERT, GPT, and subsequent large language models.
"""

async def setup_seminal_paper_corpus():
    """Setup a corpus with the transformer paper for testing"""
    print("🔧 Setting up seminal paper corpus for academic research testing...")
    
    try:
        client = MASClient()
        await client.connect()
        
        # Step 1: Create corpus using RAG agent
        print("\n1️⃣ Creating corpus for seminal papers...")
        response = await client.send_message(
            "Please create a new corpus called 'seminal_papers' for storing important research papers"
        )
        print(f"Response: {response[:200]}...")
        
        # Step 2: Add the transformer paper to the corpus
        print("\n2️⃣ Adding transformer paper to corpus...")
        response = await client.send_message(
            f"Please add this seminal paper to the seminal_papers corpus:\n\n{TRANSFORMER_PAPER}"
        )
        print(f"Response: {response[:200]}...")
        
        # Step 3: Verify the corpus has the paper
        print("\n3️⃣ Verifying corpus contents...")
        response = await client.send_message(
            "Can you search the seminal_papers corpus for information about the Transformer architecture?"
        )
        print(f"Response: {response[:200]}...")
        
        print("\n✅ Seminal paper corpus setup complete!")
        print("The academic research agents can now use this paper as context.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up corpus: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    success = await setup_seminal_paper_corpus()
    if success:
        print("\n🎯 Ready for academic research agent testing!")
    else:
        print("\n⚠️ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())