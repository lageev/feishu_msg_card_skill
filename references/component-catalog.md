# Component catalog

## Contents

- Shared rules
- Containers
- Display components
- Interactive components
- Nesting rules

## Shared rules

All body components use a `tag`. Most support `element_id` and `margin`. `element_id` must be globally unique, begin with a letter, contain only letters/numbers/underscore, and contain at most 20 characters.

Use exact component documentation when applying uncommon fields. The table below captures the construction-critical fields and limits.

## Containers

| Component | Tag | Core fields | Key rules |
|---|---|---|---|
| Columns | `column_set` | `columns`, `flex_mode`, spacing, alignment, background, action | Each child uses `tag: column`, `elements`, width/weight, padding and alignment. Use responsive flex modes. |
| Form | `form` | `name`, `elements`, direction/spacing | Application bot only. Must contain submit button. No nested form/table/chart. Interactive descendants need unique `name`. |
| Interactive container | `interactive_container` | `elements`, `behaviors`, width/height, background, border, disabled/confirm | Inner interactive controls take click priority. Use for clickable compound rows/cards. |
| Collapsible panel | `collapsible_panel` | `expanded`, `header`, `elements`, border/background/layout | JSON-only; no nested form; use for secondary content. |

The CardKit-only recycling container is not expressible as raw Card JSON. Use a published template and object-array variables instead.

## Display components

| Component | Tag/location | Core fields | Key rules |
|---|---|---|---|
| Header | root `header` | `title`, `subtitle`, `text_tag_list`, `template`, `icon`, `padding` | Only one root header. At most three suffix tags per locale. |
| Plain text | `div` | `text`, optional `icon`, `width` | `text.tag` is `plain_text` or `lark_md`. |
| Rich text | `markdown` | `content`, `text_align`, `text_size`, optional `icon` | Supports CommonMark except HTMLBlock and selected Feishu HTML-like tags. |
| Image | `img` | `img_key`, `alt`, `scale_type`, `size`, `corner_radius`, `preview` | `img_key` and `alt` required. Use negative margin for full bleed. |
| Multi-image | `img_combination` | `combination_mode`, `img_list` | Modes: `double`, `triple`, `bisect` (up to 6), `trisect` (up to 9). |
| Person | `person` | `user_id`, `size`, `show_avatar`, `show_name`, `style` | Displays identity; does not notify. ID may be open/user/union ID where supported. |
| Person list | `person_list` | `persons`, `lines`, display flags, size | Can ignore invalid IDs with `drop_invalid_user_id`; displays identities only. |
| Chart | `chart` | `chart_spec`, `aspect_ratio`, `color_theme`, `preview`, `height` | Uses VChart spec; no JavaScript. Test mobile compatibility. |
| Table | `table` | `columns`, `rows`, `page_size`, `row_height`, header style | Max five tables/card, 50 columns/table, and page size 1–10. |
| Audio | `audio` | `file_key`, `audio_id`, playback/time/style fields, fallback | OPUS only, V7.49+, JSON-only, set `enable_forward: false`. |
| Divider | `hr` | optional `margin` | Prefer whitespace unless a strong section boundary is needed. |

Table column data types:

- `text`: plain text;
- `lark_md`: limited Markdown;
- `options`: one or more colored tags;
- `number`: numeric alignment and optional symbol/precision formatting;
- `persons`: one or more user IDs;
- `date`: Unix millisecond timestamp rendered in the viewer's timezone;
- `markdown`: full Markdown.

Chart supports VChart definitions for line, area, bar/column, donut, pie, combo, funnel, scatter, radar, linear/circular progress, and word cloud. Desktop and mobile clients may embed different VChart versions; avoid JavaScript formatters and unsupported SVG/background features.

## Interactive components

These components require an application bot for server callbacks. Inside a form, add unique `name` and use `required` only where meaningful.

| Component | Tag | Core fields | Key rules |
|---|---|---|---|
| Input | `input` | `placeholder`, `default_value`, `width`, `max_length`, `input_type`, rows/resize, label, `behaviors` | `name` required in form. Use `max_length` 1–1000. |
| Button | `button` | `text`, `type`, `size`, `width`, `icon`, `behaviors`, `confirm` | Text max 100 chars. In form add `name` and `form_action_type`. |
| Overflow actions | `overflow` | `options`, `width`, `behaviors`, `confirm` | Use for lower-priority actions. Each option provides text and URL/callback data. |
| Static single select | `select_static` | `options`, `placeholder`, initial selection, `behaviors` | Options carry text, value, and optional icon. |
| Static multi-select | `multi_select_static` | `options`, `placeholder`, initial selections, `behaviors` | Callback returns `options`; form returns an array. |
| Person single select | `select_person` | `options`, `placeholder`, initial selection, `behaviors` | Restrict `options` when only specified people are allowed. |
| Person multi-select | `multi_select_person` | `options`, `placeholder`, initial selections, `behaviors` | Returns multiple IDs. |
| Date picker | `date_picker` | `initial_date`, `placeholder`, `behaviors` | Date format `yyyy-MM-dd`; callback includes timezone. |
| Time picker | `picker_time` | `initial_time`, `placeholder`, `behaviors` | Time format `HH:mm`; explain the business timezone. |
| Datetime picker | `picker_datetime` | `initial_datetime`, `placeholder`, `behaviors` | Format `yyyy-MM-dd HH:mm`; callback includes timezone. |
| Image picker | `select_img` | `options`, `multi_select`, `layout`, `aspect_ratio`, `behaviors` | JSON-only. Multi-select must be inside a form. |
| Checker | `checker` | `checked`, `text`, optional buttons/style, `behaviors` | JSON-only. Without behavior, the check is local-only. Max three embedded buttons. |

Common interactive fields:

- `disabled` and `disabled_tips`;
- `hover_tips`;
- `confirm`;
- `behaviors`;
- `name` and `required` in a form;
- `width`: `default`, `fill`, or a supported explicit pixel width.

## Nesting rules

- Keep container nesting at five levels or fewer.
- `column_set` columns can contain display and interactive components and supported containers.
- A form cannot contain `form`, `table`, or `chart`.
- A collapsible panel cannot contain `form`.
- Table does not contain arbitrary child components; its content is row data interpreted by column types.
- Chart content is VChart JSON, not card components.
- Inner controls take priority over an outer interactive container or column action.
- Avoid nested horizontal layouts; they collapse poorly on narrow clients.
- Use explicit `fallback` on version-gated controls.
