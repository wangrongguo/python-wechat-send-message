import json
import os

class MessageHandler:
    def __init__(self):
        self.templates_path = os.path.join('templates', 'message_templates.json')
        self.load_templates()

    def load_templates(self):
        """加载消息模板"""
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except FileNotFoundError:
            self.templates = {}
            self.save_templates()

    def save_templates(self):
        """保存消息模板"""
        os.makedirs('templates', exist_ok=True)
        with open(self.templates_path, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)

    def add_template(self, name, content):
        """添加新模板"""
        self.templates[name] = content
        self.save_templates()

    def get_template(self, name):
        """获取模板"""
        return self.templates.get(name, '')

    def delete_template(self, name):
        """删除模板"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates() 