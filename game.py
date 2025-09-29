import sys
import random
import math
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                               QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout,
                               QFrame, QDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette


class ShopDialog(QDialog):
    """井盖商店对话框"""

    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("老家井盖商店")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        # 商店标题
        title = QLabel("欢迎来到老家井盖商店！")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 商品列表
        self.food_btn = QPushButton(f"1. 胡辣汤 - 5个井盖 (恢复生命值)")
        self.scroll_btn = QPushButton(f"2. 下水道口 - 10个井盖 (立即回家)")

        self.food_btn.clicked.connect(self.buy_food)
        self.scroll_btn.clicked.connect(self.buy_scroll)

        layout.addWidget(self.food_btn)
        layout.addWidget(self.scroll_btn)

        # 玩家井盖数量
        self.coins_label = QLabel(f"当前井盖数量: {self.player['gold']}个")
        layout.addWidget(self.coins_label)

        # 关闭按钮
        close_btn = QPushButton("关闭商店")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def buy_food(self):
        if self.player['gold'] >= 5:
            self.player['gold'] -= 5
            if 'food' in self.player['items']:
                self.player['items']['food'] += 1
            else:
                self.player['items']['food'] = 1
            QMessageBox.information(self, "购买成功", "你购买了1份胡辣汤！")
            self.coins_label.setText(f"当前井盖数量: {self.player['gold']}个")
        else:
            QMessageBox.warning(self, "购买失败", "你的井盖不够！")

    def buy_scroll(self):
        if self.player['gold'] >= 10:
            self.player['gold'] -= 10
            if 'scroll' in self.player['items']:
                self.player['items']['scroll'] += 1
            else:
                self.player['items']['scroll'] = 1
            QMessageBox.information(self, "购买成功", "你购买了1个下水道口！")
            self.coins_label.setText(f"当前井盖数量: {self.player['gold']}个")
        else:
            QMessageBox.warning(self, "购买失败", "你的井盖不够！")


class TextAdventureGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_game_data()
        self.init_ui()
        # 先设置玩家位置，再创建地图
        self.change_player(self.mapSize)
        self.makeMap(self.mapSize, self.mapSize)
        self.setup_initial_game()

    def init_game_data(self):
        # 玩家数据 - 增加详细属性系统
        self.player = {
            'name': '小明',
            'hp': 20,
            'maxhp': 20,
            'gold': 0,  # 井盖数量
            'items': {},  # 物品及数量
            'level': 1,
            'xp': 0,
            'xpForNextLevel': 100,
            'locationX': 0,
            'locationY': 0,
            'locationID': 1,  # 初始化为1而不是0，避免KeyError
            'exploredAreas': 1,
            'home_locationID': 1,  # 初始化为1
            # 核心属性
            'strength': 5,  # 力量：影响物理攻击和携带能力
            'agility': 3,  # 敏捷：影响闪避和命中
            'vitality': 4,  # 活力：影响生命值和恢复速度
            'luck': 2,  # 运气：影响暴击和稀有物品获取
            # 衍生属性
            'attack': 10,  # 基础攻击力
            'defense': 2,  # 基础防御力
            'critical_chance': 5,  # 暴击几率(%)
            # 祝福与诅咒
            'attack_bonus': 0,  # 攻击力加成
            'gold_bonus': 0,  # 井盖获取百分比加成
            'curses': {
                'maxhp_penalty': 0,  # 最大生命值惩罚
                'attack_penalty': 0  # 攻击力惩罚
            }
        }

        # 游戏地图数据 - 河南地名
        self.gameMap = {}
        self.mapSize = 5
        self.map_Num = math.floor(math.pow(self.mapSize, 2))
        self.areaType = [
            "郑州", "洛阳", "开封", "安阳", "新乡",
            "焦作", "濮阳", "许昌", "漯河", "三门峡",
            "南阳", "商丘", "信阳", "周口", "驻马店",
            "平顶山", "鹤壁", "济源", "巩义", "兰考"
        ]
        self.still_alive = True
        self.home_x = 0  # 老家X坐标
        self.home_y = 0  # 老家Y坐标

    def init_ui(self):
        self.setWindowTitle('河南冒险记')
        self.setGeometry(100, 100, 1000, 700)

        # 主布局
        main_layout = QVBoxLayout()

        # 游戏标题
        title_label = QLabel("河南冒险记")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # 游戏内容区域（分为输出区域和地图区域）
        content_layout = QHBoxLayout()

        # 游戏输出区域
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumWidth(500)
        content_layout.addWidget(self.output_area)

        # 地图显示区域
        map_frame = QFrame()
        map_frame.setFrameShape(QFrame.StyledPanel)
        self.map_layout = QGridLayout(map_frame)
        self.map_layout.setSpacing(5)
        self.map_widgets = {}  # 存储地图单元格部件
        content_layout.addWidget(map_frame)

        main_layout.addLayout(content_layout)

        # 输入框和确认按钮（用于输入名字）
        input_layout = QHBoxLayout()
        self.name_input = QLabel("请输入你的名字: ")
        self.name_edit = QTextEdit()
        self.name_edit.setMaximumHeight(30)
        self.confirm_name_btn = QPushButton("确认")
        self.confirm_name_btn.clicked.connect(self.confirm_name)

        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.name_edit)
        input_layout.addWidget(self.confirm_name_btn)
        main_layout.addLayout(input_layout)

        # 移动按钮布局 - 上下左右
        move_layout = QHBoxLayout()
        self.move_up_btn = QPushButton("向上移动 (↑)")
        self.move_down_btn = QPushButton("向下移动 (↓)")
        self.move_left_btn = QPushButton("向左移动 (←)")
        self.move_right_btn = QPushButton("向右移动 (→)")

        self.move_up_btn.clicked.connect(lambda: self.move_player('up'))
        self.move_down_btn.clicked.connect(lambda: self.move_player('down'))
        self.move_left_btn.clicked.connect(lambda: self.move_player('left'))
        self.move_right_btn.clicked.connect(lambda: self.move_player('right'))

        move_layout.addWidget(self.move_up_btn)
        move_layout.addWidget(self.move_down_btn)
        move_layout.addWidget(self.move_left_btn)
        move_layout.addWidget(self.move_right_btn)
        main_layout.addLayout(move_layout)

        # 动作按钮布局
        action_layout = QHBoxLayout()
        self.explore_btn = QPushButton("探索地区 (x)")
        self.rest_btn = QPushButton("恢复休息 (r)")
        self.items_btn = QPushButton("查看物品 (i)")
        self.status_btn = QPushButton("角色状态 (c)")
        self.map_btn = QPushButton("刷新地图 (m)")
        self.shop_btn = QPushButton("井盖商店 (s)")
        self.use_item_btn = QPushButton("使用物品 (u)")

        self.explore_btn.clicked.connect(self.explore_area)
        self.rest_btn.clicked.connect(self.rest)
        self.items_btn.clicked.connect(self.show_items)
        self.status_btn.clicked.connect(self.show_status)
        self.map_btn.clicked.connect(self.update_map_display)
        self.shop_btn.clicked.connect(self.open_shop)
        self.use_item_btn.clicked.connect(self.use_item)

        action_layout.addWidget(self.explore_btn)
        action_layout.addWidget(self.rest_btn)
        action_layout.addWidget(self.items_btn)
        action_layout.addWidget(self.status_btn)
        action_layout.addWidget(self.map_btn)
        action_layout.addWidget(self.shop_btn)
        action_layout.addWidget(self.use_item_btn)
        main_layout.addLayout(action_layout)

        # 设置中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 初始禁用大部分按钮，直到输入名字
        self.disable_game_buttons(True)

    def disable_game_buttons(self, disable):
        self.move_up_btn.setDisabled(disable)
        self.move_down_btn.setDisabled(disable)
        self.move_left_btn.setDisabled(disable)
        self.move_right_btn.setDisabled(disable)
        self.explore_btn.setDisabled(disable)
        self.rest_btn.setDisabled(disable)
        self.items_btn.setDisabled(disable)
        self.status_btn.setDisabled(disable)
        self.map_btn.setDisabled(disable)
        self.shop_btn.setDisabled(disable)
        self.use_item_btn.setDisabled(disable)

    def setup_initial_game(self):
        self.append_text("欢迎来到《河南冒险记》！")
        self.append_text("在这个游戏中，你将探索河南各地，收集井盖，与怪物战斗！")
        self.append_text("离老家越远，遇到的怪物可能越强大，但奖励也更丰厚！")
        self.append_text("请在下方输入框中输入你的名字，然后点击确认开始游戏。")

    def confirm_name(self):
        name = self.name_edit.toPlainText().strip()
        if name:
            self.player["name"] = name
            self.name_input.hide()
            self.name_edit.hide()
            self.confirm_name_btn.hide()
            self.disable_game_buttons(False)

            self.append_text(f"\n你的游戏主角名字叫 {self.player['name']}。")
            self.append_text(
                f"初始属性: 生命值 {self.player['hp']}/{self.player['maxhp']}, 攻击力 {self.player['attack']}, 防御力 {self.player['defense']}")
            self.append_text(f"你现在有 {self.player['gold']} 个井盖，身上没有任何物品。")
            self.append_text(f"\n你的冒险开始于老家，去探索河南的更多地方吧...")

            # 确保老家已正确设置
            if self.player['home_locationID'] in self.gameMap:
                self.description()
                self.update_map_display()  # 初始化地图显示
            else:
                self.append_text("游戏初始化时出现问题，正在重新设置老家位置...")
                # 重新设置老家位置
                self.change_player(self.mapSize)
                self.makeMap(self.mapSize, self.mapSize)
                self.description()
                self.update_map_display()

    def append_text(self, text):
        self.output_area.append(text)
        # 自动滚动到底部
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())

    def change_player(self, mapSize):
        # 计算中心位置作为初始位置
        center = math.floor((mapSize - 1) / 2)
        self.player['locationX'] = center
        self.player['locationY'] = center
        # 确保locationID从1开始，而不是0
        self.player['locationID'] = center * mapSize + center + 1
        self.home_x = center
        self.home_y = center
        self.player['home_locationID'] = self.player['locationID']  # 确保老家位置ID正确

    def makeArea(self, id, x, y):
        area = {
            'mapID': id,
            'x': x,
            'y': y,
            'type': random.choice(self.areaType),
            'explored': False,
            'distance_from_home': self.calculate_distance(x, y)  # 记录离老家的距离
        }
        return area

    def calculate_distance(self, x, y):
        """计算与老家的曼哈顿距离"""
        return abs(x - self.home_x) + abs(y - self.home_y)

    def makeMap(self, rows, columns):
        self.gameMap.clear()
        for y in range(0, rows):
            for x in range(0, columns):
                area_id = y * columns + x + 1  # 确保ID从1开始
                self.gameMap[area_id] = self.makeArea(area_id, x, y)
                # 确保老家位置正确设置
                if area_id == self.player['home_locationID']:
                    self.gameMap[area_id]['type'] = '老家'
                    self.gameMap[area_id]['explored'] = True
                    self.append_text(f"老家位置设置在区域 {area_id}")  # 调试信息

    def description(self):
        # 检查玩家位置ID是否有效
        if self.player["locationID"] not in self.gameMap:
            self.append_text(f"警告：无效的位置ID {self.player['locationID']}，正在重置位置...")
            self.change_player(self.mapSize)
            self.makeMap(self.mapSize, self.mapSize)

        current_area = self.gameMap[self.player["locationID"]]
        isExplored = "已探索" if current_area["explored"] else "未探索"
        self.append_text(f"\n当前位置: {current_area['type']}")
        self.append_text(f"(X: {self.player['locationX']}, Y: {self.player['locationY']}) 该区域状态：{isExplored}")
        self.append_text(f"距离老家: {current_area['distance_from_home']} 步")

        # 显示是否可以休息或进入商店
        if current_area['type'] == '老家':
            self.append_text("你现在可以休息恢复生命值，也可以去井盖商店购物！")

    def move_player(self, direction):
        """移动方向：上下左右"""
        if not self.still_alive:
            return

        # 保存当前位置ID，用于出错时恢复
        current_id = self.player["locationID"]

        if direction == 'up':  # 上移，Y坐标减1
            if self.player['locationY'] - 1 >= 0:
                self.player['locationY'] -= 1
                self.player['locationID'] -= self.mapSize
            else:
                self.player["locationY"] = self.mapSize - 1
                self.player["locationID"] = (self.player['locationID'] - self.mapSize) + self.map_Num
        elif direction == 'down':  # 下移，Y坐标加1
            if self.player['locationY'] + 1 <= self.mapSize - 1:
                self.player['locationY'] += 1
                self.player['locationID'] += self.mapSize
            else:
                self.player['locationY'] = 0
                self.player['locationID'] = (self.player['locationID'] + self.mapSize) - self.map_Num
        elif direction == "left":  # 左移，X坐标减1
            if self.player["locationX"] - 1 >= 0:
                self.player["locationX"] -= 1
                self.player["locationID"] -= 1
            else:
                self.player["locationX"] = self.mapSize - 1
                self.player["locationID"] += self.mapSize - 1
        elif direction == "right":  # 右移，X坐标加1
            if self.player["locationX"] + 1 <= self.mapSize - 1:
                self.player["locationX"] += 1
                self.player["locationID"] += 1
            else:
                self.player["locationX"] = 0
                self.player["locationID"] -= self.mapSize - 1

        # 检查移动后的位置是否有效
        if self.player["locationID"] not in self.gameMap or self.player["locationID"] <= 0:
            self.append_text(f"移动出错，位置ID无效: {self.player['locationID']}，已恢复原位置")
            self.player["locationID"] = current_id
            # 恢复坐标
            area = self.gameMap[current_id]
            self.player['locationX'] = area['x']
            self.player['locationY'] = area['y']
        else:
            self.description()
            self.update_map_display()  # 移动后更新地图
            self.check_game_state()

    def level_up(self):
        """玩家升级时提升属性"""
        self.player['level'] += 1
        self.append_text(f'\n恭喜你，升级了！{self.player["name"]} 现在是 {self.player["level"]} 级了！')

        # 升级属性点
        points_to_distribute = 3
        self.append_text(f"获得 {points_to_distribute} 点属性点！")

        # 自动分配属性点
        self.player['strength'] += 1
        self.player['agility'] += 1
        self.player['vitality'] += 1

        # 更新衍生属性
        self.update_derived_attributes()

        # 增加生命值并回满
        prev_maxhp = self.player['maxhp']
        self.player['maxhp'] = max(1, self.player['maxhp'] - self.player['curses']['maxhp_penalty'])
        self.player['hp'] = self.player['maxhp']

        # 调整下一级所需经验
        self.player['xpForNextLevel'] = int(self.player['xpForNextLevel'] * 1.5)

        # 显示升级信息
        self.append_text(f"属性提升: 力量+1, 敏捷+1, 活力+1")
        self.append_text(f"最大生命值增加到 {self.player['maxhp']} 点！")

    def update_derived_attributes(self):
        """根据基础属性更新衍生属性"""
        # 攻击力 = 基础值 + 力量/2
        self.player['attack'] = 10 + (self.player['strength'] // 2) + self.player['attack_bonus'] - \
                                self.player['curses']['attack_penalty']

        # 防御力 = 基础值 + 敏捷/3
        self.player['defense'] = 2 + (self.player['agility'] // 3)

        # 最大生命值 = 基础值 + 活力*3
        self.player['maxhp'] = 20 + (self.player['vitality'] * 3)

        # 暴击几率 = 基础值 + 运气/2
        self.player['critical_chance'] = 5 + (self.player['luck'] // 2)

    def addXp(self, num):
        self.player['xp'] += num
        self.append_text(f'\n{self.player["name"]} 获得了 {num} 点经验值。')
        while self.player['xp'] >= self.player['xpForNextLevel']:
            # 溢出的经验保留
            self.player['xp'] -= self.player['xpForNextLevel']
            self.level_up()

    def addGold(self, num):
        # 应用井盖获取加成
        bonus = int(num * self.player['gold_bonus'] / 100)
        total = num + bonus
        self.player['gold'] += total
        message = f'\n{self.player["name"]} 捡到了 {num} 个井盖！'
        if bonus > 0:
            message += f' (获得{bonus}个额外井盖奖励)'
        self.append_text(message)

    def healhp(self, amount=None):
        if amount is None:
            # 完全恢复
            healed = self.player['maxhp'] - self.player['hp']
            self.player['hp'] = self.player['maxhp']
        else:
            # 恢复指定数量
            healed = min(amount, self.player['maxhp'] - self.player['hp'])
            self.player['hp'] += healed

        self.append_text(f'你恢复了 {healed} 点生命值。')

    def create_monster(self, distance):
        """根据距离老家的距离生成怪物，越远越强"""
        # 怪物类型
        monster_types = [
            {"name": "精神小妹", "base_hp": 5, "base_attack": 3, "base_defense": 0, "base_reward": 2},
            {"name": "豆角", "base_hp": 8, "base_attack": 5, "base_defense": 1, "base_reward": 3},
            {"name": "不中", "base_hp": 12, "base_attack": 7, "base_defense": 2, "base_reward": 5},
            {"name": "六魔", "base_hp": 6, "base_attack": 8, "base_defense": 0, "base_reward": 4},
            {"name": "信球", "base_hp": 15, "base_attack": 10, "base_defense": 3, "base_reward": 7},
            {"name": "俺拾嘞", "base_hp": 20, "base_attack": 12, "base_defense": 4, "base_reward": 10},
            {"name": "高考", "base_hp": 30, "base_attack": 15, "base_defense": 6, "base_reward": 15},
            {"name": "中", "base_hp": 40, "base_attack": 20, "base_defense": 8, "base_reward": 20}
        ]

        # 根据距离选择怪物类型和强度
        max_distance = (self.mapSize - 1) * 2  # 最大可能距离
        difficulty_factor = min(1.0, distance / max_distance)  # 0-1之间的难度因子
        monster_index = min(len(monster_types) - 1, int(difficulty_factor * len(monster_types)))

        # 选择基础怪物
        base_monster = monster_types[monster_index]

        # 根据距离调整属性
        level_multiplier = 1 + (distance * 0.2)  # 距离越远，属性乘数越大

        monster = {
            'name': base_monster["name"],
            'hp': max(1, int(base_monster["base_hp"] * level_multiplier)),
            'attack': max(1, int(base_monster["base_attack"] * level_multiplier)),
            'defense': max(0, int(base_monster["base_defense"] * level_multiplier)),
            'reward': max(1, int(base_monster["base_reward"] * level_multiplier)),
            'xp_reward': max(5, int(base_monster["base_reward"] * level_multiplier * 3))
        }

        return monster

    def battle(self, monster):
        """玩家与怪物战斗系统"""
        self.append_text(f"\n=== 战斗开始: {self.player['name']} vs {monster['name']} ===")
        self.append_text(
            f"{monster['name']} - 生命值: {monster['hp']}, 攻击力: {monster['attack']}, 防御力: {monster['defense']}")

        player_hp = self.player['hp']
        monster_hp = monster['hp']

        # 战斗回合
        round_count = 1
        while player_hp > 0 and monster_hp > 0:
            self.append_text(f"\n--- 第 {round_count} 回合 ---")

            # 玩家攻击
            # 计算命中几率
            hit_chance = 80 + (self.player['agility'] - 5) * 2  # 基础80%命中率，受敏捷影响
            hit_chance = max(50, min(95, hit_chance))  # 限制在50%-95%之间

            if random.randint(1, 100) <= hit_chance:
                # 命中，计算伤害
                damage = max(1, self.player['attack'] - monster['defense'] // 2)

                # 检查暴击
                is_critical = random.randint(1, 100) <= self.player['critical_chance']
                if is_critical:
                    damage = int(damage * 1.5)
                    self.append_text(f"你对{monster['name']}发动了暴击！")

                monster_hp -= damage
                self.append_text(f"你攻击了{monster['name']}，造成了 {damage} 点伤害！")
            else:
                self.append_text(f"你的攻击被{monster['name']}闪避了！")

            # 怪物攻击（如果还活着）
            if monster_hp > 0:
                # 怪物命中几率
                monster_hit_chance = 70
                if random.randint(1, 100) <= monster_hit_chance:
                    # 命中，计算伤害
                    damage = max(1, monster['attack'] - self.player['defense'] // 2)
                    player_hp -= damage
                    self.append_text(f"{monster['name']}攻击了你，造成了 {damage} 点伤害！")
                else:
                    self.append_text(f"{monster['name']}的攻击被你闪避了！")

            # 显示当前状态
            self.append_text(
                f"状态: {self.player['name']} {player_hp}/{self.player['maxhp']} HP | {monster['name']} {max(0, monster_hp)} HP")

            round_count += 1
            # 防止无限循环
            if round_count > 20:
                self.append_text("战斗陷入僵局，双方都精疲力尽了...")
                return 0, 0  # 无奖励，玩家受轻伤

        # 战斗结果
        if player_hp > 0 and monster_hp <= 0:
            self.append_text(f"\n=== 战斗胜利！你击败了{monster['name']} ===")
            self.player['hp'] = player_hp  # 更新玩家生命值
            return monster['reward'], monster['xp_reward']
        else:
            self.append_text(f"\n=== 战斗失败！你被{monster['name']}击败了 ===")
            self.player['hp'] = 0  # 玩家死亡
            return 0, 0

    def explore_area(self):
        if not self.still_alive:
            return

        # 检查玩家位置是否有效
        if self.player["locationID"] not in self.gameMap:
            self.append_text(f"无法探索，位置无效: {self.player['locationID']}，正在重置位置...")
            self.change_player(self.mapSize)
            self.makeMap(self.mapSize, self.mapSize)
            self.description()
            return

        current_area = self.gameMap[self.player["locationID"]]
        is_first_explore = not current_area["explored"]

        # 初次探索奖励加倍
        multiplier = 1.0
        if is_first_explore:
            multiplier = 3.33  # 使后续探索为初次的30%左右
            self.player["exploredAreas"] += 1
            self.append_text(f"\n你第一次来到{current_area['type']}，发现了很多值得探索的地方！")

        # 增加更多随机事件
        event_type = random.randint(1, 10)  # 10种可能的事件

        if event_type == 1:  # 发现井盖
            base_gold = random.randrange(5, 15) if is_first_explore else random.randrange(2, 6)
            gold = int(base_gold * multiplier)
            self.addGold(gold)
            self.addXp(int(gold / 2))

        elif event_type == 2 or event_type == 3:  # 遭遇怪物 (20%几率)
            # 根据距离生成相应强度的怪物
            monster = self.create_monster(current_area['distance_from_home'])
            self.append_text(f"\n一只{monster['name']}出现在你的面前！")

            # 进行战斗
            reward, xp = self.battle(monster)

            if reward > 0 and xp > 0:
                self.addGold(int(reward * multiplier))
                self.addXp(int(xp * multiplier))
                self.append_text(f"你从{monster['name']}身上获得了{reward}个井盖和{xp}点经验！")

            # 检查玩家是否死亡
            if self.player['hp'] <= 0:
                self.check_death()
                return

        elif event_type == 4:  # 发现宝箱
            base_gold = random.randrange(8, 20) if is_first_explore else random.randrange(3, 8)
            gold = int(base_gold * multiplier)
            self.addGold(gold)
            self.addXp(int(gold / 1.5))
            self.append_text("你发现了一个宝箱！里面有不少井盖！")

            # 宝箱有几率获得额外物品
            if random.random() < 0.3:
                if random.random() < 0.5:
                    self.player['items']['food'] = self.player['items'].get('food', 0) + 1
                    self.append_text("宝箱里还有一份胡辣汤！")
                else:
                    self.player['items']['scroll'] = self.player['items'].get('scroll', 0) + 1
                    self.append_text("宝箱里还有一个下水道口！")

        elif event_type == 5:  # 获得祝福 - 增加攻击力
            bonus = random.randint(1, 2)
            self.player['attack_bonus'] += bonus
            self.update_derived_attributes()  # 更新衍生属性
            self.append_text(f"你感受到一股力量涌入体内！攻击力永久增加{bonus}点！当前攻击力: {self.player['attack']}")
            self.addXp(20)

        elif event_type == 6:  # 获得祝福 - 增加血量上限
            bonus = random.randint(2, 4)
            self.player['vitality'] += 1  # 增加活力属性
            self.update_derived_attributes()  # 更新衍生属性
            self.player['hp'] = self.player['maxhp']  # 回满生命值
            self.append_text(f"你感觉身体变强了！最大生命值永久增加！当前最大生命值: {self.player['maxhp']}")
            self.addXp(20)

        elif event_type == 7:  # 获得祝福 - 增加井盖获取
            bonus = random.randint(10, 20)
            self.player['gold_bonus'] += bonus
            self.append_text(f"你受到财富女神的眷顾！井盖获取量永久增加{bonus}%！当前加成: {self.player['gold_bonus']}%")
            self.addXp(20)

        elif event_type == 8:  # 受到轻微诅咒 - 减少血量上限
            penalty = random.randint(1, 2)
            self.player['curses']['maxhp_penalty'] += penalty
            self.update_derived_attributes()  # 更新衍生属性
            if self.player['hp'] > self.player['maxhp']:
                self.player['hp'] = self.player['maxhp']
            self.append_text(f"你感觉身体有点不适...最大生命值减少{penalty}点。当前最大生命值: {self.player['maxhp']}")

        elif event_type == 9:  # 受到轻微诅咒 - 减少攻击力
            penalty = random.randint(1, 1)
            self.player['curses']['attack_penalty'] += penalty
            self.update_derived_attributes()  # 更新衍生属性
            self.append_text(f"你感觉力量有点流失...攻击力减少{penalty}点。当前攻击力: {self.player['attack']}")

        elif event_type == 10:  # 发现有趣的事物
            xp_gain = int(random.randrange(5, 15) * multiplier)
            self.append_text(f'你在{current_area["type"]}发现了一些有趣的风土人情，增长了见识。')
            self.addXp(xp_gain)

        current_area["explored"] = True
        self.update_map_display()  # 探索后更新地图
        self.check_game_state()

    def rest(self):
        """只有在老家才能休息"""
        if not self.still_alive:
            return

        # 检查玩家位置是否有效
        if self.player["locationID"] not in self.gameMap:
            self.append_text(f"位置无效，无法休息，正在重置位置...")
            self.change_player(self.mapSize)
            self.makeMap(self.mapSize, self.mapSize)
            self.description()
            return

        # 检查是否在老家
        if self.gameMap[self.player["locationID"]]['type'] == '老家':
            if self.player["hp"] < self.player["maxhp"]:
                # 休息恢复量与活力相关
                heal_amount = 5 + (self.player['vitality'] // 2)
                self.healhp(heal_amount)
            else:
                self.append_text("你的生命值已经是满的了，不需要休息。")
        else:
            self.append_text("你只能在老家休息恢复生命值！")

    def show_items(self):
        if not self.still_alive:
            return

        items_text = "你目前携带的物品: "
        if not self.player["items"]:
            items_text += "没有任何物品"
        else:
            item_list = []
            if 'food' in self.player["items"] and self.player["items"]['food'] > 0:
                item_list.append(f"胡辣汤 x{self.player['items']['food']}")
            if 'scroll' in self.player["items"] and self.player["items"]['scroll'] > 0:
                item_list.append(f"下水道口 x{self.player['items']['scroll']}")
            items_text += ", ".join(item_list)

        self.append_text(items_text)
        self.append_text(f"井盖数量: {self.player['gold']} 个")

    def show_status(self):
        if not self.still_alive:
            return

        # 显示基础属性
        self.append_text(f"{self.player['name']} / 等级: {self.player['level']}级")
        self.append_text(f"经验值: {self.player['xp']}/{self.player['xpForNextLevel']}")
        self.append_text(f"生命值: {self.player['hp']}/{self.player['maxhp']}")
        self.append_text(f"井盖数量: {self.player['gold']} 个")

        # 显示战斗属性
        self.append_text(f"\n战斗属性:")
        self.append_text(f"攻击力: {self.player['attack']} (基础: {10 + (self.player['strength'] // 2)})")
        self.append_text(f"防御力: {self.player['defense']}")
        self.append_text(f"暴击几率: {self.player['critical_chance']}%")

        # 显示基础属性
        self.append_text(f"\n基础属性:")
        self.append_text(f"力量: {self.player['strength']} (影响攻击力)")
        self.append_text(f"敏捷: {self.player['agility']} (影响防御力和命中率)")
        self.append_text(f"活力: {self.player['vitality']} (影响生命值)")
        self.append_text(f"运气: {self.player['luck']} (影响暴击率)")

        # 显示祝福与诅咒状态
        bonuses = []
        if self.player['attack_bonus'] > 0:
            bonuses.append(f"攻击力+{self.player['attack_bonus']}")
        if self.player['gold_bonus'] > 0:
            bonuses.append(f"井盖获取+{self.player['gold_bonus']}%")

        curses = []
        if self.player['curses']['maxhp_penalty'] > 0:
            curses.append(f"最大生命值-{self.player['curses']['maxhp_penalty']}")
        if self.player['curses']['attack_penalty'] > 0:
            curses.append(f"攻击力-{self.player['curses']['attack_penalty']}")

        if bonuses:
            self.append_text(f"\n获得的祝福: {', '.join(bonuses)}")
        if curses:
            self.append_text(f"受到的诅咒: {', '.join(curses)}")

    def update_map_display(self):
        """地图显示：已探索地区显示为金色"""
        # 清除现有地图部件
        for widget in self.map_widgets.values():
            self.map_layout.removeWidget(widget)
            widget.deleteLater()
        self.map_widgets.clear()

        # 按网格形式添加地图单元格
        for area_id, area in self.gameMap.items():
            # 创建区域标签
            cell = QLabel(f"{area['type'][:2]}\n{area_id}")
            cell.setAlignment(Qt.AlignCenter)
            cell.setMinimumSize(60, 60)
            cell.setFrameShape(QFrame.StyledPanel)

            # 设置样式
            palette = cell.palette()

            # 玩家当前位置
            if area_id == self.player["locationID"]:
                palette.setColor(QPalette.Window, QColor(144, 238, 144))  # 浅绿色
                cell.setFont(self.bold_font())
            # 已探索区域（包括老家）
            elif area['explored']:
                palette.setColor(QPalette.Window, QColor(255, 215, 0))  # 金色
            # 未探索区域
            else:
                palette.setColor(QPalette.Window, QColor(240, 240, 240))  # 白色

            cell.setPalette(palette)
            cell.setAutoFillBackground(True)

            # 添加到网格布局
            row = area['y']  # Y坐标作为行号
            col = area['x']  # X坐标作为列号
            self.map_layout.addWidget(cell, row, col)
            self.map_widgets[area_id] = cell

    def bold_font(self):
        font = self.font()
        font.setBold(True)
        return font

    def check_game_state(self):
        # 检查是否探索完所有区域
        if self.player["exploredAreas"] == self.map_Num:
            self.append_text("你已经探索了该地图所有区域!")
            self.append_text("现在进入一个全新的地图...")
            self.mapSize += 2
            self.map_Num = math.floor(math.pow(self.mapSize, 2))
            self.change_player(self.mapSize)
            self.makeMap(self.mapSize, self.mapSize)
            self.player["exploredAreas"] = 1
            self.description()
            self.update_map_display()  # 更新地图

        # 检查玩家是否死亡
        if self.player["hp"] <= 0:
            self.check_death()

    def check_death(self):
        """处理玩家死亡，提供复活选项"""
        self.append_text("\n你不幸倒下了...")
        self.still_alive = False
        self.disable_game_buttons(True)

        # 检查是否有足够的井盖复活
        if self.player['gold'] >= 10:
            reply = QMessageBox.question(self, '复活',
                                         f'你愿意花费10个井盖复活吗？(当前拥有: {self.player["gold"]}个)',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.resurrect()
            else:
                self.append_text("游戏结束。请重新开始游戏。")
        else:
            QMessageBox.information(self, '无法复活',
                                    f'你没有足够的井盖复活（需要10个，当前只有{self.player["gold"]}个）。游戏结束。')
            self.append_text("游戏结束。请重新开始游戏。")

    def resurrect(self):
        """复活玩家"""
        self.player['gold'] -= 10
        self.player['hp'] = max(1, self.player['maxhp'] // 3)  # 复活后恢复1/3生命值
        self.still_alive = True
        self.disable_game_buttons(False)

        # 将玩家移动到老家
        prev_location = self.gameMap[self.player["locationID"]]['type'] if self.player[
                                                                               "locationID"] in self.gameMap else "未知区域"
        self.player['locationID'] = self.player['home_locationID']
        home_area = self.gameMap[self.player['locationID']]
        self.player['locationX'] = home_area['x']
        self.player['locationY'] = home_area['y']

        self.append_text(f"\n你花费10个井盖成功复活了！生命值恢复到 {self.player['hp']} 点。")
        self.append_text(f"你被传送回了老家。")
        self.update_map_display()

    def open_shop(self):
        """打开井盖商店"""
        if not self.still_alive:
            return

        # 检查玩家位置是否有效
        if self.player["locationID"] not in self.gameMap:
            self.append_text(f"位置无效，无法打开商店，正在重置位置...")
            self.change_player(self.mapSize)
            self.makeMap(self.mapSize, self.mapSize)
            self.description()
            return

        # 只有在老家才能打开商店
        if self.gameMap[self.player["locationID"]]['type'] == '老家':
            shop_dialog = ShopDialog(self.player, self)
            shop_dialog.exec_()
            self.show_items()  # 显示更新后的物品
        else:
            self.append_text("只有在老家才能找到井盖商店！")

    def use_item(self):
        """使用物品"""
        if not self.still_alive:
            return

        if not self.player['items']:
            self.append_text("你没有可以使用的物品！")
            return

        # 创建物品使用对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("使用物品")
        layout = QVBoxLayout(dialog)

        # 添加可用物品按钮
        if 'food' in self.player['items'] and self.player['items']['food'] > 0:
            food_btn = QPushButton(f"使用食物 (剩余: {self.player['items']['food']}) - 恢复生命值")
            food_btn.clicked.connect(lambda: self.use_food(dialog))
            layout.addWidget(food_btn)

        if 'scroll' in self.player['items'] and self.player['items']['scroll'] > 0:
            scroll_btn = QPushButton(f"使用回城卷轴 (剩余: {self.player['items']['scroll']}) - 返回老家")
            scroll_btn.clicked.connect(lambda: self.use_scroll(dialog))
            layout.addWidget(scroll_btn)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        layout.addWidget(cancel_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def use_food(self, dialog):
        """使用食物恢复生命值"""
        if 'food' in self.player['items'] and self.player['items']['food'] > 0:
            self.player['items']['food'] -= 1
            if self.player['items']['food'] == 0:
                del self.player['items']['food']

            # 食物恢复量与活力相关
            heal_amount = 5 + (self.player['vitality'] // 3)
            self.healhp(heal_amount)
            dialog.close()
        else:
            self.append_text("你没有食物可以使用！")

    def use_scroll(self, dialog):
        """使用回城卷轴返回老家"""
        if 'scroll' in self.player['items'] and self.player['items']['scroll'] > 0:
            self.player['items']['scroll'] -= 1
            if self.player['items']['scroll'] == 0:
                del self.player['items']['scroll']

            # 记录之前的位置
            prev_location = self.gameMap[self.player["locationID"]]['type'] if self.player[
                                                                                   "locationID"] in self.gameMap else "未知区域"
            # 移动到老家
            self.player['locationID'] = self.player['home_locationID']
            # 更新坐标
            home_area = self.gameMap[self.player['locationID']]
            self.player['locationX'] = home_area['x']
            self.player['locationY'] = home_area['y']

            self.append_text(f"你使用了下水道口，从{prev_location}回到了老家！")
            self.description()
            self.update_map_display()
            dialog.close()
        else:
            self.append_text("你没有下水道口可以使用！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextAdventureGame()
    window.show()
    sys.exit(app.exec())
