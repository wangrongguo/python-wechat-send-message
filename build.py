import os
import shutil
import sys
import PyInstaller.__main__

def build_exe():
    """打包程序为可执行文件"""
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller 参数
    params = [
        'main.py',                    # 主程序文件
        '--name=微信消息助手',        # 可执行文件名称
        '--windowed',                 # 无控制台窗口
        '--icon=images/down-arrow.png', # 程序图标
        '--add-data=config;config',   # 添加配置文件夹
        '--add-data=images;images',   # 添加图片文件夹
        '--hidden-import=win32timezone',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32gui',
        '--hidden-import=keyboard',
        '--hidden-import=requests',
        '--hidden-import=bs4',
        '--collect-all=PyQt5',
        '--noconfirm',
        '--clean',
        '--onefile',                  # 打包为单个文件
    ]
    
    try:
        # 执行打包
        PyInstaller.__main__.run(params)
        print("开始打包...")
        
        # 创建dist/config目录
        dist_config_dir = os.path.join('dist', 'config')
        os.makedirs(dist_config_dir, exist_ok=True)
        
        # 复制配置文件
        shutil.copy2('config/friends.json', dist_config_dir)
        shutil.copy2('config/encouragements.txt', dist_config_dir)
        
        # 复制images文件夹
        dist_images_dir = os.path.join('dist', 'images')
        if os.path.exists('images'):
            shutil.copytree('images', dist_images_dir, dirs_exist_ok=True)
            
        print("打包完成！")
            
    except Exception as e:
        print(f"打包过程中出现错误: {str(e)}")

if __name__ == "__main__":
    build_exe() 