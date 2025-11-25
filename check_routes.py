from app import app

print("所有已注册的路由:")
print("=" * 50)

for rule in app.url_map.iter_rules():
    if not str(rule).startswith('/static'):  # 过滤掉静态文件路由
        print(f"{rule}")
        
print("\n价格分布相关路由:")
print("=" * 50)
for rule in app.url_map.iter_rules():
    if 'price' in str(rule).lower() or 'distribution' in str(rule).lower():
        print(f"{rule}")
        
print("\nanalytics相关路由:")
print("=" * 50)
for rule in app.url_map.iter_rules():
    if 'analytics' in str(rule).lower():
        print(f"{rule}")