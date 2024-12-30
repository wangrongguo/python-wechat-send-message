from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLineEdit, QTextEdit, QLabel, QSpinBox,
                           QComboBox, QMessageBox, QListWidget, QCheckBox,
                           QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QTimer
from utils.wechat_controller import WeChatController
from utils.message_handler import MessageHandler
import json
import time
import requests
from bs4 import BeautifulSoup
import re
import os
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口图标
        self.setWindowIcon(QIcon('D:/rongo/pro/demo012/images/down-arrow.png'))  # 设置窗口图标
        
        self.wechat = WeChatController()
        self.message_handler = MessageHandler()
        self.current_friend_index = 0
        self.is_loop_enabled = False
        self.weather_api_key = "a09a9fa8494440839cdc4c824b6e002d"  # 和风天气API密钥
        self.location = None  # 初始化为None
        self.city_location_cache = {}  # 添加城市位置缓存
        self.huangli_cache = {}
        self.rainbow_cache = None  # 移除彩虹屁缓存的初始化，因为不再需要缓存
        self.encouragements = self.load_encouragements()  # 从文件加载励志文本
        self.current_loop = 0  # 添加当前循环次数计数
        self.total_loops = 0  # 添加总循环次数
        self.current_friend_name = ""  # 添加当前发送的好友名称
        
        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_next_message)  # 连接定时器信号到发送方法
        
        # 设置所有消息框的默认按钮文本
        QMessageBox.Ok = "确认"
        QMessageBox.Yes = "确认"
        QMessageBox.No = "取消"
        QMessageBox.Cancel = "取消"

        # 设置消息框按钮文本
        self.yes_button = QPushButton('确认')
        self.no_button = QPushButton('取消')
        self.ok_button = QPushButton('确认')

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 设置应用程序样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5ECD7;
            }
            QWidget {
                background-color: #F5ECD7;
                color: #353535;
            }
            QPushButton {
                background-color: #8FBF9F;
                border: none;
                padding: 8px 15px;
                color: #353535;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #68a67d;
            }
            QPushButton:pressed {
                background-color: #24613b;
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: #ebe2cd;
                border: 1px solid #c2baa6;
                padding: 5px;
                border-radius: 4px;
                color: #353535;
            }
            QListWidget {
                background-color: #ebe2cd;
                border: 1px solid #c2baa6;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #8FBF9F;
                color: #353535;
            }
            QLabel {
                color: #5f5f5f;
            }
            QComboBox {
                background-color: #ebe2cd;
                border: 1px solid #c2baa6;
                padding: 5px;
                border-radius: 4px;
                color: #353535;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(images/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            QSpinBox {
                background-color: #ebe2cd;
                border: 1px solid #c2baa6;
                padding: 5px;
                border-radius: 4px;
            }
            QCheckBox {
                color: #5f5f5f;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #c2baa6;
                background-color: #ebe2cd;
            }
            QCheckBox::indicator:checked {
                background-color: #8FBF9F;
                border: 1px solid #68a67d;
            }
            .status-label {
                color: #F18F01;
                font-weight: bold;
            }
        """)

        self.setWindowTitle('微信消息助手')
        self.setGeometry(200, 100, 1200, 800)  # 保持窗口大小

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(15)  # 保持间距
        
        # 左侧面板 - 好友列表
        left_panel = QWidget()
        left_panel.setObjectName("left_panel")
        left_panel.setFixedWidth(int(self.width() * 0.3))  # 修改为总宽度的3/10
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        # 好友输入和添加区域
        friend_input_layout = QHBoxLayout()
        self.friend_input = QLineEdit()
        self.friend_input.setPlaceholderText('输入好友名称...')
        add_friend_btn = QPushButton('添加好友')
        friend_input_layout.addWidget(self.friend_input)
        friend_input_layout.addWidget(add_friend_btn)
        left_layout.addLayout(friend_input_layout)

        # 好友列表
        self.friend_list = QListWidget()
        self.friend_list.setSelectionMode(QListWidget.MultiSelection)  # 允许多选
        left_layout.addWidget(QLabel('好友列表 (可多选):'))
        left_layout.addWidget(self.friend_list)
        
        # 好友列表控制按钮
        friend_control_layout = QHBoxLayout()
        delete_friend_btn = QPushButton('删除选中')
        select_all_btn = QPushButton('全选')
        clear_selection_btn = QPushButton('取消选择')
        import_friends_btn = QPushButton('导入好友')
        friend_control_layout.addWidget(delete_friend_btn)
        friend_control_layout.addWidget(select_all_btn)
        friend_control_layout.addWidget(clear_selection_btn)
        friend_control_layout.addWidget(import_friends_btn)
        left_layout.addLayout(friend_control_layout)

        layout.addWidget(left_panel, 3)  # 修改为占3份

        # 右侧面板 - 消息编辑和控制
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        # 消息模板选择
        template_layout = QHBoxLayout()
        template_label = QLabel('消息模板:')
        self.template_combo = QComboBox()
        self.update_template_list()
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        right_layout.addLayout(template_layout)

        # 消息编辑区域
        message_layout = QVBoxLayout()
        
        # 创建网格布局的变量提示区域
        variables_info = QTextEdit()
        variables_info.setReadOnly(True)
        variables_info.setMaximumHeight(120)  # 减小高度
        variables_info.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用垂直滚动条
        variables_info.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        variables_info.setStyleSheet("""
            QTextEdit {
                background-color: #F5ECD7;
                border: none;
                color: #5f5f5f;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        
        # 将变量信息按三列排列
        variables = [
            ("{nickname}", "好友名称"),
            ("{date}", "当前日期"),
            ("{time}", "当前时间(24小时制)"),
            ("{weekday}", "星期几"),
            ("{lunar_date}", "农历日期"),
            ("{city}", "城市名称"),
            ("{weather}", "天气状况"),
            ("{temp_low}/{temp_high}", "最低/最高温度"),
            ("{wind}", "风向和风力"),
            ("{constellation}", "星座"),
            ("{rainbow}", "彩虹屁文本"),
            ("{encouragement}", "随机鼓励文本"),
            ("{horoscope}", "运势")
        ]
        
        # 构建三列布局的文本
        variables_text = "消息内容支持以下变量：\n\n"
        for i in range(0, len(variables), 3):
            row_vars = variables[i:i+3]  # 每行取3个变量
            row_text = "    ".join(f"{var} - {desc}" for var, desc in row_vars)
            variables_text += f"{row_text}\n"
        
        variables_info.setText(variables_text)
        
        message_layout.addWidget(variables_info)
        self.message_edit = QTextEdit()
        message_layout.addWidget(self.message_edit)
        right_layout.addLayout(message_layout)

        # 发送设置区域
        settings_layout = QVBoxLayout()
        
        # 循环发送设置
        loop_layout = QHBoxLayout()
        self.loop_checkbox = QCheckBox('循环发送')
        self.loop_count_spin = QSpinBox()
        self.loop_count_spin.setRange(1, 999)
        self.loop_count_spin.setValue(1)
        self.loop_count_spin.setEnabled(False)
        loop_layout.addWidget(self.loop_checkbox)
        loop_layout.addWidget(QLabel('循环次数:'))
        loop_layout.addWidget(self.loop_count_spin)
        settings_layout.addLayout(loop_layout)

        # 发送间隔设置
        interval_layout = QHBoxLayout()
        interval_label = QLabel('发送间隔(秒):')
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(2)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spin)
        
        # 好友间隔设置
        friend_interval_label = QLabel('好友间隔(秒):')
        self.friend_interval_spin = QSpinBox()
        self.friend_interval_spin.setRange(1, 3600)
        self.friend_interval_spin.setValue(5)
        interval_layout.addWidget(friend_interval_label)
        interval_layout.addWidget(self.friend_interval_spin)
        
        settings_layout.addLayout(interval_layout)

        # 添加城市选择区域
        city_layout = QHBoxLayout()
        city_label = QLabel('城市:')
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText('输入城市名称')
        self.city_input.setText('北京')  # 默认城市
        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_input)
        settings_layout.addLayout(city_layout)

        # 绑定城市输入框的回车事件
        self.city_input.returnPressed.connect(self.update_city_location)
        
        right_layout.addLayout(settings_layout)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('开始发送')
        self.stop_button = QPushButton('停止发送')
        self.save_template_button = QPushButton('保存模板')
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_template_button)
        right_layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel('就绪')
        right_layout.addWidget(self.status_label)

        layout.addWidget(right_panel, 7)  # 修改为占7份

        # 定事件
        add_friend_btn.clicked.connect(self.add_friend)
        delete_friend_btn.clicked.connect(self.delete_friend)
        select_all_btn.clicked.connect(self.friend_list.selectAll)
        clear_selection_btn.clicked.connect(self.friend_list.clearSelection)
        self.start_button.clicked.connect(self.start_sending)
        self.stop_button.clicked.connect(self.stop_sending)
        self.save_template_button.clicked.connect(self.save_template)
        self.template_combo.currentTextChanged.connect(self.load_template)
        self.loop_checkbox.stateChanged.connect(self.toggle_loop_count)
        import_friends_btn.clicked.connect(self.import_friends)
        # 添加回车键绑定
        self.friend_input.returnPressed.connect(self.add_friend)

        # 初始化定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_message)
        self.stop_button.setEnabled(False)

        # 加载保存的好友列表
        self.load_friends()

        # 设置状态标签的样式类
        self.status_label.setProperty('class', 'status-label')

        # 添加窗口大小变化事件处理
        self.resizeEvent = self.on_resize

    def on_resize(self, event):
        """处理窗口大小变化事件"""
        # 更新左侧面板的宽度为总宽度的3/10
        left_panel_width = int(self.width() * 0.3)  # 修改比例
        left_panel = self.findChild(QWidget, "left_panel")
        if left_panel:
            left_panel.setFixedWidth(left_panel_width)
        super().resizeEvent(event)

    def toggle_loop_count(self, state):
        """启用/禁用循环次数输入"""
        self.loop_count_spin.setEnabled(state == Qt.Checked)
        self.is_loop_enabled = state == Qt.Checked

    def start_sending(self):
        """开始发送消息"""
        selected_items = self.friend_list.selectedItems()
        if not selected_items:
            self.show_warning('警告', '请选择要发送的好友')
            return
        
        message = self.message_edit.toPlainText()
        if not message:
            self.show_warning('警告', '请输入消息内容')
            return

        if self.show_confirm('确认', f'确定要向选中的 {len(selected_items)} 个好友发送消息吗？'):
            self.selected_friends = [item.text() for item in selected_items]
            self.current_friend_index = 0
            self.current_loop = 1
            self.total_loops = self.loop_count_spin.value() if self.is_loop_enabled else 1
            self.update_status()
            self.timer.start(self.interval_spin.value() * 1000)
            self.update_ui_state(True)

    def send_message(self):
        """发送消息给当前好友"""
        # 检查是否还有好友需要发送
        if self.current_friend_index >= len(self.selected_friends):
            self.current_friend_index = 0
            self.current_loop += 1
            
            # 检查是否完成所有循环
            if not self.is_loop_enabled or self.current_loop >= self.total_loops:
                self.stop_sending()
                total_messages = len(self.selected_friends) * self.current_loop
                completion_status = f"发送完成！共发送 {self.current_loop} 轮，总计 {total_messages} 条消息"
                self.status_label.setText(completion_status)
                self.show_info('完成', completion_status)
                return
        
        try:
            friend_name = self.selected_friends[self.current_friend_index]
            message_template = self.message_edit.toPlainText()
            
            # 替换消息模板中的变量，生成完整消息
            message = self.replace_template_variables(message_template, friend_name)
            
            # 发送完整消息
            success = self.wechat.send_to_friend(friend_name, message)
            if not success:
                self.stop_sending()
                error_msg = f'发送给 {friend_name} 失败'
                self.status_label.setText(error_msg)
                self.show_warning('错误', error_msg)
                return

            self.current_friend_index += 1
            self.update_status()
            
            # 设置下一条消息的发送间隔
            if self.current_friend_index >= len(self.selected_friends):
                # 一轮发送完成，使用循环间隔
                next_interval = self.interval_spin.value() * 1000
            else:
                # 使用好友间隔
                next_interval = self.friend_interval_spin.value() * 1000
            self.timer.setInterval(int(next_interval))
            
        except Exception as e:
            self.stop_sending()
            error_msg = f'发送消息时出错：{str(e)}'
            self.status_label.setText(error_msg)
            self.show_warning('错误', error_msg)

    def replace_template_variables(self, template, friend_name):
        """替换模板中的变量"""
        # 获取所有信息
        lunar_date = self.get_lunar_date()
        weather_info = self.get_weather_info()
        horoscope_info = self.get_horoscope()
        rainbow_text = self.get_rainbow_text()
        encouragement_text = self.get_random_encouragement()
        
        # 获取当前时间，格式化为24小时制，精确到秒
        current_time = time.strftime('%H:%M:%S')
        
        # 组装天气信息
        weather_text = (
            f"【日出日落】{weather_info.get('sunrise_sunset', '--')}\n"
            f"【月相信息】{weather_info.get('moon_phase', '--')}\n"
            f"【白天天气】{weather_info.get('weather_day', '--')}\n"
            f"【夜间天气】{weather_info.get('weather_night', '--')}\n"
            f"【温度范围】{weather_info.get('temp_low', '--')}℃ ~ {weather_info.get('temp_high', '--')}℃\n"
            f"【白天风况】{weather_info.get('wind_day', '--')}\n"
            f"【夜间风况】{weather_info.get('wind_night', '--')}\n"
            f"【相对湿度】{weather_info.get('humidity', '--')}%\n"
            f"【紫外线级别】{weather_info.get('uv_index', '--')}\n"
            f"【能见度】{weather_info.get('visibility', '--')}km\n"
            f"【气压】{weather_info.get('pressure', '--')}hPa\n"
            f"【降水量】{weather_info.get('precipitation', '--')}mm\n"
            f"【出行建议】{self.get_weather_tips(weather_info.get('weather_day', ''))}"
        )

        # 组装运势信息（不重复显示星座名称）
        horoscope_text = (
            f"【幸运颜色】{horoscope_info.get('lucky_color', '未知')}\n"
            f"【幸运数字】{horoscope_info.get('lucky_number', '未知')}\n"
            f"【综合运势】{horoscope_info.get('text', '未知')}"
        )

        # 定义变量映射
        variables = {
            '{nickname}': friend_name,
            '{date}': time.strftime('%Y-%m-%d'),
            '{time}': current_time,
            '{weekday}': ['一','二','三','四','五','六','日'][time.localtime().tm_wday],
            '{lunar_date}': lunar_date,
            '{suitable}': self.get_suitable_activities(),
            '{unsuitable}': self.get_unsuitable_activities(),
            '{city}': weather_info.get('city', '未知'),
            '{weather}': weather_text,
            '{constellation}': horoscope_info.get('name', '未知'),
            '{horoscope}': horoscope_text,
            '{love_days}': str(self.calculate_love_days('2022-01-01')),
            '{rainbow}': rainbow_text,
            '{encouragement}': encouragement_text
        }
        
        # 替换所有变量
        message = template
        for var, value in variables.items():
            message = message.replace(var, str(value))
            
        return message

    def get_lunar_date(self):
        """获取农历日期"""
        try:
            from lunar_python import Lunar, Solar
            
            # 获取当前日期
            now = time.localtime()
            solar = Solar.fromYmd(now.tm_year, now.tm_mon, now.tm_mday)
            lunar = Lunar.fromSolar(solar)
            
            # 获取农历月份和日期
            lunar_month = lunar.getMonthInChinese()
            lunar_day = lunar.getDayInChinese()
            
            # 获取节气信息
            jieqi = self.get_jieqi(solar)
            jieqi_text = f" {jieqi}" if jieqi else ""
            
            return f"农历{lunar_month}月{lunar_day}{jieqi_text}"
        except Exception as e:
            print(f"获取农历日期失败: {str(e)}")
            return "农历日期获取失败"

    def get_jieqi(self, solar):
        """获取节气信息"""
        try:
            from lunar_python import JieQi
            
            # 获取当前日期的节气
            jieqi = JieQi.fromSolar(solar)
            if jieqi:
                return f"【{jieqi.getName()}】"
            return None
        except:
            return None

    def get_weather_info(self):
        """获取天气信息"""
        try:
            city_name = self.city_input.text().strip()
            if not city_name:
                return self.get_default_weather()

            # 获取城市位置
            city_info = self.get_city_location(city_name)
            if not city_info:
                return self.get_default_weather()

            # 调用和风天气API
            url = "https://devapi.qweather.com/v7/weather/3d"
            params = {
                'location': city_info['location'],
                'key': self.weather_api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['code'] == '200' and data['daily']:
                today = data['daily'][0]  # 获取今天的天气数据
                
                # 获取日出日落时间
                sunrise_sunset = f"{today['sunrise']}-{today['sunset']}"
                
                # 获取月相信息
                moon_info = f"{today['moonPhase']} ({today['moonrise']}-{today['moonset']})"
                
                # 获取风向和风力
                day_wind = f"{today['windDirDay']}{today['windScaleDay']}级 {today['windSpeedDay']}km/h"
                night_wind = f"{today['windDirNight']}{today['windScaleNight']}级 {today['windSpeedNight']}km/h"
                
                # 组装天气信息
                return {
                    'city': city_name,
                    'weather_day': today['textDay'],
                    'weather_night': today['textNight'],
                    'temp_low': today['tempMin'],
                    'temp_high': today['tempMax'],
                    'wind_day': day_wind,
                    'wind_night': night_wind,
                    'humidity': today['humidity'],
                    'uv_index': today['uvIndex'],
                    'sunrise_sunset': sunrise_sunset,
                    'moon_phase': moon_info,
                    'visibility': today['vis'],
                    'pressure': today['pressure'],
                    'precipitation': today['precip']
                }
            else:
                return self.get_default_weather()
        except Exception as e:
            print(f"获取天气信息失败: {str(e)}")
            return self.get_default_weather()

    def get_default_weather(self):
        """获取默认天气信息"""
        return {
            'city': self.city_input.text().strip(),
            'weather_day': '获取失败',
            'weather_night': '获取失败',
            'temp_low': '--',
            'temp_high': '--',
            'wind_day': '未知',
            'wind_night': '未知',
            'humidity': '--',
            'uv_index': '--',
            'sunrise_sunset': '--',
            'moon_phase': '--',
            'visibility': '--',
            'pressure': '--',
            'precipitation': '--'
        }

    def get_weather_tips(self, weather):
        """根据天气状况生成出行提示"""
        weather_tips = {
            '晴': '天气晴朗，适合外出，注意防晒',
            '多云': '天气较好，适合外出活动',
            '阴': '天气较暗，外出请注意安全',
            '雨': '今天有雨，出门记得带伞',
            '阵雨': '阵雨来袭，出门记得带伞',
            '雪': '今天有雪，注意保暖，路面可能结冰',
            '雾': '能见度较低，出行注意安全',
            '霾': '空气质量较差，建议戴口罩'
        }
        
        # 遍历天气提示字典，找到匹配的提示
        for key, tip in weather_tips.items():
            if key in weather:
                return tip
        
        return '天气变化莫测，注意适时增减衣物'

    def get_horoscope(self):
        """获取星座运势"""
        try:
            # 这里需要集成星座运势 API
            # 示例返回格式
            return {
                'name': '处女座',
                'lucky_color': '薄荷绿',
                'lucky_number': '2',
                'text': '今天的你有机会重逢旧同学...'
            }
        except:
            return {}

    def calculate_love_days(self, start_date):
        """计算恋爱天数"""
        try:
            start = time.strptime(start_date, "%Y-%m-%d")
            start_timestamp = time.mktime(start)
            now_timestamp = time.time()
            days = int((now_timestamp - start_timestamp) / (24 * 3600))
            return days
        except:
            return 0

    def get_huangli_info(self):
        """获取黄历信息"""
        try:
            # 获取当前日期
            current_date = time.strftime('%Y-%m-%d')
            
            # 如果缓存中有今天的数据，直接返回
            if current_date in self.huangli_cache:
                return self.huangli_cache[current_date]
            
            # 构建请求URL
            url = f"https://mobile.51wnl-cq.com/huangli_tab_h5/?posId=BDSS&STIME={current_date}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找宜和忌的内容
            yi_div = soup.find('div', class_='row yi flex-left')
            ji_div = soup.find('div', class_='row ji flex-left')
            
            if yi_div and ji_div:
                # 提取文本并清理
                yi_text = yi_div.get_text(strip=True)
                ji_text = ji_div.get_text(strip=True)
                
                # 分割成列表并清理空白
                yi_list = [item.strip() for item in yi_text.split() if item.strip()]
                ji_list = [item.strip() for item in ji_text.split() if item.strip()]
                
                result = {
                    'suitable': yi_list,
                    'unsuitable': ji_list
                }
                
                # 保存到缓存
                self.huangli_cache[current_date] = result
                return result
            
            return self.get_default_huangli()
            
        except Exception as e:
            print(f"获取黄历信息失败: {str(e)}")
            return self.get_default_huangli()

    def get_default_huangli(self):
        """获取默认黄历信息"""
        # 基础黄历数据
        basic_activities = {
            'suitable': [
                "祭祀", "祈福", "求嗣", "开光", "出行",
                "解除", "教牛马", "会亲友", "入学", "纳采",
                "订盟", "冠笄", "纳婿", "裁衣", "合帐",
                "安床", "造床", "安门", "安香", "谢土",
                "入殓", "移柩", "破土", "启钻", "修坟",
                "立碑", "成服", "除服", "开生坟", "合寿木"
            ],
            'unsuitable': [
                "诉讼", "安葬", "开市", "动土", "破土",
                "伐木", "作梁", "放水", "开渠", "破屋",
                "坏垣", "补垣", "造船", "造桥", "作灶",
                "治病", "针灸", "扫舍", "施药", "乘船",
                "渡水", "开仓", "开柜", "开渠"
            ]
        }
        
        # 随机选择4-6个项目
        import random
        result = {
            'suitable': random.sample(basic_activities['suitable'], random.randint(4, 6)),
            'unsuitable': random.sample(basic_activities['unsuitable'], random.randint(3, 5))
        }
        
        return result

    def get_suitable_activities(self):
        """获取宜做的事情"""
        huangli = self.get_huangli_info()
        return '、'.join(huangli['suitable'])

    def get_unsuitable_activities(self):
        """获取忌做的事情"""
        huangli = self.get_huangli_info()
        return '、'.join(huangli['unsuitable'])

    def update_status(self):
        """更新状态显示"""
        if self.timer.isActive():
            try:
                total_friends = len(self.selected_friends)
                current_friend = self.current_friend_index
                friend_name = self.selected_friends[current_friend - 1]  # 当前刚发送的好友
                
                if current_friend < total_friends:
                    next_friend = self.selected_friends[current_friend]  # 下一个要发送的好友
                    if self.is_loop_enabled:
                        status = f"循环 {self.current_loop}/{self.total_loops} - "
                    else:
                        status = ""
                    status += f"已发送: {friend_name} → 下一个: {next_friend} ({current_friend}/{total_friends})"
                else:
                    # 一轮发送完成
                    if self.is_loop_enabled and self.current_loop < self.total_loops:
                        next_friend = self.selected_friends[0]
                        status = (f"循环 {self.current_loop}/{self.total_loops} - "
                                f"已完成一轮发送，准备开始下一轮 → 下一个: {next_friend}")
                    else:
                        status = f"正在完成最后一轮发送 ({current_friend}/{total_friends})"
                
                self.status_label.setText(status)
            except IndexError:
                self.status_label.setText("准备开始下一轮发送...")
        else:
            self.status_label.setText("就绪")

    def update_ui_state(self, is_sending):
        """更新UI状态"""
        self.start_button.setEnabled(not is_sending)
        self.stop_button.setEnabled(is_sending)
        self.friend_list.setEnabled(not is_sending)
        self.message_edit.setEnabled(not is_sending)
        self.interval_spin.setEnabled(not is_sending)
        self.loop_checkbox.setEnabled(not is_sending)
        self.loop_count_spin.setEnabled(not is_sending and self.is_loop_enabled)

    def stop_sending(self):
        """停止发送消息"""
        self.timer.stop()
        self.update_ui_state(False)
        self.status_label.setText(f"发送已停止 (循环 {self.current_loop}/{self.total_loops})")

    def update_template_list(self):
        """更新模板列表"""
        self.template_combo.clear()
        self.template_combo.addItems(self.message_handler.templates.keys())

    def load_template(self, template_name):
        """加载选中的模板"""
        if template_name:
            self.message_edit.setText(self.message_handler.get_template(template_name))

    def save_template(self):
        """保存当前消息为模板"""
        name, ok = QInputDialog.getText(self, '保存模板', '请输入模板名称:')
        if ok and name:
            self.message_handler.add_template(name, self.message_edit.toPlainText())
            self.update_template_list()
            msg = QMessageBox.information(self, '提示', 
                                        '模板保存成功！\n'
                                        '支持的变量：\n'
                                        '{nickname} - 好友名称\n'
                                        '{date} - 当前日期\n'
                                        '{time} - 当前时间(24小时制)\n'
                                        '{weekday} - 星期几\n'
                                        '{lunar_date} - 农历日期\n'
                                        '{suitable} - 宜做的事\n'
                                        '{unsuitable} - 忌做的事\n'
                                        '{city} - 城市名称\n'
                                        '{weather} - 天气完整信息\n'
                                        '{constellation} - 星座名称\n'
                                        '{horoscope} - 运势完整信息\n'
                                        '{love_days} - 恋爱天数\n'
                                        '{rainbow} - 彩虹屁文本\n'
                                        '{encouragement} - 随机鼓励文本')  # 添加鼓励文本变量说明
            msg.button(QMessageBox.Ok).setText('确认')

    def add_friend(self):
        """添加好友"""
        friend_name = self.friend_input.text().strip()
        if friend_name:
            self.wechat.add_friend(friend_name)
            self.load_friends()
            self.friend_input.clear()  # 清空输入框

    def delete_friend(self):
        """删除好友"""
        selected_items = self.friend_list.selectedItems()
        if not selected_items:
            self.show_warning('警告', '请选择要删除的好友')
            return
        
        if self.show_confirm('确认', f'确定要删除选中的 {len(selected_items)} 个好友吗？'):
            for item in selected_items:
                self.wechat.delete_friend(item.text())
            self.load_friends()

    def load_friends(self):
        """加载好友列表"""
        self.friend_list.clear()
        for friend in self.wechat.get_friends():
            self.friend_list.addItem(friend)

    def import_friends(self):
        """从文件导入好友列表"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择好友列表文件",
            "",
            "文本文件 (*.txt);;JSON文件 (*.json);;所有文件 (*)",
            options=options
        )
        
        if file_name:
            try:
                if file_name.endswith('.json'):
                    # 导入JSON格式文件
                    with open(file_name, 'r', encoding='utf-8') as f:
                        friends = json.load(f)
                        if isinstance(friends, list):
                            for friend in friends:
                                if isinstance(friend, str) and friend.strip():
                                    self.wechat.add_friend(friend.strip())
                else:
                    # 导入文本文件，每行一个好友名称
                    with open(file_name, 'r', encoding='utf-8') as f:
                        for line in f:
                            friend = line.strip()
                            if friend:
                                self.wechat.add_friend(friend)
                
                self.load_friends()
                msg = QMessageBox.information(self, '成功', '好友列表导入成功！')
                msg.button(QMessageBox.Ok).setText('确认')
            except Exception as e:
                msg = QMessageBox.warning(self, '错误', f'导入失败：{str(e)}')
                msg.button(QMessageBox.Ok).setText('确认')

    def update_city_location(self):
        """更新城市位置信息"""
        city_name = self.city_input.text().strip()
        if not city_name:
            return
            
        city_info = self.get_city_location(city_name)
        if city_info:
            self.location = city_info['location']
            msg = QMessageBox.information(self, '成功', f'已更新城市位置：{city_info["name"]}')
            msg.button(QMessageBox.Ok).setText('确认')
        else:
            msg = QMessageBox.warning(self, '错误', '未找到该城市')
            msg.button(QMessageBox.Ok).setText('确认')

    def get_city_location(self, city_name):
        """获取城市的经纬度"""
        try:
            # 检查缓存
            if city_name in self.city_location_cache:
                return self.city_location_cache[city_name]

            # 调用和风天气城市查询API
            url = f"https://geoapi.qweather.com/v2/city/lookup"
            params = {
                'location': city_name,
                'key': self.weather_api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['code'] == '200' and data['location']:
                location = data['location'][0]
                result = {
                    'location': f"{location['lon']},{location['lat']}",
                    'name': location['name']
                }
                # 保存到缓存
                self.city_location_cache[city_name] = result
                return result
            return None
        except Exception as e:
            print(f"获取城市位置失败: {str(e)}")
            return None

    def get_rainbow_text(self):
        """获取彩虹屁文本"""
        try:
            # 直接请求API，不使用缓存
            url = "https://api.shadiao.pro/chp"
            response = requests.get(url)
            data = response.json()
            
            if data and 'data' in data and 'text' in data['data']:
                return data['data']['text']
            return "你是我温暖的太阳，让我的世界充满光明。"  # 默认文本
            
        except Exception as e:
            print(f"获取彩虹屁文本失败: {str(e)}")
            return "你是我温暖的太阳，让我的世界充满光明。"  # 出错时返回默认文本

    def get_random_encouragement(self):
        """获取随机励志文本"""
        try:
            import random
            return random.choice(self.encouragements)
        except Exception as e:
            print(f"获取励志文本失败: {str(e)}")
            return "你是最棒的！"

    def load_encouragements(self):
        """从文件加载励志文本"""
        try:
            encouragements_file = os.path.join('config', 'encouragements.txt')
            if not os.path.exists(encouragements_file):
                # 如果文件不存在，返回默认文本列表
                return ["你是最棒的！"]
            
            with open(encouragements_file, 'r', encoding='utf-8') as f:
                # 读取所有行并过滤掉空行
                return [line.strip() for line in f.readlines() if line.strip()]
                
        except Exception as e:
            print(f"加载励志文本失败: {str(e)}")
            return ["你是最棒的！"]  # 返回默认文本 

    def send_next_message(self):
        """发送下一条消息"""
        try:
            if self.current_friend_index < len(self.selected_friends):
                friend_name = self.selected_friends[self.current_friend_index]
                message = self.message_edit.toPlainText()
                
                # 替换模板变量
                message = self.replace_template_variables(message, friend_name)
                
                # 发送消息
                if self.wechat.send_to_friend(friend_name, message):
                    self.current_friend_index += 1
                    
                    # 更新状态显示
                    if self.current_friend_index < len(self.selected_friends):
                        # 更新进度状态
                        total_friends = len(self.selected_friends)
                        current_friend = self.current_friend_index + 1
                        next_friend = self.selected_friends[self.current_friend_index]
                        
                        if self.is_loop_enabled:
                            status = f"循环 {self.current_loop}/{self.total_loops} - "
                        else:
                            status = ""
                            
                        status += (f"已发送: {friend_name} → 下一个: {next_friend} "
                                 f"({current_friend}/{total_friends})")
                        self.status_label.setText(status)
                        
                        # 设置好友间隔
                        self.timer.setInterval(self.friend_interval_spin.value() * 1000)
                    else:
                        # 一轮发送完成
                        if self.is_loop_enabled and self.current_loop < self.total_loops:
                            self.current_loop += 1
                            self.current_friend_index = 0
                            next_friend = self.selected_friends[0]
                            
                            status = (f"循环 {self.current_loop}/{self.total_loops} - "
                                    f"已完成一轮发送，准备开始下一轮 → 下一个: {next_friend}")
                            self.status_label.setText(status)
                            
                            # 设置循环间隔
                            self.timer.setInterval(self.interval_spin.value() * 1000)
                        else:
                            # 所有发送完成
                            self.timer.stop()
                            self.update_ui_state(False)
                            total_messages = len(self.selected_friends) * self.current_loop
                            completion_status = (f"发送完成！共发送 {self.current_loop} 轮，"
                                              f"总计 {total_messages} 条消息")
                            self.status_label.setText(completion_status)
                            msg = QMessageBox.information(self, '完成', completion_status)
                            msg.button(QMessageBox.Ok).setText('确认')
                else:
                    self.timer.stop()
                    self.update_ui_state(False)
                    error_msg = f'发送给 {friend_name} 失败'
                    self.status_label.setText(error_msg)
                    msg = QMessageBox.warning(self, '错误', error_msg)
                    msg.button(QMessageBox.Ok).setText('确认')
            
        except Exception as e:
            self.timer.stop()
            self.update_ui_state(False)
            error_msg = f'发送消息时出错：{str(e)}'
            self.status_label.setText(error_msg)
            msg = QMessageBox.warning(self, '错误', error_msg)
            msg.button(QMessageBox.Ok).setText('确认') 

    def show_warning(self, title, message):
        """显示警告消息框"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.addButton('确认', QMessageBox.AcceptRole)
        msg_box.exec_()

    def show_info(self, title, message):
        """显示信息消息框"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.addButton(self.ok_button, QMessageBox.AcceptRole)
        msg_box.exec_()

    def show_confirm(self, title, message):
        """显示确认消息框"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.addButton(self.yes_button, QMessageBox.YesRole)
        msg_box.addButton(self.no_button, QMessageBox.NoRole)
        return msg_box.exec_() == 0  # 返回True表示点击了确认 