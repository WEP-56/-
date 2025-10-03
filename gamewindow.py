import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                               QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout,
                               QFrame, QDialog, QMessageBox, QListWidget, QListWidgetItem,
                               QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class EquipmentDialog(QDialog):
    """装备操作对话框"""

    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("装备管理")
        self.setGeometry(300, 200, 500, 400)
        main_layout = QVBoxLayout()

        # 标题
        title_label = QLabel("装备列表（点击装备/卸下）")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = title_label.font()
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # 分栏布局
        split_layout = QHBoxLayout()

        # 背包装备列表
        self.backpack_list = QListWidget()
        self.update_backpack_list()
        self.backpack_list.itemClicked.connect(self.handle_equipment_click)
        split_layout.addWidget(self.backpack_list)

        # 已装备状态显示
        equipped_layout = QVBoxLayout()
        self.armor_label = QLabel("已装备甲胄（0/4）：")
        self.armor_display = QLabel("无")
        self.weapon_label = QLabel("已装备武器（0/1）：")
        self.weapon_display = QLabel("无")
        self.suit_effect = QLabel("")
        suit_font = self.suit_effect.font()
        suit_font.setItalic(True)
        self.suit_effect.setStyleSheet("color: #FF4500;")

        equipped_layout.addWidget(self.armor_label)
        equipped_layout.addWidget(self.armor_display)
        equipped_layout.addSpacing(10)
        equipped_layout.addWidget(self.weapon_label)
        equipped_layout.addWidget(self.weapon_display)
        equipped_layout.addSpacing(20)
        equipped_layout.addWidget(self.suit_effect)
        split_layout.addLayout(equipped_layout)

        main_layout.addLayout(split_layout)
        self.setLayout(main_layout)
        self.update_equipped_display()

    def update_backpack_list(self):
        self.backpack_list.clear()
        for eq_name, eq_info in self.player.equipment.items():
            if eq_info['obtained']:
                eq_type = "【甲胄】" if eq_info['type'] == 'armor' else "【武器】"
                equipped_status = "（已装备）" if (
                        eq_info['type'] == 'armor' and eq_name in self.player.equipped_armors
                        or eq_info['type'] == 'weapon' and eq_name == self.player.equipped_weapon
                ) else ""
                item_text = f"{eq_type} {eq_name} | 血量+{eq_info['hp']} | 攻击+{eq_info['attack']} {equipped_status}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, eq_name)
                self.backpack_list.addItem(item)

    def update_equipped_display(self):
        armor_count = len(self.player.equipped_armors)
        self.armor_label.setText(f"已装备甲胄（{armor_count}/4）：")
        self.armor_display.setText(
            ", ".join(self.player.equipped_armors) if self.player.equipped_armors else "无")

        weapon = self.player.equipped_weapon
        self.weapon_label.setText("已装备武器（1/1）：")
        self.weapon_display.setText(weapon if weapon else "无")

        # 井盖套装特效
        if armor_count == 4 and all(
                armor in self.player.equipped_armors
                for armor in ["井盖面甲", "井盖肚兜", "井盖内裤", "井盖臭鞋"]
        ):
            self.suit_effect.setText("✅ 井盖套装生效：血量+50% | 诅咒概率-50%")
        else:
            self.suit_effect.setText("")

    def handle_equipment_click(self, item):
        eq_name = item.data(Qt.UserRole)
        eq_info = self.player.equipment[eq_name]

        # 卸下装备
        if (eq_info['type'] == 'armor' and eq_name in self.player.equipped_armors) or (
                eq_info['type'] == 'weapon' and eq_name == self.player.equipped_weapon
        ):
            if eq_info['type'] == 'armor':
                self.player.equipped_armors.remove(eq_name)
                QMessageBox.information(self, "操作成功", f"已卸下甲胄：{eq_name}")
            else:
                self.player.equipped_weapon = None
                QMessageBox.information(self, "操作成功", f"已卸下武器：{eq_name}")
            self.parent().update_player_attributes()
            self.update_backpack_list()
            self.update_equipped_display()
            return

        # 装备物品
        if eq_info['type'] == 'armor':
            if len(self.player.equipped_armors) >= 4:
                QMessageBox.warning(self, "装备失败", "甲胄最多只能装备4件！")
                return
            self.player.equipped_armors.append(eq_name)
            QMessageBox.information(self, "操作成功", f"已装备甲胄：{eq_name}")
        else:
            if self.player.equipped_weapon is not None:
                QMessageBox.warning(self, "装备失败", f"已装备武器：{self.player.equipped_weapon}，请先卸下！")
                return
            self.player.equipped_weapon = eq_name
            if eq_name == "中之剑":
                QMessageBox.information(self, "神器激活", "✅ 中之剑特效：所有操作前将输出「中！」")
            else:
                QMessageBox.information(self, "操作成功", f"已装备武器：{eq_name}")

        self.parent().update_player_attributes()
        self.update_backpack_list()
        self.update_equipped_display()


class ShopDialog(QDialog):
    """井盖商店对话框"""

    def __init__(self, player, item_system, parent=None):
        super().__init__(parent)
        self.player = player
        self.item_system = item_system
        self.is_interactive = True

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("老家井盖商店")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout()

        # 商店标题
        title = QLabel("欢迎来到老家井盖商店！")
        title.setAlignment(Qt.AlignCenter)
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # 商品列表
        self.shop_items = {
            "胡辣汤": {"price": 5, "type": "consumable", "desc": "恢复生命值"},
            "下水道口": {"price": 10, "type": "consumable", "desc": "立即回家"},
            "井盖面甲": {"price": 200, "type": "equipment", "desc": "甲胄 | 血量+10 | 套装部件"},
            "井盖肚兜": {"price": 350, "type": "equipment", "desc": "甲胄 | 血量+18 | 套装部件"},
            "井盖内裤": {"price": 280, "type": "equipment", "desc": "甲胄 | 血量+15 | 套装部件"},
            "井盖臭鞋": {"price": 200, "type": "equipment", "desc": "甲胄 | 血量+12 | 套装部件"},
            "沾了胡辣汤的油条": {"price": 450, "type": "equipment", "desc": "武器 | 攻击+10 | 战斗胜利回满血量"}
        }

        # 添加商品按钮
        for item_name, item_info in self.shop_items.items():
            btn_text = f"{item_name} - {item_info['price']}个井盖 | {item_info['desc']}"
            if item_info['type'] == 'equipment' and self.player.equipment[item_name]['obtained']:
                btn = QPushButton(f"{btn_text}（已购买）")
                btn.setDisabled(True)
            else:
                btn = QPushButton(btn_text)
                btn.clicked.connect(lambda _, name=item_name: self.buy_item(name))
            layout.addWidget(btn)

        # 井盖数量显示
        self.coins_label = QLabel(f"当前井盖数量: {self.player.gold}个")
        layout.addWidget(self.coins_label)

        # 关闭按钮
        close_btn = QPushButton("关闭商店")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def buy_item(self, item_name):
        result = self.item_system.buy_item(item_name, self.shop_items)
        QMessageBox.information(self, "购买结果", result)
        self.coins_label.setText(f"当前井盖数量: {self.player.gold}个")
        # 刷新按钮状态
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QPushButton) and item_name in widget.text():
                if self.shop_items[item_name]['type'] == 'equipment':
                    widget.setText(
                        f"{item_name} - {self.shop_items[item_name]['price']}个井盖 | {self.shop_items[item_name]['desc']}（已购买）")
                    widget.setDisabled(True)
                break


class GameWindow(QMainWindow):
    """游戏主窗口"""

    def __init__(self, player, game_map, events, item_system):
        super().__init__()
        self.player = player
        self.game_map = game_map
        self.events = events
        self.item_system = item_system
        self.is_interactive = True
        self.init_ui()

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

        # 内容区域（输出+地图）
        content_layout = QHBoxLayout()

        # 输出区域
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumWidth(500)
        self.output_area.setAcceptRichText(True)
        content_layout.addWidget(self.output_area)

        # 地图显示
        map_frame = QFrame()
        map_frame.setFrameShape(QFrame.StyledPanel)
        self.map_layout = QGridLayout(map_frame)
        self.map_layout.setSpacing(5)
        self.map_widgets = {}
        content_layout.addWidget(map_frame)

        main_layout.addLayout(content_layout)

        # 名字输入
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

        # 移动按钮
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

        # 动作按钮
        action_layout = QHBoxLayout()
        self.explore_btn = QPushButton("探索地区 (x)")
        self.rest_btn = QPushButton("恢复休息 (r)")
        self.items_btn = QPushButton("查看物品 (i)")
        self.status_btn = QPushButton("角色信息")
        self.map_btn = QPushButton("刷新地图 (m)")
        self.shop_btn = QPushButton("井盖商店 (s)")

        self.explore_btn.clicked.connect(self.explore_area)
        self.rest_btn.clicked.connect(self.rest)
        self.items_btn.clicked.connect(self.show_items)
        self.status_btn.clicked.connect(self.show_character_info)
        self.map_btn.clicked.connect(self.update_map_display)
        self.shop_btn.clicked.connect(self.open_shop)

        action_layout.addWidget(self.explore_btn)
        action_layout.addWidget(self.rest_btn)
        action_layout.addWidget(self.items_btn)
        action_layout.addWidget(self.status_btn)
        action_layout.addWidget(self.map_btn)
        action_layout.addWidget(self.shop_btn)
        main_layout.addLayout(action_layout)

        # 战斗按钮
        battle_layout = QHBoxLayout()
        self.attack_btn = QPushButton("攻击 (a)")
        self.item_btn = QPushButton("道具 (i)")
        self.flee_btn = QPushButton("逃跑 (f)")

        self.attack_btn.clicked.connect(self.battle_attack)
        self.item_btn.clicked.connect(self.battle_use_item)
        self.flee_btn.clicked.connect(self.battle_flee)

        battle_layout.addWidget(self.attack_btn)
        battle_layout.addWidget(self.item_btn)
        battle_layout.addWidget(self.flee_btn)
        main_layout.addLayout(battle_layout)

        # 设置中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 初始禁用按钮
        self.disable_game_buttons(True)
        self.disable_battle_buttons(True)
        self.setup_initial_game()

    def disable_battle_buttons(self, disable):
        self.attack_btn.setDisabled(disable)
        self.item_btn.setDisabled(disable)
        self.flee_btn.setDisabled(disable)

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

    def start_battle(self, monster):
        self.is_interactive = False
        self.current_monster = monster
        self.disable_game_buttons(True)
        self.disable_battle_buttons(False)
        self.append_text(f"\n进入战斗！对手是 {monster['name']} (HP: {monster['hp']})。")

    def battle_attack(self):
        result = self.events.battle_turn(self.current_monster)
        self.current_monster['hp'] = result['monster_hp']
        for msg in result['messages']:
            self.append_text(msg)

        if self.player.hp <= 0:
            self.player.still_alive = False
            self.end_battle(False)
            return

        if result['battle_over']:
            self.end_battle(result['victory'])
        else:
            self.append_text(f"\n{self.current_monster['name']} 剩余生命值: {self.current_monster['hp']}")
            self.append_text(f"你的剩余生命值: {self.player.hp}")

    def battle_use_item(self):
        result = self.item_system.use_consumable('胡辣汤')
        self.append_text(result)
        if "恢复了" in result: # 判断是否使用成功
            # 怪物回合
            monster_damage = max(1, self.current_monster['attack'] - self.player.defense)
            self.player.hp -= monster_damage
            self.append_text(f"{self.current_monster['name']}对你造成{monster_damage}点伤害")
            if self.player.hp <= 0:
                self.player.still_alive = False
                self.end_battle(False)

    def battle_flee(self):
        self.player.hp -= 2
        self.append_text(f"你选择了逃跑，损失了2点生命值。剩余生命值：{self.player.hp}")
        if self.player.hp <= 0:
            self.player.still_alive = False
            self.append_text("你因伤势过重而倒下...")
            self.end_battle(False)
        else:
            self.end_battle(False) # 逃跑算作非胜利

    def end_battle(self, victory):
        self.is_interactive = True
        self.disable_battle_buttons(True)

        if victory:
            self.append_text("战斗胜利！")
            self.disable_game_buttons(False)
        elif not self.player.still_alive:
            self.append_text("你被打败了...")
            if self.player.gold >= 88:
                reply = QMessageBox.question(self, '复活',
                                             "你拥有足够的井盖，是否花费88个井盖复活？",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.player.gold -= 88
                    self.player.hp = self.player.maxhp // 2
                    self.player.still_alive = True
                    self.append_text("你消耗了88个井盖，原地复活了！")
                    self.show_status()
                    self.disable_game_buttons(False)
                    self.current_monster = None
                    return

            # If no resurrection
            self.append_text("游戏结束。")
            self.disable_game_buttons(True)
            QMessageBox.information(self, "游戏结束", "你已经死亡，游戏结束。")
            self.close()
            return
        else:  # Fleeing
            self.append_text("你逃离了战斗。")
            self.disable_game_buttons(False)

        self.current_monster = None

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

    def setup_initial_game(self):
        self.append_text("欢迎来到《河南冒险记》！")
        self.append_text("在这个游戏中，你将探索河南各地，收集井盖，与怪物战斗！")
        self.append_text("离老家越远，遇到的怪物可能越强大，但奖励也更丰厚！")
        self.append_text("特殊说明：输入名字「WEP」可激活管理员模式，直接获得所有装备！")
        self.append_text("请在下方输入框中输入你的名字，然后点击确认开始游戏。")

    def confirm_name(self):
        name = self.name_edit.toPlainText().strip()
        if not name:
            return

        self.player.name = name
        # 管理员模式
        if name == "WEP":
            self.append_text("\n【管理员模式激活】已自动获得所有装备！")
            for eq_name in self.player.equipment.keys():
                self.player.equipment[eq_name]['obtained'] = True
            self.player.gold = 9999

        self.name_input.hide()
        self.name_edit.hide()
        self.confirm_name_btn.hide()
        self.disable_game_buttons(False)

        # 初始化属性
        self.player.update_derived_attributes()

        self.append_text(f"\n你的游戏主角名字叫 {self.player.name}。")
        self.append_text(
            f"初始属性: 生命值 {self.player.hp}/{self.player.maxhp}, 攻击力 {self.player.attack}, 防御力 {self.player.defense}")
        self.append_text(f"你现在有 {self.player.gold} 个井盖，身上没有任何消耗品。")
        if name == "WEP":
            self.append_text("✅ 管理员福利：所有装备已解锁，可在「装备管理」中装备")
        self.append_text(f"\n你的冒险开始于老家，去探索河南的更多地方吧...")

        self.description()
        self.update_map_display()

    def append_text(self, text):
        # 中之剑特效
        if self.player.equipped_weapon == "中之剑":
            super_append = f'<span style="font-size:24px; color:#FF0000; font-weight:bold;">中！</span>\n{text}'
        else:
            super_append = text
        self.output_area.append(super_append)
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())

    def description(self):
        current_area = self.game_map.get_area(self.player.locationID)
        if not current_area:
            self.append_text("警告：无效的位置信息")
            return

        is_explored = "已探索" if current_area["explored"] else "未探索"
        self.append_text(f"\n当前位置: {current_area['type']}")
        self.append_text(f"(X: {self.player.locationX}, Y: {self.player.locationY}) 该区域状态：{is_explored}")
        self.append_text(f"距离老家: {current_area['distance_from_home']} 步")

        if current_area['type'] == '老家':
            self.append_text("你现在可以休息恢复生命值，也可以去井盖商店购物！")

        # 装备状态
        armor_count = len(self.player.equipped_armors)
        weapon = self.player.equipped_weapon or "无"
        self.append_text(f"当前装备：甲胄({armor_count}/4) | 武器：{weapon}")
        if armor_count == 4 and all(
                armor in self.player.equipped_armors
                for armor in ["井盖面甲", "井盖肚兜", "井盖内裤", "井盖臭鞋"]
        ):
            self.append_text("✅ 井盖套装生效：血量+50% | 诅咒概率-50%")

    def update_player_attributes(self):
        """更新玩家属性（装备变更后调用）"""
        self.player.update_derived_attributes()
        self.show_status()

    def move_player(self, direction):
        if not self.player.still_alive:
            return

        current_id = self.player.locationID
        map_size = self.game_map.map_size
        map_num = self.game_map.map_num

        if direction == 'up':
            if self.player.locationY - 1 >= 0:
                self.player.locationY -= 1
                self.player.locationID -= map_size
            else:
                self.player.locationY = map_size - 1
                self.player.locationID = (self.player.locationID - map_size) + map_num
        elif direction == 'down':
            if self.player.locationY + 1 <= map_size - 1:
                self.player.locationY += 1
                self.player.locationID += map_size
            else:
                self.player.locationY = 0
                self.player.locationID = (self.player.locationID + map_size) - map_num
        elif direction == "left":
            if self.player.locationX - 1 >= 0:
                self.player.locationX -= 1
                self.player.locationID -= 1
            else:
                self.player.locationX = map_size - 1
                self.player.locationID += map_size - 1
        elif direction == "right":
            if self.player.locationX + 1 <= map_size - 1:
                self.player.locationX += 1
                self.player.locationID += 1
            else:
                self.player.locationX = 0
                self.player.locationID -= map_size - 1

        # 验证位置有效性
        if self.player.locationID not in self.game_map.areas or self.player.locationID <= 0:
            self.append_text(f"移动出错，已恢复原位置")
            self.player.locationID = current_id
            area = self.game_map.get_area(current_id)
            self.player.locationX = area['x']
            self.player.locationY = area['y']
        else:
            self.description()
            self.update_map_display()

    def update_map_display(self):
        """刷新地图显示"""
        # 清空现有地图部件
        for widget in self.map_widgets.values():
            self.map_layout.removeWidget(widget)
            widget.deleteLater()
        self.map_widgets.clear()

        # 重新创建地图单元格
        for y in range(self.game_map.map_size):
            for x in range(self.game_map.map_size):
                area_id = y * self.game_map.map_size + x + 1
                area = self.game_map.get_area(area_id)
                if not area:
                    continue

                # 单元格样式
                cell = QLabel(f"{area['type'][0]}\n{area_id}")
                cell.setAlignment(Qt.AlignCenter)
                cell.setMinimumSize(50, 50)
                cell.setStyleSheet("border: 1px solid #ccc;")

                # 玩家位置高亮
                if area_id == self.player.locationID:
                    cell.setStyleSheet("background-color: yellow; border: 2px solid red;")
                # 老家标记
                elif area_id == self.game_map.home_id:
                    cell.setStyleSheet("background-color: green; color: white; border: 1px solid #ccc;")
                # 已探索区域
                elif area['explored']:
                    cell.setStyleSheet("background-color: #eee; border: 1px solid #ccc;")

                self.map_layout.addWidget(cell, y, x)
                self.map_widgets[area_id] = cell

    def explore_area(self):
        if not self.player.still_alive:
            return
        result = self.events.explore_area(self.player.locationID)

        if isinstance(result, dict) and result.get("type") == "battle":
            monster = result["monster"]
            reply = QMessageBox.question(self, '遭遇战斗', 
                                       f"你遇到了 {monster['name']}！\n\n是否战斗？\n选择“否”将逃跑并损失5点生命值。",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.start_battle(monster)
            else:
                self.player.hp -= 5
                self.append_text(f"你选择了逃跑，损失了5点生命值。剩余生命值：{self.player.hp}")
                if self.player.hp <= 0:
                    self.player.still_alive = False
                    self.append_text("你因伤势过重而倒下...")
                    self.end_battle(False)
        else:
            self.append_text(result)

        if self.game_map.check_all_explored():
            self.append_text("\n恭喜你！已探索当前所有区域，地图正在扩展...")
            self.game_map.expand_map()
            self.update_map_display()
            self.append_text("地图已扩展！新的区域等待你的探索！")
        else:
            self.update_map_display()

    def rest(self):
        if not self.player.still_alive:
            return
        current_area = self.game_map.get_area(self.player.locationID)
        if current_area['type'] != '老家':
            self.append_text("只有在老家才能休息恢复生命值")
            return

        healed = self.player.heal_hp()
        self.append_text(f"在老家休息，恢复了{healed}点生命值！")

    def show_items(self):
        if not self.player.items:
            self.append_text("你的背包是空的")
            return

        item_list = []
        for item, count in self.player.items.items():
            item_list.append(f"{item}: {count}个")
        self.append_text("背包物品：\n" + "\n".join(item_list))

    def show_character_info(self):
        self.is_interactive = False
        dialog = QDialog(self)
        dialog.setWindowTitle("角色信息")
        layout = QVBoxLayout()

        status_button = QPushButton("角色状态")
        status_button.clicked.connect(self.show_status)
        layout.addWidget(status_button)

        item_button = QPushButton("使用物品")
        item_button.clicked.connect(self.use_item)
        layout.addWidget(item_button)

        equip_button = QPushButton("装备管理")
        equip_button.clicked.connect(self.open_equipment)
        layout.addWidget(equip_button)

        dialog.setLayout(layout)
        dialog.exec_()
        self.is_interactive = True

    def show_status(self):
        status = [
            f"角色状态 - {self.player.name} Lv.{self.player.level}",
            f"生命值: {self.player.hp}/{self.player.maxhp}",
            f"攻击力: {self.player.attack} (基础+装备)",
            f"防御力: {self.player.defense}",
            f"井盖数量: {self.player.gold}",
            f"经验值: {self.player.xp}/{self.player.xpForNextLevel}",
            f"属性: 力量{self.player.strength} 敏捷{self.player.agility} "
            f"活力{self.player.vitality} 运气{self.player.luck}"
        ]
        self.append_text("\n".join(status))

    def open_shop(self):
        current_area = self.game_map.get_area(self.player.locationID)
        if current_area['type'] != '老家':
            self.append_text("只有在老家才能进入井盖商店")
            return

        self.is_interactive = False
        shop_dialog = ShopDialog(self.player, self.item_system, self)
        shop_dialog.exec_()
        self.is_interactive = True

    def use_item(self):
        if not self.player.items:
            QMessageBox.information(self, "提示", "背包里没有可以使用的物品")
            return

        self.is_interactive = False
        # 简单物品选择（实际项目可做更复杂的选择界面）
        items = [name for name, count in self.player.items.items() if count > 0]
        if not items:
            QMessageBox.information(self, "提示", "没有可用的物品了。")
            self.is_interactive = True
            return

        item_name, ok = QInputDialog.getItem(self, "使用物品", "选择要使用的物品:", items, 0, False)
        if ok and item_name:
            result = self.item_system.use_consumable(item_name)
            self.append_text(result)
            self.update_map_display()
        self.is_interactive = True

    def keyPressEvent(self, event):
        if not self.is_interactive:
            return

        if event.key() == Qt.Key_W:
            self.move_player('up')
        elif event.key() == Qt.Key_S:
            self.move_player('down')
        elif event.key() == Qt.Key_A:
            self.move_player('left')
        elif event.key() == Qt.Key_D:
            self.move_player('right')
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.explore_area()

    def open_equipment(self):
        self.is_interactive = False
        equip_dialog = EquipmentDialog(self.player, self)
        equip_dialog.exec_()
        self.is_interactive = True
