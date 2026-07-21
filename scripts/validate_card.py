#!/usr/bin/env python3
"""Validate construction-critical Feishu Card JSON 2.0 rules.

This is intentionally a focused validator, not a replacement for Feishu's
server-side validation or client preview.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ELEMENT_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,19}$")
SUPPORTED_LOCALES = {
    "zh_cn",
    "en_us",
    "zh_hk",
    "zh_tw",
    "ja_jp",
    "id_id",
    "vi_vn",
    "th_th",
    "pt_br",
    "es_es",
    "ko_kr",
    "de_de",
    "fr_fr",
    "it_it",
    "ru_ru",
    "ms_my",
}
CONTAINER_TAGS = {
    "column_set",
    "column",
    "form",
    "interactive_container",
    "collapsible_panel",
}
INTERACTIVE_TAGS = {
    "input",
    "button",
    "overflow",
    "select_static",
    "multi_select_static",
    "select_person",
    "multi_select_person",
    "date_picker",
    "picker_time",
    "picker_datetime",
    "select_img",
    "checker",
}


def iter_nodes(value: Any, path: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield from iter_nodes(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_nodes(child, f"{path}[{index}]")


def descendants(value: Any) -> Iterable[dict[str, Any]]:
    for _, node in iter_nodes(value):
        yield node


def unwrap(
    payload: dict[str, Any], requested_mode: str
) -> tuple[str, dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    mode = requested_mode

    if mode == "auto":
        if payload.get("msg_type") == "interactive" or "msg_type" in payload:
            mode = "custom-bot"
        elif isinstance(payload.get("card"), dict) and payload["card"].get("type") in {
            "raw",
            "template",
        }:
            mode = "callback-response"
        else:
            mode = "raw"

    if mode == "custom-bot":
        if payload.get("msg_type") != "interactive":
            errors.append('custom-bot payload must set "msg_type" to "interactive"')
        card = payload.get("card")
        if not isinstance(card, dict):
            errors.append('custom-bot payload must contain an object-valued "card"')
            return mode, {}, errors, warnings
        return mode, card, errors, warnings

    if mode == "callback-response":
        response_card = payload.get("card")
        if not isinstance(response_card, dict):
            errors.append('callback response must contain an object-valued "card"')
            return mode, {}, errors, warnings
        if response_card.get("type") != "raw":
            errors.append('callback response card must use "type": "raw" for raw JSON')
        card = response_card.get("data")
        if not isinstance(card, dict):
            errors.append('callback response "card.data" must be an object')
            return mode, {}, errors, warnings
        toast = payload.get("toast")
        if toast is not None and not isinstance(toast, dict):
            errors.append('"toast" must be an object when present')
        elif isinstance(toast, dict) and toast.get("type") not in {
            None,
            "info",
            "success",
            "error",
            "warning",
        }:
            errors.append("toast.type must be info, success, error, or warning")
        return mode, card, errors, warnings

    return mode, payload, errors, warnings


def validate_card(card: dict[str, Any], mode: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if card.get("schema") != "2.0":
        errors.append('card must explicitly set "schema": "2.0"')

    if "elements" in card:
        errors.append('JSON 2.0 uses "body.elements"; root "elements" is legacy')
    if "i18n_elements" in card:
        errors.append('JSON 2.0 does not support root "i18n_elements"')

    config = card.get("config", {})
    if config is not None and not isinstance(config, dict):
        errors.append('"config" must be an object')
        config = {}
    if isinstance(config, dict):
        if config.get("update_multi") is False:
            errors.append('JSON 2.0 supports only shared cards; "update_multi" cannot be false')
        locales = config.get("locales")
        if locales is not None:
            if not isinstance(locales, list) or not all(
                isinstance(item, str) for item in locales
            ):
                errors.append('"config.locales" must be an array of locale strings')
            else:
                invalid = sorted(set(locales) - SUPPORTED_LOCALES)
                if invalid:
                    errors.append(
                        "unsupported locale key(s): " + ", ".join(invalid)
                    )

    body = card.get("body")
    if body is None:
        warnings.append("card has no body")
    elif not isinstance(body, dict):
        errors.append('"body" must be an object')
    elif not isinstance(body.get("elements"), list):
        errors.append('"body.elements" must be an array')
    elif not body["elements"]:
        warnings.append("body.elements is empty")

    card_link = card.get("card_link")
    if card_link is not None:
        if not isinstance(card_link, dict):
            errors.append('"card_link" must be an object')
        else:
            default_url = card_link.get("url")
            platform_urls = [
                card_link.get("pc_url"),
                card_link.get("ios_url"),
                card_link.get("android_url"),
            ]
            if not default_url and not all(platform_urls):
                errors.append(
                    "card_link requires a non-empty url or all three platform URLs"
                )

    header = card.get("header")
    if header is not None:
        if not isinstance(header, dict):
            errors.append('"header" must be an object')
        else:
            if not isinstance(header.get("title"), dict):
                errors.append("header.title must be an object when header is present")
            tags = header.get("text_tag_list", [])
            if isinstance(tags, list) and len(tags) > 3:
                errors.append("header.text_tag_list supports at most three tags")
            i18n_tags = header.get("i18n_text_tag_list", {})
            if isinstance(i18n_tags, dict):
                for locale, locale_tags in i18n_tags.items():
                    if isinstance(locale_tags, list) and len(locale_tags) > 3:
                        errors.append(
                            f"header.i18n_text_tag_list.{locale} supports at most three tags"
                        )

    tagged_count = 0
    element_ids: dict[str, str] = {}
    form_names: dict[str, str] = {}
    max_container_depth = 0

    def visit(value: Any, path: str, container_depth: int, inside_form: bool) -> None:
        nonlocal tagged_count, max_container_depth
        if isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]", container_depth, inside_form)
            return
        if not isinstance(value, dict):
            return

        tag = value.get("tag")
        next_depth = container_depth
        if isinstance(tag, str):
            tagged_count += 1
            if tag in CONTAINER_TAGS:
                next_depth += 1
                max_container_depth = max(max_container_depth, next_depth)

        element_id = value.get("element_id")
        if element_id is not None:
            if not isinstance(element_id, str) or not ELEMENT_ID_RE.fullmatch(element_id):
                errors.append(f"{path}.element_id has an invalid format")
            elif element_id in element_ids:
                errors.append(
                    f'duplicate element_id "{element_id}" at {path} and {element_ids[element_id]}'
                )
            else:
                element_ids[element_id] = path

        now_inside_form = inside_form or tag == "form"
        if inside_form and tag in {"form", "table", "chart"}:
            errors.append(f"{path}: {tag} cannot be nested inside a form")

        if now_inside_form and tag in INTERACTIVE_TAGS:
            name = value.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"{path}: interactive component inside form requires name")
            elif name in form_names:
                errors.append(
                    f'duplicate form component name "{name}" at {path} and {form_names[name]}'
                )
            else:
                form_names[name] = path

        if tag == "form":
            submit_found = any(
                node.get("tag") == "button"
                and (
                    node.get("form_action_type") == "submit"
                    or node.get("action_type") == "form_submit"
                )
                for node in descendants(value.get("elements", []))
            )
            if not submit_found:
                errors.append(f"{path}: form requires a submit button")

        if tag == "collapsible_panel" and any(
            node.get("tag") == "form"
            for node in descendants(value.get("elements", []))
        ):
            errors.append(f"{path}: collapsible_panel cannot contain form")

        if tag == "audio":
            if not value.get("file_key"):
                errors.append(f"{path}: audio requires file_key")
            if not isinstance(config, dict) or config.get("enable_forward") is not False:
                errors.append(
                    f"{path}: a card containing audio must set config.enable_forward to false"
                )

        behaviors = value.get("behaviors")
        if behaviors is not None and not isinstance(behaviors, list):
            errors.append(f"{path}.behaviors must be an array")

        if mode == "custom-bot" and tag in INTERACTIVE_TAGS:
            behavior_types = {
                behavior.get("type")
                for behavior in behaviors or []
                if isinstance(behavior, dict)
            }
            if "callback" in behavior_types:
                errors.append(f"{path}: custom-bot cards do not support callback behavior")
            if tag == "button" and "open_url" not in behavior_types:
                errors.append(
                    f"{path}: custom-bot buttons must provide an open_url behavior"
                )
            if tag not in {"button", "overflow"}:
                warnings.append(
                    f"{path}: {tag} cannot provide server interaction through a custom bot"
                )

        for key, child in value.items():
            visit(child, f"{path}.{key}", next_depth, now_inside_form)

    visit(card, "$", 0, False)

    if tagged_count > 200:
        errors.append(f"card contains {tagged_count} tagged elements; maximum is 200")
    if max_container_depth > 5:
        errors.append(
            f"card container nesting depth is {max_container_depth}; maximum is 5"
        )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate construction-critical Feishu Card JSON 2.0 rules."
    )
    parser.add_argument("payload", type=Path, help="JSON payload path, or - for stdin")
    parser.add_argument(
        "--mode",
        choices=("auto", "raw", "custom-bot", "callback-response"),
        default="auto",
        help="payload envelope type (default: auto)",
    )
    args = parser.parse_args()

    try:
        if str(args.payload) == "-":
            payload = json.load(sys.stdin)
        else:
            with args.payload.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(payload, dict):
        print("ERROR: root JSON value must be an object", file=sys.stderr)
        return 2

    mode, card, errors, warnings = unwrap(payload, args.mode)
    if card:
        card_errors, card_warnings = validate_card(card, mode)
        errors.extend(card_errors)
        warnings.extend(card_warnings)

    print(
        f"mode={mode} errors={len(errors)} warnings={len(warnings)}",
        file=sys.stderr if errors else sys.stdout,
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
