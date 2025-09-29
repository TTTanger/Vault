#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码保险库 - 本地密码管理应用 (现代化UI版本)
作者: AI Assistant
功能: 安全存储和管理密码，完全离线运行
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import threading
import time
import subprocess
import platform

class ModernPasswordVault:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔐 密码保险库")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 数据文件路径
        self.data_file = "passwords.json"
        
        # 认证状态
        self.is_unlocked = False
        self.passwords = []
        self.show_passwords = False
        
        # 设置现代化主题
        self.setup_modern_theme()
        
        # 创建界面
        self.create_modern_interface()
        
        # 使用系统认证保护应用
        self.system_auth_on_startup()
    
    def is_touchid_available(self):
        """检查Touch ID是否可用"""
        if platform.system() != 'Darwin':
            return False
        
        # 检查TouchID可执行文件是否存在
        touchid_path = os.path.join(os.path.dirname(__file__), 'touchid_test')
        if not os.path.exists(touchid_path):
            # 如果没有可执行文件，尝试编译
            try:
                self._compile_touchid_binary()
            except:
                return False
            
        try:
            # 使用我们的TouchID测试程序检查可用性（不进行认证）
            result = subprocess.run([touchid_path], 
                                  capture_output=True, text=True, timeout=3)
            return 'TOUCHID_AVAILABLE' in result.stdout
        except:
            return False
    
    def system_auth_on_startup(self):
        """应用启动时使用系统认证"""
        self.show_auth_dialog()
    
    def show_auth_dialog(self):
        """显示认证对话框"""
        # 创建认证对话框
        auth_dialog = tk.Toplevel(self.root)
        auth_dialog.title("系统认证")
        auth_dialog.geometry("400x300")
        auth_dialog.resizable(False, False)
        auth_dialog.configure(bg=self.colors['light'])
        
        # 居中显示
        auth_dialog.transient(self.root)
        auth_dialog.grab_set()
        
        # 标题
        title_label = tk.Label(auth_dialog, text="🔐 密码保险库", 
                              font=("SF Pro Display", 18, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['light'])
        title_label.pack(pady=(30, 10))
        
        desc_label = tk.Label(auth_dialog, text="请使用Touch ID验证身份", 
                             font=("SF Pro Text", 12),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['light'])
        desc_label.pack(pady=(0, 30))
        
        # 状态标签
        status_label = tk.Label(auth_dialog, text="", 
                               font=("SF Pro Text", 11),
                               fg=self.colors['danger'],
                               bg=self.colors['light'])
        status_label.pack(pady=(0, 20))
        
        # 按钮
        button_frame = tk.Frame(auth_dialog, bg=self.colors['light'])
        button_frame.pack(pady=20)
        
        auth_btn = tk.Button(button_frame, text="使用Touch ID验证", 
                            font=("SF Pro Text", 12, "bold"),
                            bg=self.colors['surface'],
                            fg=self.colors['text'],
                            relief='flat', bd=1,
                            cursor='hand2',
                            command=lambda: self.perform_auth(auth_dialog, status_label))
        auth_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=20, ipady=8)
        
        exit_btn = tk.Button(button_frame, text="退出", 
                            font=("SF Pro Text", 12, "bold"),
                            bg=self.colors['surface'],
                            fg=self.colors['text'],
                            relief='flat', bd=1,
                            cursor='hand2',
                            command=self.root.quit)
        exit_btn.pack(side=tk.LEFT, ipadx=20, ipady=8)
        
        # 自动开始第一次验证
        self.root.after(500, lambda: self.perform_auth(auth_dialog, status_label))
    
    def perform_auth(self, dialog, status_label):
        """执行认证"""
        status_label.config(text="正在验证...")
        self.root.update()
        
        if self.verify_touchid("请验证身份以使用密码保险库"):
            # 认证成功
            dialog.destroy()
            self.is_unlocked = True
            self.status_indicator.config(text="🔓 已通过系统认证", fg=self.colors['success'])
            self.enable_buttons()
            self.load_passwords()
        else:
            # 认证失败，显示重试选项
            status_label.config(text="认证失败，请重试或退出应用")
    
    def _compile_touchid_binary(self):
        """编译TouchID验证二进制文件"""
        touchid_source = os.path.join(os.path.dirname(__file__), 'touchid_test.m')
        touchid_binary = os.path.join(os.path.dirname(__file__), 'touchid_test')
        
        if not os.path.exists(touchid_source):
            raise Exception("TouchID源文件不存在")
        
        # 编译Objective-C源文件
        result = subprocess.run([
            'clang',
            '-framework', 'Foundation',
            '-framework', 'LocalAuthentication',
            touchid_source,
            '-o', touchid_binary
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"编译TouchID程序失败: {result.stderr}")
    
    def verify_touchid(self, reason="验证身份以访问密码保险库"):
        """使用Touch ID验证身份"""
        if not self.is_touchid_available():
            return False
        
        try:
            # 使用真正的Touch ID硬件验证
            touchid_path = os.path.join(os.path.dirname(__file__), 'touchid_test')
            
            if not os.path.exists(touchid_path):
                print("TouchID程序不存在，尝试编译...")
                self._compile_touchid_binary()
            
            # 调用我们的TouchID验证程序（带--auth参数进行真正的认证）
            result = subprocess.run([touchid_path, '--auth'], 
                                  capture_output=True, text=True, timeout=60)
            
            output = result.stdout.strip()
            print(f"TouchID验证结果: {output}")
            
            if output == "TOUCHID_SUCCESS":
                return True
            elif output == "TOUCHID_CANCELLED":
                print("用户取消了Touch ID验证")
                return False
            elif output == "TOUCHID_FALLBACK":
                print("用户选择了密码验证")
                return False
            elif output == "TOUCHID_NOT_AVAILABLE":
                print("Touch ID不可用")
                return False
            elif output == "TOUCHID_NOT_ENROLLED":
                print("未设置Touch ID")
                return False
            elif output == "TOUCHID_LOCKOUT":
                print("Touch ID被锁定")
                return False
            else:
                print(f"Touch ID验证错误: {output}")
                return False
            
        except Exception as e:
            print(f"Touch ID验证错误: {e}")
            return False
    
    
    def setup_modern_theme(self):
        """设置现代化主题和颜色"""
        # Streamlit风格的现代化颜色方案
        self.colors = {
            'primary': '#FF4B4B',      # Streamlit红
            'primary_dark': '#E03E3E', # 深红
            'secondary': '#00D4AA',    # Streamlit绿
            'success': '#00D4AA',      # 成功绿
            'warning': '#FFA726',      # 警告橙
            'danger': '#FF4B4B',       # 危险红
            'info': '#1F77B4',         # 信息蓝
            'light': '#FAFAFA',        # 极浅灰
            'white': '#FFFFFF',        # 纯白
            'dark': '#262730',         # 深色
            'text': '#262730',         # 主文本
            'text_primary': '#262730', # 主文本
            'text_secondary': '#808495', # 次要文本
            'background': '#FFFFFF',   # 背景色
            'surface': '#F0F2F6',      # 表面色
            'border': '#E6E9EF',       # 边框色
            'hover': '#F0F2F6',        # 悬停色
            'gray_100': '#F8F9FA',
            'gray_200': '#E9ECEF',
            'gray_300': '#DEE2E6',
            'gray_400': '#CED4DA',
            'gray_500': '#ADB5BD',
            'gray_600': '#6C757D',
            'gray_700': '#495057',
            'gray_800': '#343A40',
            'gray_900': '#212529',
            'text_muted': '#95a5a6'
        }
        
        # 配置ttk样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义Treeview样式
        style.configure("Modern.Treeview",
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['white'],
                       borderwidth=0,
                       font=('SF Pro Text', 11))
        
        style.configure("Modern.Treeview.Heading",
                       background=self.colors['gray_100'],
                       foreground=self.colors['gray_700'],
                       font=('SF Pro Display', 12, 'bold'),
                       borderwidth=0,
                       relief='flat')
        
        style.map("Modern.Treeview.Heading",
                 background=[('active', self.colors['gray_200'])])
        
        # 配置根窗口
        self.root.configure(bg=self.colors['background'])
    
    def create_modern_interface(self):
        """创建Streamlit风格的用户界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部导航栏 - Streamlit风格
        self.create_streamlit_header(main_container)
        
        # 内容区域 - 更像Streamlit的布局
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # 工具栏 - Streamlit风格
        self.create_streamlit_toolbar(content_frame)
        
        # 数据表格 - Streamlit风格
        self.create_streamlit_data_table(content_frame)
        
        # 底部状态栏
        self.create_status_bar(main_container)
    
    def create_streamlit_header(self, parent):
        """创建Streamlit风格的头部"""
        # 头部容器
        header_frame = tk.Frame(parent, bg=self.colors['background'])
        header_frame.pack(fill=tk.X, padx=0, pady=(0, 30))
        
        # 主标题
        title_label = tk.Label(header_frame, text="🔐 密码保险库", 
                              font=("SF Pro Display", 32, "bold"), 
                              fg=self.colors['text_primary'], 
                              bg=self.colors['background'])
        title_label.pack(pady=(20, 5))
        
        # 副标题
        subtitle_label = tk.Label(header_frame, text="安全管理您的所有密码账户", 
                                 font=("SF Pro Text", 14), 
                                 fg=self.colors['text_secondary'], 
                                 bg=self.colors['background'])
        subtitle_label.pack()
        
        # 状态指示器
        self.status_indicator = tk.Label(header_frame, text="🔒 已锁定", 
                                        font=("SF Pro Text", 12, "bold"),
                                        fg=self.colors['danger'],
                                        bg=self.colors['background'])
        self.status_indicator.pack(pady=(10, 0))
        
        # 分隔线
        separator = tk.Frame(header_frame, bg=self.colors['border'], height=1)
        separator.pack(fill=tk.X, pady=(20, 0))
    
    def create_streamlit_toolbar(self, parent):
        """创建Streamlit风格的工具栏"""
        # 工具栏容器
        toolbar_frame = tk.Frame(parent, bg=self.colors['background'])
        toolbar_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 左侧：搜索框
        search_frame = tk.Frame(toolbar_frame, bg=self.colors['background'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 搜索标签
        search_label = tk.Label(search_frame, text="🔍 搜索密码", 
                               font=("SF Pro Text", 12, "bold"), 
                               fg=self.colors['text_primary'], 
                               bg=self.colors['background'])
        search_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame,
                                    textvariable=self.search_var,
                                    font=("SF Pro Text", 12),
                                    relief='flat', bd=1,
                                    bg=self.colors['white'],
                                    fg=self.colors['text_primary'])
        self.search_entry.pack(fill=tk.X, ipady=8, pady=(0, 20))
        
        # 搜索功能绑定
        self.search_var.trace_add('write', lambda *args: self.filter_entries())
        
        # 右侧：按钮组 - 改为横向排列
        button_frame = tk.Frame(toolbar_frame, bg=self.colors['background'])
        button_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Streamlit风格的横向按钮布局
        buttons_container = tk.Frame(button_frame, bg=self.colors['background'])
        buttons_container.pack()
        
        # 第一行按钮
        row1_frame = tk.Frame(buttons_container, bg=self.colors['background'])
        row1_frame.pack(fill=tk.X, pady=(0, 8))
        
        # 添加密码按钮
        self.add_btn = tk.Button(row1_frame, text="➕ 添加密码", 
                                bg=self.colors['surface'], fg=self.colors['text'],
                                font=("SF Pro Text", 10, 'bold'),
                                relief='flat', bd=1,
                                cursor='hand2',
                                command=self.add_password)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 8), ipadx=15, ipady=8)
        
        # 显示/隐藏密码按钮
        self.toggle_btn = tk.Button(row1_frame, text="👁️ 显示密码", 
                                   bg=self.colors['surface'], fg=self.colors['text'],
                                   font=("SF Pro Text", 10, 'bold'),
                                   relief='flat', bd=1,
                                   cursor='hand2',
                                   command=self.toggle_password_visibility)
        self.toggle_btn.pack(side=tk.LEFT, padx=(0, 8), ipadx=15, ipady=8)
        
        # 刷新按钮
        refresh_btn = tk.Button(row1_frame, text="🔄 刷新", 
                               bg=self.colors['surface'], fg=self.colors['text'],
                               font=("SF Pro Text", 10, 'bold'),
                               relief='flat', bd=1,
                               cursor='hand2',
                               command=self.refresh_list)
        refresh_btn.pack(side=tk.LEFT, ipadx=15, ipady=8)
        
        # 第二行按钮
        row2_frame = tk.Frame(buttons_container, bg=self.colors['background'])
        row2_frame.pack(fill=tk.X)
        
        # 导出数据按钮
        export_btn = tk.Button(row2_frame, text="📤 导出数据", 
                              bg=self.colors['surface'], fg=self.colors['text'],
                              font=("SF Pro Text", 10, 'bold'),
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=self.export_data)
        export_btn.pack(side=tk.LEFT, padx=(0, 8), ipadx=15, ipady=8)
        
        # 导入数据按钮
        import_btn = tk.Button(row2_frame, text="📥 导入数据", 
                              bg=self.colors['surface'], 
                              fg=self.colors['text'],
                              font=("SF Pro Text", 10, 'bold'),
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=self.import_data)
        import_btn.pack(side=tk.LEFT, ipadx=15, ipady=8)
    
    def create_streamlit_data_table(self, parent):
        """创建Streamlit风格的数据表格"""
        # 表格标题
        table_title = tk.Label(parent, text="📊 密码数据", 
                              font=("SF Pro Text", 16, "bold"), 
                              fg=self.colors['text_primary'], 
                              bg=self.colors['background'])
        table_title.pack(anchor=tk.W, pady=(0, 10))
        
        # 统计信息
        self.stats_label = tk.Label(parent, text="0 个网站/应用，0 个账户", 
                                   font=("SF Pro Text", 11), 
                                   fg=self.colors['text_secondary'], 
                                   bg=self.colors['background'])
        self.stats_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 表格容器 - Streamlit风格
        table_container = tk.Frame(parent, bg=self.colors['white'], relief='flat', bd=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建TreeView
        columns = ('网站/应用', '账号', '密码', '描述', '创建时间')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', 
                                style='Modern.Treeview', height=15)
        
        # 设置列标题和宽度
        self.tree.heading('网站/应用', text='🌐 网站/应用')
        self.tree.heading('账号', text='👤 账号')
        self.tree.heading('密码', text='🔑 密码')
        self.tree.heading('描述', text='📝 描述')
        self.tree.heading('创建时间', text='🕒 创建时间')
        
        self.tree.column('网站/应用', width=150)
        self.tree.column('账号', width=150)
        self.tree.column('密码', width=120)
        self.tree.column('描述', width=200)
        self.tree.column('创建时间', width=130)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 使用pack布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.tree.bind('<Double-1>', lambda e: self.quick_edit_account())
        self.tree.bind('<Button-1>', self.on_item_select)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_header(self, parent):
        """创建顶部导航栏"""
        header_frame = tk.Frame(parent, bg=self.colors['white'], height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # 添加阴影效果
        shadow = tk.Frame(parent, bg=self.colors['gray_200'], height=1)
        shadow.pack(fill=tk.X)
        
        # 左侧标题区域
        title_frame = tk.Frame(header_frame, bg=self.colors['white'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y, padx=30, pady=15)
        
        # 主标题 - Streamlit风格
        title_label = tk.Label(title_frame, text="🔐 密码保险库", 
                              font=("SF Pro Display", 24, "bold"), 
                              fg=self.colors['text_primary'], 
                              bg=self.colors['white'])
        title_label.pack(anchor=tk.W)
        
        # 副标题
        subtitle_label = tk.Label(title_frame, text="安全、简洁的密码管理工具", 
                                 font=("SF Pro Text", 13), 
                                 fg=self.colors['text_secondary'], 
                                 bg=self.colors['white'])
        subtitle_label.pack(anchor=tk.W, pady=(4, 0))
        
        # 右侧状态指示器
        status_frame = tk.Frame(header_frame, bg=self.colors['white'])
        status_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=30, pady=15)
        
        self.status_indicator = tk.Label(status_frame, text="🔒 已锁定", 
                                        font=("SF Pro Text", 12, "bold"),
                                        fg=self.colors['danger'],
                                        bg=self.colors['white'])
        self.status_indicator.pack(anchor=tk.E)
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar_frame = tk.Frame(parent, bg=self.colors['white'], relief='flat', bd=0)
        toolbar_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 添加圆角效果
        toolbar_inner = tk.Frame(toolbar_frame, bg=self.colors['white'], 
                                relief='flat', bd=1)
        toolbar_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧搜索区域
        search_frame = tk.Frame(toolbar_inner, bg=self.colors['white'])
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 搜索框
        search_container = tk.Frame(search_frame, bg=self.colors['gray_100'], 
                                   relief='flat', bd=0)
        search_container.pack(fill=tk.X, padx=(0, 20))
        
        # 搜索图标
        search_icon = tk.Label(search_container, text="🔍", 
                              font=("SF Pro Text", 14), 
                              bg=self.colors['gray_100'], 
                              fg=self.colors['gray_600'])
        search_icon.pack(side=tk.LEFT, padx=(15, 10), pady=12)
        
        # 搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_container, textvariable=self.search_var, 
                                    font=("SF Pro Text", 13), relief='flat', bd=0,
                                    bg=self.colors['gray_100'], 
                                    fg=self.colors['text_primary'],
                                    insertbackground=self.colors['text_primary'])
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                              padx=(0, 15), pady=12)
        
        # 添加占位符文本
        self.search_entry.insert(0, "搜索网站、应用或账号...")
        self.search_entry.configure(fg=self.colors['gray_500'])
        
        # 绑定搜索事件
        self.search_var.trace_add('write', self.on_search_change)
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        
        # 右侧按钮区域
        button_frame = tk.Frame(toolbar_inner, bg=self.colors['white'])
        button_frame.pack(side=tk.RIGHT)
        
        # 现代化按钮样式
        button_style = {
            'font': ('SF Pro Display', 11, 'bold'),
            'relief': 'flat',
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': self.colors['gray_200'],
            'activeforeground': self.colors['text_primary']
        }
        
        # Streamlit风格的按钮
        # 添加密码按钮
        self.add_btn = tk.Button(button_frame, text="➕ 添加密码", 
                                bg=self.colors['primary'], fg=self.colors['white'],
                                font=("SF Pro Text", 11, 'bold'),
                                relief='flat', bd=0,
                                cursor='hand2',
                                command=self.add_password)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 8), ipadx=15, ipady=8)
        
        # 显示/隐藏密码按钮
        self.toggle_btn = tk.Button(button_frame, text="👁️ 显示密码", 
                                   bg=self.colors['secondary'], fg=self.colors['white'],
                                   font=("SF Pro Text", 11, 'bold'),
                                   relief='flat', bd=0,
                                   cursor='hand2',
                                   command=self.toggle_password_visibility)
        self.toggle_btn.pack(side=tk.LEFT, padx=(0, 8), ipadx=15, ipady=8)
        
        # 刷新按钮
        refresh_btn = tk.Button(button_frame, text="🔄 刷新", 
                               bg=self.colors['info'], fg=self.colors['white'],
                               font=("SF Pro Text", 11, 'bold'),
                               relief='flat', bd=0,
                               cursor='hand2',
                               command=self.refresh_list)
        refresh_btn.pack(side=tk.LEFT, ipadx=15, ipady=8)
    
    def create_password_list(self, parent):
        """创建密码列表"""
        # 列表容器
        list_container = tk.Frame(parent, bg=self.colors['white'], relief='flat', bd=1)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 列表标题栏
        list_header = tk.Frame(list_container, bg=self.colors['white'])
        list_header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        list_title = tk.Label(list_header, text="密码列表", 
                             font=("SF Pro Display", 16, "bold"), 
                             fg=self.colors['text_primary'], 
                             bg=self.colors['white'])
        list_title.pack(side=tk.LEFT)
        
        # 统计信息
        self.stats_label = tk.Label(list_header, text="0 个密码", 
                                   font=("SF Pro Text", 11), 
                                   fg=self.colors['text_secondary'], 
                                   bg=self.colors['white'])
        self.stats_label.pack(side=tk.RIGHT)
        
        # Treeview容器
        tree_container = tk.Frame(list_container, bg=self.colors['white'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 创建Treeview
        columns = ('网站/应用', '账号', '密码', '添加时间')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', 
                                height=15, style="Modern.Treeview")
        
        # 设置列标题和宽度
        self.tree.heading('网站/应用', text='网站/应用')
        self.tree.heading('账号', text='账号')
        self.tree.heading('密码', text='密码')
        self.tree.heading('添加时间', text='添加时间')
        
        self.tree.column('网站/应用', width=250, minwidth=200)
        self.tree.column('账号', width=200, minwidth=150)
        self.tree.column('密码', width=180, minwidth=120)
        self.tree.column('添加时间', width=150, minwidth=120)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, 
                                   command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, 
                                   command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, 
                           xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.tree.bind('<Double-1>', lambda e: self.quick_edit_account())
        self.tree.bind('<Button-1>', self.on_item_select)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        status_frame = tk.Frame(parent, bg=self.colors['gray_800'], height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="就绪", 
                                    font=("SF Pro Text", 10), 
                                    fg=self.colors['white'], 
                                    bg=self.colors['gray_800'])
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        # 版本信息
        version_label = tk.Label(status_frame, text="v1.0.0", 
                                font=("SF Pro Text", 10), 
                                fg=self.colors['gray_400'], 
                                bg=self.colors['gray_800'])
        version_label.pack(side=tk.RIGHT, padx=15, pady=5)
    
    def on_search_change(self, *args):
        """搜索框内容变化事件"""
        self.filter_entries()
    
    def on_search_focus_in(self, event):
        """搜索框获得焦点"""
        if self.search_entry.get() == "搜索网站、应用或账号...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg=self.colors['text_primary'])
    
    def on_search_focus_out(self, event):
        """搜索框失去焦点"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "搜索网站、应用或账号...")
            self.search_entry.configure(fg=self.colors['gray_500'])
    
    def on_item_select(self, event):
        """列表项选择事件"""
        selection = self.tree.selection()
        if selection:
            # 启用编辑和删除按钮
            pass
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="编辑密码", command=self.edit_password)
            context_menu.add_command(label="删除密码", command=self.delete_password)
            context_menu.add_separator()
            context_menu.add_command(label="复制密码", command=self.copy_password)
            context_menu.add_command(label="复制账号", command=self.copy_username)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    
    
    
    
    def enable_buttons(self):
        """启用按钮"""
        self.add_btn.config(state='normal')
    
    def load_passwords(self):
        """加载密码数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.passwords = json.load(f)
            else:
                self.passwords = []
            
            # 确保数据结构正确（向后兼容）
            self.migrate_data_structure()
            self.update_password_list()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("错误", f"加载密码数据失败: {str(e)}")
    
    def migrate_data_structure(self):
        """迁移数据结构以支持多账户"""
        migrated = False
        for item in self.passwords:
            # 检查是否是旧格式（直接包含website, username, password）
            if 'website' in item and 'username' in item and 'password' in item:
                # 转换为新格式
                website = item['website']
                username = item['username']
                password = item['password']
                created_time = item.get('created_time', time.strftime('%Y-%m-%d %H:%M'))
                
                # 创建新的数据结构
                new_item = {
                    'website': website,
                    'accounts': [{
                        'username': username,
                        'password': password,
                        'created_time': created_time,
                        'description': ''
                    }]
                }
                
                # 替换旧项目
                index = self.passwords.index(item)
                self.passwords[index] = new_item
                migrated = True
        
        if migrated:
            self.save_passwords()
    
    def save_passwords(self):
        """保存密码数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.passwords, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存密码数据失败: {str(e)}")
    
    def update_password_list(self):
        """更新密码列表显示"""
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加密码项目 - 每个账户显示为独立行
        for password_data in self.passwords:
            website = password_data.get('website', '')
            accounts = password_data.get('accounts', [])
            
            if accounts:
                for i, account in enumerate(accounts):
                    username = account.get('username', '')
                    password = account.get('password', '')
                    created_time = account.get('created_time', '')
                    description = account.get('description', '')
                    
                    # 根据显示设置决定密码显示方式
                    display_password = password if self.show_passwords else '•' * len(password)
                    
                    # 网站名显示：第一个账户显示完整网站名，其他账户显示缩进
                    display_website = website if i == 0 else f"  └─ {website}"
                    
                    self.tree.insert('', 'end', values=(display_website, username, display_password, description, created_time))
    
    def update_stats(self):
        """更新统计信息"""
        website_count = len(self.passwords)
        total_accounts = sum(len(item.get('accounts', [])) for item in self.passwords)
        self.stats_label.config(text=f"{website_count} 个网站/应用，{total_accounts} 个账户")
    
    def filter_entries(self):
        """过滤密码条目"""
        search_term = self.search_var.get().lower()
        
        # 如果搜索框是占位符文本，显示所有项目
        if search_term == "搜索网站、应用或账号...":
            search_term = ""
        
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 过滤并添加匹配的项目
        filtered_websites = 0
        filtered_accounts = 0
        for password_data in self.passwords:
            website = password_data.get('website', '').lower()
            accounts = password_data.get('accounts', [])
            
            # 检查网站名称或任何账户是否匹配
            matches = False
            if search_term in website:
                matches = True
            else:
                for account in accounts:
                    username = account.get('username', '').lower()
                    if search_term in username:
                        matches = True
                        break
            
            if matches and accounts:
                filtered_websites += 1
                filtered_accounts += len(accounts)
                
                # 显示第一个账户作为主要信息
                first_account = accounts[0]
                username = first_account.get('username', '')
                password = first_account.get('password', '')
                created_time = first_account.get('created_time', '')
                
                display_password = password if self.show_passwords else '•' * len(password)
                account_count = len(accounts)
                display_username = username
                if account_count > 1:
                    display_username = f"{username} (+{account_count-1}个账户)"
                
                self.tree.insert('', 'end', values=(website, display_username, display_password, created_time))
        
        # 更新统计信息
        if search_term:
            self.stats_label.config(text=f"找到 {filtered_websites} 个网站/应用，{filtered_accounts} 个账户")
        else:
            self.update_stats()
    
    def add_password(self):
        """添加密码"""
        dialog = PasswordDialog(self.root, self.colors, "添加密码")
        if dialog.result:
            website = dialog.result['website']
            username = dialog.result['username']
            password = dialog.result['password']
            description = dialog.result.get('description', '')
            
            # 检查是否已存在该网站
            existing_item = None
            for item in self.passwords:
                if item.get('website', '').lower() == website.lower():
                    existing_item = item
                    break
            
            if existing_item:
                # 添加新账户到现有网站
                new_account = {
                    'username': username,
                    'password': password,
                    'created_time': time.strftime('%Y-%m-%d %H:%M'),
                    'description': description
                }
                existing_item['accounts'].append(new_account)
                self.status_label.config(text=f"已为 {website} 添加新账户")
            else:
                # 创建新的网站条目
                new_item = {
                    'website': website,
                    'accounts': [{
                        'username': username,
                        'password': password,
                        'created_time': time.strftime('%Y-%m-%d %H:%M'),
                        'description': description
                    }]
                }
                self.passwords.append(new_item)
                self.status_label.config(text=f"已添加新网站 {website}")
            
            self.save_passwords()
            self.update_password_list()
            self.update_stats()
    
    def quick_edit_account(self):
        """快速编辑单个账户（双击）"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        display_website = str(item['values'][0])
        username = str(item['values'][1])
        
        # 处理缩进的网站名
        website = display_website.replace("  └─ ", "").strip()
        
        # 找到对应的账户数据
        for pwd in self.passwords:
            if str(pwd.get('website', '')) == website:
                accounts = pwd.get('accounts', [])
                for account in accounts:
                    if str(account.get('username', '')) == username:
                        # 直接编辑这个账户
                        dialog = PasswordDialog(self.root, self.colors, f"编辑 {website} 的账户", {
                            'website': website,
                            'username': account['username'],
                            'password': account['password'],
                            'description': account.get('description', '')
                        })
                        if dialog.result:
                            account['username'] = dialog.result['username']
                            account['password'] = dialog.result['password']
                            account['description'] = dialog.result.get('description', '')
                            account['modified_time'] = time.strftime('%Y-%m-%d %H:%M')
                            self.save_passwords()
                            self.update_password_list()
                            self.update_stats()
                            self.status_label.config(text="账户已更新")
                        return
    
    def edit_password(self):
        """编辑密码"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的密码条目")
            return
        
        item = self.tree.item(selection[0])
        display_website = str(item['values'][0])
        
        # 处理缩进的网站名
        website = display_website.replace("  └─ ", "").strip()
        
        # 找到对应的密码数据
        password_data = None
        for pwd in self.passwords:
            if str(pwd.get('website', '')) == website:
                password_data = pwd
                break
        
        if password_data:
            # 显示账户管理对话框
            dialog = AccountManagerDialog(self.root, self.colors, website, password_data['accounts'])
            if dialog.result:
                password_data['accounts'] = dialog.result
                password_data['modified_time'] = time.strftime('%Y-%m-%d %H:%M')
                self.save_passwords()
                self.update_password_list()
                self.update_stats()
                self.status_label.config(text="密码已更新")
    
    def delete_password(self):
        """删除密码"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的密码条目")
            return
        
        item = self.tree.item(selection[0])
        display_website = str(item['values'][0])
        
        # 处理缩进的网站名
        website = display_website.replace("  └─ ", "").strip()
        
        # 找到对应的密码数据
        password_data = None
        for pwd in self.passwords:
            if str(pwd.get('website', '')) == website:
                password_data = pwd
                break
        
        if password_data:
            account_count = len(password_data['accounts'])
            if account_count > 1:
                # 如果有多个账户，询问是否删除整个网站或单个账户
                choice = messagebox.askyesnocancel("确认删除", 
                    f"'{website}' 有 {account_count} 个账户。\n\n"
                    "是：删除整个网站及其所有账户\n"
                    "否：选择要删除的账户\n"
                    "取消：取消删除")
                
                if choice is True:
                    # 删除整个网站
                    self.passwords = [pwd for pwd in self.passwords if pwd['website'] != website]
                    self.save_passwords()
                    self.update_password_list()
                    self.update_stats()
                    self.status_label.config(text="网站及其所有账户已删除")
                elif choice is False:
                    # 显示账户选择对话框
                    dialog = AccountDeleteDialog(self.root, self.colors, website, password_data['accounts'])
                    if dialog.result:
                        password_data['accounts'] = dialog.result
                        if not password_data['accounts']:
                            # 如果没有账户了，删除整个网站
                            self.passwords = [pwd for pwd in self.passwords if pwd['website'] != website]
                        self.save_passwords()
                        self.update_password_list()
                        self.update_stats()
                        self.status_label.config(text="账户已删除")
            else:
                # 只有一个账户，直接删除整个网站
                if messagebox.askyesno("确认删除", f"确定要删除 '{website}' 及其账户吗？"):
                    self.passwords = [pwd for pwd in self.passwords if pwd['website'] != website]
                    self.save_passwords()
                    self.update_password_list()
                    self.update_stats()
                    self.status_label.config(text="网站已删除")
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        self.show_passwords = not self.show_passwords
        if self.show_passwords:
            self.toggle_btn.config(text="🙈 隐藏密码")
            self.status_label.config(text="密码已显示")
        else:
            self.toggle_btn.config(text="👁️ 显示密码")
            self.status_label.config(text="密码已隐藏")
        
        self.update_password_list()
    
    def refresh_list(self):
        """刷新列表"""
        self.load_passwords()
        self.status_label.config(text="列表已刷新")
    
    def export_data(self):
        """导出所有密码数据"""
        if not self.passwords:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        # 选择导出路径
        file_path = filedialog.asksaveasfilename(
            title="选择导出位置",
            defaultextension=".json",
            filetypes=[
                ("JSON文件", "*.json"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return  # 用户取消了选择
        
        try:
            # 准备导出数据
            export_data = {
                "export_info": {
                    "export_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "total_websites": len(self.passwords),
                    "total_accounts": sum(len(item.get('accounts', [])) for item in self.passwords),
                    "app_version": "2.0.0"
                },
                "passwords": self.passwords
            }
            
            # 根据文件扩展名决定导出格式
            if file_path.lower().endswith('.json'):
                # JSON格式导出
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                # 文本格式导出（便于阅读）
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("密码保险库 - 数据导出\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"导出时间: {export_data['export_info']['export_time']}\n")
                    f.write(f"网站数量: {export_data['export_info']['total_websites']}\n")
                    f.write(f"账户总数: {export_data['export_info']['total_accounts']}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for website_data in self.passwords:
                        website = website_data.get('website', '')
                        accounts = website_data.get('accounts', [])
                        
                        f.write(f"🌐 网站: {website}\n")
                        f.write(f"   账户数量: {len(accounts)}\n")
                        f.write("-" * 40 + "\n")
                        
                        for i, account in enumerate(accounts, 1):
                            f.write(f"   账户 {i}:\n")
                            f.write(f"     用户名: {account.get('username', '')}\n")
                            f.write(f"     密码: {account.get('password', '')}\n")
                            f.write(f"     描述: {account.get('description', '无')}\n")
                            f.write(f"     创建时间: {account.get('created_time', '未知')}\n")
                            f.write("\n")
                        f.write("\n")
            
            messagebox.showinfo("导出成功", f"数据已成功导出到：\n{file_path}")
            self.status_label.config(text=f"数据已导出到: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时发生错误：\n{str(e)}")
            self.status_label.config(text="数据导出失败")
    
    def import_data(self):
        """从JSON文件导入密码数据"""
        # 选择导入文件
        file_path = filedialog.askopenfilename(
            title="选择要导入的JSON文件",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return  # 用户取消了选择
        
        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 验证数据格式
            if not isinstance(import_data, dict):
                messagebox.showerror("导入失败", "文件格式不正确：必须是JSON对象")
                return
            
            # 检查是否是我们的导出格式
            if 'passwords' in import_data and 'export_info' in import_data:
                # 标准导出格式
                passwords_to_import = import_data['passwords']
                import_info = import_data['export_info']
                total_websites = import_info.get('total_websites', 0)
                total_accounts = import_info.get('total_accounts', 0)
                export_time = import_info.get('export_time', '未知')
            elif isinstance(import_data, list):
                # 直接是密码列表
                passwords_to_import = import_data
                total_websites = len(passwords_to_import)
                total_accounts = sum(len(item.get('accounts', [])) for item in passwords_to_import)
                export_time = "未知"
            else:
                # 检查是否是单个密码对象格式
                if 'website' in import_data:
                    passwords_to_import = [import_data]
                    total_websites = 1
                    total_accounts = len(import_data.get('accounts', []))
                    export_time = "未知"
                else:
                    messagebox.showerror("导入失败", "无法识别的JSON格式")
                    return
            
            # 验证密码数据格式
            if not self._validate_import_data(passwords_to_import):
                return
            
            # 询问导入选项
            import_option = self._show_import_options_dialog(total_websites, total_accounts, export_time)
            if import_option is None:
                return  # 用户取消
            
            # 执行导入
            imported_count, merged_count = self._perform_import(passwords_to_import, import_option)
            
            # 更新界面
            self.update_password_list()
            self.save_passwords()
            
            # 显示导入结果
            if import_option == "replace":
                message = f"导入完成！\n\n替换了所有数据：\n- 网站数量: {imported_count}\n- 总账户数: {sum(len(item.get('accounts', [])) for item in self.passwords)}"
            else:
                message = f"导入完成！\n\n导入统计：\n- 新增网站: {imported_count}\n- 合并网站: {merged_count}\n- 当前总网站数: {len(self.passwords)}\n- 当前总账户数: {sum(len(item.get('accounts', [])) for item in self.passwords)}"
            
            self._show_import_success_dialog(message)
            self.status_label.config(text=f"成功导入 {imported_count} 个网站的数据")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("导入失败", f"JSON文件格式错误：\n{str(e)}")
            self.status_label.config(text="JSON文件格式错误")
        except Exception as e:
            messagebox.showerror("导入失败", f"导入数据时发生错误：\n{str(e)}")
            self.status_label.config(text="数据导入失败")
    
    def _validate_import_data(self, passwords_data):
        """验证导入数据的格式"""
        if not isinstance(passwords_data, list):
            messagebox.showerror("导入失败", "密码数据必须是列表格式")
            return False
        
        for i, item in enumerate(passwords_data):
            if not isinstance(item, dict):
                messagebox.showerror("导入失败", f"第 {i+1} 项数据格式不正确：必须是对象")
                return False
            
            if 'website' not in item:
                messagebox.showerror("导入失败", f"第 {i+1} 项缺少 'website' 字段")
                return False
            
            if 'accounts' not in item:
                messagebox.showerror("导入失败", f"第 {i+1} 项缺少 'accounts' 字段")
                return False
            
            if not isinstance(item['accounts'], list):
                messagebox.showerror("导入失败", f"第 {i+1} 项的 'accounts' 必须是列表")
                return False
            
            # 验证账户数据
            for j, account in enumerate(item['accounts']):
                if not isinstance(account, dict):
                    messagebox.showerror("导入失败", f"第 {i+1} 项的第 {j+1} 个账户格式不正确")
                    return False
                
                required_fields = ['username', 'password']
                for field in required_fields:
                    if field not in account:
                        messagebox.showerror("导入失败", f"第 {i+1} 项的第 {j+1} 个账户缺少 '{field}' 字段")
                        return False
        
        return True
    
    def _show_import_options_dialog(self, total_websites, total_accounts, export_time):
        """显示导入选项对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("导入选项")
        dialog.geometry("550x520")
        dialog.configure(bg=self.colors['background'])
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = None
        
        # 标题
        title_label = tk.Label(dialog, text="📥 导入数据选项", 
                              font=("SF Pro Text", 16, "bold"),
                              bg=self.colors['background'], 
                              fg=self.colors['text'])
        title_label.pack(pady=20)
        
        # 文件信息框
        info_frame = tk.Frame(dialog, bg=self.colors['surface'], relief='raised', bd=1)
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(info_frame, text="📊 导入文件信息", 
                font=("SF Pro Text", 12, "bold"),
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(pady=(15, 5))
        
        tk.Label(info_frame, text=f"网站数量: {total_websites}", 
                font=("SF Pro Text", 11),
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(pady=2)
        
        tk.Label(info_frame, text=f"账户总数: {total_accounts}", 
                font=("SF Pro Text", 11),
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(pady=2)
        
        tk.Label(info_frame, text=f"导出时间: {export_time}", 
                font=("SF Pro Text", 11),
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(pady=(2, 15))
        
        # 选项框
        options_frame = tk.Frame(dialog, bg=self.colors['background'])
        options_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(options_frame, text="🔧 导入选项", 
                font=("SF Pro Text", 12, "bold"),
                bg=self.colors['background'], 
                fg=self.colors['text']).pack(anchor=tk.W, pady=(0, 10))
        
        # 单选按钮变量
        import_mode = tk.StringVar(value="merge")
        
        # 合并选项
        merge_frame = tk.Frame(options_frame, bg=self.colors['background'])
        merge_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(merge_frame, text="🔄 合并数据", 
                      variable=import_mode, value="merge",
                      font=("SF Pro Text", 11, "bold"),
                      bg=self.colors['background'], 
                      fg=self.colors['text'],
                      selectcolor=self.colors['surface']).pack(anchor=tk.W)
        
        tk.Label(merge_frame, text="   将导入的数据与现有数据合并（推荐）", 
                font=("SF Pro Text", 10),
                bg=self.colors['background'], 
                fg=self.colors['secondary']).pack(anchor=tk.W)
        
        # 替换选项
        replace_frame = tk.Frame(options_frame, bg=self.colors['background'])
        replace_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(replace_frame, text="⚠️ 替换所有数据", 
                      variable=import_mode, value="replace",
                      font=("SF Pro Text", 11, "bold"),
                      bg=self.colors['background'], 
                      fg=self.colors['danger'],
                      selectcolor=self.colors['surface']).pack(anchor=tk.W)
        
        tk.Label(replace_frame, text="   删除所有现有数据，用导入数据替换", 
                font=("SF Pro Text", 10),
                bg=self.colors['background'], 
                fg=self.colors['danger']).pack(anchor=tk.W)
        
        # 按钮框
        button_frame = tk.Frame(dialog, bg=self.colors['background'])
        button_frame.pack(pady=20, fill=tk.X)
        
        def on_import():
            nonlocal result
            result = import_mode.get()
            dialog.destroy()
        
        def on_cancel():
            nonlocal result
            result = None
            dialog.destroy()
        
        # 取消按钮
        cancel_btn = tk.Button(button_frame, text="取消", 
                              bg=self.colors['surface'], 
                              fg=self.colors['text'],
                              font=("SF Pro Text", 11, 'bold'),
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 20), ipadx=20, ipady=8)
        
        # 导入按钮
        import_btn = tk.Button(button_frame, text="开始导入", 
                              bg=self.colors['primary'], 
                              fg='#262730',  # 深灰色文本
                              font=("SF Pro Text", 11, 'bold'),
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=on_import)
        import_btn.pack(side=tk.RIGHT, ipadx=20, ipady=8)
        
        dialog.wait_window()
        return result
    
    def _show_import_success_dialog(self, message):
        """显示导入成功对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("导入成功")
        dialog.geometry("500x300")
        dialog.configure(bg=self.colors['background'])
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 标题
        title_label = tk.Label(dialog, text="✅ 导入成功", 
                              font=("SF Pro Text", 16, "bold"),
                              bg=self.colors['background'], 
                              fg=self.colors['success'])
        title_label.pack(pady=20)
        
        # 消息内容
        message_frame = tk.Frame(dialog, bg=self.colors['surface'], relief='raised', bd=1)
        message_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        message_label = tk.Label(message_frame, text=message, 
                               font=("SF Pro Text", 11),
                               bg=self.colors['surface'], 
                               fg=self.colors['text'],
                               justify=tk.LEFT,
                               wraplength=450)
        message_label.pack(pady=20, padx=20, expand=True)
        
        # 确定按钮
        button_frame = tk.Frame(dialog, bg=self.colors['background'])
        button_frame.pack(pady=20)
        
        ok_btn = tk.Button(button_frame, text="确定", 
                          bg=self.colors['success'], 
                          fg=self.colors['white'],
                          font=("SF Pro Text", 11, 'bold'),
                          relief='flat', bd=1,
                          cursor='hand2',
                          command=dialog.destroy)
        ok_btn.pack(ipadx=30, ipady=8)
        
        dialog.wait_window()
    
    def _perform_import(self, import_passwords, import_mode):
        """执行数据导入"""
        imported_count = 0
        merged_count = 0
        
        if import_mode == "replace":
            # 替换所有数据
            self.passwords = import_passwords.copy()
            imported_count = len(self.passwords)
        else:
            # 合并数据
            for import_item in import_passwords:
                import_website = import_item['website']
                import_accounts = import_item['accounts']
                
                # 查找现有网站
                existing_item = None
                for existing in self.passwords:
                    if existing['website'] == import_website:
                        existing_item = existing
                        break
                
                if existing_item:
                    # 合并账户
                    merged_count += 1
                    existing_accounts = existing_item['accounts']
                    
                    for import_account in import_accounts:
                        # 检查是否已存在相同用户名的账户
                        account_exists = False
                        for existing_account in existing_accounts:
                            if existing_account['username'] == import_account['username']:
                                # 更新密码和其他信息
                                existing_account.update(import_account)
                                account_exists = True
                                break
                        
                        if not account_exists:
                            # 添加新账户，确保有创建时间
                            new_account = import_account.copy()
                            if 'created_time' not in new_account:
                                new_account['created_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            existing_accounts.append(new_account)
                else:
                    # 添加新网站
                    imported_count += 1
                    new_item = import_item.copy()
                    
                    # 确保所有账户都有创建时间
                    for account in new_item['accounts']:
                        if 'created_time' not in account:
                            account['created_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    self.passwords.append(new_item)
        
        return imported_count, merged_count
    
    def copy_password(self):
        """复制密码"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            display_website = str(item['values'][0])
            
            # 处理缩进的网站名
            website = display_website.replace("  └─ ", "").strip()
            
            username = str(item['values'][1])
            
            for pwd in self.passwords:
                if str(pwd.get('website', '')) == website:
                    accounts = pwd.get('accounts', [])
                    # 找到匹配的账户
                    for account in accounts:
                        if str(account.get('username', '')) == username:
                            password = account.get('password', '')
                            
                            self.root.clipboard_clear()
                            self.root.clipboard_append(password)
                            self.status_label.config(text="密码已复制到剪贴板")
                            return
                    break
    
    def copy_username(self):
        """复制账号"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            website = str(item['values'][0])
            
            for pwd in self.passwords:
                if pwd['website'] == website:
                    accounts = pwd.get('accounts', [])
                    if accounts:
                        # 复制第一个账户的用户名
                        first_account = accounts[0]
                        username = first_account.get('username', '')
                        self.root.clipboard_clear()
                        self.root.clipboard_append(username)
                        self.status_label.config(text="账号已复制到剪贴板")
                    break
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

class VaultSetupDialog:
    """保险库设置对话框"""
    def __init__(self, parent, colors):
        self.result = None
        self.colors = colors
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置主密码")
        self.dialog.geometry("520x450")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=colors['light'])
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """创建对话框组件"""
        main_frame = tk.Frame(self.dialog, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 标题
        title_label = tk.Label(main_frame, text="🔐 设置主密码", 
                              font=("SF Pro Display", 18, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['light'])
        title_label.pack(pady=(0, 10))
        
        desc_label = tk.Label(main_frame, text="请设置一个强密码来保护您的密码库", 
                             font=("SF Pro Text", 11),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['light'])
        desc_label.pack(pady=(0, 30))
        
        # 密码输入框
        password_frame = tk.Frame(main_frame, bg=self.colors['light'])
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(password_frame, text="主密码:", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.password_entry = tk.Entry(password_frame, show="*", 
                                      font=("SF Pro Text", 12),
                                      relief='flat', bd=1,
                                      bg=self.colors['white'])
        self.password_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 确认密码输入框
        confirm_frame = tk.Frame(main_frame, bg=self.colors['light'])
        confirm_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(confirm_frame, text="确认密码:", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.confirm_entry = tk.Entry(confirm_frame, show="*", 
                                     font=("SF Pro Text", 12),
                                     relief='flat', bd=1,
                                     bg=self.colors['white'])
        self.confirm_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 按钮
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(button_frame, text="取消", 
                              font=("SF Pro Text", 12, 'bold'),
                              bg=self.colors['surface'],
                              fg=self.colors['text'],
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0), ipadx=20, ipady=6)
        
        ok_btn = tk.Button(button_frame, text="确定", 
                          font=("SF Pro Text", 12, "bold"),
                          bg=self.colors['surface'],
                          fg=self.colors['text'],
                          relief='flat', bd=1,
                          cursor='hand2',
                          command=self.ok)
        ok_btn.pack(side=tk.RIGHT, ipadx=20, ipady=6)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.password_entry.focus()
    
    def ok(self):
        """确定按钮"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showerror("错误", "请输入主密码")
            return
        
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        if len(password) < 6:
            messagebox.showerror("错误", "密码长度至少6位")
            return
        
        self.result = password
        self.dialog.destroy()
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()

class VaultUnlockDialog:
    """保险库解锁对话框"""
    def __init__(self, parent, colors):
        self.result = None
        self.colors = colors
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("解锁保险库")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=colors['light'])
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """创建对话框组件"""
        main_frame = tk.Frame(self.dialog, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 标题
        title_label = tk.Label(main_frame, text="🔓 解锁保险库", 
                              font=("SF Pro Display", 18, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['light'])
        title_label.pack(pady=(0, 20))
        
        # 密码输入框
        password_frame = tk.Frame(main_frame, bg=self.colors['light'])
        password_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(password_frame, text="主密码:", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.password_entry = tk.Entry(password_frame, show="*", 
                                      font=("SF Pro Text", 12),
                                      relief='flat', bd=1,
                                      bg=self.colors['white'])
        self.password_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 按钮
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(button_frame, text="取消", 
                              font=("SF Pro Text", 12, 'bold'),
                              bg=self.colors['surface'],
                              fg=self.colors['text'],
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0), ipadx=20, ipady=6)
        
        ok_btn = tk.Button(button_frame, text="解锁", 
                          font=("SF Pro Text", 12, "bold"),
                          bg=self.colors['primary'],
                          fg=self.colors['white'],
                          relief='flat', bd=0,
                          cursor='hand2',
                          command=self.ok)
        ok_btn.pack(side=tk.RIGHT, ipadx=20, ipady=6)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.password_entry.focus()
    
    def ok(self):
        """确定按钮"""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("错误", "请输入主密码")
            return
        
        self.result = password
        self.dialog.destroy()
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()

class PasswordDialog:
    """密码编辑对话框"""
    def __init__(self, parent, colors, title, password_data=None):
        self.result = None
        self.colors = colors
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("520x600")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=colors['light'])
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets(password_data)
        self.dialog.wait_window()
    
    def create_widgets(self, password_data):
        """创建对话框组件"""
        main_frame = tk.Frame(self.dialog, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 标题
        title_label = tk.Label(main_frame, text="📝 密码信息", 
                              font=("SF Pro Display", 16, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['light'])
        title_label.pack(pady=(0, 20))
        
        # 网站/应用
        website_frame = tk.Frame(main_frame, bg=self.colors['light'])
        website_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(website_frame, text="网站/应用:", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.website_entry = tk.Entry(website_frame, 
                                     font=("SF Pro Text", 12),
                                     relief='flat', bd=1,
                                     bg=self.colors['white'])
        self.website_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 账号
        username_frame = tk.Frame(main_frame, bg=self.colors['light'])
        username_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(username_frame, text="账号:", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.username_entry = tk.Entry(username_frame, 
                                      font=("SF Pro Text", 12),
                                      relief='flat', bd=1,
                                      bg=self.colors['white'])
        self.username_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 密码
        password_frame = tk.Frame(main_frame, bg=self.colors['light'])
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(password_frame, text="密码:", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.password_entry = tk.Entry(password_frame, show="*", 
                                      font=("SF Pro Text", 12),
                                      relief='flat', bd=1,
                                      bg=self.colors['white'])
        self.password_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 显示/隐藏密码按钮
        toggle_btn = tk.Button(password_frame, text="👁️ 显示密码", 
                              font=("SF Pro Text", 10, 'bold'),
                              bg=self.colors['surface'],
                              fg=self.colors['text'],
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=self.toggle_password_visibility)
        toggle_btn.pack(anchor=tk.W, pady=(5, 0), ipadx=12, ipady=6)
        
        # 描述
        desc_frame = tk.Frame(main_frame, bg=self.colors['light'])
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(desc_frame, text="描述 (可选):", 
                font=("SF Pro Text", 12),
                fg=self.colors['text_primary'],
                bg=self.colors['light']).pack(anchor=tk.W)
        
        self.desc_entry = tk.Entry(desc_frame, 
                                  font=("SF Pro Text", 12),
                                  relief='flat', bd=1,
                                  bg=self.colors['white'])
        self.desc_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # 按钮
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="取消", 
                              font=("SF Pro Text", 12, 'bold'),
                              bg=self.colors['surface'],
                              fg=self.colors['text'],
                              relief='flat', bd=1,
                              cursor='hand2',
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0), ipadx=20, ipady=6)
        
        ok_btn = tk.Button(button_frame, text="确定", 
                          font=("SF Pro Text", 12, "bold"),
                          bg=self.colors['surface'],
                          fg=self.colors['text'],
                          relief='flat', bd=1,
                          cursor='hand2',
                          command=self.ok)
        ok_btn.pack(side=tk.RIGHT, ipadx=20, ipady=6)
        
        # 如果提供了现有数据，填充表单
        if password_data:
            self.website_entry.insert(0, password_data.get('website', ''))
            self.username_entry.insert(0, password_data.get('username', ''))
            self.password_entry.insert(0, password_data.get('password', ''))
            self.desc_entry.insert(0, password_data.get('description', ''))
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.website_entry.focus()
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def ok(self):
        """确定按钮"""
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if not website:
            messagebox.showerror("错误", "请输入网站/应用名称")
            return
        
        if not username:
            messagebox.showerror("错误", "请输入账号")
            return
        
        if not password:
            messagebox.showerror("错误", "请输入密码")
            return
        
        self.result = {
            'website': website,
            'username': username,
            'password': password,
            'description': description
        }
        self.dialog.destroy()
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()

class AccountManagerDialog:
    """账户管理对话框"""
    def __init__(self, parent, colors, website, accounts):
        self.result = None
        self.colors = colors
        self.website = website
        self.accounts = accounts.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"管理 {website} 的账户")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=colors['light'])
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """创建对话框组件"""
        main_frame = tk.Frame(self.dialog, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 标题
        title_label = tk.Label(main_frame, text=f"📱 {self.website} 账户管理", 
                              font=("SF Pro Display", 16, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['light'])
        title_label.pack(pady=(0, 20))
        
        # 账户列表
        list_frame = tk.Frame(main_frame, bg=self.colors['white'], relief='flat', bd=0)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建Treeview显示账户
        columns = ('账号', '密码', '描述', '创建时间')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.tree.heading('账号', text='账号')
        self.tree.heading('密码', text='密码')
        self.tree.heading('描述', text='描述')
        self.tree.heading('创建时间', text='创建时间')
        
        self.tree.column('账号', width=150)
        self.tree.column('密码', width=120)
        self.tree.column('描述', width=150)
        self.tree.column('创建时间', width=120)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 更新账户列表
        self.update_account_list()
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(fill=tk.X)
        
        # 左侧按钮
        left_buttons = tk.Frame(button_frame, bg=self.colors['light'])
        left_buttons.pack(side=tk.LEFT)
        
        add_btn = tk.Button(left_buttons, text="➕ 添加账户", 
                           font=("SF Pro Text", 11, 'bold'),
                           bg=self.colors['surface'],
                           fg=self.colors['text'],
                           relief='flat', bd=1,
                           cursor='hand2',
                           command=self.add_account)
        add_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=8)
        
        edit_btn = tk.Button(left_buttons, text="✏️ 编辑", 
                            font=("SF Pro Text", 11, 'bold'),
                            bg=self.colors['surface'],
                            fg=self.colors['text'],
                            relief='flat', bd=1,
                            cursor='hand2',
                            command=self.edit_account)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=15, ipady=8)
        
        delete_btn = tk.Button(left_buttons, text="🗑️ 删除", 
                              font=("SF Pro Text", 11, 'bold'),
                              bg=self.colors['danger'],
                              fg=self.colors['white'],
                              relief='flat', bd=0,
                              cursor='hand2',
                              command=self.delete_account)
        delete_btn.pack(side=tk.LEFT, ipadx=15, ipady=8)
        
        # 右侧按钮
        right_buttons = tk.Frame(button_frame, bg=self.colors['light'])
        right_buttons.pack(side=tk.RIGHT)
        
        cancel_btn = tk.Button(right_buttons, text="取消", 
                              font=("SF Pro Text", 11, 'bold'),
                              bg='#6C757D',
                              fg=self.colors['white'],
                              relief='flat', bd=0,
                              cursor='hand2',
                              command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=(10, 0), ipadx=25, ipady=8)
        
        ok_btn = tk.Button(right_buttons, text="确定", 
                          font=("SF Pro Text", 11, "bold"),
                          bg=self.colors['surface'],
                          fg=self.colors['text'],
                          relief='flat', bd=1,
                          cursor='hand2',
                          command=self.ok)
        ok_btn.pack(side=tk.LEFT, ipadx=25, ipady=8)
    
    def update_account_list(self):
        """更新账户列表"""
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加账户项目
        for account in self.accounts:
            username = account.get('username', '')
            password = '•' * len(account.get('password', ''))
            description = account.get('description', '')
            created_time = account.get('created_time', '')
            
            self.tree.insert('', 'end', values=(username, password, description, created_time))
    
    def add_account(self):
        """添加账户"""
        dialog = PasswordDialog(self.dialog, self.colors, "添加账户")
        if dialog.result:
            new_account = {
                'username': dialog.result['username'],
                'password': dialog.result['password'],
                'description': dialog.result['description'],
                'created_time': time.strftime('%Y-%m-%d %H:%M')
            }
            self.accounts.append(new_account)
            self.update_account_list()
    
    def edit_account(self):
        """编辑账户"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的账户")
            return
        
        item = self.tree.item(selection[0])
        username = str(item['values'][0])
        
        # 找到对应的账户
        account = None
        for acc in self.accounts:
            if acc.get('username') == username:
                account = acc
                break
        
        if account:
            dialog = PasswordDialog(self.dialog, self.colors, "编辑账户", account)
            if dialog.result:
                account.update(dialog.result)
                account['modified_time'] = time.strftime('%Y-%m-%d %H:%M')
                self.update_account_list()
    
    def delete_account(self):
        """删除账户"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的账户")
            return
        
        item = self.tree.item(selection[0])
        username = str(item['values'][0])
        
        if messagebox.askyesno("确认删除", f"确定要删除账户 '{username}' 吗？"):
            self.accounts = [acc for acc in self.accounts if acc.get('username') != username]
            self.update_account_list()
    
    def ok(self):
        """确定按钮"""
        self.result = self.accounts
        self.dialog.destroy()
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()

class AccountDeleteDialog:
    """账户删除选择对话框"""
    def __init__(self, parent, colors, website, accounts):
        self.result = None
        self.colors = colors
        self.website = website
        self.accounts = accounts.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"选择要删除的账户 - {website}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=colors['light'])
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """创建对话框组件"""
        main_frame = tk.Frame(self.dialog, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 标题
        title_label = tk.Label(main_frame, text=f"🗑️ 选择要删除的账户", 
                              font=("SF Pro Display", 16, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['light'])
        title_label.pack(pady=(0, 10))
        
        desc_label = tk.Label(main_frame, text=f"网站/应用: {self.website}", 
                             font=("SF Pro Text", 12),
                             fg=self.colors['text_secondary'],
                             bg=self.colors['light'])
        desc_label.pack(pady=(0, 20))
        
        # 账户列表
        list_frame = tk.Frame(main_frame, bg=self.colors['white'], relief='flat', bd=0)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建Checkbox列表
        self.checkboxes = []
        for i, account in enumerate(self.accounts):
            var = tk.BooleanVar()
            username = account.get('username', '')
            description = account.get('description', '')
            
            checkbox_frame = tk.Frame(list_frame, bg=self.colors['white'])
            checkbox_frame.pack(fill=tk.X, padx=10, pady=5)
            
            cb = tk.Checkbutton(checkbox_frame, 
                               text=f"{username} {f'({description})' if description else ''}",
                               variable=var,
                               font=("SF Pro Text", 11),
                               bg=self.colors['white'],
                               fg=self.colors['text_primary'])
            cb.pack(anchor=tk.W)
            
            self.checkboxes.append((var, account))
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(button_frame, text="取消", 
                              font=("SF Pro Text", 11, 'bold'),
                              bg=self.colors['surface'],
                              fg=self.colors['text'],
                              relief='flat', bd=1,
                              command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0), ipadx=20, ipady=6)
        
        ok_btn = tk.Button(button_frame, text="删除选中", 
                          font=("SF Pro Text", 11, "bold"),
                          bg=self.colors['danger'],
                          fg=self.colors['white'],
                          relief='flat', bd=0,
                          cursor='hand2',
                          command=self.ok)
        ok_btn.pack(side=tk.RIGHT, ipadx=20, ipady=6)
    
    def ok(self):
        """确定按钮"""
        # 获取未选中的账户（保留的账户）
        remaining_accounts = []
        for var, account in self.checkboxes:
            if not var.get():  # 如果未选中，则保留
                remaining_accounts.append(account)
        
        self.result = remaining_accounts
        self.dialog.destroy()
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()

if __name__ == "__main__":
    app = ModernPasswordVault()
    app.run()
