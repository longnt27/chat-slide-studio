# Ordo Studio

**Create editable presentations with ChatGPT + GitHub.** This is the technical
repository powering the Ordo Studio workflow. No Work mode, installed Skill ZIP,
or wireframe approval step is required.

Repo: https://github.com/longnt27/chat-slide-studio

## Ba tier dịch vụ

| Tier | Dành cho | Khả năng |
| --- | --- | --- |
| **Basic** (`tier=basic`) | Slide nội dung rõ ràng, chỉnh sửa được | Tĩnh, không On Click/Fade/Morph; chart dùng khi có dữ liệu |
| **Studio** (`tier=studio`) | Thuyết trình có người dẫn dắt | Nhóm nội dung xuất hiện theo On Click, Morph có chọn lọc |
| **Pro** (`tier=pro`) | Storytelling cao cấp, báo cáo dữ liệu phức tạp | Bố cục nâng cao; chart có nguồn; optional photo TOC, chapter return/Morph |

**Cả ba tier đều phải đạt QA.** Không bắt Basic có animation, Studio có Morph hay Pro có chart khi không cần. Pro có thể dùng `animation_mode=none` nếu không muốn hiệu ứng.

### Mỗi bài dùng branch và deck slug riêng

Để làm nhiều bài đồng thời mà không ghi đè:

- **Git branch:** ví dụ `decks/vietnam-history-1945`
- **Deck slug:** `vietnam-history-1945`, chứa file trong `decks/vietnam-history-1945/`
- **Primary color:** ví dụ `#2563EB`
- **Visual style:** ví dụ *Swiss minimalist*, *editorial*, *corporate*, *academic* hoặc mô tả riêng

ChatGPT phải tạo branch **đúng tên** từ `main`, kiểm tra branch không thuộc công việc khác, commit mọi sửa đổi liên quan đến bài vào branch đó và chỉ build deck slug tương ứng. Không đổi sang branch đang dùng cho bài khác, không tự merge vào `main`.

`design.primary_color` và `design.style` được lưu trong storyboard nội bộ lẫn `deck.json`. Engine dùng màu chủ đạo cho điểm nhấn/biểu đồ, điều chỉnh độ tương phản để dễ đọc. Style được dùng để lên bố cục và chọn nền tảng typography; mô tả style quá đặc thù vẫn cần AI tự triển khai trong từng slide.

## Prompt mẫu: Basic

```text
Use https://github.com/longnt27/chat-slide-studio and read AGENTS.md.
Create a new branch named [BRANCH_NAME] from main exclusively for this
presentation. Use deck slug [DECK_SLUG]; write only to decks/[DECK_SLUG]/.
Do not reuse a branch or slug belonging to another presentation.

Create 12 slides about [TOPIC] for [AUDIENCE], lasting [DURATION].
Tier: basic. Animation mode: none.
Primary brand color: [PRIMARY_COLOR_HEX].
Visual style: [VISUAL_STYLE].

Apply the chosen color and style consistently to the actual slide design.
Plan the storyboard internally, then build editable PPTX/PDF and render
individual slide previews. Run CI, inspect every slide, fix any defects
and provide verified artifacts plus a QA summary.
Do not ask for wireframe approval or merge into main.
```

## Prompt mẫu: Studio

```text
Use https://github.com/longnt27/chat-slide-studio and read AGENTS.md.
Create a new branch named [BRANCH_NAME] from main exclusively for this
presentation. Use deck slug [DECK_SLUG]; write only to decks/[DECK_SLUG]/.
Do not reuse a branch or slug belonging to another presentation.

Create 15 slides about [TOPIC] for [AUDIENCE], lasting [DURATION].
Tier: studio. Animation mode: presenter.
Primary brand color: [PRIMARY_COLOR_HEX].
Visual style: [VISUAL_STYLE].

Use grouped On Click reveals when they improve speaker pacing. Apply
Morph only to a meaningful shared subject across adjacent slides.
Include sourced visuals, speaker notes and click cues.
Plan internally; immediately build editable PPTX/PDF and slide previews.
Run structural and visual QA. Show the finished slides for revision.
Do not ask for wireframe approval or merge into main.
```

## Prompt mẫu: Pro

```text
Use https://github.com/longnt27/chat-slide-studio and read AGENTS.md.
Create a new branch named [BRANCH_NAME] from main exclusively for this
presentation. Use deck slug [DECK_SLUG]; write only to decks/[DECK_SLUG]/.
Do not reuse a branch or slug belonging to another presentation.

Create 20 unique logical slides about [TOPIC] for [AUDIENCE],
lasting [DURATION]. Tier: pro. Animation mode: presenter.
Primary brand color: [PRIMARY_COLOR_HEX].
Visual style: [VISUAL_STYLE].

Include a photo table of contents on logical slide 2 and return to
it after logical slides 5, 9 and 14. Clearly report 20 logical
slides versus 23 physical PPTX/PDF pages. Use verified imagery,
editable charts only with source data, and purposeful Morph.
Write full speaker notes with click cues and image credits.

Plan internally, build PPTX/PDF immediately, render every page,
run CI QA, fix defects, and present the actual slides for feedback.
Do not ask for storyboard approval or merge into main.
```

Những TOC/Morph trong prompt Pro chỉ là **ví dụ tùy chọn**. Đổi hoặc bỏ theo từng bài. Số slide hỗ trợ: **1** hoặc **3–80**; bài đúng 2 slide chưa được hỗ trợ trong workflow hiện tại.

## Chỉnh sửa sau khi có slide

Dùng **chính branch và deck slug của bài đó**. Không tạo một branch mới chỉ vì muốn sửa slide 5:

```text
Open https://github.com/longnt27/chat-slide-studio.
Continue on branch [BRANCH_NAME], deck decks/[DECK_SLUG]/.
Revise logical slide 5: remove [EXACT CONTENT].
Preserve the remaining animations and leave all other slides unchanged.

Record the feedback and measurable acceptance checks against the
previous deck commit in revision_requests.json. Rebuild only this
presentation, run revision and visual QA, and provide before/after
previews. Do not mark the changes accepted on my behalf.
```

Bộ QA tự động kiểm tra những điều đo được, nhưng người dùng vẫn quyết định slide có đúng ý hay không.

## Chạy và kiểm tra CI

Mở [GitHub Actions](https://github.com/longnt27/chat-slide-studio/actions), chọn **Build and QA PowerPoint decks** và lọc đúng branch. Artifacts chứa PPTX, PDF, montage, từng slide, credits và QA report. Khi có revision sẽ có thêm báo cáo so sánh trước/sau.

```bash
npm install
python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema
python -m unittest discover -s tests -p 'test_*.py' -v

# Create only after checking out a matching dedicated branch.
python scripts/new_deck.py vietnam-history-1945 \
  --title "History of Vietnam" --slides 20 --tier pro \
  --branch decks/vietnam-history-1945 \
  --primary-color '#2563EB' --style 'Swiss minimalist'
# Complete the internal storyboard, then:
python scripts/check_storyboard.py decks/vietnam-history-1945 --proposals-only
python scripts/new_deck.py vietnam-history-1945 --from-internal-plan
# Complete the deck content, sources, notes, and build:
python scripts/run_pipeline.py --deck vietnam-history-1945
```

## Tài liệu

- [Prompt mẫu đầy đủ](CHAT_PROMPT.md)
- [Quy trình agent](AGENTS.md)
- [Tier và navigation](references/tiers-and-navigation.md)
- [Hướng dẫn sử dụng](references/usage-guide.md)
- [Revision QA](references/revision-workflow.md)
- [Bố cục theo ngữ nghĩa](references/semantic-layout.md)
- [Animation và Morph](references/animation-direction.md)
- [Sourcing ảnh](references/image-sourcing.md)
- [Visual QA](references/design-qa.md)

**Giới hạn:** QA qua LibreOffice/OOXML không chứng minh hiệu ứng sẽ chạy giống hệt trên Keynote, Google Slides hoặc PowerPoint Slide Show. Với biểu đồ, hãy kiểm tra ứng dụng đích; native PowerPoint chart không bảo đảm import nguyên vẹn vào mọi nền tảng.
