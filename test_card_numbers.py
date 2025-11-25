#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试校园卡号搜索功能"""
import requests
import json

def test_card_numbers_api():
    """测试/api/card-numbers API端点"""
    print("测试校园卡号API...")
    try:
        # 设置Cookie以模拟登录状态
        cookies = {'session': 'test_session'}
        
        # 发送请求到API端点
        response = requests.get('http://localhost:5000/api/card-numbers', cookies=cookies)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("API响应成功！")
            print(f"返回的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'card_numbers' in data:
                print(f"获取到的校园卡号数量: {len(data['card_numbers'])}")
                if len(data['card_numbers']) > 0:
                    print(f"前5个校园卡号: {data['card_numbers'][:5]}")
            
        elif response.status_code == 403:
            print("提示: 需要管理员权限访问此API")
            print("在实际使用中，您需要先登录管理员账号")
        else:
            print(f"API调用失败: {response.text}")
    
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

def test_manual_search():
    """模拟手动输入校园卡号搜索"""
    print("\n模拟手动输入校园卡号搜索...")
    
    # 从数据库中已知的校园卡号
    test_card_numbers = ['181316', '181317', '181318']
    
    for card_no in test_card_numbers:
        print(f"\n测试搜索校园卡号: {card_no}")
        try:
            # 模拟搜索请求
            params = {
                'card_no': card_no,
                'start_date': '',
                'end_date': ''
            }
            
            cookies = {'session': 'test_session'}
            response = requests.get('http://localhost:5000/api/consumption-records', 
                                  params=params, 
                                  cookies=cookies)
            
            print(f"搜索响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'records' in data:
                    print(f"找到 {len(data['records'])} 条消费记录")
            elif response.status_code == 403:
                print("提示: 需要管理员权限访问此API")
            else:
                print(f"搜索请求失败: {response.text}")
                
        except Exception as e:
            print(f"搜索过程中出现错误: {str(e)}")

if __name__ == '__main__':
    print("========== 校园卡号搜索功能测试 ==========\n")
    test_card_numbers_api()
    test_manual_search()
    print("\n========== 测试完成 ==========")
    print("\n注意事项:")
    print("1. 在实际使用中，您需要先登录管理员账号")
    print("2. 校园卡号下拉列表应显示所有可用的卡号")
    print("3. 手动输入卡号后按搜索按钮应能正常查询")
    print("4. 前端已优化错误处理，即使API调用失败也会有友好提示")