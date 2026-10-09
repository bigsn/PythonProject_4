"""Test OpenAI client connection and generation."""

from openai import AsyncOpenAI
import asyncio
import os
from dotenv import load_dotenv

# Загрузить .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")
proxy = os.getenv("PROXY", "")
model = os.getenv("OPENAI_MODEL", "gpt-4")

def test_openai_client_creation():
    """Test that OpenAI client can be created."""
    try:

        print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else f"API Key: {api_key}")
        
        if not api_key:
            print("❌ ERROR: OPENAI_API_KEY not set in .env")
            return False
        
        client = AsyncOpenAI(api_key=api_key, base_url=proxy)
        print("✅ OpenAI client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ ERROR creating client: {e}")
        return False


async def test_openai_simple_request():
    """Test a simple request to OpenAI API."""
    try:
        client = AsyncOpenAI(api_key=api_key, base_url=proxy)
        
        print(f"\nTesting simple request with model: {model}")
        print("Sending request to OpenAI API...")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello' in one word."},
            ],
            max_completion_tokens=10,
            temperature=1,
        )
        
        generated_text = response.choices[0].message.content.strip()
        print(f"✅ Response received: '{generated_text}'")
        print(f"   Tokens used: {response.usage.total_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        if "Invalid API Key" in str(e):
            print("   → Check your OPENAI_API_KEY in .env file")
        elif "Rate limit" in str(e):
            print("   → Rate limit exceeded, wait a moment")
        elif "Not Found" in str(e):
            print("   → Model not available for your API key")
        return False


async def test_news_generation():
    """Test generating a news-style post."""
    try:
        client = AsyncOpenAI(api_key=api_key, base_url=proxy)
        
        # Тестовая новость
        news_text = """
        Компания OpenAI представила новую версию модели GPT-4, 
        которая работает в 2 раза быстрее предыдущей и поддерживает 
        работу с контекстом до 128 тысяч токенов.
        """
        
        print(f"\nGenerating news post from:")
        print(f"News: {news_text[:100]}...")
        print("\nGenerating...")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Telegram content creator. Create engaging posts with emojis and call to action."
                },
                {
                    "role": "user",
                    "content": f"Make a brief, interesting description for a Telegram channel, add emoji, call to action.\n\nNews text:\n{news_text}"
                },
            ],
            max_completion_tokens=300,
            temperature=1,
        )
        
        generated_post = response.choices[0].message.content.strip()
        print(f"\n✅ Generated post:")
        print(f"{'='*50}")
        print(generated_post)
        print(f"{'='*50}")
        print(f"\nTokens used: {response.usage.total_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("OpenAI Client Test")
    print("="*60)
    
    # Тест 1: Создание клиента
    print("\n[Test 1] Creating OpenAI client...")
    test1 = test_openai_client_creation()
    
    if not test1:
        print("\n❌ Tests stopped - cannot create client")
        exit(1)
    
    # Тест 2: Простой запрос
    print("\n[Test 2] Simple API request...")
    test2 = asyncio.run(test_openai_simple_request())
    
    # Тест 3: Генерация поста
    if test2:
        print("\n[Test 3] News post generation...")
        test3 = asyncio.run(test_news_generation())
    
    # Итог
    print("\n" + "="*60)
    print("Results:")
    print(f"  Client creation: {'✅' if test1 else '❌'}")
    print(f"  Simple request:  {'✅' if test2 else '❌'}")
    if test2:
        print(f"  News generation: {'✅' if test3 else '❌'}")
    print("="*60)
