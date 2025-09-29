#!/bin/bash

# 密码保险库打包脚本

echo "🔐 开始构建密码保险库应用..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 清理之前的构建
echo "清理之前的构建..."
rm -rf build dist

# 构建应用
echo "构建Mac应用..."
python setup.py py2app

# 检查构建结果
if [ -d "dist/密码保险库.app" ]; then
    echo "✅ 应用构建成功！"
    echo "应用位置: $(pwd)/dist/密码保险库.app"
    echo ""
    echo "使用方法："
    echo "1. 双击 dist/密码保险库.app 启动应用"
    echo "2. 首次运行需要设置主密码"
    echo "3. 之后每次启动需要输入主密码解锁"
    echo ""
    echo "数据文件将保存在应用目录中："
    echo "- passwords.json (加密的密码数据)"
    echo "- vault.key (加密密钥)"
else
    echo "❌ 应用构建失败！"
    exit 1
fi

echo "构建完成！"
