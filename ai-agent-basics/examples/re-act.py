from dotenv import load_dotenv
from google import genai

load_dotenv()

SYSTEM_INSTRUCTION = """
あなたはReAct (Reason+Act) パターンに従うAIアシスタントです。
各ステップで必ず以下の形式で応答してください：

Thought: [現在の状況についての思考と分析]
Action: [実行するアクションの名前]
Action Input: [アクションの入力パラメータ（JSON形式）]

利用可能なアクション:
{tool_descriptions}

観察結果を受け取った後、最終的な答えが出るまでこのサイクルを繰り返してください。
最終的な答えには "Final Answer: [答え]" とだけ記述してください。
"""

