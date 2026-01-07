#!/bin/bash

# Quick POI Selection Verification Script
# 快速验证当前是否有 "总是返回固定 3 个 POI" 的问题

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "================================================"
echo "Quick POI Selection Verification"
echo "================================================"
echo "Base URL: $BASE_URL"
echo ""

# Test 1: 显式选择 tiantan 和 yiheyuan
echo "Test 1: Requesting [tiantan, yiheyuan]"
echo "--------------------------------------"

response1=$(curl -s -X POST "$BASE_URL/api/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "selected_themes": ["tiantan", "yiheyuan"],
    "time_budget": "half_day",
    "transportation": "walking",
    "mbti": "ENFP",
    "pace_preference": "medium"
  }')

poi_ids1=$(echo "$response1" | jq -r '.plan.stops[].poi_id' | tr '\n' ',' | sed 's/,$//')
echo "Returned POIs: $poi_ids1"

if echo "$poi_ids1" | grep -q "tiantan" && echo "$poi_ids1" | grep -q "yiheyuan"; then
    echo "✅ PASS: tiantan 和 yiheyuan 都在结果中"
else
    echo "❌ FAIL: 缺少 tiantan 或 yiheyuan"
    echo "Full response:"
    echo "$response1" | jq '.'
    exit 1
fi

echo ""

# Test 2: 显式选择 gugong
echo "Test 2: Requesting [gugong]"
echo "----------------------------"

response2=$(curl -s -X POST "$BASE_URL/api/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "selected_themes": ["gugong"],
    "time_budget": "half_day",
    "transportation": "walking",
    "mbti": "INTJ",
    "pace_preference": "medium"
  }')

poi_ids2=$(echo "$response2" | jq -r '.plan.stops[].poi_id' | tr '\n' ',' | sed 's/,$//')
echo "Returned POIs: $poi_ids2"

if echo "$poi_ids2" | grep -q "gugong"; then
    echo "✅ PASS: gugong 在结果中"
else
    echo "❌ FAIL: 缺少 gugong"
    echo "Full response:"
    echo "$response2" | jq '.'
    exit 1
fi

echo ""

# Test 3: 检查是否总是返回相同的 3 个 POI
echo "Test 3: Comparing results"
echo "-------------------------"

if [ "$poi_ids1" == "$poi_ids2" ]; then
    echo "⚠️  WARNING: 两次请求返回相同的 POI 列表"
    echo "  Request 1: $poi_ids1"
    echo "  Request 2: $poi_ids2"
    echo "  可能存在 '总是返回固定 3 个 POI' 的问题"
    exit 1
else
    echo "✅ PASS: 两次请求返回不同的 POI 列表（符合预期）"
    echo "  Request 1: $poi_ids1"
    echo "  Request 2: $poi_ids2"
fi

echo ""

# Test 4: 验证坐标字段
echo "Test 4: Checking coordinates"
echo "-----------------------------"

coords_count=$(echo "$response1" | jq '[.plan.stops[] | select(.lat != null and .lon != null)] | length')
total_stops=$(echo "$response1" | jq '.plan.stops | length')

if [ "$coords_count" == "$total_stops" ]; then
    echo "✅ PASS: 所有 stops 都有 lat/lon 坐标 ($coords_count/$total_stops)"
else
    echo "❌ FAIL: 部分 stops 缺少坐标 ($coords_count/$total_stops)"
    echo "Stops without coordinates:"
    echo "$response1" | jq '.plan.stops[] | select(.lat == null or .lon == null) | {poi_id, name, lat, lon}'
    exit 1
fi

echo ""
echo "================================================"
echo "✅ All quick checks passed!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Run full test suite: python test_poi_selection.py"
echo "  2. Check backend logs for POI matching details"
echo "  3. Verify frontend sends correct POI IDs (not Chinese names)"
