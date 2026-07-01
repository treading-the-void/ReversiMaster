from player_class import HumanPlayer, AIPlayer
from game_class import Game

# AI玩家 黑棋初始化
black_player =  AIPlayer("X", time_limit=3)

# 原始AI玩家 白棋初始化
white_player = HumanPlayer("O")

# 游戏初始化，第一个玩家是黑棋，第二个玩家是白棋
game = Game(black_player, white_player)

# 开始下棋
game.run()
