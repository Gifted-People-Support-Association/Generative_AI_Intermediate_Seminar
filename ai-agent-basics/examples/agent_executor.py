import json
import re
import uuid
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langgraph.graph import MessagesState, StateGraph

ACTION_PATTERN = re.compile(r"^Action:\s*(.+)$", re.MULTILINE)
ACTION_INPUT_PATTERN = re.compile(r"^Action Input:\s*(.+)$", re.MULTILINE | re.DOTALL)
EMPTY_TOOL_ARGS: dict[str, Any] = {}


def stringify_message(message: BaseMessage) -> str:
    content = message.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        return "\n".join(
            item.get("text", json.dumps(item, ensure_ascii=False))
            if isinstance(item, dict)
            else str(item)
            for item in content
        ).strip()

    return str(content).strip()


def parse_tool_args(raw_args: str) -> dict[str, Any]:
    try:
        parsed_args = json.loads(raw_args)
    except json.JSONDecodeError:
        parsed_args = {"input": raw_args}

    if isinstance(parsed_args, dict):
        return parsed_args

    return {"input": parsed_args}


def build_tool_call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "args": args,
        "id": f"call_{uuid.uuid4().hex}",
        "type": "tool_call",
    }


def extract_action_from_content(content: str) -> tuple[str | None, dict[str, Any]]:
    action_match = ACTION_PATTERN.search(content)
    input_match = ACTION_INPUT_PATTERN.search(content)

    if not action_match:
        return None, EMPTY_TOOL_ARGS

    action_name = action_match.group(1).strip()
    raw_args = input_match.group(1).strip() if input_match else "{}"
    return action_name, parse_tool_args(raw_args)


def normalize_tool_call(message: BaseMessage, tool_names: set[str]) -> BaseMessage:
    if not isinstance(message, AIMessage) or message.tool_calls:
        return message

    content = stringify_message(message)
    action_name, action_args = extract_action_from_content(content)

    if not action_name or action_name not in tool_names:
        return message

    return AIMessage(
        content=message.content,
        tool_calls=[build_tool_call(action_name, action_args)],
        additional_kwargs=message.additional_kwargs,
        response_metadata=message.response_metadata,
        id=message.id,
        name=message.name,
    )


class AgentExecutor:
    def __init__(self, graph: StateGraph[MessagesState]):
        self.graph = graph

    async def run(self, user_input: str, verbose: bool = True) -> MessagesState:
        state: MessagesState = {"messages": [HumanMessage(content=user_input)]}

        if verbose:
            print("=== ワークフロー実行開始 ===")

        async for mode, chunk in self.graph.astream(
            state,
            stream_mode=["updates", "values"]
        ):
            if mode == "updates" and verbose:
                self._print_updates(chunk)
            elif mode == "values":
                state = chunk

        if verbose:
            print("\n=== 最終出力 ===")
            print(self.get_final_output(state))

        return state

    def get_final_output(self, state: MessagesState) -> str:
        return self._stringify_message(state["messages"][-1])

    def _print_updates(self, updates: dict[str, Any]) -> None:
        for node_name, node_output in updates.items():
            print(f"\n[{node_name}]")

            messages = node_output.get("messages", [])
            if not messages:
                print(node_output)
                continue

            for message in messages:
                self._print_message(message)

    def _print_message(self, message: BaseMessage) -> None:
        if isinstance(message, AIMessage):
            self._print_ai_message(message)
            return

        if isinstance(message, ToolMessage):
            self._print_tool_message(message)
            return

        print(f"{message.type}: {self._stringify_message(message)}")

    def _stringify_message(self, message: BaseMessage) -> str:
        return stringify_message(message)

    def _print_ai_message(self, message: AIMessage) -> None:
        content = self._stringify_message(message)
        if content:
            print(f"AI: {content}")

        for tool_call in message.tool_calls:
            print(
                "Tool Call: "
                f"{tool_call['name']}"
                f"({json.dumps(tool_call['args'], ensure_ascii=False)})"
            )

    def _print_tool_message(self, message: ToolMessage) -> None:
        tool_name = message.name or "tool"
        print(f"Tool Result [{tool_name}]: {self._stringify_message(message)}")
