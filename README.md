# Chat Slide Studio

**Một repo GitHub để tạo PowerPoint chuyên nghiệp bằng cách chat.** ChatGPT dùng GitHub connector để đọc quy tắc từ `AGENTS.md`, tạo nội dung dưới `decks/`, còn GitHub Actions lo tải ảnh, dựng PPTX, animation, render PDF và kiểm thử.

Không cần ChatGPT Work, không cần cài skill ZIP. Đây là một repository chứa *hướng dẫn + công cụ sản xuất* mà ChatGPT có thể đọc khi bạn đưa link repo vào đoạn chat bình thường.

## Repo đã được thiết lập

**Repository:** https://github.com/longnt27/chat-slide-studio

Các file instruction, source, tests, workflow và demo đều đã được commit trên `main`.
Chỉ cần đưa link repo vào ChatGPT (có GitHub connector), yêu cầu đọc `AGENTS.md` và mô tả bài thuyết trình cần làm.
Không cần tải ZIP hoặc cài một Skill riêng.

## Cách dùng trong ChatGPT thường

Paste nguyên văn câu dưới đây, thay URL và phần nội dung:

> https://github.com/longnt27/chat-slide-studio
>
> Đọc `AGENTS.md` của repo này và làm đúng quy trình. Tạo một bài PPTX hoàn chỉnh 15 slide về **[CHỦ ĐỀ]** dựa trên **[NỘI DUNG/OUTLINE]**, có ảnh tư liệu, speaker notes, On Click hợp lý, Morph khi cần. Tạo branch mới, build bằng GitHub Actions, xem montage và sửa đến khi qua QA. Gửi PPTX, PDF và link CI.

Khi đã quen, có thể nói ngắn hơn: `Dùng repo https://github.com/longnt27/chat-slide-studio tạo 12 slide về ..., theo AGENTS.md.`

**Lưu ý kỹ thuật:** Repo GitHub **không tự động trở thành một custom Skill cài trong tài khoản**. Ở chat mới, cần paste link và bảo ChatGPT đọc `AGENTS.md` để kích hoạt quy trình. Đó là hành vi Chat + connector, không phải tính năng tự cài skill.

## File quan trọng

- `AGENTS.md`: luật làm việc mà ChatGPT phải đọc trước.
- `SKILL.md`: hợp đồng chất lượng slide.
- `references/`: story, ảnh, animation, QA và cách dùng GitHub qua Chat.
- `decks/<slug>/deck.json`: nội dung bài slide, cấu trúc, notes, reveal, Morph.
- `decks/<slug>/sources.json`: nguồn ảnh, tác giả, bản quyền, link gốc.
- `schemas/deck.schema.json`: format dữ liệu; `decks/demo/`: ví dụ chạy được.
- `scripts/`: builder, xử lý ảnh, patch animation, QA, render.
- `.github/workflows/build-slides.yml`: CI build tự động, artifact PPTX/PDF/PNG/credits.

## Tạo deck mới (chủ yếu dành cho ChatGPT)

Dùng `python scripts/new_deck.py my-topic --title "Tên bài"` để tạo bộ khung, rồi viết nội dung và nguồn ảnh phù hợp. **Không copy nguyên nội dung demo hoặc chủ đề của bài nhà Nguyễn**. Mọi thay đổi cần commit vào feature branch, CI tự build khi có push vào `decks/**`. Trường `requested_slide_count` trong `deck.json` là số slide người dùng yêu cầu, **không được tự suy theo số trang Chat đã viết**: yêu cầu 15 mà JSON chỉ có 8 thì CI phải fail.

Bộ `decks/demo` hiện có **15 slide** để kiểm tra đúng hành vi của prompt ví dụ. Với deck mới, tạo skeleton bằng `python scripts/new_deck.py ten-deck --title "Tên bài" --slides 15`, sau đó Chat viết nội dung thật cho đủ số trang và thay tất cả placeholder `TODO:` trước khi build.

GitHub Actions sẽ upload artifact tên `powerpoint-decks-<run number>` chứa từng deck trong `decks/<slug>/dist`.

## Chạy trực tiếp nếu cần

```bash
npm install
python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema
# Linux: sudo apt-get install libreoffice-impress fonts-noto-core
python scripts/run_pipeline.py --deck demo
# Hoặc: python scripts/run_pipeline.py --all
```

Thư mục `decks/<slug>/dist/` chứa `.pptx`, `.pdf`, `montage.png`, `qa-report.json`, `delivery.json`, `credits.csv` và `preview/slides/*.png`. Không commit `dist` vào git.

## Kiểm thử đúng số slide

`decks/demo` có 15 slide, được build end-to-end bằng cùng công cụ và CI dùng cho tất cả deck mới. Chạy `python scripts/run_pipeline.py --deck demo` phải xuất đúng 15 slide và PDF 15 trang. `requested_slide_count` là trường bắt buộc, được đối chiếu ở 4 bước: JSON schema, `check_spec.py`, `build_deck.cjs`, `qa_pptx.py` / PDF render. Hai tình huống âm tính (khai báo 15 nhưng viết 8 hoặc 16) phải bị chặn ngay từ đầu.

## Quality gates

Bộ dựng fail nếu thiếu/không xác minh được ảnh, sai schema, ảnh tư liệu bị yêu cầu crop cover, Morph không có chủ thể liền kề, nhóm animation bị chia sai, caption căn giữa giả, card lệch lề hoặc text/text chồng lấn và nội dung vượt khung. **QA máy không thể thay việc xem từng slide bằng mắt** để phát hiện ảnh sai ngữ cảnh, text đè lên ảnh hay một bố cục tuy hợp lệ nhưng xấu. Morph/On Click phải được thử phát trong PowerPoint nếu cần xác nhận cảm giác chuyển động.

Toàn bộ README, scripts, tests và ví dụ đều được thiết kế dùng lại cho các chủ đề mới, không giới hạn triều Nguyễn.
