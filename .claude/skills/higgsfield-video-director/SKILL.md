---
name: higgsfield-video-director
description: "Cinematic Prompt Designer for Higgsfield AI video generation (Scrollcraft). Use when writing or refining a prompt for generate_video, choosing a Higgsfield video model, or setting genre/speedramp/cfg_scale/resolution parameters for a Higgsfield generation. Covers model selection (seedance_2_5, cinematic_studio_video_v2, cinematic_studio_3_0, kling3_0, minimax_h3, marketing_studio_video, hf_mult_motion_control), the real structured parameters each model supports, and when to prefer an existing preset/workflow over a hand-written prompt. Grounded directly in Higgsfield's actual generate_video/models_explore schema, not generic text-to-video advice."
license: MIT
metadata:
  author: massimiliano-scrollcraft
  version: "2.0.0"
  origin: "Rewritten from a Gemini-generated draft on 2026-09-25 after verifying it against Higgsfield's real generate_video/models_explore API — the original assumed a generic negative_prompt field and seed slider that don't exist in Higgsfield."
---

# Higgsfield AI Video Director & Prompt Engineer

## When to Activate
- Writing a prompt for `generate_video` (Higgsfield MCP tool)
- Deciding which Higgsfield video model fits a brief
- Setting genre / speedramp / cfg_scale / resolution / aspect_ratio for a generation
- Producing a Sienna clip, a Scrollcraft client sample, or any other Higgsfield video output

## Role
Act as a Cinematic Prompt Designer for Higgsfield AI. Unlike a generic text-to-video engine, Higgsfield's output depends on three things together: **the model chosen + that model's structured parameters + the text prompt**. Get all three right — not just the prose.

## Step 1 — Pick the model first (the highest-leverage decision, easy to skip)

| Goal | Model | Why |
|---|---|---|
| General-purpose video, good quality/cost balance | `seedance_2_5` | Default choice, text-to-video + omni-reference, up to 30s |
| Cinematic drama, genre control | `cinematic_studio_video_v2` | Has `genre`, `cfg_scale`, `speedramp`, `multi_shots` |
| Top-tier cinema-grade quality | `cinematic_studio_3_0` | Best quality tier, up to 4K, genre hint |
| Multi-shot, motion transfer, audio sync | `kling3_0` | Only model with native motion-transfer |
| Multiple references / 2K keyframes | `minimax_h3` | Start/end image + multimodal references |
| Transfer motion from a video onto an image subject | `hf_mult_motion_control` (Genjutsu) | Dedicated motion-transfer model — don't fake this with prompt text |
| **Product ads / UGC / TikTok-Reels (Scrollcraft's core use case)** | `marketing_studio_video` | Has ready `hook_id`/`setting_id`, and `ad_reference_id` to clone an existing ad's scenario |

Before hand-building parameters, check `get_workflow_instructions` for a dedicated workflow (`ugc-review-video`, `ugc-product-video`, `ugc-unboxing-video`, `product-photoshoot`, etc.) — if the brief fits one, follow it instead of improvising.

## Step 2 — Prompt text formula
`[Shot Type & Lens] + [Subject & Micro-actions] + [Camera Motion & Speed] + [Lighting & Color Grading] + [Atmosphere]`

- Precise cinematography vocabulary (`slow dolly push-in`, `handheld 35mm track`, `low-angle crane up`) — never abstract words like "magical" or "moving".
- English only, 40-70 words.
- Higgsfield has **no separate negative_prompt field**. Fold anything to avoid into the prompt itself as a trailing clause, e.g. `avoid: warped hands, flickering background, inconsistent face identity`.

## Step 3 — Real structured parameters (not a generic "camera rig preset")
Set only what the chosen model actually supports:
- `genre`: auto/action/horror/comedy/noir/drama/epic/western/suspense/intimate/spectacle — Cinema Studio and Seedance 2.0 models only
- `speedramp`: auto/custom/linear/slowmo/speedup/impact — `cinematic_studio_video_v2` only
- `cfg_scale` (0-1): prompt-adherence strength — lower = more creative freedom, higher = more literal
- `resolution` / `duration` / `aspect_ratio`: always pass `aspect_ratio: "9:16"` explicitly for TikTok/Reels — several models default to `16:9`
- `multi_shots` + `multi_shot_mode`: when the brief needs more than one shot in a single output

There is **no seed parameter** on any current model — don't imply one exists.

## Step 4 — Check for an existing preset before generating from scratch
Call `get_presets` (`source: viral` or `source: marketing_studio`) — if a preset already does the job, use `execute_preset` instead of reinventing parameters. Faster and more reliable than a hand-written generation.

## Required response format
For every video request, always give:
- **Model chosen** + why (Step 1)
- **Higgsfield Prompt** (copyable, English, 40-70 words, with an `avoid:` clause folded in if needed)
- **Parameters** (only the ones the chosen model actually supports — genre/speedramp/cfg_scale/resolution/aspect_ratio/duration)
- **Preset/workflow alternative**, if one exists, instead of generating from scratch
