import asyncio
import random
from django.http import StreamingHttpResponse

# 模拟股票价格变化的异步生成器
async def stock_price_stream():
    """
    模拟股票价格的变化，每秒更新一次股票价格并推送给客户端。
    """
    stock_symbols = ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT']  # 股票代码
    while True:
        stock = random.choice(stock_symbols)  # 随机选择一个股票代码
        price = round(random.uniform(100, 1500), 2)  # 随机生成一个股票价格
        message = f"data: {stock} - ${price}\n\n"  # 格式化股票价格数据
        yield message  # 通过 yield 发送实时数据
        await asyncio.sleep(3)  # 每秒钟更新一次股票价格

# SSE 视图：实时推送股票价格
async def stock_price_view(request):
    """
    该视图通过 SSE 持续推送股票价格更新。
    """
    return StreamingHttpResponse(stock_price_stream(), content_type='text/event-stream')
