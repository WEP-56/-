import random


class ExplorationEvents:
    def __init__(self, player, game_map):
        self.player = player
        self.game_map = game_map

    def explore_area(self, area_id):
        """处理探索事件"""
        area = self.game_map.get_area(area_id)
        if not area:
            return "无效的探索区域"

        if area['explored']:
            return "这个区域已经探索过了"

        self.game_map.mark_explored(area_id)
        distance = area['distance_from_home']
        events = [
            self._find_gold,
            self._encounter_monster,
            self._find_equipment,
            self._get_blessing,
            self._get_cursed
        ]
        # 根据距离调整事件概率（越远战斗概率越高）
        weights = [0.3 - (distance * 0.02),
                   0.3 + (distance * 0.05),
                   0.15,
                   0.1,
                   0.15 + (distance * 0.02)]
        # 确保概率不为负
        weights = [max(0.05, w) for w in weights]

        event = random.choices(events, weights=weights, k=1)[0]
        return event(distance)

    def _find_gold(self, distance):
        """发现井盖"""
        base_gold = 5 + (distance * 2)
        total, bonus = self.player.add_gold(base_gold)
        msg = f"你找到了{base_gold}个井盖！"
        if bonus > 0:
            msg += f" 获得{bonus}个额外奖励！"
        return msg

    def _encounter_monster(self, distance):
        """遭遇怪物"""
        monster = self._create_monster(distance)
        return {"type": "battle", "monster": monster}

    def _create_monster(self, distance):
        """创建怪物"""
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

        max_distance = (self.game_map.map_size - 1) * 2
        difficulty_factor = min(1.0, distance / max_distance)
        monster_index = min(len(monster_types) - 1, int(difficulty_factor * len(monster_types)))
        base_monster = monster_types[monster_index]
        level_multiplier = 1 + (distance * 0.2)

        return {
            'name': base_monster["name"],
            'hp': max(1, int(base_monster["base_hp"] * level_multiplier)),
            'attack': max(1, int(base_monster["base_attack"] * level_multiplier)),
            'defense': max(0, int(base_monster["base_defense"] * level_multiplier)),
            'reward': max(1, int(base_monster["base_reward"] * level_multiplier)),
            'xp': max(1, int(base_monster["base_reward"] * 5 * level_multiplier))
        }

    def battle_turn(self, monster):
        """处理一轮战斗"""
        messages = []
        player_hp = self.player.hp
        monster_hp = monster['hp']
        battle_over = False
        victory = False

        # 玩家攻击
        damage = max(1, self.player.attack - monster['defense'])
        if random.random() < self.player.critical_chance / 100:
            damage *= 2
            messages.append(f"你打出了暴击！对{monster['name']}造成{damage}点伤害")
        else:
            messages.append(f"你对{monster['name']}造成{damage}点伤害")
        monster_hp -= damage

        if monster_hp <= 0:
            battle_over = True
            victory = True
            self.player.add_xp(monster['xp'])
            gold, _ = self.player.add_gold(monster['reward'])
            if self.player.equipped_weapon == "沾了胡辣汤的油条":
                self.player.heal_hp()
                messages.append("沾了胡辣汤的油条特效：战斗胜利回满血量！")

            # 50%几率掉落井盖
            if random.random() < 0.5:
                manhole_covers = random.randint(1, 5)
                if '井盖' not in self.player.items:
                    self.player.items['井盖'] = 0
                self.player.items['井盖'] += manhole_covers
                messages.append(f"意外地发现了{manhole_covers}个井盖！")

            messages.append(f"战胜了{monster['name']}，获得{gold}个井盖和{monster['xp']}点经验！")
        else:
            # 怪物攻击
            monster_damage = max(1, monster['attack'] - self.player.defense)
            messages.append(f"{monster['name']}对你造成{monster_damage}点伤害")
            player_hp -= monster_damage
            self.player.hp = player_hp

            if player_hp <= 0:
                battle_over = True
                victory = False
                self.player.still_alive = False
                messages.append("你被打败了...")

        return {"messages": messages, "monster_hp": monster_hp, "battle_over": battle_over, "victory": victory}

    def _find_equipment(self, distance):
        """发现装备"""
        # 可随机获取的装备列表
        rare_equipments = ["冻住的两掺", "中之剑"]
        equip = random.choice(rare_equipments)

        if self.player.equipment[equip]['obtained']:
            return "你发现了一件装备，但已经拥有了"

        self.player.equipment[equip]['obtained'] = True
        return f"恭喜！你找到了稀有装备：{equip}！"

    def _get_blessing(self, distance):
        """获得祝福"""
        blessings = [
            ("attack_bonus", 10, "攻击力提升10点！"),
            ("gold_bonus", 20, "井盖获取增加20%！"),
        ]
        attr, value, msg = random.choice(blessings)
        setattr(self.player, attr, getattr(self.player, attr) + value)
        return f"获得祝福：{msg}"

    def _get_cursed(self, distance):
        """受到诅咒"""
        curses = [
            ("maxhp_penalty", 5, "最大生命值减少5点！"),
            ("attack_penalty", 3, "攻击力减少3点！"),
        ]
        attr, value, msg = random.choice(curses)
        self.player.curses[attr] += value
        self.player.update_derived_attributes()  # 重新计算属性
        return f"受到诅咒：{msg}"
