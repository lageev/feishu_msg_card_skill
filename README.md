# Feishu Card JSON 2.0 Skill

[简体中文](README.zh-CN.md)

An agent skill for creating, reviewing, validating, and packaging production-oriented Feishu/Lark Card JSON 2.0 payloads.

## What it provides

- Guidance for custom-bot webhooks, application bots, callback responses, and CardKit templates.
- Practical rules for layout, interaction, localization, responsive design, and dark mode.
- Reusable templates for notifications, reports, actions, forms, and callback responses.
- A focused validator for common JSON 2.0 construction errors.
- A helper that wraps a raw card in a custom-bot webhook envelope without sending it.

## Install

The simplest option is to follow the interactive prompts:

```bash
npx skills add lageev/feishu_msg_card_skill
```

Optional installation modes:

```bash
# Install globally, then choose an agent interactively
npx skills add lageev/feishu_msg_card_skill -g

# Install globally for Codex without confirmation prompts
npx skills add lageev/feishu_msg_card_skill -g -a codex -y
```

You can also install manually by cloning the repository into your Codex skills directory:

```bash
git clone https://github.com/lageev/feishu_msg_card_skill.git \
  ~/.codex/skills/feishu-card-json-v2
```

Restart Codex if the skill is not discovered immediately.

## Use

Invoke the skill explicitly in your prompt:

```text
Use $feishu-card-json-v2 to create a deployment-failure notification for a custom bot webhook.
```

The skill first distinguishes the delivery surface because custom-bot webhooks do not support callbacks, forms, or data collection.

## Validate a payload

```bash
python3 scripts/validate_card.py path/to/payload.json
```

Select a mode when automatic envelope detection is ambiguous:

```bash
python3 scripts/validate_card.py --mode custom-bot path/to/payload.json
python3 scripts/validate_card.py --mode raw path/to/payload.json
python3 scripts/validate_card.py --mode callback-response path/to/payload.json
```

Wrap a raw card for a custom-bot webhook without sending it:

```bash
python3 scripts/wrap_webhook.py path/to/card.json
```

To add a signature, keep the signing secret in an environment variable:

```bash
python3 scripts/wrap_webhook.py path/to/card.json \
  --secret-env FEISHU_BOT_SECRET
```

The helper writes JSON only. It never sends a webhook request.

## Repository layout

```text
SKILL.md                    Core skill instructions
agents/openai.yaml          Skill display metadata
assets/templates/           Reusable card payloads
references/                 Schema, components, recipes, and sources
scripts/validate_card.py    Focused JSON 2.0 validator
scripts/wrap_webhook.py     Custom-bot envelope/signature helper
```

## Scope

The validator catches common construction mistakes but does not replace Feishu server-side validation or client preview. Keep webhook URLs, bot secrets, app secrets, and callback tokens out of card payloads and source control.

## License

[MIT](LICENSE)
