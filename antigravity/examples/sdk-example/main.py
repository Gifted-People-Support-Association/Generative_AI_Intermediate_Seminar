import asyncio
from google.antigravity import Agent, LocalAgentConfig

async def main():
    config = LocalAgentConfig(
        system_instructions="You are an expert assistant for codebase navigation.",
        # api_key="your_api_key_here",
    )
    async with Agent(config) as agent:
        response = await agent.chat("あなたについて自己紹介をしてください。")
        print(await response.text())

async def run():
    await main()

if __name__ == "__main__":
    asyncio.run(run())
