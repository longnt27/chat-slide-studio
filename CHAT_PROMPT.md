# Mẫu prompt dùng với ChatGPT thường

Repo: https://github.com/longnt27/chat-slide-studio

Cần kết nối GitHub với ChatGPT và cấp quyền phù hợp. Các prompt bên dưới áp dụng cho **ChatGPT thường, không cần Work hoặc Skill ZIP**. Số slide chỉ là ví dụ: thay 20 bằng 1 slide đơn hoặc 3–80 slide theo yêu cầu (hiện chưa hỗ trợ bài đúng 2 slide).

## Chọn mức độ công phu theo nhu cầu

**Content:** “Create 12 slides using the Content tier. Keep the deck fully editable and static, without On Click, Fade, or Morph.”

**Presenter:** “Create 20 slides using the Presenter tier, with grouped On Click reveals where appropriate and selective, purposeful Morph transitions.”

**Studio:** “Create **20 unique logical slides** using the Studio tier, with a photo table of contents and returns after logical slides 5, 9, and 14. Use Morph only for meaningful subject continuity and charts only with verified data. Report the **23 physical PPTX/PDF pages** separately.”

Tier nằm trong storyboard để duyệt. Xem `references/tiers-and-navigation.md`. Không nâng tier, thêm slide vật lý hoặc đổi đường Morph sau khi được duyệt.

## 1. Đề xuất bố cục trước (HITL)

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and all relevant repository documentation.

Create a 20-slide PowerPoint presentation about [TOPIC] for
[AUDIENCE], with a presentation duration of [DURATION].
Use the Presenter tier (tier=presenter, animation_mode=presenter).
Key content and reference materials: [BRIEF / SOURCES].

At this stage, propose ONLY the complete 20-slide storyboard
and wireframe previews. For each slide, specify:
- A factual headline, takeaway, and planned visual or source
- A layout reflecting the actual relationships between ideas
- Grouped Auto/On Click reveal order, when appropriate
- Justified Morph pairs, if any, and proposed speaker notes

Avoid decorative dividers and unnecessary slogans.
Create a feature branch, commit storyboard.json, run preview CI,
and present the proposal for review. Do not create deck.json,
approval.json, PPTX, or PDF files before explicit approval.
```

## 2. Yêu cầu chỉnh storyboard, vẫn chưa build

```text
Please revise the proposed storyboard as follows:
- Slide [N]: change the layout/relationship to [LAYOUT / RELATIONSHIP]
  because [REASON].
- Slide [M]: revise the image, caption, or reveal sequence to
  [REQUIREMENT].
- Keep all other slides unchanged.

Update the storyboard and wireframe previews, then present
the complete revised proposal for review.
Do not build a PPTX or mark the storyboard as approved.
```

## 3. Duyệt bản cuối và triển khai

```text
I approve the final storyboard presented above.
Lock that exact version in approval.json and create deck.json
in accordance with the approved slide order, layouts,
relationships, On Click reveals, and Morph transitions.

Run GitHub Actions, generate PPTX/PDF outputs, and inspect
all slides at full resolution. Fix any problems in the source
and rerun CI. Provide the files, artifact links, and QA report.
Do not merge into main without my explicit permission.
```

## 4. Rà soát một deck đã build

```text
Review the presentation [DECK / BRANCH] in the
chat-slide-studio repository.

Inspect every slide at full resolution for image cropping,
text overlap, optical alignment, unnecessary dividers,
semantic layout, click timing, grouping of frames/images/text,
and Morph between adjacent slides.
Fix issues in the source branch and rerun CI. If a fix changes
the approved structure, request a revised storyboard approval
before building. Do not treat a PDF or static preview as proof
that PowerPoint animations work correctly.
```

## 5. Khi cần Morph có chủ đích

```text
Use Morph only when it meaningfully clarifies the narrative.
For each proposed Morph pair, identify the shared subject,
its position and scale before and after the transition,
and what the audience should learn from the change.
If no suitable pair exists, explain why.
Do not apply Morph to page numbers, decorative headings,
or unrelated objects.
```

## Những điều dễ nhầm

- `decks/demo` có 15 slide **không có nghĩa** bài mới phải 15. Số lượng do user đặt trong prompt.
- Khi chưa có duyệt HITL, CI chỉ tạo storyboard preview; không có PPTX là **đúng**.
- Không gọi trang cảm ơn là cơ hội thêm slogan kiểu “Lịch sử là mạch nối”.
- Khác biệt quan trọng: `peers` = đồng cấp; `hierarchy` = phân cấp; `reciprocal` = hai chiều. Không xếp bố cục chỉ để lấp ô.
- Đường ngang thực sự là trục timeline có thể hợp lý; divider trang trí thì bỏ.
- PowerPoint bản PDF và ảnh tĩnh không hiển thị animation. Chỉ xác nhận phát Morph/On Click sau khi thử Slide Show trong Microsoft PowerPoint.
- Người dùng có quyền duyệt storyboard, **không đồng nghĩa** đã cho phép merge branch lên `main`.