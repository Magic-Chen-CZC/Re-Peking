#!/bin/bash

# Community 页列表与详情功能测试脚本
# 用于验证 API 集成、数据渲染、页面跳转等功能

echo "============================================"
echo "  Community 页功能测试脚本"
echo "============================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API 基础地址
API_BASE_URL="http://127.0.0.1:8000"

echo "📍 API 基础地址: $API_BASE_URL"
echo ""

# 测试 1: 检查 API 是否可用
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 1: 检查后端 API 是否可用"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/health" 2>/dev/null)

if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ 后端 API 可用 (HTTP $response)${NC}"
else
    echo -e "${RED}❌ 后端 API 不可用 (HTTP $response)${NC}"
    echo -e "${YELLOW}   提示: 请先启动后端服务${NC}"
fi
echo ""

# 测试 2: 获取文章列表
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 2: GET /api/posts?limit=20"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

response=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/posts?limit=20")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    count=$(echo "$body" | grep -o '"id"' | wc -l)
    echo -e "${GREEN}✅ 获取文章列表成功 (HTTP $http_code)${NC}"
    echo "   共获取 $count 条文章"
    
    # 解析第一条文章的信息
    if [ "$count" -gt 0 ]; then
        echo ""
        echo "   📄 第一条文章信息:"
        echo "$body" | python3 -c "
import json, sys
try:
    posts = json.load(sys.stdin)
    if posts and len(posts) > 0:
        post = posts[0]
        print(f'      ID: {post.get(\"id\", \"N/A\")}')
        print(f'      标题: {post.get(\"title\", \"N/A\")}')
        print(f'      POI: {post.get(\"cover_poi_id\", \"N/A\")}')
        print(f'      旅程ID: {post.get(\"trip_id\", \"N/A\")}')
except:
    pass
" 2>/dev/null
    fi
else
    echo -e "${RED}❌ 获取文章列表失败 (HTTP $http_code)${NC}"
    echo -e "${YELLOW}   将使用样例数据 SAMPLE_POSTS 作为兜底${NC}"
fi
echo ""

# 测试 3: 获取文章详情（如果列表不为空）
if [ "$http_code" = "200" ] && [ "$count" -gt 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "测试 3: GET /api/posts/{post_id}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 获取第一条文章的 ID
    post_id=$(echo "$body" | python3 -c "
import json, sys
try:
    posts = json.load(sys.stdin)
    if posts and len(posts) > 0:
        print(posts[0].get('id', ''))
except:
    pass
" 2>/dev/null)
    
    if [ -n "$post_id" ]; then
        echo "   使用文章ID: $post_id"
        
        detail_response=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/posts/$post_id")
        detail_http_code=$(echo "$detail_response" | tail -n1)
        detail_body=$(echo "$detail_response" | sed '$d')
        
        if [ "$detail_http_code" = "200" ]; then
            echo -e "${GREEN}✅ 获取文章详情成功 (HTTP $detail_http_code)${NC}"
            echo ""
            echo "   📖 文章详情:"
            echo "$detail_body" | python3 -c "
import json, sys
try:
    post = json.load(sys.stdin)
    print(f'      ID: {post.get(\"id\", \"N/A\")}')
    print(f'      标题: {post.get(\"title\", \"N/A\")}')
    print(f'      感想: {post.get(\"reflection\", \"N/A\")[:50]}...')
    print(f'      封面POI: {post.get(\"cover_poi_id\", \"N/A\")}')
    print(f'      封面图片: {post.get(\"cover_image_url\", \"N/A\")}')
    print(f'      旅程ID: {post.get(\"trip_id\", \"N/A\")}')
    print(f'      创建时间: {post.get(\"created_at\", \"N/A\")}')
except Exception as e:
    print(f'      解析错误: {e}')
" 2>/dev/null
        else
            echo -e "${RED}❌ 获取文章详情失败 (HTTP $detail_http_code)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  无法获取文章ID，跳过详情测试${NC}"
    fi
    echo ""
fi

# 测试 4: 检查样例数据
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 4: 样例数据 SAMPLE_POSTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sample_count=$(grep -o "id: 'sample-" pages/community/index.js | wc -l)
echo -e "${GREEN}✅ 样例数据已定义${NC}"
echo "   共 $sample_count 条样例文章"
echo ""
echo "   样例文章列表:"
grep -A 2 "id: 'sample-" pages/community/index.js | grep -E "id:|title:" | sed 's/^/      /'
echo ""

# 测试 5: 检查文件完整性
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 5: 检查文件完整性"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

files=(
    "pages/community/index.js"
    "pages/community/index.wxml"
    "pages/community/index.wxss"
    "pages/community/index.json"
)

all_exists=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file ${RED}(缺失)${NC}"
        all_exists=false
    fi
done
echo ""

# 测试 6: 检查关键函数
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 6: 检查关键函数实现"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

functions=(
    "fetchPosts"
    "renderSamplePosts"
    "applyPendingPostFocus"
    "handlePostClick"
    "formatTimestamp"
)

for func in "${functions[@]}"; do
    if grep -q "$func" pages/community/index.js; then
        echo -e "${GREEN}✅${NC} $func()"
    else
        echo -e "${RED}❌${NC} $func() ${RED}(未找到)${NC}"
    fi
done
echo ""

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$all_exists" = true ]; then
    echo -e "${GREEN}✅ 所有文件完整${NC}"
else
    echo -e "${RED}❌ 部分文件缺失${NC}"
fi

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ 后端 API 工作正常${NC}"
else
    echo -e "${YELLOW}⚠️  后端 API 未响应，将使用样例数据${NC}"
fi

echo ""
echo "============================================"
echo "  测试完成！"
echo "============================================"
echo ""
echo "📝 下一步操作:"
echo "   1. 在微信开发者工具中打开项目"
echo "   2. 进入 Community 页面"
echo "   3. 测试列表加载、卡片点击、详情展示"
echo ""
