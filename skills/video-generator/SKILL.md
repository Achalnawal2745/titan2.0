---
name: "video-generator"
description: "Specialized skill for video generator workflows and automation."
---

# Video Generation

## Workflow Overview

1. **Phase 1: Initial** → Gather requirements, STOP for user confirmation
2. **Phase 2: Global Definitions** → Define style, characters, voices, BGM (text only, no images)
3. **Phase 3: Clip Planning** → Segment into clips, plan each clip, determine reference image needs
4. **Phase 4: Reference Images** → Generate reference images (MANDATORY before Phase 5)
5. **Phase 5: Execution** → Generate keyframes, videos, audio

---

## Critical Rules (MUST Follow)

Before starting, memorize these non-negotiable rules:

1. **[PHASE 1 STOP]** MUST ask questions to gather information. DO NOT assume or guess missing details—always ask the user. Never proceed without explicit user confirmation.

2. **[DETAILED VIDEO PROMPT]** Video prompts must include detailed transition_description (2-4 sentences). One-line prompts are insufficient.

3. **[KEYFRAME DIFFERENCE]** Last keyframe must show interpolatable change from first keyframe: subject position/pose, subject state (open/close, appear/disappear), or composition change. Subtle-only changes (lighting, background) while subject stays static cause unnatural video motion.

4. **[PHASE 4 MANDATORY]** MUST generate reference images before keyframes. Never skip Phase 4.

5. **[ASPECT RATIO]** ALL keyframes must use 16:9 or 9:16, and must be upright (not rotated). Never generate 1:1 or other ratios.

6. **[NO TTS FOR ON-SCREEN]** Never use TTS for on-screen dialogue or singing. Video model generates audio with lip sync.

7. **[NARRATION CLIP BY CLIP]** Generate off-screen narration separately for each clip, not all at once.

8. **[AUDIO MIXING]** When combining audio tracks (video audio, narration, BGM), preserve ALL tracks—overlay, never replace. Narration must be clearly audible and maintain consistent volume across all clips.

---

## Image Generation Tools

| Tool | Use When |
|------|----------|
| `generate_image` | Create new images (with or without references) |
| `generate_image_variation` | Edit existing images |

---

## Phase 1: Initial

### Gather Information

| Field | Description |
|-------|-------------|
| Purpose | Goal and target audience |
| Narrative arc | Story structure and key points |
| Duration | Total length in seconds |
| Aspect ratio | 16:9 or 9:16 only |
| Visual style | Sub-genre aesthetic (e.g., "Makoto Shinkai anime", "Pixar 3D") |
| Reference materials | Reference videos, images, brand guidelines |
| Language | For dialogue and narration |
| Recurring elements | Characters/objects with appearance descriptions |
| Dialogue/singing needs | On-screen character audio |
| Narration needs | Off-screen narrator (gender, tone, pace) |


### Five-Dimension Expert Framework

Use these perspectives to guide your questions:

| Dimension | Expert Role | Key Questions |
|-----------|-------------|---------------|
| **Strategy & Audience** | Creative Director | Who is this for? What's the goal? What action should viewers take? |
| **Narrative & Structure** | Screenwriter | What's the story? Key moments? Emotional arc? |
| **Visual Style** | Director + Art Director | What look and feel? Reference videos/images? Color mood? |
| **Shot Execution** | Cinematographer | Any specific shots in mind? Product hero shots needed? |
| **Sound Design** | Sound Designer | Voiceover? Music mood? Dialogue? Sound effects? |

Ask questions across all dimensions. Prioritize based on user's initial description.

> **[MANDATORY STOP - DO NOT PROCEED WITHOUT USER CONFIRMATION]**
> Summarize gathered information and wait for user confirmation before Phase 2.

---

## Phase 2: Global Definitions (Text Only)

### Visual Style Specification

Define these 4 dimensions (applied to primary reference images in Phase 4):

| Dimension | Example Values |
|-----------|----------------|
| **Sub-genre** | Makoto Shinkai anime, Pixar 3D, cyberpunk noir |
| **Rendering + Line** | 2D hand-drawn with thick outlines, 3D cel-shading |
| **Color + Lighting** | High saturation neon, soft diffused natural light |
| **Detail density** | Minimalist, highly detailed backgrounds |

**Example specification:**

```
Sub-genre: Cyberpunk anime
Rendering + Line: 2D digital painting, thin glowing outlines
Color + Lighting: High saturation neon (pink, cyan, purple), dark backgrounds, rim lighting
Detail density: Highly detailed backgrounds, moderate character detail
```

### Recurring Elements

For each character/object:

| Field | Description |
|-------|-------------|
| unique_identifier | Name for reference |
| appearance | Text description for prompts |
| outfit_description | Clothing/accessories (characters) |
| language | Spoken/sung language (if applicable) |
| mechanical_properties | Physical behavior (if applicable) |

### Voice Profiles

- **On-screen**: From character definitions (dialogue/singing)
- **Off-screen narrator**: name, gender, tone, pace, language

### BGM Source Decision

| Scenario | BGM Source |
|----------|------------|
| Music video / diegetic music (visible source) | **Embedded** (in video prompt) |
| Background mood music | **Separate** (Phase 5 BGM Preparation) |
| No music | **None** |

**If Separate**, define: genre, instruments, tempo

---

## Phase 3: Clip Planning

### Segmentation Rules

- Clips: **4, 6, or 8 seconds only**
- Each clip: **one action, one scene**

### Per-Clip Specification

| Field | Values |
|-------|--------|
| **narrative_purpose** | establish / develop / climax / resolve / transition / supplementary (product shot, detail, reaction, insert, B-roll, POV) |
| **pacing** | slow / moderate / fast |
| **scene** | Environment description |
| **content_action** | Subject + action + trajectory |
| **transition_description** | **[REQUIRED]** Detailed transition process. Must include: subject appearance, movement trajectory, state changes, existence statements. 2-4 sentences minimum. |
| **duration** | 4 / 6 / 8 |
| **camera_movement** | static / pan / tilt / dolly / zoom / crane / arc / handheld |
| **first_keyframe_framing** | Shot size + angle + composition |
| **first_keyframe_visible_content** | What's visible |
| **last_keyframe_framing** | Shot size + angle + composition |
| **last_keyframe_visible_content** | What's visible |
| **last_keyframe_edit_from_first** | yes / no (see decision table below) |
| **inter_clip_boundary** | continuous / scene_cut |
| **first_keyframe_reuse** | yes / no |
| **last_keyframe_required** | yes / no |
| **on_screen_dialogue** | "Name: text" or "Name: [lyrics] (style)" or None |
| **sound_effects** | Sources or None |
| **bgm_source** | embedded / separate / none |
| **bgm_cue** | If embedded: style, BPM, instruments. If separate: emotion, intensity |
| **narration_cue** | Narrator text or None |

### Field Dependencies

- `inter_clip_boundary = continuous` → next clip's `first_keyframe_reuse = yes`
- `first_keyframe_reuse = yes` → previous clip must have `last_keyframe_required = yes`

### Keyframe Difference Requirement

When planning `last_keyframe_visible_content`, ensure interpolatable change from `first_keyframe_visible_content`:
- Subject position/pose change (movement, rotation, action)
- Subject state change (open/close, appear/disappear, expression)
- Composition change from camera movement (zoom, pan result)

> **[WARNING]** Avoid last keyframes with only lighting or background changes while subject remains static—this causes unnatural video motion.

### Decision: last_keyframe_edit_from_first

| Camera Movement | First & Last Keyframe Overlap? | Set to |
|-----------------|-------------------------------|--------|
| static, small pan/tilt, zoom | Yes (same scene area) | `yes` |
| large pan, dolly, tracking, crane, arc | No (different area) | `no` |

### transition_description Requirements

This field directly becomes part of the video prompt. **The more detailed, the better.**

**Must include:**
1. **Subject appearance**: Key visual features that must remain consistent throughout
2. **Movement trajectory**: How subject/camera moves through space and time
3. **State changes**: How objects/environment change over the duration
4. **Existence statements**: What is present throughout (prevents pop-in/pop-out)

**Length guideline:** 2-4 sentences minimum. One-line descriptions are insufficient.

### transition_description Examples

| Insufficient | Sufficient |
|--------------|------------|
| "Open box revealing jar" | "The frosted glass jar with gold lid is inside the box from the start, hidden by the closed cream-colored lid. Elegant hands with manicured nails lift the lid upward smoothly. As the lid rises, the jar gradually comes into view - first the gold cap edge, then the full jar nestled in champagne velvet." |
| "Person walks left to right" | "Woman in white dress with brown hair starts at left edge of frame, walks steadily rightward at moderate pace, maintaining upright posture, reaches right edge by end of clip." |
| "Light turns on" | "Room starts in complete darkness. Light gradually increases from the ceiling fixture at center, warm yellow glow spreading outward across the wooden furniture until fully illuminated." |

### Physical Consistency Check

| Movement | Constraint |
|----------|------------|
| Pan/Tilt/Zoom | Camera fixed, content within rotational/zoom range |
| Dolly/Tracking/Crane | Content physically traversable within duration |
| Arc | Subject centered in both keyframes, environment allows orbit |
| Handheld | Similar to Dolly but allows irregularity |
| Combined | Must satisfy ALL involved movement constraints |

**Common Mistakes:**

| Mistake | Correction |
|---------|------------|
| "Pan from corridor entrance to middle" | Use "dolly forward" |
| First: room A, Last: room B | Split into two clips |
| 6-second clip covering 100 meters | Extend duration or reduce distance |

### [MANDATORY] Reference Image Requirements

After all clips planned, list required reference images:

| Element | Clips Using It | Required Images |
|---------|----------------|-----------------|
| (name) | Clip X (MS), Clip Y (CU) | Full body, Face close-up |

> **[WARNING]** Only generate what clips actually need. Do NOT generate all angles by default.

---

## [MANDATORY] Phase 4: Reference Image Generation

**MANDATORY. Do not skip to Phase 5.**

### Generation Order

**Step 1: Primary reference (visual anchor)**
- Tool: `generate_image` (no references)
- Prompt MUST include: **Full Visual Style Specification** from Phase 2 + element description
- White background
- Ends with "no text, no watermarks, no logos, no labels, no annotations"

**Step 2: Additional angles/shots**
- Tool: `generate_image` with **primary reference as reference**
- Prompt: New angle/shot only (style inherited from reference)
- White background
- Ends with "no text, no watermarks, no logos, no labels, no annotations"

> **[WARNING]** Never generate additional refs without using primary ref as reference.

---

## Phase 5: Execution

### Global Rules

> **[CRITICAL]** ALL keyframes: aspect ratio from Phase 1 (16:9 or 9:16). Never 1:1.

### First Keyframe

```
first_keyframe_reuse = yes → Use previous clip's last keyframe (no generation)
first_keyframe_reuse = no  → Generate new keyframe
```

**If generating first keyframe:**
- [ ] Tool: `generate_image`
- [ ] References: Appropriate Phase 4 images
- [ ] Aspect ratio: 16:9 or 9:16
- [ ] Prompt includes:
  - [ ] Visual style (sub-genre + key characteristics, brief)
  - [ ] Scene environment
  - [ ] Framing (shot size + angle + lens)
  - [ ] Visible content
  - [ ] Subject appearance + outfit
- [ ] Prompt ends with: "no text, no watermarks, no logos, no annotations"

### Last Keyframe

```
last_keyframe_required = no  → Skip
last_keyframe_required = yes:
  last_keyframe_edit_from_first = yes → Edit mode
  last_keyframe_edit_from_first = no  → Generate mode
```

**If EDIT mode:**
- [ ] Tool: `generate_image_variation`
- [ ] References: [first_keyframe, Phase 4 refs...]
- [ ] Prompt: "Edit this image: [changes only]"
- [ ] Do NOT repeat unchanged elements

**If GENERATE mode:**
- [ ] Tool: `generate_image`
- [ ] References: [first_keyframe (scene ref), Phase 4 refs...]
- [ ] Aspect ratio: 16:9 or 9:16
- [ ] Prompt includes:
  - [ ] Visual style (brief)
  - [ ] Last keyframe framing + visible content
  - [ ] Subject appearance and end state
  - [ ] "Same location/environment as reference"
- [ ] Prompt ends with: "no text, no watermarks, no logos, no annotations"

### Consistency Checklist (Easily Overlooked)

When generating last keyframe, verify:
- [ ] **Interpolatable change**: Clear difference in subject position/pose, state, or composition (not just lighting/background)
- [ ] Same lighting direction and shadows as first keyframe
- [ ] Same color temperature (warm/cool)
- [ ] Same depth of field
- [ ] Same outfit, facial features, body proportions
- [ ] Environment details consistent

### Video Generation

**Video prompt should be detailed.** Even with keyframes, video models may drift during generation.

**Prompt includes:**
- [ ] Visual style (brief)
- [ ] Pacing (slow / moderate / fast)
- [ ] **transition_description** from Phase 3 (detailed, 2-4 sentences)
- [ ] **Subject appearance** (key features for consistency)
- [ ] **Scene environment** (brief)
- [ ] Audio (see below)

**Audio in prompt:**

| Type | Include |
|------|---------|
| On-screen dialogue | "Name says: text" with tone, language |
| On-screen singing | "Name sings: [lyrics]" with style, language |
| Sound effects | Source + quality |
| Embedded BGM | Style, BPM, instruments, mood |

**Prompt ending by bgm_source:**
- embedded → (no ending, music described in prompt body)
- separate/none → End with "No background music."

**Example (music video with embedded BGM):**
```
Hatsune Miku center stage, singing in Japanese with sweet electronic voice: 
"ラララ、光の中で踊り出す", energetic J-pop at 140 BPM with synthesizer, 
crowd cheering, concert atmosphere
```

> **[CRITICAL]** Never use TTS for on-screen dialogue/singing. Video model generates audio with lip sync.

### BGM Sourcing (if bgm_source = separate)

**Method:** Search and download from royalty-free music libraries (e.g., Pixabay, YouTube Audio Library).

**[CRITICAL]** Generating music with Python or any other tools is strictly prohibited. You must only use pre-existing, royalty-free tracks.

Match the downloaded music to the style defined in Phase 2.

### Narration Generation (if narration exists)

> **[WARNING]** Generate **clip by clip**, not all at once.

- TTS for off-screen narrator only
- Same voice profile across all clips
- Verify audio duration fits clip duration

### Audio Summary

| Type | Method | Output |
|------|--------|--------|
| On-screen dialogue/singing | Video model | Embedded |
| Sound effects | Video model | Embedded |
| Embedded BGM | Video model | Embedded |
| Separate BGM | Search only | Separate track |
| Narration | TTS (clip by clip) | Separate track |

### Audio Mixing (Final Assembly)

When combining multiple audio sources:

| Track | Source |
|-------|--------|
| Video audio | Embedded in video clips (dialogue, sound effects, embedded BGM) |
| Narration | TTS generated (off-screen narrator) |
| Separate BGM | Searched from royalty-free source |

**[CRITICAL]** Mixing rules:
- Preserve ALL audio tracks—overlay, never replace one with another
- Narration must be clearly audible—not drowned out by other tracks
- Narration volume must be consistent across all clips
