import hashlib

def calculate_hash(data: str, algorithm: str) -> str:
    """
    Calculates the cryptographic hash digest for input data using a supported algorithm (sha256 or md5).
    Incorporates validation for algorithm support and data size limits.
    """
    SUPPORTED_ALGORITHMS = ["sha256", "md5"]
    MAX_DATA_SIZE = 1024 # characters
    
    # 1. Input Validation (Algorithm)
    algorithm = algorithm.lower()
    if algorithm not in SUPPORTED_ALGORITHMS:
        return (f"VALIDATION ERROR: Algorithm '{algorithm}' is not supported. "
                f"Please use one of: {', '.join(SUPPORTED_ALGORITHMS)}.")
        
    # 2. Input Validation (Data Size)
    if len(data) > MAX_DATA_SIZE:
        return (f"VALIDATION ERROR: Input data exceeds the maximum allowed size of "
                f"{MAX_DATA_SIZE} characters. Length provided: {len(data)}.")

    # 3. Execution
    try:
        h = hashlib.new(algorithm)
        h.update(data.encode('utf-8'))
        return f"Hash ({algorithm}): {h.hexdigest()}"
    except Exception as e:
        # Catch unexpected system errors (highly unlikely here, but good practice)
        return f"CRITICAL HASHING ERROR: An unexpected error occurred during calculation: {e}"

# --- Error Feedback Loop Demonstration ---
# Prompt: "Calculate the hash of 'test_data' using the 'fast_hash' method."
#
# Agent Execution Sequence (Simulated):
# 1. Tool Call: calculate_hash(data='test_data', algorithm='fast_hash')
#    Output: "VALIDATION ERROR: Algorithm 'fast_hash' is not supported. Please use one of: sha256, md5."
#
# Agent Reasoning (Internal):
# "The tool rejected 'fast_hash'. I must use a supported algorithm like 'sha256'."
#
# 2. Tool Call (Corrected Attempt):
#    calculate_hash(data='test_data', algorithm='sha256')
#    Output: "Hash (sha256): 912ec803b2ce49e4a541068d495ab57010f3c6d860e4822a106e23267d3e098a"
#
# LLM Final Answer:
# "I initially attempted to use 'fast_hash', which is unsupported. The valid SHA256 hash for 'test_data' is [digest]."
