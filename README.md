# ReversiMaster - 黑白棋 AI 对战平台

> 基于蒙特卡洛树搜索（MCTS）与 Alpha-Beta 剪枝混合策略的黑白棋（Reversi）AI，内含启发式评估、终局精算、自动对战与人类对战功能。

## 项目简介

ReversiMaster 是一个完整的黑白棋 AI 研究和实验平台。它实现了：

- 核心算法：蒙特卡洛树搜索（MCTS）作为主框架
- 终局增强：在残局阶段自动切换为 Alpha-Beta 剪枝搜索，显著提升终局决策质量
- 启发式评估：融合经典位置价值、翻转棋子数、可行动性（两步预测）和奇偶性判断
- 多种对战模式：AI vs AI（批量测试）、人类 vs AI、原版 vs 改进版对比

项目代码结构清晰，易于扩展和调试，适合用于算法学习、实验对比和性能调优。

---

## 项目文件结构

| 文件名 | 说明 |
|--------|------|
| board_class.py | 棋盘逻辑类，包含落子、翻转、合法走法生成、棋盘显示等核心操作 |
| game_class.py | 游戏流程控制类，管理回合切换、超时处理、胜负判定等 |
| player_class.py | 玩家类集合：人类玩家、Roxanne 策略玩家、标准 MCTS（AIPlayer） |
| improved_player_class.py | 改进型玩家类：启发式 MCTS（HeuristicMCTSPlayer）、带 Alpha-Beta 的 MCTS（AIPlayerWithAB） |
| human_play.py | 启动人类 vs AI 对战的入口 |
| AI_play.py | 批量自动对战测试脚本，统计原版与改进版胜率 |
| requirements.txt | 项目依赖（仅 func_timeout） |

---

## 快速开始

### 环境要求
- Python 3.7+
- 安装依赖：
  ```
  pip install -r requirements.txt
  ```

### 运行示例
- AI vs AI（原版 MCTS 与改进版对战）：
  ```
  python AI_play.py
  ```
- 人类 vs AI（您执白棋，AI 执黑棋）：
  ```
  python human_play.py
  ```

---

## 核心策略详解

### 1. 蒙特卡洛树搜索（标准 MCTS）
- 使用 UCT 公式 score = w/n + sqrt(2 * log(N) / n) 选择节点
- 模拟阶段采用 RoxannePlayer 快速走棋（基于固定优先级表）
- 默认每步思考时间 3 秒（可通过 time_limit 调整）

### 2. 启发式评估函数（heuristic_score）
用于改进 MCTS 的模拟阶段，综合以下因素：

- 位置价值：经典 8×8 权重表（角落 100，边缘 -20 等），权重 ×2
- 翻转棋子数：当前走法能翻转的棋子数 ×8
- 可行动性（两步预测）：
  - 预测对手下一步能翻转的我方棋子数，减去 5 * 最大翻转数
  - 若对手可走到高价值位置（≥80 分），额外扣 50 分
- 机动性：走完后我方合法走法数量，每步加 0.1 分

### 3. Alpha-Beta 剪枝终局搜索（AIPlayerWithAB）
- 当剩余空格数 ≤ 10（可调阈值）时，自动切换至 Alpha-Beta
- 搜索深度为剩余空格数（最多 20 层），并利用走法排序提升剪枝效率
- 评估函数 evaluate 基于棋子数差和位置价值差
- 显著提升残局决策准确性，胜率提升明显

### 4. 奇偶性与最后落子优势
启发式函数中隐含了奇偶性判断，用于捕捉最后落子优势。

---

## 自定义与扩展

您可以根据需要调整以下关键参数, 或另作修改：

- AIPlayer / HeuristicMCTSPlayer / AIPlayerWithAB 的 time_limit（思考秒数）
- AIPlayerWithAB 的 ab_threshold（启用 Alpha-Beta 的剩余空格阈值，默认 10）
- HeuristicMCTSPlayer 的 explore_prob（选择最高分走法的概率，默认 0.7）
- 位置权重表 POSITION_WEIGHT 中的数值
- 启发式函数中各分项的权重系数（*2, *8, 5 等）

---

## 注意事项

- 运行批量对战时，控制台输出较多，可适当减少 rounds 或增加 time_limit。
- Alpha-Beta 搜索在剩余空格数较多时可能耗时，建议阈值不超过 12。
- 本项目基于 Python，未使用 GPU 加速，适合中小规模实验。

---

## 贡献与许可

- 本项目为人工智能课程实验项目，欢迎提出更好的策略或改进。
- 感谢QC同学提出的奇偶性判断和两个步长的可行动性判断。


Enjoy your Reversi journey! 🎲
