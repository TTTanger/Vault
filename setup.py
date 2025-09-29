"""
py2app setup script for Password Vault
"""

from setuptools import setup

APP = ['main_modern.py']
DATA_FILES = [('', ['touchid_test.m', 'touchid_test'])]
OPTIONS = {
    'argv_emulation': False,
    'includes': ['cryptography', 'cryptography.fernet', 'cryptography.hazmat', 'cffi', '_cffi_backend'],
    'packages': ['cryptography', 'cffi'],
    'iconfile': 'vault_icon.icns',
    'plist': {
        'CFBundleName': '密码保险库',
        'CFBundleDisplayName': '密码保险库',
        'CFBundleIdentifier': 'com.passwordvault.app',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'NSPrincipalClass': 'NSApplication',
        'LSBackgroundOnly': False,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
