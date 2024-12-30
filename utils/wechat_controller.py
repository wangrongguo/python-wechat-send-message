import os
import time
import keyboard
import win32gui
import win32con
import win32api
import json
import win32clipboard

class WeChatController:
    def __init__(self, wechat_path="D:\\Program Files\\Tencent\\WeChat\\WeChat.exe"):
        """
        初始化微信控制器
        Args:
            wechat_path: 微信安装路径
        """
        self.wechat_path = wechat_path
        self.window_handle = None
        self.friends_file = os.path.join('config', 'friends.json')
        self._ensure_config_dir()
        self.friends = self._load_friends()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        os.makedirs('config', exist_ok=True)

    def _load_friends(self):
        """从文件加载好友列表"""
        try:
            with open(self.friends_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_friends(self):
        """保存好友列表到文件"""
        with open(self.friends_file, 'w', encoding='utf-8') as f:
            json.dump(self.friends, f, ensure_ascii=False, indent=2)

    def get_friends(self):
        """获取好友列表"""
        return self.friends

    def add_friend(self, friend_name):
        """
        添加好友到列表
        Args:
            friend_name: 好友名称
        """
        if friend_name not in self.friends:
            self.friends.append(friend_name)
            self._save_friends()

    def delete_friend(self, friend_name):
        """
        从列表删除好友
        Args:
            friend_name: 好友名称
        """
        if friend_name in self.friends:
            self.friends.remove(friend_name)
            self._save_friends()

    def start_wechat(self):
        """启动微信并等待窗口出现"""
        if not self.is_wechat_running():
            os.startfile(self.wechat_path)
            time.sleep(2)
        self.window_handle = win32gui.FindWindow("WeChatMainWndForPC", None)
        self.bring_to_front()

    def is_wechat_running(self):
        """检查微信是否在运行"""
        return win32gui.FindWindow("WeChatMainWndForPC", None) != 0

    def bring_to_front(self):
        """将微信窗口置于前台"""
        if self.window_handle:
            win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.window_handle)
            time.sleep(1)

    def search_friend(self, friend_name):
        """
        搜索好友
        Args:
            friend_name: 好友名称
        """
        self.bring_to_front()
        keyboard.press_and_release('ctrl+f')
        time.sleep(0.5)
        keyboard.write(friend_name)
        time.sleep(0.5)
        keyboard.press_and_release('enter')
        time.sleep(1)

    def send_message(self, message):
        """
        发送消息
        Args:
            message: 要发送的消息内容
        """
        # 将整个消息复制到剪贴板
        self.copy_to_clipboard(message)
        # 使用 Ctrl+V 粘贴整个消息
        keyboard.press_and_release('ctrl+v')
        time.sleep(0.5)
        # 发送消息
        keyboard.press_and_release('enter')
        time.sleep(0.5)

    def copy_to_clipboard(self, text):
        """
        将文本复制到剪贴板
        Args:
            text: 要复制的文本
        """
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

    def send_to_friend(self, friend_name, message, interval=2):
        """
        向指定好友发送消息
        Args:
            friend_name: 好友名称
            message: 消息内容
            interval: 发送间隔（秒）
        Returns:
            bool: 发送是否成功
        """
        try:
            self.start_wechat()
            time.sleep(interval)
            self.search_friend(friend_name)
            time.sleep(interval)
            self.send_message(message)
            return True
        except Exception as e:
            print(f"发送消息失败: {str(e)}")
            return False

    def close_chat(self):
        """关闭当前聊天窗口"""
        keyboard.press_and_release('ctrl+w')
        time.sleep(0.5)