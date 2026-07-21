# Design recipes

## Contents

- General hierarchy
- Static webhook notification
- Alert or incident
- KPI/status report
- Approval/action card
- Form card
- AI streaming card
- Review checklist

## General hierarchy

Use this content order:

1. Header: topic and semantic status.
2. One-line outcome/summary.
3. Compact structured details.
4. Optional evidence: table, chart, image, or collapsible detail.
5. Actions.
6. Quiet metadata such as source and update time.

Do not use every component simply because it exists. One card should answer one question.

## Static webhook notification

Use:

- root header with theme and title;
- Markdown summary;
- optional two-column metadata rows;
- one URL button;
- optional source/time line.

Start from `assets/templates/webhook-notification.json`.

Avoid input, select, picker, checker callback, form, or callback behavior. A custom bot cannot receive those actions.

## Alert or incident

Suggested structure:

- red/carmine header for critical, orange/yellow for warning;
- severity and state tags;
- Markdown summary with affected service;
- two or three metric columns for start time, duration, owner, or scope;
- collapsible panel for logs/remediation notes;
- primary URL button to open the incident;
- secondary URL for runbook.

Do not dump raw logs into the main card. Redact credentials and tokens.

## KPI/status report

Suggested structure:

- neutral blue/indigo header;
- Markdown period and headline;
- 2–4 `column_set` metrics;
- `chart` when trend/relative shape matters;
- `table` for exact values;
- small source/update-time footer.

Use `width_mode: fill`. For columns, choose `bisect`, `trisect`, or `flow` and keep labels short.

Use number formatting in table columns instead of manually formatting numeric strings when sorting/alignment matters.

Start from `assets/templates/status-report-card.json`.

## Approval/action card

Application bot only.

Suggested structure:

- title and status;
- requester/resource/amount/deadline details;
- collapsible policy or history;
- primary approve button with callback;
- danger or default reject button with `confirm`;
- view-details URL.

Return stable opaque identifiers in callback values. Re-fetch the approval state and re-authorize the operator on the server. Make callbacks idempotent.

Start from `assets/templates/application-action-card.json`.

## Form card

Application bot only.

Suggested structure:

- short instruction;
- `form` with a unique name;
- labels next to controls only when narrow-screen behavior remains readable;
- `required: true` only for essential fields;
- submit and reset buttons;
- `confirm` when submission is consequential.

Every interactive descendant must have a globally unique `name`. Do not embed a table, chart, or another form.

Start from `assets/templates/application-form-card.json`.

## AI streaming card

Application bot and CardKit streaming APIs only.

Suggested structure:

- header and compact generation state tag;
- `config.streaming_mode: true`;
- summary defaulting to a localized "generating" state;
- a Markdown component with stable `element_id`;
- optional source/citation area updated after generation;
- final actions added or enabled after the stream completes.

Do not assume setting `streaming_mode` sends incremental data. Implement the corresponding CardKit create/update/stream calls with strictly increasing sequence values where required.

## Review checklist

Content:

- Does the first screen show the outcome?
- Is every metric user-provided or explicitly marked as a placeholder?
- Is a full document/log better represented by a link?
- Are status colors semantically correct?

Layout:

- Is there only one primary action?
- Are columns responsive?
- Are margins/padding intentional rather than duplicated?
- Does dark mode remain legible?

Behavior:

- Does the delivery surface support every interaction?
- Do forms have names and a submit button?
- Are callback values non-sensitive?
- Are confirmation dialogs used for consequential actions?

Compatibility:

- Is `schema` exactly `2.0`?
- Are component/client restrictions handled with fallbacks?
- Does audio disable forwarding?
- Are IDs and component counts within limits?

Security:

- No webhook URL, secret, token, or private log data in output.
- URLs use expected schemes and domains.
- User-generated Markdown cannot inject mentions or arbitrary links.
