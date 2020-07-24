import sys
from cx_Freeze import setup, Executable

base = None
# 判断Windows系统
if sys.platform == 'win32':
    base = 'Win32GUI'

packages = []

for dbmodule in ['win32gui', 'win32api', 'win32con', 'cx_Freeze']:

    try:
        __import__(dbmodule)

    except ImportError:
        pass

    else:
        packages.append(dbmodule)

options = {
    'build_exe':
        {
        "excludes":[],
        "includes":[],
        "include_files":[],
        "packages":packages
        }}

executables = [
    Executable(
        # 工程的 入口
        'GUI.py'
        , base=base
        # 生成 的文件 名字
        , targetName='环境科研小助手.exe'
        # 生成的EXE的图标
        # , icon = "test_32.ico" #图标, 32*32px
    )
]

setup(
    # 产品名称
    name='环境科研小助手',
    # 版本号
    version='0.1',
    # 产品说明
    description='环境科研小助手',
    options=options,
    executables=executables
)