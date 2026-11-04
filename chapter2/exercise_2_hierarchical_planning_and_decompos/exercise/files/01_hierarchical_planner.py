import json
from typing import List, Dict, Any, Optional

# --- Boilerplate Components Used ---
# MockLLM, StockPriceLookup, CalculateMovingAverage, BaseTool

# Define the tools available to the Worker Agent
worker_tools = {
    "StockPriceLookup": StockPriceLookup(),
    "CalculateMovingAverage": CalculateMovingAverage()
}

def orchestrator(high_level_goal: str, manager_llm: 'MockLLM', worker_tools: Dict[str, BaseTool]) -> str:
    """
    Manages the execution flow: Planning -> Execution -> Synthesis.
    """
    print("--- Step A: Manager Agent (Planning) ---")
    
    # Manager Prompt: Instructs the LLM to output a strict JSON plan
    planning_prompt = f"""
    You are the Manager Agent. Your task is to decompose the following high-level goal into a sequence of actionable steps, specifying the tool and inputs for each step.
    Goal: {high_level_goal}
    
    Output the plan as a single JSON object under the key 'plan'. Ensure the plan uses the available tools: {list(worker_tools.keys())}.
    The plan must include: lookup_price, calculate_ma, and synthesize_summary.
    """
    
    # 1. Run the Manager Agent (MockLLM is configured to return the specific plan JSON)
    plan_json_str = manager_llm.invoke(planning_prompt)
    
    try:
        plan_data = json.loads(plan_json_str)
        plan = plan_data.get('plan', [])
        print(f"Manager Plan Generated ({len(plan)} steps): \n{json.dumps(plan, indent=2)}")
    except json.JSONDecodeError:
        return f"Error: Manager Agent failed to produce valid JSON plan: {plan_json_str}"

    print("\n--- Step B: Orchestrator (Execution by Worker Agent) ---")
    
    execution_results = {}
    
    for step_config in plan:
        step_num = step_config['step']
        action = step_config['action']
        tool_name = step_config.get('tool')
        
        print(f"\n[Executing Step {step_num}: {action}]")

        if tool_name and tool_name in worker_tools:
            tool = worker_tools[tool_name]
            inputs = dict(step_config.get('input', {}))
            # Step-level keys are arguments too: `window` sits next to `input`,
            # not inside it, and the moving-average tool needs it.
            for key, value in step_config.items():
                if key not in {"step", "action", "tool", "input", "input_from"}:
                    inputs[key] = value
            
            # Handle input dependencies from previous steps (input_from logic)
            if 'input_from' in step_config:
                # Assuming simple dependency: step 1 output feeds step 2 input
                source_step = step_config['input_from']
                if isinstance(source_step, int):
                    # Pass the raw result from the source step as the primary input
                    inputs['price_data_json'] = execution_results[source_step]
            
            # Tool invocation (using dynamic run arguments)
            try:
                # Filter inputs to match the tool's expected signature
                if tool_name == "StockPriceLookup":
                    result = tool.run(ticker=inputs['ticker'], period=inputs['period'])
                elif tool_name == "CalculateMovingAverage":
                    result = tool.run(price_data_json=inputs['price_data_json'], window=inputs['window'])
                else:
                    result = f"Unknown tool: {tool_name}"
                
                execution_results[step_num] = result
                print(f"Step {step_num} Result (Tool: {tool_name}): {result[:80]}...")
            except Exception as e:
                execution_results[step_num] = f"Execution Error: {e}"
                print(f"Execution failed: {e}")
        
        elif tool_name is None and action == "synthesize_summary":
            # Synthesis step (handled by Manager in Step C)
            execution_results[step_num] = "Awaiting final synthesis."
            
    print("\n--- Step C: Manager Agent (Final Synthesis) ---")
    
    # Aggregate all results for the Manager
    aggregated_data = {k: v for k, v in execution_results.items() if v != "Awaiting final synthesis."}
    
    synthesis_prompt = f"""
    Synthesize the final answer based on the original goal and the following data:
    Goal: {high_level_goal}
    Data: {aggregated_data}
    
    Provide a clear buy/sell recommendation.
    """
    
    # Final Mock Synthesis
    if 2 in execution_results:
        final_summary = f"Synthesis Complete: The analysis of TSLA stock was successful. The moving average calculation resulted in {execution_results[2]}. Based on this data, the current price is likely above the MA, indicating a potential HOLD signal."
    else:
        final_summary = "Synthesis failed due to missing execution results."
        
    return final_summary

# --- Execution ---
goal = "Analyze the stock performance of TSLA over the last year, calculate its 50-day moving average, and summarize whether the current price indicates a buy or sell signal based on the moving average crossover."

# Initialize MockLLM (configured to output the specific plan)
manager_llm = MockLLM()

final_report = orchestrator(goal, manager_llm, worker_tools)
print("\n=============================================")
print(f"FINAL REPORT:\n{final_report}")
