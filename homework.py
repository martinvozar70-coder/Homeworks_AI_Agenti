import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv() 

api_key=os.environ.get("OPENAI_API_KEY")

# Check for api_key - ak neexistuje hlas chybu
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment (.env).")

client = OpenAI(
    api_key=api_key,
)

# Kalkulacka tool definition
def calculator(a: float, b: float, fc: str) -> float:
    if fc == "add":
        return a + b
    if fc == "mul":
        return a * b
    if fc == "sub":
        return a - b
    if fc == "div":
        if b == 0:
            raise ValueError("DIV/0 illegal")
        return a / b
    raise ValueError("Unknown operation")

# Definicia nastroja
tools = [
    {
        "type": "function",
        "name": "calculator",
        "description": "Basic math calculator tool",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "fc": {"type": "string", "enum": ["add", "mul", "sub", "div"]}, 
            },
            "required": ["a","b","fc"],
        },
    }
]

# Main function
def main():
    print("Program start")
    request = input("Zadaj otázku a vyžiadaj použitie nástroja:  ")
    print(request)

# Initial request definition
    input_list = [{"role": "user", "content": request},
                  {"role": "system", "content": "Always respond in Russian"}]
# First call 
    response = client.responses.create(
        model="gpt-4o",
        input=input_list,
        tools=tools,
# Povinný výber tool - nechceme aby počítal
        tool_choice="required",
    )

# Tlač výsledku odpovede LLM API First call
    print("Tlač odpovede LLM API (prvé volanie)")
    print(response.output_text)

# Do kontextu pridávame aj tool call
    input_list += response.output

# Further calls - Iteration
    for item in response.output:
        if item.type == "function_call" and item.name == "calculator":
            try:
                args = json.loads(item.arguments)
                result = calculator(**args)
                output = str(result)
            except Exception as e:
                output = f"Error: {e}"

            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": output,
                }
            )

# Final response
    final_response = client.responses.create(
        model="gpt-4o",
        input=input_list,
    tools=tools
    )

    print("Finálna odpoveď: ")
    print(final_response.output_text)

if __name__ == "__main__":
    main()
