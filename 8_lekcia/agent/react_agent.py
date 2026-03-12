"""
ReAct Agent Implementation
==========================
ReAct = Reasoning + Acting
The agent loops through: Thought → Action → Observation → ... → Final Answer

Reference: "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2022)
"""

import json
import re
from typing import Any
from openai import OpenAI


class ReActAgent:
    """
    A simple ReAct agent that:
    1. Receives a user question
    2. Thinks about what tool to use (Thought)
    3. Calls a tool (Action)
    4. Observes the result (Observation)
    5. Repeats until it can answer (Final Answer)
    """

    def __init__(self, tools: list, model: str = "gpt-4o-mini", max_steps: int = 10):
        self.client = OpenAI()  # reads OPENAI_API_KEY from environment
        self.model = model
        self.max_steps = max_steps

        # Build a dict of tool_name -> tool instance for easy lookup
        self.tools = {tool.name: tool for tool in tools}

        # Build the system prompt that explains the ReAct format to the LLM
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        tool_descriptions = "\n".join(
            f"- {name}: {tool.description}\n  Input schema: {json.dumps(tool.input_schema)}"
            for name, tool in self.tools.items()
        )

        return f"""You are a helpful AI assistant that answers questions by using tools.

You operate in a Thought → Action → Observation loop:

1. THOUGHT: Reason about what you know and what you need to find out.
2. ACTION: Call one tool to get more information. Format:
   Action: <tool_name>
   Action Input: <json with tool parameters>
3. OBSERVATION: You will receive the tool result.
4. Repeat until you have enough information.
5. FINAL ANSWER: When you know the answer, write:
   Final Answer: <your answer here>

Available tools:
{tool_descriptions}

IMPORTANT RULES:
- Always start with a Thought.
- Use exactly one Action per step.
- After receiving an Observation, think again before acting.
- Write "Final Answer:" when you are ready to answer.
- If a tool returns an error, try a different approach or tool.
"""

    def run(self, question: str, verbose: bool = True) -> str:
        """
        Run the ReAct loop for a given question.
        Returns the final answer string.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question},
        ]

        if verbose:
            print(f"\n{'='*60}")
            print(f"QUESTION: {question}")
            print(f"{'='*60}")

        for step in range(self.max_steps):
            if verbose:
                print(f"\n--- Step {step + 1} ---")

            # Ask the LLM what to do next
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
            )
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})

            if verbose:
                print(assistant_message)

            # Check if the agent is done
            if "Final Answer:" in assistant_message:
                final_answer = assistant_message.split("Final Answer:")[-1].strip()
                if verbose:
                    print(f"\n{'='*60}")
                    print(f"FINAL ANSWER: {final_answer}")
                    print(f"{'='*60}\n")
                return final_answer

            # Parse the action the agent wants to take
            action, action_input = self._parse_action(assistant_message)

            if action is None:
                # LLM didn't follow the format — nudge it
                observation = "Error: Could not parse your action. Please use the format:\nAction: <tool_name>\nAction Input: <json>"
            elif action not in self.tools:
                observation = f"Error: Unknown tool '{action}'. Available tools: {list(self.tools.keys())}"
            else:
                # Execute the tool
                try:
                    observation = self.tools[action].run(action_input)
                except Exception as e:
                    observation = f"Tool error: {str(e)}"

            observation_text = f"Observation: {observation}"
            messages.append({"role": "user", "content": observation_text})

            if verbose:
                print(observation_text)

        return "Max steps reached without a final answer."

    def _parse_action(self, text: str) -> tuple[str | None, dict]:
        """
        Extract tool name and input from the LLM's response.
        Handles several formatting variations the LLM might produce:
          - "Action: tool_name\nAction Input: {...}"   (ideal)
          - "ACTION: tool_name\n{...}"                 (uppercase, no "Action Input:")
          - "Action: tool_name\n{...}"                 (JSON on next line, no label)
        """
        # Match action name — case-insensitive, allow uppercase ACTION:
        action_match = re.search(r"(?i)action:\s*(\w+)", text)
        if not action_match:
            return None, {}

        action = action_match.group(1).strip()

        # Try "Action Input: {...}" first (the preferred format)
        input_match = re.search(r"(?i)action input:\s*(\{.*?\})", text, re.DOTALL)

        # Fallback: any JSON object anywhere after the action line
        if not input_match:
            input_match = re.search(r"(\{.*?\})", text, re.DOTALL)

        if input_match:
            try:
                action_input = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                action_input = {}
        else:
            action_input = {}

        return action, action_input