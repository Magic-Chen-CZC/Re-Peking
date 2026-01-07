#!/bin/bash
# VS Code 缓存清理脚本

echo "=" 
echo "🧹 VS Code 工作区清理脚本"
echo "="

PROJECT_DIR="/Users/czc/vscode/Beijing_guide/BeijingGuideAI"

echo ""
echo "📍 项目目录: $PROJECT_DIR"
echo ""

# 1. 清理项目工作区缓存
echo "1️⃣ 清理项目工作区缓存..."
cd "$PROJECT_DIR"
rm -rf .vscode/workspaceStorage 2>/dev/null && echo "   ✅ 清理 .vscode/workspaceStorage" || echo "   ⏭️  无需清理"

# 2. 验证文件位置
echo ""
echo "2️⃣ 验证文件结构..."
echo "   README/ 目录下的文档数量: $(ls -1 README/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   test/ 目录下的测试文件数量: $(ls -1 test/*.py 2>/dev/null | wc -l | tr -d ' ')"
echo "   根目录下的孤立 README 文件: $(ls -1 *.md 2>/dev/null | wc -l | tr -d ' ')"

# 3. 检查是否有遗留文件
echo ""
echo "3️⃣ 检查根目录遗留文件..."
if ls *.md 2>/dev/null | grep -q "README"; then
    echo "   ⚠️  发现遗留 README 文件："
    ls -1 *.md 2>/dev/null | grep "README"
    echo ""
    read -p "   是否删除这些文件? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f README*.md SEARCH_README.md TASK_*.md
        echo "   ✅ 已删除遗留文件"
    fi
else
    echo "   ✅ 无遗留文件"
fi

# 4. Git 状态检查
echo ""
echo "4️⃣ Git 状态检查..."
if git status &>/dev/null; then
    DELETED_FILES=$(git status --short | grep "^ D" | wc -l | tr -d ' ')
    MODIFIED_FILES=$(git status --short | grep "^ M" | wc -l | tr -d ' ')
    echo "   删除的文件: $DELETED_FILES"
    echo "   修改的文件: $MODIFIED_FILES"
    
    if [ "$DELETED_FILES" -gt 0 ] || [ "$MODIFIED_FILES" -gt 0 ]; then
        echo ""
        echo "   💡 建议执行 git status 查看变更"
    fi
else
    echo "   ⏭️  非 Git 仓库"
fi

echo ""
echo "=" 
echo "✨ 清理完成！"
echo "="
echo ""
echo "📝 下一步操作："
echo "   1. 关闭 VS Code"
echo "   2. 重新打开: code $PROJECT_DIR"
echo "   3. 或使用命令: Cmd+Shift+P → 'Developer: Reload Window'"
echo ""
