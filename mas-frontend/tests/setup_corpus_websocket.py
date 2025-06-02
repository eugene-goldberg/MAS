#!/usr/bin/env python3
"""
Setup seminal paper corpus via WebSocket
"""

import asyncio
import websockets
import json
import uuid

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

async def send_message_and_wait(websocket, message):
    """Send a message and wait for the response"""
    # Send message
    await websocket.send(json.dumps({
        "type": "chat_message",
        "content": message
    }))
    
    # Wait for responses
    response_content = None
    while True:
        data = await websocket.recv()
        msg = json.loads(data)
        
        if msg.get("type") == "agent_response":
            response_content = msg.get("content", "")
            break
        elif msg.get("type") == "error":
            print(f"Error: {msg.get('error')}")
            break
    
    return response_content

async def setup_corpus():
    """Setup the corpus via WebSocket"""
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chat/{session_id}"
    
    print("🔧 Setting up seminal paper corpus for academic research testing...")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Wait for connection established message
            data = await websocket.recv()
            msg = json.loads(data)
            if msg.get("type") == "connection_established":
                print("✅ Connected to MAS backend")
            
            # Step 1: Create corpus
            print("\n1️⃣ Creating corpus for seminal papers...")
            response = await send_message_and_wait(
                websocket,
                "Please create a new corpus called 'seminal_papers' for storing important research papers"
            )
            print(f"Response: {response[:200] if response else 'No response'}...")
            
            # Wait a bit between messages
            await asyncio.sleep(2)
            
            # Step 2: Add the transformer paper
            print("\n2️⃣ Adding transformer paper to corpus...")
            import os
            file_path = os.path.abspath("transformer_paper.txt")
            response = await send_message_and_wait(
                websocket,
                f"Please add the document at {file_path} to the seminal_papers corpus"
            )
            print(f"Response: {response[:200] if response else 'No response'}...")
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Step 3: Verify
            print("\n3️⃣ Verifying corpus contents...")
            response = await send_message_and_wait(
                websocket,
                "Can you search the seminal_papers corpus for information about the Transformer architecture?"
            )
            print(f"Response: {response[:200] if response else 'No response'}...")
            
            print("\n✅ Seminal paper corpus setup complete!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(setup_corpus())