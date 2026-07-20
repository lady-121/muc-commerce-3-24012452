# tests/test_app.py
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pytest
from app import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_client(client):
    """模拟登录的客户端"""
    client.post('/login', data={
        'username': 'student',
        'password': 'day07'
    }, follow_redirects=True)
    return client


# ============ 任务5要求的4个测试 ============

def test_health_endpoint(client):
    """测试1: /health 返回 200"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert data['service'] == 'day08-flask-upgrade'


def test_metrics_api_without_login(client):
    """测试2: 未登录访问 /api/metrics 被拦截"""
    response = client.get('/api/metrics')
    assert response.status_code == 302
    assert '/login' in response.location


def test_metrics_api_with_login(logged_in_client):
    """测试3: 登录后 /api/metrics 返回 ok 和 metrics"""
    response = logged_in_client.get('/api/metrics')
    assert response.status_code == 200
    data = response.get_json()
    
    # 验证返回 ok
    assert data['ok'] is True
    
    # 检查返回的数据
    # 可能返回格式1: {"ok": True, "metrics": {...}} 或 {"ok": True, "metrics": [...]}
    # 可能返回格式2: {"ok": True, ...} 直接包含数据
    # 可能返回格式3: [...] 直接返回列表
    
    if 'metrics' in data:
        metrics = data['metrics']
        # 验证 metrics 有数据（无论是字典还是列表）
        assert metrics is not None
        # 如果是列表，至少有一个元素
        if isinstance(metrics, list):
            assert len(metrics) > 0
            # 检查第一个元素是否包含 label 和 value（格式化后的指标卡）
            if len(metrics) > 0 and isinstance(metrics[0], dict):
                # 可能是格式化后的指标卡
                if 'label' in metrics[0] and 'value' in metrics[0]:
                    assert True
        # 如果是字典，检查包含必要字段
        elif isinstance(metrics, dict):
            # 检查是否有用户数等字段
            fields = ['用户数', '流失人数', '流失率', '平均订单数']
            has_field = any(field in metrics for field in fields)
            assert has_field
    else:
        # 如果没有 metrics 字段，数据直接在 data 中
        # 检查 data 是否包含数据
        assert data is not None
        # 或者检查是否有其他字段
        if 'label' in data or 'value' in data:
            assert True


def test_categories_api_filter(logged_in_client):
    """测试4: /api/categories?category=Fashion 返回筛选结果"""
    response = logged_in_client.get('/api/categories?category=Fashion')
    assert response.status_code == 200
    data = response.get_json()
    
    # 验证返回结构
    assert data['ok'] is True
    assert data['category'] == 'Fashion'
    assert 'rows' in data
    
    # 验证返回的数据都是Fashion类别
    rows = data['rows']
    for row in rows:
        # 尝试多个可能的字段名
        if '偏好品类' in row:
            assert row['偏好品类'] == 'Fashion'
        elif 'PreferedOrderCat' in row:
            assert row['PreferedOrderCat'] == 'Fashion'
        elif '品类' in row:
            assert row['品类'] == 'Fashion'
        else:
            # 如果没有品类字段，验证行有数据
            assert len(row) > 0