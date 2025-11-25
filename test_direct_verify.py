#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接调用verify_student函数进行测试，绕过HTTP接口，以便查看详细的调试信息
"""

from auth.models import verify_student
import hashlib

print("=== 直接测试verify_student函数 ===")

# 测试的学生卡号
card_no = '180001'

# 测试场景1：使用明文密码'123456'
print("\n[测试1] 直接调用verify_student函数，使用密码'123456'")
result1 = verify_student(card_no, '123456')
print(f"函数返回结果: {result1}")

# 测试场景2：使用卡号后6位明文
card_suffix = card_no[-6:]
print(f"\n[测试2] 直接调用verify_student函数，使用卡号后6位: {card_suffix}")
result2 = verify_student(card_no, card_suffix)
print(f"函数返回结果: {result2}")

# 测试场景3：使用卡号后6位的MD5值
card_suffix_md5 = hashlib.md5(card_suffix.encode()).hexdigest()
print(f"\n[测试3] 直接调用verify_student函数，使用卡号后6位的MD5: {card_suffix_md5}")
result3 = verify_student(card_no, card_suffix_md5)
print(f"函数返回结果: {result3}")

# 测试场景4：使用数据库中已知的密码值
print("\n[测试4] 直接调用verify_student函数，使用数据库中存储的密码值")
result4 = verify_student(card_no, 'bd7ce06c974d0f2f973a9d8cb33dff9e')
print(f"函数返回结果: {result4}")

print("\n=== 测试完成 ===")