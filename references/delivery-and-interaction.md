# Delivery and interaction

## Contents

- Decision table
- Custom-bot webhook
- Application bot
- Behaviors
- Forms
- Callback request and response
- Updating
- Streaming
- Security checklist

## Decision table

| Need | Choose |
|---|---|
| Send a static card to one fixed group with minimal setup | Custom-bot webhook |
| Send to users, multiple chats, or use OpenAPI capabilities | Application bot |
| Receive clicks, submit forms, or update after interaction | Application bot |
| Reuse a visual template with variables | CardKit template |
| Stream AI-generated text | Application bot and CardKit streaming APIs |

## Custom-bot webhook

Use this envelope:

```json
{
  "msg_type": "interactive",
  "card": {
    "schema": "2.0",
    "config": {
      "update_multi": true
    },
    "body": {
      "elements": []
    }
  }
}
```

Capabilities and restrictions:

- Sends only to the group containing that custom bot.
- Does not need application API permissions.
- Supports static content and URL navigation.
- Does not support request callbacks, form submission, server-side user interaction, or subsequent card updates.
- Raw JSON delivery does not provide CardKit template variables.
- May use keyword, IP allowlist, or signature protection.

Never reveal a webhook URL. Treat it as a credential.

If signature verification is enabled, add:

```json
{
  "timestamp": "UNIX_SECONDS",
  "sign": "BASE64_HMAC_SHA256"
}
```

The official algorithm builds `timestamp + "\n" + secret`, uses that value as the HMAC-SHA256 key over an empty message, and Base64-encodes the digest. The timestamp must be within one hour and the server clock must be accurate. Use `scripts/wrap_webhook.py` so the secret remains in an environment variable.

## Application bot

Use an application bot for:

- sending to users, groups, or multiple conversations;
- callback behaviors;
- inputs, selectors, pickers, forms, and approvals;
- OpenAPI card updates;
- streaming updates;
- application-owned image and file resources.

Resource keys are scoped: upload an image/audio file with the same application that sends the card.

For API send calls, card content is often serialized as the `content` of an `interactive` message. Follow the exact server API or SDK signature requested by the user; do not confuse this API envelope with the custom-bot `card` envelope.

## Behaviors

`behaviors` is an array. Use `open_url` or `callback`.

Open URL:

```json
{
  "type": "open_url",
  "default_url": "https://example.com",
  "pc_url": "https://example.com",
  "ios_url": "https://example.com",
  "android_url": "https://example.com"
}
```

Callback:

```json
{
  "type": "callback",
  "value": {
    "action": "approve",
    "entity_id": "${ENTITY_ID}"
  }
}
```

Keep callback values opaque and small. Never place secrets, privileged claims, prices to charge, or authorization decisions in callback values. Re-fetch authoritative state and authorize the operator on the server.

Use `confirm` for destructive or consequential actions. A confirmation dialog contains `title` and `text`, each with a `plain_text` object.

## Forms

A form:

- has `tag: form`, a globally unique `name`, and `elements`;
- cannot contain another form, a table, or a chart;
- must contain a submit button;
- requires every interactive descendant to have a globally unique `name`;
- delays child interactions until the submit button is used;
- returns submitted values in `event.action.form_value`.

Submit button:

```json
{
  "tag": "button",
  "name": "submit_request",
  "form_action_type": "submit",
  "text": {
    "tag": "plain_text",
    "content": "提交"
  },
  "type": "primary_filled"
}
```

Use `form_action_type: reset` for a reset button. Prefer the current `form_action_type` field over historical `action_type`.

## Callback request and response

Subscribe to callback type `card.action.trigger`.

The current callback envelope uses:

- root `schema: "2.0"`;
- `header.event_id`, `token`, `create_time`, `event_type`, `tenant_key`, and `app_id`;
- `event.operator`;
- `event.token`, valid for 30 minutes and usable for at most two updates;
- `event.action.value`, `tag`, `timezone`, `name`, and form/input/option fields;
- `event.context.open_message_id` and `open_chat_id`.

Respond within three seconds with HTTP 200. Do not redirect. Choose one:

1. Return a toast and optional immediate replacement card.
2. Return only a toast/no card.
3. Acknowledge first, then update within 30 minutes using the callback token.

Immediate raw-card response:

```json
{
  "toast": {
    "type": "success",
    "content": "处理成功",
    "i18n": {
      "zh_cn": "处理成功",
      "en_us": "Completed"
    }
  },
  "card": {
    "type": "raw",
    "data": {
      "schema": "2.0",
      "body": {
        "elements": []
      }
    }
  }
}
```

Toast types: `info`, `success`, `error`, `warning`.

Preserve schema generation: a JSON 2.0 card cannot be replaced with JSON 1.0.

## Updating

JSON 2.0 updates are shared: every recipient sees the same new state.

Use:

- immediate callback response for sub-three-second work;
- callback token update for work completed within 30 minutes;
- message/card update OpenAPI for changes initiated outside a click;
- CardKit element APIs when operating on stable `element_id` components.

When an API uses `sequence`, make each update strictly greater than the prior one. Design idempotency around callback `event_id`.

The JSON 2.0 interaction and update lifetime is 14 days.

## Streaming

Set `config.streaming_mode: true` and use CardKit streaming APIs. A JSON flag alone does not perform transport updates.

Use stable `element_id` values on streamed components. Configure print frequency/step conservatively. Prefer `fast` for ordinary token streaming and `delay` when the final text should arrive before client animation completes.

Do not use custom-bot webhooks for streaming or updating.

## Security checklist

- Keep webhook URLs, bot secrets, app secrets, tokens, and callback tokens out of source files and card bodies.
- Verify callback signatures/tokens according to the application event-subscription configuration.
- Deduplicate callback `event_id`.
- Authorize the operator independently of client-provided values.
- Validate every returned URL against the intended scheme/domain policy.
- Escape user-generated Markdown and do not let user input create arbitrary mentions or links.
- Acknowledge callbacks before long-running work.
- Never log full callback/update tokens.
