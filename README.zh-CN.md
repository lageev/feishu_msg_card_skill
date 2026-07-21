# 飞书卡片 JSON 2.0 Skill

[English](README.md)

这是一个用于构造、审查、校验和封装生产级飞书/Lark 卡片 JSON 2.0 Payload 的 Agent Skill。

## 能做什么

- 区分自定义机器人 Webhook、应用机器人、回调响应和 CardKit 模板等投递方式。
- 提供布局、交互、多语言、响应式设计和深色模式的实用规则。
- 内置通知、报告、操作、表单和回调响应模板。
- 校验 JSON 2.0 中常见的结构与交互错误。
- 将原始卡片封装成自定义机器人 Webhook Payload，可选生成签名，但不会发送请求。

## 安装

最简单的安装方式是运行下面的命令，然后按照交互提示选择：

```bash
npx skills add lageev/feishu_msg_card_skill
```

也可以按需要使用以下安装方式：

```bash
# 全局安装，然后通过交互提示选择 Agent
npx skills add lageev/feishu_msg_card_skill -g

# 全局安装到 Codex，并跳过所有确认提示
npx skills add lageev/feishu_msg_card_skill -g -a codex -y
```

如果希望手动安装，也可以把仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/lageev/feishu_msg_card_skill.git \
  ~/.codex/skills/feishu-card-json-v2
```

如果 Codex 没有立即发现这个 Skill，重启 Codex 即可。

## 使用

在提示词里显式调用：

```text
使用 $feishu-card-json-v2 为自定义机器人 Webhook 创建一张部署失败通知卡片。
```

Skill 会先判断投递方式，因为自定义机器人 Webhook 不支持回调、表单或数据采集。

## 校验 Payload

```bash
python3 scripts/validate_card.py path/to/payload.json
```

自动识别不明确时，可以指定模式：

```bash
python3 scripts/validate_card.py --mode custom-bot path/to/payload.json
python3 scripts/validate_card.py --mode raw path/to/payload.json
python3 scripts/validate_card.py --mode callback-response path/to/payload.json
```

只封装自定义机器人 Webhook Payload，不发送请求：

```bash
python3 scripts/wrap_webhook.py path/to/card.json
```

如果需要签名，请把密钥保存在环境变量中：

```bash
python3 scripts/wrap_webhook.py path/to/card.json \
  --secret-env FEISHU_BOT_SECRET
```

该脚本只输出 JSON，不会发送 Webhook 请求。

## 目录结构

```text
SKILL.md                    Skill 核心说明
agents/openai.yaml          Skill 展示信息
assets/templates/           可复用卡片模板
references/                 Schema、组件、设计方案和官方资料
scripts/validate_card.py    JSON 2.0 专项校验器
scripts/wrap_webhook.py     Webhook 封装与签名工具
```

## 能力边界

校验器用于发现常见构造错误，不能替代飞书服务端校验或客户端预览。请勿把 Webhook 地址、机器人密钥、应用密钥或回调 Token 写入卡片和代码仓库。

## 开源许可

[MIT](LICENSE)
