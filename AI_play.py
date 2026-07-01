from player_class import AIPlayer
from improved_player_class import AIPlayerWithAB
from game_class import Game
import random

def battle(rounds=50, time_limit=3):
    wins_original = 0
    wins_improved = 0
    draws = 0

    for i in range(rounds):
        # 交替先后手
        if i % 2 == 0:
            black = AIPlayer("X", time_limit)
            white = AIPlayerWithAB("O", time_limit)
        else:
            black = AIPlayerWithAB("X", time_limit)
            white = AIPlayer("O", time_limit)

        game = Game(black, white)
        result, diff = game.run()   # 假设返回 (winner, diff)，winner 是整数或字符串

        # 统一转换为整数
        if isinstance(result, int):
            winner = result
        elif isinstance(result, str):
            # 转换字符串结果
            if result == 'black_win':
                winner = 0
            elif result == 'white_win':
                winner = 1
            else:  # 'draw'
                winner = 2
        else:
            winner = 2  # 默认平局

        # 统计结果
        if winner == 0:
            if isinstance(black, AIPlayer) and isinstance(white, HeuristicMCTSPlayer):
                wins_original += 1
            else:
                wins_improved += 1
        elif winner == 1:
            if isinstance(white, AIPlayer) and isinstance(black, HeuristicMCTSPlayer):
                wins_original += 1
            else:
                wins_improved += 1
        else:
            draws += 1

        print(f"第{i+1}局结束，胜者：{['黑棋','白棋','平局'][winner]}")

    print(f"\n原版MCTS胜率：{wins_original/rounds:.2%}")
    print(f"改进版MCTS胜率：{wins_improved/rounds:.2%}")
    print(f"平局率：{draws/rounds:.2%}")

if __name__ == "__main__":
    random.seed(42)
    battle(rounds=100, time_limit=3)