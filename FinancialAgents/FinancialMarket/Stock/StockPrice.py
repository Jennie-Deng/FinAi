
import numpy as np
import pandas as pd  # 用于创建和保存表格
import matplotlib.pyplot as plt

# 参数设置
num_sectors = 11  # 行业板块数
num_stocks_per_sector = 10  # 每个行业的股票数
num_stocks = num_sectors * num_stocks_per_sector  # 总股票数
num_days = 500  # 交易日数
dt = 1/num_days  # 每日时间步长

# 行业名称列表
sector_names = [
    "Energy", "Materials", "Industrials", "Consumer Discretionary",
    "Consumer Staples", "Health Care", "Financials",
    "Information Technology", "Communication Services",
    "Utilities", "Real Estate"
]

# 初始化数据结构
stock_prices = np.zeros((num_days, num_stocks))
stock_codes = []
stock_sectors = []
stock_labels = []

# 模拟每只股票的路径
for sector in range(num_sectors):
    for stock_num in range(num_stocks_per_sector):
        # 生成初始价格
        S0 = np.random.uniform(10, 500)

        # 生成波动率
        sigma = np.random.uniform(0.01, 0.3)

        # 生成预期回报率
        mu = np.random.uniform(0.01, 0.2)

        # 初始化股票价格路径
        prices = np.zeros(num_days)
        prices[0] = S0

        # 生成GBM路径并引入事件影响
        for t in range(1, num_days):
            Z = np.random.standard_normal()

            if t == 75:
                # 地震导致股票价格下降 10%-30%
                prices[t] = prices[t-1] * (1 - np.random.uniform(0.1, 0.3))
            elif t == 200:
                # 政府和美联储的经济刺激政策推动股市上涨 0%-50%
                prices[t] = prices[t-1] * (1 + np.random.uniform(0, 0.5))
            elif t == 300:
                # 银行倒闭导致股市下降 10%-30%
                prices[t] = prices[t-1] * (1 - np.random.uniform(0.1, 0.3))
            else:
                # 正常的GBM路径
                prices[t] = prices[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)

        # 保留两位小数
        prices = np.round(prices, 2)

        # 存储结果
        stock_index = sector * num_stocks_per_sector + stock_num
        stock_prices[:, stock_index] = prices

        stock_code = f"{str(stock_index + 1).zfill(3)}"  # 生成股票代码（从001开始）
        stock_codes.append(stock_code)
        stock_sectors.append(sector_names[sector])  # 对应实际行业名称
        stock_labels.append(f"{stock_code}_{sector_names[sector]}_Stock_{stock_num+1}")

# 将价格数据转换为DataFrame，并添加股票代码、日期和行业列
dates = pd.date_range(start='2023-01-01', periods=num_days)
df = pd.DataFrame(stock_prices, columns=stock_codes, index=dates)



# 将表格转换为长格式以包含股票代码和行业
df_long = df.reset_index().melt(id_vars=['index'], var_name='Stock_Code', value_name='Price')
df_long['Sector'] = df_long['Stock_Code'].apply(lambda x: stock_sectors[int(x)-1])
df_long.rename(columns={'index': 'Date'}, inplace=True)

df_long["Return"] = df_long['Price'].pct_change()
# df_long["Volatility"] = df_long['Return'].std()

df_long['Volatility_5D'] = df_long.groupby('Stock_Code')['Return'].rolling(window=5).std().reset_index(level=0, drop=True)

# 提取包含波动率的DataFrame
# volatility_df = df_long[['Date', 'Stock_Code', 'Sector', 'Price', 'Return', 'Volatility_5D']]

# import ace_tools as tools; 
# tools.display_dataframe_to_user(name="Volatility Data", dataframe=volatility_df)
csv_file = 'stock_prices_with_sector.csv'
df_long.to_csv(csv_file, index=False)

# 绘制一个行业中的部分股票价格路径
plt.figure(figsize=(14, 8))
for i in range(5):  # 选择行业1中的前5只股票绘制路径
    plt.plot(dates, stock_prices[:, i], label=stock_labels[i])

# 标注事件日期
plt.axvline(x=dates[75], color='red', linestyle='--', label='Earthquake (Day 75)')
plt.axvline(x=dates[200], color='green', linestyle='--', label='Stimulus (Day 200)')
plt.axvline(x=dates[300], color='blue', linestyle='--', label='Bank Failure (Day 300)')

# 图表设置
plt.title('Stock Price Paths with Major Events')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.grid(True)
plt.show()
