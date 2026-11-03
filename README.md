# Chat Slide Studio

**Tạo PowerPoint bằng ChatGPT thường + GitHub**, với bước duyệt bố cục trước khi dựng file. Không cần ChatGPT Work, không cần cài ZIP Skill. Repo là nơi lưu hướng dẫn, code dựng slide, bộ QA và GitHub Actions.

**Repository:** https://github.com/longnt27/chat-slide-studio

## Chọn tier trước khi làm slide

| Tier | Khi nào dùng | Animation | Chart và navigation |
|---|---|---|---|
| **Content** | Chỉ cần slide đẹp, có nội dung; tối ưu công sức | Không có hiệu ứng hay chuyển trang | Chart chỉnh sửa được nếu có số liệu |
| **Presenter** | Người nói muốn tự kiểm soát lúc hiện từng ý | Auto, On Click; Morph chọn lọc | Chart khi thực sự cần |
| **Studio** | Storytelling, báo cáo dữ liệu, phần mục lục nhiều chương | On Click và Morph theo đối tượng | Chart và TOC ảnh ↔ nội dung nếu có ích |

Không bắt mọi bài trình chiếu phải có animation. **20 slide logic + 3 lượt quay lại TOC = 23 trang PowerPoint/PDF vật lý**, nhưng vẫn là 20 nội dung độc nhất. Con số này được duyệt trước khi build và được ghi trong `slide-route.json`.

[Xem đầy đủ tier, chart, Morph và cách đếm slide](references/tiers-and-navigation.md).

## Tạo slide trước, review trực tiếp trên thành phẩm

Kết nối GitHub với ChatGPT (quyền đọc/ghi branch và xem Actions), sau đó gửi **một prompt duy nhất**. ChatGPT đọc `AGENTS.md`, tự lập storyboard **nội bộ** và dựng PPTX/PDF cùng các ảnh preview. **Không có bước duyệt wireframe**. Người dùng review các slide thật rồi comment để sửa.

Số slide trong các ví dụ là tham số, không phải giới hạn: công cụ hỗ trợ một slide độc lập hoặc từ 3–80 slide (chưa hỗ trợ bài đúng 2 slide).

### Content: slide tĩnh, có thể chỉnh sửa

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and the relevant repository documentation.
Create a 12-slide PowerPoint about [TOPIC] for [AUDIENCE],
with an estimated duration of [DURATION].
Use tier=content and animation_mode=none.
Prioritize factual accuracy, clear composition, properly sourced
visuals, editable charts when useful, and speaker notes.

Plan the full storyboard internally. Do not request wireframe approval.
Build the complete PPTX and PDF, render every slide, run GitHub Actions
QA, and fix any failures before presenting the actual slide previews.
Provide artifact links, a QA summary, and any remaining limitations.
Do not merge the presentation branch into main without permission.
```

### Presenter: animation phục vụ thuyết trình

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and the relevant repository documentation.
Create a 15-slide PowerPoint about [TOPIC] for [AUDIENCE],
with an estimated duration of [DURATION].
Use tier=presenter and animation_mode=presenter.
Use grouped On Click reveals when a speaker needs to control pacing.
Use Morph only for meaningful continuity of the same subject.
Provide speaker notes with click cues and properly credited visuals.

Create and validate the storyboard internally, without an approval step.
Generate the editable PPTX/PDF and slide previews immediately, run full
QA in GitHub Actions, inspect every slide, and correct any defects.
Present the actual slides for feedback, not wireframes.
Do not merge into main without permission.
```

### Studio: bố cục chuyên sâu, điều hướng theo chương

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and references/tiers-and-navigation.md.
Create 20 unique logical slides about [TOPIC] for [AUDIENCE],
lasting approximately [DURATION].
Use tier=studio and animation_mode=presenter.
Include a photo table of contents at logical slide 2 and revisit it
after logical slides 5, 9 and 14. Report 20 logical slides and
23 physical PPTX/PDF pages. Use purposeful Morph pairs only with a
shared verified subject; use sourced editable charts where valuable.

Plan all content, routes and animations internally, then produce the
PPTX/PDF without requesting storyboard or wireframe approval.
Run structural and visual QA on every slide; provide actual previews,
artifact links, image credits and a QA summary for review.
Do not merge into main without permission.
```

Studio **không bắt buộc** có Morph, TOC lặp hay biểu đồ. Nếu cần bố cục chuyên sâu nhưng không muốn animation, có thể chọn `animation_mode=none` và không đặt `navigation`.

### Sửa slide sau khi build

Người dùng có thể comment từng slide hoặc toàn bộ presentation:

```text
Revise the existing deck [DECK / BRANCH].
On logical slide 5, remove [EXACT CONTENT] and preserve the
remaining animations. On slide 8, replace [OLD TEXT] with [NEW TEXT].
Keep all other slides unchanged.

Record the original feedback and measurable acceptance checks in
revision_requests.json, pinned to the previous deck commit.
Rebuild the PPTX/PDF, run structural, revision, and visual QA, and
provide before/after previews for my review.
Do not declare user acceptance on my behalf.
```

ChatGPT sẽ kiểm tra thay đổi đối chiếu **baseline commit** của deck trước đó. CI có thể chứng minh việc sửa đúng điều kiện đo được và phát hiện thay đổi ngoài phạm vi, nhưng không thể tự đảm bảo diễn giải ý định chủ quan là hoàn hảo. **Người dùng duyệt slide thành phẩm**, không duyệt wireframe. [Xem cơ chế revision](references/revision-workflow.md).

## Quy tắc quan trọng

- **Số slide là tham số:** 1 slide độc lập hoặc từ 3 đến 80 slide tùy đề bài (bộ dựng hiện chưa hỗ trợ bài đúng 2 slide). Storyboard và deck phải có đúng số slide logic người dùng yêu cầu. PPTX/PDF phải khớp số trang vật lý được tính từ route; không lặp TOC thì hai số bằng nhau. `decks/demo` có 15 trang chỉ để test.
- **Bố cục theo ý nghĩa:** `diagram_relationship` có `peers` (đồng cấp), `hierarchy` (phân cấp) và `reciprocal` (tương hỗ). Không xếp 2 ô trên, 1 ô dưới chỉ vì bộ dựng chọn hai cột; hàng lẻ phải cân trục. Đây là nguyên tắc, không phải luật "ba ô luôn nằm ngang".
- **Đường kẻ có lý do:** mặc định không có divider trang trí. Đường trục thời gian hoặc liên kết nội dung có thể giữ nếu phục vụ diễn giải và được đề xuất trong storyboard.
- **Animation phục vụ người nói:** title/ý mở đầu có thể Fade tự động, các nội dung tiếp theo chờ On Click; khung + chữ + ảnh xuất hiện cùng nhóm.
- **Morph có chọn lọc:** chỉ dùng khi cùng chủ thể tiếp nối giữa hai slide, có thay đổi bố cục/khung hình và lý do rõ ràng. Không Morph số trang, đồ trang trí; **không bắt buộc deck nào cũng phải có Morph**. Nếu yêu cầu Morph, ChatGPT phải đề xuất cặp hợp lý hoặc giải thích vì sao không phù hợp.
- **Ảnh và chữ:** ảnh có nguồn/credit, không cắt giữa mặt người hoặc hiện vật; caption tự nhiên. Không chế slogan hoặc câu triết lý cho trang cảm ơn.
- **QA thật:** CI phải dựng PPTX, PDF, preview và kiểm tra nội dung/animation/notes/bố cục. PDF không thể hiện On Click/Morph; chỉ Microsoft PowerPoint Slide Show mới cho kiểm chứng phát hiệu ứng thực tế.

## Lấy file sau khi build

Mở tab [GitHub Actions](https://github.com/longnt27/chat-slide-studio/actions), chọn run **Build and QA PowerPoint decks** trên branch của bài, kiểm tra trạng thái **Success**, kéo xuống phần **Artifacts** và tải gói đầu ra. Gói có thể gồm PPTX, PDF, montage, ảnh từng trang, credits và QA report. Nếu chưa thấy PPTX, kiểm tra `deck.json`, nguồn ảnh và log CI. Wireframe chỉ là preview nội bộ; pipeline build PPTX ngay khi deck spec đầy đủ.

Nếu ChatGPT không lấy được artifact qua connector, dùng link GitHub Actions thay vì tự bịa `sandbox:/mnt/data/...`.

## Hướng dẫn chi tiết

- [Hướng dẫn sử dụng từ đầu đến cuối, các tình huống thường gặp](references/usage-guide.md)
- [Mẫu prompt copy vào ChatGPT](CHAT_PROMPT.md)
- [Quy trình dành cho ChatGPT/agent](AGENTS.md)
- [Revision và nghiệm thu thay đổi](references/revision-workflow.md)
- [Bố cục theo ngữ nghĩa, chống lạm dụng divider](references/semantic-layout.md)
- [Animation / Morph](references/animation-direction.md)
- [Nguồn ảnh và bản quyền](references/image-sourcing.md)
- [QA và kiểm tra trực quan](references/design-qa.md)
- [Sự cố CI](references/ci-troubleshooting.md)

## Dành cho người muốn chạy local

```bash
npm install
python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema
# Trên Linux: cài libreoffice-impress và fonts-noto-core
python -m unittest discover -s tests -p 'test_*.py' -v

# Nội bộ: lập kế hoạch 20 slide trước khi tạo slide thật
python scripts/new_deck.py my-topic --title "Tiêu đề bài thuyết trình" --slides 20
# Viết đủ storyboard.json nội bộ, không để TODO
python scripts/check_storyboard.py decks/my-topic --proposals-only
python scripts/render_storyboard.py decks/my-topic

# Dựng deck ngay sau khi hoàn thiện internal storyboard
python scripts/new_deck.py my-topic --from-internal-plan
# Viết nội dung thật vào deck.json, thêm sources.json và assets
python scripts/run_pipeline.py --deck my-topic
```

Hướng dẫn trong repo là **quy trình cho ChatGPT đọc qua GitHub**, không phải Skill đã cài trong tài khoản. Luôn yêu cầu đọc `AGENTS.md` khi bắt đầu chat/bài mới. **Không tự merge vào `main`** chỉ vì CI xanh; cần sự đồng ý của chủ repo.