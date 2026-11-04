from typing import List

import tiktoken

# --- Setup for Token Counting (Used in Exercises 2 and 4) ---
TOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")

def calculate_tokens(text: str) -> int:
    """Calculates the token count for a given string."""
    return len(TOKEN_ENCODER.encode(text))

# =============================================================
# Exercise 2 Solution
# =============================================================

def trim_context(documents: List[str], query: str, key_fact: str) -> List[str]:
    """
    Simulates a context trimming process by prioritizing documents 
    based on relevance (keyword match simulating semantic re-ranking).
    """
    print(f"\n[Trimmer] Starting with {len(documents)} documents.")
    
    # 1. Separate based on simulated relevance (keyword match)
    high_relevance = []
    low_relevance = []
    
    for doc in documents:
        if key_fact in doc:
            high_relevance.append(doc)
        else:
            low_relevance.append(doc)
            
    # 2. Implement Trimming Strategy: Keep all high-relevance docs (2), and only
    #    one low-relevance doc. Two would leave the reduction at 51%, under the
    #    60% the exercise asks for.
    trimmed_context = high_relevance + low_relevance[:1]
    
    print(f"[Trimmer] Identified {len(high_relevance)} high-relevance documents.")
    print(f"[Trimmer] Discarded {len(low_relevance) - 2} low-relevance documents.")
    print(f"[Trimmer] Retained {len(trimmed_context)} documents total.")
    
    return trimmed_context

def run_exercise_2():
    query = "What is the primary function of the 'Flux Capacitor' and who invented it?"
    key_fact = "invented by Dr. Emmett Brown"
    
    # 1. Define Documents (10 total: 2 key, 8 irrelevant)
    initial_documents = [
        "Document 1: General history of 1980s cinema.",
        "Document 2: The DeLorean chassis specifications are complex.",
        f"Document 3: The Flux Capacitor is the core component for time travel, {key_fact}.", # Key Doc 1
        "Document 4: Details on the required 1.21 gigawatts of power.",
        "Document 5: A biography of Michael J. Fox.",
        "Document 6: Notes on temporal paradoxes.",
        "Document 7: The importance of plutonium in initial tests.",
        f"Document 8: Confirmation that the device was {key_fact} in 1985.", # Key Doc 2
        "Document 9: Analysis of Hill Valley town planning.",
        "Document 10: Recipe for a perfect chocolate malt."
    ]
    
    # Calculate Initial Cost
    initial_context_text = " ".join(initial_documents)
    initial_tokens = calculate_tokens(initial_context_text)
    
    print("--- Running Exercise 2: Context Trimming ---")
    print(f"Initial Context Size (10 documents): {initial_tokens} tokens.")

    # Trim the context (10 documents -> 4 documents)
    final_documents = trim_context(initial_documents, query, key_fact)
    
    # Calculate Final Cost
    final_context_text = " ".join(final_documents)
    final_tokens = calculate_tokens(final_context_text)
    
    # Cost Demonstration
    reduction = initial_tokens - final_tokens
    percent_reduction = (reduction / initial_tokens) * 100
    
    print("\n--- Cost Analysis ---")
    print(f"Final Context Size ({len(final_documents)} documents): {final_tokens} tokens.")
    print(f"Token Reduction Achieved: {reduction} tokens.")
    print(f"Percentage Cost Saving for LLM Input: {percent_reduction:.2f}%")
    
    # Verification of the cost reduction goal
    assert percent_reduction >= 60, f"Trimming only achieved {percent_reduction:.2f}%, failed to meet the 60% reduction goal."

run_exercise_2()
