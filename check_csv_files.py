import pandas as pd

# 设置中文显示
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

print("=== data1.csv 内容预览 ===")
df1 = pd.read_csv('data1.csv', encoding='gbk')
print(df1.head())
print(f"\n数据形状: {df1.shape}")
print(f"列名: {list(df1.columns)}")

print("\n=== data2.csv 内容预览 ===")
df2 = pd.read_csv('data2.csv', encoding='gbk')
print(df2.head())
print(f"\n数据形状: {df2.shape}")
print(f"列名: {list(df2.columns)}")

print("\n=== data3.csv 内容预览 ===")
df3 = pd.read_csv('data3.csv', encoding='gbk')
print(df3.head())
print(f"\n数据形状: {df3.shape}")
print(f"列名: {list(df3.columns)}")