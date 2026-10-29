# Chat Slide Studio

**GitHub repo dùng với ChatGPT thường:** người dùng paste link + chủ đề, ChatGPT đọc `AGENTS.md` qua GitHub connector, đề xuất một storyboard/wireframe rồi **dừng chờ người dùng duyệt**. Chỉ sau khi duyệt mới được build PPTX/PDF từ bố cục đã chốt, có ảnh nguồn, Speaker Notes, On Click và Morph chọn lọc, QA và GitHub Actions artifact.

**Repo:** https://github.com/longnt27/chat-slide-studio

## Dùng trong ChatGPT

**Turn 1: Đề xuất (chưa làm PPTX).**

> Dùng https://github.com/longnt27/chat-slide-studio, đọc `AGENTS.md`. Chuẩn bị bài thuyết trình **15 slide về [CHỦ ĐỀ]**, nội dung [BRIEF]. Trước tiên đề xuất đầy đủ 15 bố cục và wireframe để tao duyệt, chưa được dựng PPTX.

ChatGPT sẽ đề xuất thứ tự slide, mục tiêu/tựa đề, grid và số khối nội dung, hình ảnh/dữ liệu, các bước Fade/On Click và các cặp Morph có ý nghĩa. Quy tắc, script và dữ liệu nằm ở GitHub. `storyboard.json` được commit vào branch mới, GitHub Actions xuất ảnh `storyboard-montage.png`. Chưa có `deck.json` và chưa có file PowerPoint.

**Turn 2: Duyệt hoặc chỉnh.**

> Chốt bố cục này. Build đúng storyboard đã duyệt, chạy CI, xem QA rồi gửi PPTX/PDF/preview.

ChatGPT ghi `approval.json` kèm **trích nguyên văn sự đồng ý** và SHA-256 storyboard; từ đó mới được tạo `deck.json` và chạy build. Nếu bố cục, thứ tự slide, số unit, nhịp On Click hoặc Morph thay đổi, phải quay lại xin duyệt. Xem `references/hitl-approval.md`.

## Chất lượng phải đáp ứng

- Số slide **bằng chính xác con số người dùng yêu cầu**; JSON/PPTX/PDF phải khớp. Yêu cầu 15 mà tạo 8 hoặc 16 thì fail.
- Tránh slogan chung chung, sáo rỗng. **Trang cảm ơn chỉ cảm ơn và mời Q&A**, không tự chế "Lịch sử là mạch nối" hay những câu tương tự trừ khi được yêu cầu và duyệt rõ ràng.
- Giữ trọn mặt người, mái di tích, đồ vật và biểu đồ. Ảnh từ nguồn có bản quyền, tác giả/giấy phép/nguồn rõ ràng. Không có caption phủ định hiển nhiên.
- Card phải Fade theo nhóm **khung + ảnh + chữ cùng lúc**; click do người nói quyết định. Native OOXML bám PowerPoint Fade preset 10, first clickEffect + đồng bộ withEffect, `bldP` đúng shape.
- Bố cục phải thể hiện đúng **đồng cấp / phân cấp / tác động qua lại**, không chỉ xếp cho vừa ô. Bản duyệt sơ đồ cần có `diagram_relationship` để dựng đúng nghĩa và không thay đổi sau HITL.
- Giảm đường kẻ ngang: mặc định **không có divider trang trí**, nhưng cho phép các đường có chức năng thật (trục thời gian, liên kết nhân quả) nếu được thể hiện rõ trong storyboard. QA sẽ chặn các đường trang trí vô nghĩa.
- Morph là sự tiếp nối **cùng chủ thể, cùng file ảnh gốc**, thay đổi vùng nhìn thật sự có mục đích. Không morph số trang, thanh tiến trình hay decoration. Chuyển cảnh thường dùng Fade.
- Render montage + kiểm tra từng trang đáng nghi; kiểm thử lề, căn giữa thực, text overlap, tỷ lệ ảnh, notes, nguồn, animation và Morph. Không được gọi là đã thử phát PowerPoint nếu mới xem PDF/OOXML.

## Cấu trúc repo

```text
AGENTS.md, SKILL.md, CHAT_PROMPT.md
references/hitl-approval.md             # HITL là bước bắt buộc
references/story-design.md              # Nội dung/slogan/bố cục
references/animation-direction.md       # Fade On Click, Morph
references/image-sourcing.md            # Nguồn, credit, crop
references/design-qa.md                 # QA bố cục
references/semantic-layout.md           # Semantic geometry, divider, anti-overfit
scripts/diagram_geometry.cjs            # Balanced diagram layout calculations
references/chat-github.md               # Chat + GitHub connector
schemas/storyboard.schema.json          # Bố cục trước duyệt
schemas/deck.schema.json                # Nội dung PPTX sau duyệt
scripts/new_deck.py                     # Scaffold proposal trước tiên
scripts/check_storyboard.py             # Duyệt + khóa SHA
scripts/render_storyboard.py            # Preview wireframe
scripts/check_spec.py                   # Check approved layout vs deck
scripts/build_deck.cjs                  # PptxGenJS builder
scripts/patch_animations.py            # Native PowerPoint timings/Morph
scripts/qa_pptx.py, scripts/render_deck.py, scripts/run_pipeline.py
decks/demo/                             # Demo QA 15 slide
.github/workflows/build-slides.yml     # Build + artifacts
```

## Dành cho developer/agent

```bash
# Stage 1: viết và duyệt bố cục, KHÔNG build
python scripts/new_deck.py my-topic --title "Tiêu đề" --slides 15
# Hoàn tất decks/my-topic/storyboard.json, không để TODO.
python scripts/check_storyboard.py decks/my-topic --proposals-only
python scripts/render_storyboard.py decks/my-topic
# DỪNG, đưa bản này cho người dùng duyệt trong chat.

# Stage 2: chỉ sau khi người dùng duyệt
python scripts/check_storyboard.py decks/my-topic --approve-quoted "Duyệt bố cục này"
python scripts/new_deck.py my-topic --from-approved-plan
# Viết nội dung thật vào deck.json, thêm nguồn ảnh trong sources.json.
python scripts/run_pipeline.py --deck my-topic
```

`python scripts/check_storyboard.py --all-proposals` dùng để lint mọi storyboard mà không cần phê duyệt và không dựng slide. GitHub Actions chạy script này, sinh wireframe preview, và khi push branch chỉ build deck **đã có deck.json khớp approval**. Trên `main`, thay đổi engine chạy cả demo để kiểm thử hồi quy.

`decks/demo/` là fixture được duyệt phục vụ **test kỹ thuật** (`approval_channel=demo_fixture`), không thay thế sự duyệt bố cục của người dùng cho một bài thật. Bản demo 15 slide dùng để kiểm tra slide count, native clicks, Morph, PDF và QA. Artifact production chứa PPTX/PDF/preview/credits/report. CI không phải môi trường chạy Microsoft PowerPoint thực, vì vậy cảm nhận playback của PowerPoint cần được kiểm tra riêng.

## Chạy test

```bash
npm install
python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema
# Linux: sudo apt-get install libreoffice-impress fonts-noto-core
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/run_pipeline.py --deck demo
```

Toàn bộ workflow đọc được trong `AGENTS.md` và `references/`. Không cần ChatGPT Work hoặc cài một skill ZIP riêng.
