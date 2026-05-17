import asyncio

from langchain.chat_models import init_chat_model

from app.config.app_config import app_config

model_name = app_config.llm.model_name
api_key = app_config.llm.api_key

# 阿里云百炼平台（DashScope）兼容 OpenAI API
llm = init_chat_model(
    model=model_name,
    model_provider="openai",
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0,
)

if __name__ == '__main__':
    async def test():
        print(await llm.ainvoke("中国的首都是哪里？"))


    print(asyncio.run(test()))
