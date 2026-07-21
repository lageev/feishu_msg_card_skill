# Core schema, content, and style

## Contents

- Root structure and invariants
- Global config
- Layout
- Header and navigation
- Text, Markdown, and mentions
- Colors, icons, and themes
- Localization
- Limits and compatibility

## Root structure and invariants

Use this shape:

```json
{
  "schema": "2.0",
  "config": {},
  "card_link": {},
  "header": {},
  "body": {
    "direction": "vertical",
    "padding": "12px",
    "vertical_spacing": "8px",
    "elements": []
  }
}
```

All root fields are optional to the platform, but a useful card should contain `body.elements`, and usually a `header`. JSON 2.0 must explicitly set `schema` to `"2.0"`.

JSON 2.0 changes to remember:

- Place components under `body.elements`, not root `elements`.
- Do not use root `i18n_elements`; use component-local `i18n_*` fields.
- Do not use the legacy `action` module as a button group. Compose buttons with `column_set` or use `overflow`.
- Do not use `update_multi: false`.
- Do not use the removed Markdown differentiated-link syntax `[text]($urlVal)` with `href`.
- Do not use `stretch_without_padding` for full-width images; use negative horizontal margin.

## Global `config`

Useful fields:

| Field | Meaning |
|---|---|
| `streaming_mode` | Enable progressive rendering. Default `false`. |
| `streaming_config` | Configure print frequency, step, and `fast`/`delay` strategy. |
| `summary` | Chat-list preview; supports `content` and `i18n_content`. |
| `locales` | Restrict effective languages. |
| `enable_forward` | Allow forwarding. Default `true`. |
| `update_multi` | Shared-card behavior. JSON 2.0 supports only `true`. |
| `width_mode` | `default`, `compact`, or `fill`. |
| `use_custom_translation` | Use provided localized content as translation results. |
| `enable_forward_interaction` | Preserve callback interaction after forwarding. Default `false`. |
| `style.text_size` | Define named desktop/mobile text sizes. |
| `style.color` | Define named light/dark RGBA colors. |

Streaming configuration example:

```json
{
  "streaming_mode": true,
  "streaming_config": {
    "print_frequency_ms": {
      "default": 30,
      "android": 25,
      "ios": 40,
      "pc": 50
    },
    "print_step": {
      "default": 2,
      "android": 3,
      "ios": 4,
      "pc": 5
    },
    "print_strategy": "fast"
  }
}
```

## Layout

The root body and layout containers share these concepts:

- `direction`: `vertical` or `horizontal`.
- `padding`: one, two, or four CSS-like values; normally `0px`–`99px`.
- `margin`: one, two, or four values; components generally allow `-99px`–`99px`.
- `horizontal_spacing`, `vertical_spacing`: `small`/4px, `medium`/8px, `large`/12px, `extra_large`/16px, or an explicit 0–99px value.
- `horizontal_align`: `left`, `center`, `right`.
- `vertical_align`: `top`, `center`, `bottom`.

Do not create horizontal layouts with long unbounded text. For `column_set`, use a responsive `flex_mode`:

- `none`: retain columns and compress proportionally;
- `stretch`: stack columns at full width;
- `flow`: wrap columns;
- `bisect`: two equal columns;
- `trisect`: three equal columns.

Use weighted columns for label/value layouts. Keep labels short and values dominant.

## Header and card navigation

The root `header` supports:

- required `title` when the header exists;
- optional `subtitle`;
- `text_tag_list` and localized `i18n_text_tag_list`, maximum three tags per locale;
- `template`: `blue`, `wathet`, `turquoise`, `green`, `yellow`, `orange`, `red`, `carmine`, `violet`, `purple`, `indigo`, `grey`, or `default`;
- standard/custom `icon`;
- `padding`.

`card_link` makes the whole card navigable. Provide `url`, or provide all of `pc_url`, `ios_url`, and `android_url`. If both default and client-specific URLs are present, the official root-card behavior gives precedence to `url`. Use `lark://msgcard/unsupported_action` to disable a client.

Avoid combining a whole-card link with dense nested interactive controls unless the intended click priority is obvious.

## Text, Markdown, and mentions

Use `div` with a `plain_text` or `lark_md` text object for controlled plain content. Use the `markdown` component for rich content.

JSON 2.0 Markdown supports CommonMark except `HTMLBlock`, plus selected Feishu tags. Supported patterns include:

- headings, emphasis, block quotes, ordered/unordered lists, code, fenced code, links, images, horizontal rules, and tables;
- `<at id=open_id></at>` or `<at ids=id_01,id_02></at>` for mentions;
- `<text_tag color='red'>...</text_tag>`;
- `<number_tag>1</number_tag>`;
- `<link icon='chat_outlined' url='https://...'>...</link>`;
- `<person id='...' show_name=true show_avatar=true style='normal'></person>`;
- `<local_datetime millisecond='...' format_type='date'></local_datetime>`;
- `<audio ...></audio>` on supported clients.

Mention rules:

- Markdown `<at>` notifies the mentioned person when supported.
- `person` and `person_list` only display identity and do not notify.
- Custom bots support `open_id` and `user_id` mentions, not `email` or `union_id`.
- Forwarded cards do not re-notify mentioned users.

Markdown tables show at most five data rows per page and at most four Markdown tables in one Markdown component. Use the `table` component for typed data, alignment, widths, or larger datasets.

## Colors, icons, and themes

Prefer semantic built-in colors. When custom colors are necessary, define a named pair:

```json
{
  "config": {
    "style": {
      "color": {
        "brand_accent": {
          "light_mode": "rgba(51,112,255,1)",
          "dark_mode": "rgba(100,145,255,1)"
        }
      }
    }
  }
}
```

Then use `"brand_accent"` in a supported color property. Always define both modes and maintain readable contrast.

Standard icons use:

```json
{
  "tag": "standard_icon",
  "token": "chat_outlined",
  "color": "blue"
}
```

Custom icons use `tag: custom_icon` and a real `img_key`. Do not fabricate icon tokens or keys. Consult the official icon library for exact tokens.

## Localization

Supported locale keys:

`zh_cn`, `en_us`, `zh_hk`, `zh_tw`, `ja_jp`, `id_id`, `vi_vn`, `th_th`, `pt_br`, `es_es`, `ko_kr`, `de_de`, `fr_fr`, `it_it`, `ru_ru`, `ms_my`.

Common mappings:

| Base field | Localized field |
|---|---|
| `content` | `i18n_content` |
| `default_value` | `i18n_default_value` |
| `img_key` | `i18n_img_key` |
| `file_key` | `i18n_file_key` |
| `text_tag_list` | `i18n_text_tag_list` |

Keep base content as a fallback. If a viewer language is not supplied, Feishu chooses an available fallback, commonly English when present.

## Limits and compatibility

- JSON 2.0 requires Feishu client 7.20 or later. Older clients show the header and an upgrade fallback for the body.
- A card supports at most 200 tagged elements/components.
- Keep container nesting to at most five levels.
- JSON 2.0 is shared-card only; updating affects every recipient.
- Interactive and update lifetime for JSON 2.0 is 14 days.
- Add component-specific fallbacks for newer client-gated components.
- A card with `audio` requires client 7.49+, OPUS media, `enable_forward: false`, and cannot use the API that sends a card visible only to specified users.
