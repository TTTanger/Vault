#!/bin/bash

# 密码保险库启动脚本

echo "🔐 启动密码保险库..."

# 检查应用是否存在
if [ -d "dist/密码保险库.app" ]; then
    echo "✅ 找到应用，正在启动..."
    open "dist/密码保险库.app"
    echo "🚀 应用已启动！"
else
    echo "❌ 应用不存在，请先运行构建脚本："
    echo "   ./build_app.sh"
fi
