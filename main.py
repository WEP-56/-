import sys
from PySide6.QtWidgets import QApplication
from player import Player
from map import GameMap
from attack import ExplorationEvents
from item import ItemSystem
from gamewindow import GameWindow

def main():
    # 初始化游戏核心组件
    player = Player()
    game_map = GameMap(map_size=5)
    item_system = ItemSystem(player)  # 初始化装备系统
    game_map.initialize(player)  # 初始化地图并设置老家
    events = ExplorationEvents(player, game_map)  # 初始化探索事件

    # 启动GUI
    app = QApplication(sys.argv)
    window = GameWindow(player, game_map, events, item_system)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
