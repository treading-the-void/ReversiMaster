import random
from player_class import AIPlayer, oppo

def pos_to_coord(pos):
    col = ord(pos[0].upper()) - ord('A')
    row = 8 - int(pos[1])
    return row, col


def coord_to_pos(row, col):
    return chr(ord('A') + col) + str(8 - row)


# 经典位置价值表
POSITION_WEIGHT = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, 0, 0, 0, 0, -2, 10],
    [5, -2, 0, 0, 0, 0, -2, 5],
    [5, -2, 0, 0, 0, 0, -2, 5],
    [10, -2, 0, 0, 0, 0, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100]
]

def get_position_score(move):
    """获取某个棋盘坐标的位置价值"""
    row, col = pos_to_coord(move)
    return POSITION_WEIGHT[row][col]

def heuristic_score(board, move, color):
    """
    改进的启发式评估函数，融合基础评分 + 可行动性 + 奇偶性
    注意：本函数会临时修改 board，但最终会复原
    """
    oppo_color = 'O' if color == 'X' else 'X'

    # ---------- 1. 记录原始信息 ----------
    before_oppo_count = len(list(board.get_legal_actions(oppo_color)))

    # ---------- 2. 执行当前走子 ----------
    flipped_pos = board._move(move, color)          # 实际修改棋盘，返回翻转列表（棋盘坐标）
    if flipped_pos is False:                        # 理论上不会发生
        return 0

    # ---------- 3. 基础评分 ----------
    row, col = pos_to_coord(move)
    position_score = POSITION_WEIGHT[row][col] * 2
    flip_score = len(flipped_pos) * 8

    total = position_score + flip_score

    # ---------- 4. 可行动性（两步） ----------
    oppo_legal = list(board.get_legal_actions(oppo_color))
    if oppo_legal:
        max_flip = 0
        max_pos_score = -float('inf')
        for oppo_move in oppo_legal:
            # 对方走这一步能翻转我方多少棋子（不修改棋盘）
            oppo_flipped = board._can_fliped(oppo_move, oppo_color)
            max_flip = max(max_flip, len(oppo_flipped))
            # 对方走这一步的位置价值
            pos = get_position_score(oppo_move)
            max_pos_score = max(max_pos_score, pos)

        # 扣分：对方最多能翻转的我方棋子数 * 0.5
        total -= 5 * max_flip

        # 若对方能走到高价值位置（如角落），扣分
        if max_pos_score >= 80:
            total -= 50

    # 我方机动性：当前走法后，我方可走的合法步数
    my_legal = list(board.get_legal_actions(color))
    total += 0.1 * len(my_legal)

    # ---------- 7. 复原当前走子 ----------
    board.backpropagation(move, flipped_pos, color)

    return total

class HeuristicMCTSPlayer(AIPlayer):
    def __init__(self, color, time_limit=2, explore_prob=0.7):
        super().__init__(color, time_limit)
        self.explore_prob = explore_prob   # 概率按启发式选最高分，否则随机

    def simulate(self, node, board):
        sim_board = board
        color = node.color
        while True:
            legal = list(sim_board.get_legal_actions(color))
            if not legal:
                color = oppo(color)
                legal = list(sim_board.get_legal_actions(color))
                if not legal:
                    break
                else:
                    continue

            # 计算所有合法走法的启发式得分
            scores = [heuristic_score(sim_board, move, color) for move in legal]

            if random.random() < self.explore_prob:
                # 选最高分（若有并列则随机）
                max_score = max(scores)
                best_indices = [i for i, s in enumerate(scores) if s == max_score]
                idx = random.choice(best_indices)
                action = legal[idx]
            else:
                # 随机选择（保持探索）
                action = random.choice(legal)

            sim_board._move(action, color)
            color = oppo(color)

        return sim_board.get_winner()

class AIPlayerWithAB(AIPlayer):
    """
    在终局使用 Alpha-Beta 剪枝的 MCTS 玩家
    """
    def __init__(self, color, time_limit=2, ab_threshold=10):
        super().__init__(color, time_limit)
        self.ab_threshold = ab_threshold   # 空格数阈值，小于此值启用AB

    def get_move(self, board):
        # 计算剩余空格数
        empty_count = 64 - board.count('X') - board.count('O')
        if empty_count <= self.ab_threshold:
            # 使用 Alpha-Beta 搜索
            return self.alpha_beta_search(board)
        else:
            # 使用 MCTS
            return super().get_move(board)

    def alpha_beta_search(self, board):
        """Alpha-Beta 搜索入口，返回最佳走法"""
        color = self.color
        # 获取合法走法
        legal = list(board.get_legal_actions(color))
        if not legal:
            return None

        # 走法排序（提高剪枝效率）
        legal.sort(key=lambda m: heuristic_score(board, m, color), reverse=True)

        best_move = legal[0]
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        depth = 64 - board.count('X') - board.count('O')  # 搜索到终局

        # 限制最大深度以防时间超限（可根据需求调整）
        max_depth = min(depth, 20)  # 最多20层

        # 依次搜索每个走法
        for move in legal:
            # 执行走法
            flipped = board._move(move, color)
            if flipped is False:
                continue
            # 递归 negamax
            value = -self.negamax(board, oppo(color), max_depth-1, -beta, -alpha)
            # 撤销走法
            board.backpropagation(move, flipped, color)

            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, value)

        return best_move

    def negamax(self, board, color, depth, alpha, beta):
        """
        Negamax 算法，带 Alpha-Beta 剪枝
        返回当前局面对当前玩家的评估值（正数有利）
        """
        # 检查终局或深度为0
        if depth == 0:
            # 使用启发式评估（注意：启发式对当前颜色应返回正数）
            # 我们对所有合法走法评分取平均？或直接评估当前局面？
            # 简单做法：评估当前棋盘对 color 的优劣
            # 这里用 heuristic_score 评估当前位置（无走法时返回0）
            # 更常见的是统计棋子数差或位置得分差
            return self.evaluate(board, color)

        # 获取合法走法
        legal = list(board.get_legal_actions(color))
        if not legal:
            # 如果无合法走法，切换玩家
            return -self.negamax(board, oppo(color), depth-1, -beta, -alpha)

        # 走法排序
        legal.sort(key=lambda m: heuristic_score(board, m, color), reverse=True)

        best = -float('inf')
        for move in legal:
            flipped = board._move(move, color)
            if flipped is False:
                continue
            value = -self.negamax(board, oppo(color), depth-1, -beta, -alpha)
            board.backpropagation(move, flipped, color)

            if value > best:
                best = value
            alpha = max(alpha, value)
            if alpha >= beta:
                break   # 剪枝

        return best

    def evaluate(self, board, color):
        """
        评估当前棋盘对 color 的优劣（正数有利）
        使用启发式综合评分，可以考虑棋子数、位置、稳定性等
        这里简化：统计棋子数差 + 位置价值差
        """
        opp = oppo(color)
        # 基础棋子数差（每个棋子价值1）
        my_count = board.count(color)
        opp_count = board.count(opp)
        score = my_count - opp_count

        # 位置价值差（使用位置表）
        pos_score = 0
        for r in range(8):
            for c in range(8):
                pos = coord_to_pos(r, c)
                piece = board._board[r][c]
                if piece == color:
                    pos_score += POSITION_WEIGHT[r][c]
                elif piece == opp:
                    pos_score -= POSITION_WEIGHT[r][c]
        score += pos_score / 10   # 权重调整

        return score