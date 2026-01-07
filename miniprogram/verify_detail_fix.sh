#!/bin/bash
# 社区详情页修复验证脚本

echo "=========================================="
echo "  社区详情页图片与布局修复验证"
echo "=========================================="
echo ""

# 1. 检查修改的文件是否存在
echo "📂 检查修改的文件..."
files=(
  "miniprogram/utils/imageUtils.js"
  "miniprogram/pages/community/index.js"
  "miniprogram/components/scattered-ticket/index.js"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (不存在)"
  fi
done

echo ""
echo "🔍 检查关键函数..."

# 2. 检查 normalizeImageSrc 是否包含临时路径检测
if grep -q "includes('//tmp/')" miniprogram/utils/imageUtils.js; then
  echo "  ✅ normalizeImageSrc 包含临时路径检测 (includes('//tmp/'))"
else
  echo "  ❌ normalizeImageSrc 缺少临时路径检测"
fi

# 3. 检查 cleanTempImageUrl 是否包含临时路径清理
if grep -q "includes('//tmp/')" miniprogram/utils/imageUtils.js | grep -q "cleanTempImageUrl"; then
  echo "  ✅ cleanTempImageUrl 包含临时路径清理"
else
  echo "  ⚠️ cleanTempImageUrl 可能未完全更新"
fi

# 4. 检查 community/index.js 是否使用 normalizeImageSrc
if grep -q "normalizeImageSrc(post.cover_image_url" miniprogram/pages/community/index.js; then
  echo "  ✅ community/index.js 使用 normalizeImageSrc"
else
  echo "  ❌ community/index.js 未使用 normalizeImageSrc"
fi

# 5. 检查社区详情弹窗布局标识
if grep -q "detail-hero" miniprogram/pages/community/index.wxml; then
  echo "  ✅ community 详情弹窗包含主图区域"
else
  echo "  ❌ community 详情弹窗缺少主图区域"
fi

if grep -q "detail-section-title" miniprogram/pages/community/index.wxml; then
  echo "  ✅ community 详情弹窗包含中文模块标题"
else
  echo "  ❌ community 详情弹窗缺少中文模块标题"
fi

echo ""
echo "🎨 检查设计规范..."

# 8. 检查是否使用故宫图片作为兜底
if grep -q "/image/attractions/gugong.png" miniprogram/utils/imageUtils.js; then
  echo "  ✅ 使用 gugong.png 作为默认兜底图"
else
  echo "  ❌ 未使用 gugong.png 作为兜底图"
fi

# 9. 检查是否移除了 default.png 引用
if grep -q "default.png" miniprogram/utils/imageUtils.js; then
  echo "  ⚠️ imageUtils.js 仍包含 default.png 引用"
else
  echo "  ✅ 已移除 default.png 引用"
fi

echo ""
echo "📊 统计信息..."

# 10. 统计修改的行数
echo "  📄 修改的文件数量: ${#files[@]}"
echo "  📝 imageUtils.js 行数: $(wc -l < miniprogram/utils/imageUtils.js | xargs)"

echo ""
echo "=========================================="
echo "  验证完成！"
echo "=========================================="
echo ""
echo "📋 下一步测试："
echo "  1. 在开发者工具中打开小程序"
echo "  2. 进入社区页面 (Community)"
echo "  3. 点击任意帖子卡片"
echo "  4. 检查详情页布局是否正常"
echo "  5. 测试图片加载失败时的兜底效果"
echo "  6. 测试发布新帖子时的图片清理逻辑"
echo ""
echo "📖 详细验证步骤见: COMMUNITY_DETAIL_PAGE_FIX.md"
echo ""
