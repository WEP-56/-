import random


class GameMap:
    def __init__(self, map_size=5):
        self.map_size = map_size
        self.map_num = map_size * map_size
        self.areas = {}  # 区域数据 {area_id: area_data}
        self.area_types = [
            "郑州", "洛阳", "开封", "安阳", "新乡",
            "焦作", "濮阳", "许昌", "漯河", "三门峡",
            "南阳", "商丘", "信阳", "周口", "驻马店",
            "平顶山", "鹤壁", "济源", "巩义", "兰考"
        ]
        self.home_x = 0
        self.home_y = 0
        self.home_id = 1

    def initialize(self, player):
        """初始化地图并设置老家位置"""
        center = (self.map_size - 1) // 2
        self.home_x = center
        self.home_y = center
        self.home_id = center * self.map_size + center + 1

        # 创建地图区域
        for y in range(self.map_size):
            for x in range(self.map_size):
                area_id = y * self.map_size + x + 1
                self.areas[area_id] = self._create_area(area_id, x, y)

        # 标记老家
        self.areas[self.home_id]['type'] = '老家'
        self.areas[self.home_id]['explored'] = True
        player.move_to_home(self.home_x, self.home_y, self.home_id)

    def _create_area(self, area_id, x, y):
        """创建单个区域数据"""
        return {
            'mapID': area_id,
            'x': x,
            'y': y,
            'type': random.choice(self.area_types),
            'explored': False,
            'distance_from_home': self.calculate_distance(x, y)
        }

    def calculate_distance(self, x, y):
        """计算与老家的曼哈顿距离"""
        return abs(x - self.home_x) + abs(y - self.home_y)

    def get_area(self, area_id):
        """获取区域数据"""
        return self.areas.get(area_id)

    def mark_explored(self, area_id):
        """标记区域为已探索"""
        if area_id in self.areas:
            self.areas[area_id]['explored'] = True

    def check_all_explored(self):
        """检查是否所有区域都已探索"""
        return all(area['explored'] for area in self.areas.values())

    def expand_map(self):
        """扩展地图"""
        new_size = self.map_size + 2
        new_areas = {}

        # 将老家坐标平移
        self.home_x += 1
        self.home_y += 1

        # 创建新的扩展地图
        for y in range(new_size):
            for x in range(new_size):
                area_id = y * new_size + x + 1
                # 内部旧地图区域
                if 1 <= x < new_size - 1 and 1 <= y < new_size - 1:
                    old_x = x - 1
                    old_y = y - 1
                    old_area_id = old_y * self.map_size + old_x + 1
                    area_data = self.areas[old_area_id]
                    area_data['x'] = x
                    area_data['y'] = y
                    area_data['mapID'] = area_id
                    area_data['distance_from_home'] = self.calculate_distance(x, y)
                    new_areas[area_id] = area_data
                # 新增的外部区域
                else:
                    new_areas[area_id] = self._create_area(area_id, x, y)

        self.map_size = new_size
        self.map_num = new_size * new_size
        self.areas = new_areas
        self.home_id = self.home_y * self.map_size + self.home_x + 1
