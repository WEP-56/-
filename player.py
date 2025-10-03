import math


class Player:
    def __init__(self):
        # 基础属性
        self.name = '小明'
        self.hp = 20
        self.maxhp = 20
        self.base_maxhp = 20  # 基础最大血量（用于装备加成计算）
        self.gold = 0  # 井盖数量
        self.items = {}  # 消耗品（胡辣汤/下水道口）

        # 装备相关
        self.equipment = {}  # 装备数据（从装备模板初始化）
        self.equipped_armors = []  # 已装备甲胄（最多4件）
        self.equipped_weapon = None  # 已装备武器（最多1件）

        # 等级与经验
        self.level = 1
        self.xp = 0
        self.xpForNextLevel = 100

        # 位置信息
        self.locationX = 0
        self.locationY = 0
        self.locationID = 1
        self.exploredAreas = 1
        self.home_locationID = 1

        # 核心属性
        self.strength = 5  # 力量：影响物理攻击
        self.agility = 3  # 敏捷：影响闪避和命中
        self.vitality = 4  # 活力：影响生命值
        self.luck = 2  # 运气：影响暴击和稀有物品获取

        # 衍生属性
        self.attack = 10  # 基础攻击力
        self.defense = 2  # 基础防御力
        self.critical_chance = 5  # 暴击几率(%)

        # 祝福与诅咒
        self.attack_bonus = 0
        self.gold_bonus = 0
        self.curses = {
            'maxhp_penalty': 0,
            'attack_penalty': 0,
            'cursed_prob': 0.1  # 基础诅咒概率（10%）
        }

        # 状态标记
        self.still_alive = True

    def init_equipment(self, equipment_template):
        """初始化装备数据"""
        self.equipment = equipment_template.copy()

    def calculate_equipment_bonus(self):
        """计算装备属性加成"""
        # 重置基础属性
        base_maxhp = self.base_maxhp - self.curses['maxhp_penalty']
        base_attack = 10 + (self.strength // 2) + self.attack_bonus - self.curses['attack_penalty']
        total_hp_add = 0
        total_attack_add = 0
        cursed_prob = 0.1

        # 甲胄加成
        for armor in self.equipped_armors:
            if armor in self.equipment:
                total_hp_add += self.equipment[armor]['hp']

        # 井盖套装特效
        if len(self.equipped_armors) == 4 and all(
                armor in self.equipped_armors
                for armor in ["井盖面甲", "井盖肚兜", "井盖内裤", "井盖臭鞋"]
        ):
            base_maxhp = int(base_maxhp * 1.5)
            cursed_prob *= 0.5

        # 武器加成
        if self.equipped_weapon and self.equipped_weapon in self.equipment:
            total_hp_add += self.equipment[self.equipped_weapon]['hp']
            total_attack_add += self.equipment[self.equipped_weapon]['attack']

        # 更新最终属性
        self.maxhp = max(1, base_maxhp + total_hp_add)
        self.attack = max(1, base_attack + total_attack_add)
        self.curses['cursed_prob'] = cursed_prob

        # 确保当前血量不超过最大血量
        if self.hp > self.maxhp:
            self.hp = self.maxhp

    def update_derived_attributes(self):
        """更新衍生属性"""
        self.calculate_equipment_bonus()
        self.defense = 2 + (self.agility // 3)
        self.critical_chance = 5 + (self.luck // 2)

    def level_up(self):
        """玩家升级"""
        self.level += 1
        # 分配属性点
        self.strength += 1
        self.agility += 1
        self.vitality += 1

        # 更新基础最大血量
        self.base_maxhp = 20 + (self.vitality * 3)
        self.update_derived_attributes()

        # 回满生命值
        self.hp = self.maxhp

        # 调整下一级所需经验
        self.xpForNextLevel = int(self.xpForNextLevel * 1.5)

    def add_xp(self, num):
        """添加经验值"""
        self.xp += num
        while self.xp >= self.xpForNextLevel:
            self.xp -= self.xpForNextLevel
            self.level_up()

    def add_gold(self, num):
        """添加井盖（含奖励加成）"""
        bonus = int(num * self.gold_bonus / 100)
        total = num + bonus
        self.gold += total
        return total, bonus

    def heal_hp(self, amount=None):
        """恢复生命值"""
        if amount is None:
            healed = self.maxhp - self.hp
            self.hp = self.maxhp
        else:
            healed = min(amount, self.maxhp - self.hp)
            self.hp += healed
        return healed

    def set_location(self, x, y, area_id):
        """设置玩家位置"""
        self.locationX = x
        self.locationY = y
        self.locationID = area_id

    def move_to_home(self, home_x, home_y, home_id):
        """移动到老家"""
        self.set_location(home_x, home_y, home_id)
