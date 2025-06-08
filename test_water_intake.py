#!/usr/bin/env python3
# coding: utf-8

import json
import os
import sys
from datetime import datetime, timedelta
from firebase_admin import firestore
from firebase_config import firebase_config
from services.firestore_service import FirestoreService

def test_water_intake():
    """
    Kiểm tra và sửa các vấn đề với bản ghi nước uống
    """
    print("=== KIỂM TRA BẢN GHI NƯỚC UỐNG ===")
    
    # Khởi tạo Firestore
    db = firebase_config.get_db()
    fs_service = FirestoreService()
    
    # 1. Kiểm tra tất cả các bản ghi nước uống
    print("\n1. Lấy tất cả các bản ghi nước uống...")
    water_entries = db.collection('water_entries').get()
    print(f"Tổng số bản ghi nước uống: {len(water_entries)}")
    
    # Hiển thị chi tiết các bản ghi
    for doc in water_entries:
        data = doc.to_dict()
        print(f"ID: {doc.id}")
        print(f"Dữ liệu: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("------------------------------")
    
    # 2. Kiểm tra bản ghi nước uống cho một user_id cụ thể
    user_id = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    print(f"\n2. Kiểm tra bản ghi nước uống cho user_id: {user_id}")
    
    # Truy vấn với trường user_id
    print("\nTruy vấn với trường user_id:")
    query1 = db.collection('water_entries').where('user_id', '==', user_id).get()
    print(f"Tìm thấy {len(query1)} bản ghi với user_id")
    
    # Truy vấn với trường userId
    print("\nTruy vấn với trường userId:")
    query2 = db.collection('water_entries').where('userId', '==', user_id).get()
    print(f"Tìm thấy {len(query2)} bản ghi với userId")
    
    # 3. Sửa các bản ghi hiện có để thêm trường thiếu
    print("\n3. Cập nhật các bản ghi thiếu trường...")
    updated_count = 0
    
    for doc in water_entries:
        data = doc.to_dict()
        needs_update = False
        updates = {}
        
        # Kiểm tra và thêm trường userId nếu chưa có
        if 'userId' not in data and 'user_id' in data:
            updates['userId'] = data['user_id']
            needs_update = True
            
        # Kiểm tra và thêm trường user_id nếu chưa có
        if 'user_id' not in data and 'userId' in data:
            updates['user_id'] = data['userId']
            needs_update = True
            
        # Kiểm tra và thêm trường date nếu chưa có
        if 'date' not in data and 'timestamp' in data:
            # Nếu timestamp là số (milliseconds since epoch)
            if isinstance(data['timestamp'], (int, float)):
                date_obj = datetime.fromtimestamp(data['timestamp'] / 1000)
                updates['date'] = date_obj.strftime('%Y-%m-%d')
                needs_update = True
            # Nếu timestamp là chuỗi ISO
            elif isinstance(data['timestamp'], str):
                try:
                    date_obj = datetime.fromisoformat(data['timestamp'])
                    updates['date'] = date_obj.strftime('%Y-%m-%d')
                    needs_update = True
                except ValueError:
                    print(f"Không thể chuyển đổi timestamp: {data['timestamp']}")
                    
        # Đảm bảo có trường amount_ml
        if 'amount' in data and 'amount_ml' not in data:
            updates['amount_ml'] = data['amount']
            needs_update = True
            
        # Cập nhật document nếu cần
        if needs_update:
            print(f"Cập nhật document {doc.id} với dữ liệu: {updates}")
            doc.reference.update(updates)
            updated_count += 1
    
    print(f"Đã cập nhật {updated_count} bản ghi")
    
    # 4. Thêm bản ghi water test để xác minh
    print("\n4. Thêm bản ghi nước uống test...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Tạo dữ liệu nước uống
    water_data = {
        'userId': user_id,
        'user_id': user_id,  # Thêm cả hai trường để đảm bảo truy vấn hoạt động
        'date': today,
        'timestamp': datetime.now().isoformat(),
        'beverage_name': "Water Test",
        'amount_ml': 300,
        'calories': 0
    }
    
    # Thêm dữ liệu vào Firestore
    water_ref = db.collection('water_entries').document(f"water_test_{int(datetime.now().timestamp())}")
    water_ref.set(water_data)
    print(f"Đã thêm bản ghi nước uống với ID: {water_ref.id}")
    
    # 5. Kiểm tra lại truy vấn nước uống theo ngày
    print(f"\n5. Kiểm tra truy vấn nước uống cho ngày {today}")
    result = fs_service.get_water_intake_by_date(user_id, today)
    print(f"Kết quả truy vấn: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 6. Kiểm tra bản ghi cho ngày 2025-06-08
    test_date = "2025-06-08"
    print(f"\n6. Kiểm tra bản ghi cho ngày cụ thể: {test_date}")
    result = fs_service.get_water_intake_by_date(user_id, test_date)
    print(f"Tìm thấy {len(result)} bản ghi cho ngày {test_date}")
    print(f"Kết quả truy vấn: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_water_intake()) 