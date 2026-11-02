# Chat Slide Studio

**Tạo PowerPoint bằng ChatGPT thường + GitHub**, với bước duyệt bố cục trước khi dựng file. Không cần ChatGPT Work, không cần cài ZIP Skill. Repo là nơi lưu hướng dẫn, code dựng slide, bộ QA và GitHub Actions.

**Repository:** https://github.com/longnt27/chat-slide-studio

## Bắt đầu trong 2 lượt chat

Trước tiên, kết nối GitHub với ChatGPT và bảo đảm tài khoản có quyền đọc/ghi repo, tạo branch và xem GitHub Actions. Có thể làm ngay trong cuộc trò chuyện thường; mỗi khi bắt đầu bài mới, hãy gửi link repo và yêu cầu ChatGPT đọc [`AGENTS.md`](AGENTS.md).

**Lượt 1: Đề xuất storyboard, CHƯA làm PowerPoint.** Ví dụ với **20 slide** (con số là yêu cầu của bài, không phải giới hạn hay mặc định cố định):

> Dùng https://github.com/longnt27/chat-slide-studio, đọc `AGENTS.md` và các tài liệu liên quan. Tao cần **20 slide về Việt Nam thời Nguyễn**, cho người nghe không chuyên, khoảng 15 phút, có ảnh tư liệu và Speaker Notes. Đề xuất bố cục, nội dung chính, hình ảnh và nhịp On Click/Morph của **đủ 20 slide**. Render wireframe để tao duyệt. **Chưa tạo PPTX.**

ChatGPT phải đưa ra toàn bộ storyboard, số lượng nội dung trên mỗi slide, quan hệ ngữ nghĩa/bố cục, ảnh dự kiến, thứ tự xuất hiện và những cặp Morph có lý do. Nó commit `decks/<slug>/storyboard.json` trên **branch riêng** và tạo bản xem trước wireframe qua CI. Dừng ở đây chờ phản hồi của bạn.

**Lượt 2: Chỉnh hoặc duyệt rõ ràng.** Ví dụ:

> Đổi slide 5 sang sơ đồ tương hỗ, đặt nhóm chính trị/kinh tế/xã hội đồng cấp ở bên phải và văn hóa bên trái, bỏ divider trang trí. Giữ các trang còn lại. Cho tao xem storyboard đã sửa, **chưa build**.

Khi đã hài lòng với **bản storyboard cuối**, trả lời:

> Duyệt storyboard cuối cùng này. Khóa bố cục đã duyệt rồi dựng PPTX/PDF chính xác theo đó. Chạy GitHub Actions, xem từng trang, sửa lỗi và gửi link artifact cùng báo cáo QA. Chưa merge `main` nếu chưa được tao cho phép.

**Không coi việc sửa một phần là duyệt toàn bộ**. Nếu bản bố cục đổi sau khi duyệt, hệ thống phải xin duyệt lại. Dữ liệu khóa duyệt nằm trong `approval.json` với hash của `storyboard.json`.

## Quy tắc quan trọng

- **Số slide là tham số:** 1 slide độc lập hoặc từ 3 đến 80 slide tùy đề bài (bộ dựng hiện chưa hỗ trợ bài đúng 2 slide). Storyboard, deck, PPTX và số trang PDF phải khớp con số yêu cầu. `decks/demo` có 15 trang chỉ để test.
- **Bố cục theo ý nghĩa:** `diagram_relationship` có `peers` (đồng cấp), `hierarchy` (phân cấp) và `reciprocal` (tương hỗ). Không xếp 2 ô trên, 1 ô dưới chỉ vì bộ dựng chọn hai cột; hàng lẻ phải cân trục. Đây là nguyên tắc, không phải luật "ba ô luôn nằm ngang".
- **Đường kẻ có lý do:** mặc định không có divider trang trí. Đường trục thời gian hoặc liên kết nội dung có thể giữ nếu phục vụ diễn giải và được đề xuất trong storyboard.
- **Animation phục vụ người nói:** title/ý mở đầu có thể Fade tự động, các nội dung tiếp theo chờ On Click; khung + chữ + ảnh xuất hiện cùng nhóm.
- **Morph có chọn lọc:** chỉ dùng khi cùng chủ thể tiếp nối giữa hai slide, có thay đổi bố cục/khung hình và lý do rõ ràng. Không Morph số trang, đồ trang trí; **không bắt buộc deck nào cũng phải có Morph**. Nếu yêu cầu Morph, ChatGPT phải đề xuất cặp hợp lý hoặc giải thích vì sao không phù hợp.
- **Ảnh và chữ:** ảnh có nguồn/credit, không cắt giữa mặt người hoặc hiện vật; caption tự nhiên. Không chế slogan hoặc câu triết lý cho trang cảm ơn.
- **QA thật:** CI phải dựng PPTX, PDF, preview và kiểm tra nội dung/animation/notes/bố cục. PDF không thể hiện On Click/Morph; chỉ Microsoft PowerPoint Slide Show mới cho kiểm chứng phát hiệu ứng thực tế.

## Lấy file sau khi build

Mở tab [GitHub Actions](https://github.com/longnt27/chat-slide-studio/actions), chọn run **Build and QA PowerPoint decks** trên branch của bài, kiểm tra trạng thái **Success**, kéo xuống phần **Artifacts** và tải gói đầu ra. Gói có thể gồm PPTX, PDF, montage, ảnh từng trang, credits và QA report. Nếu chưa thấy PPTX, kiểm tra xem bài đã có `approval.json` hợp lệ và `deck.json` khớp storyboard chưa; trước duyệt CI **chỉ xuất wireframe** là đúng.

Nếu ChatGPT không lấy được artifact qua connector, dùng link GitHub Actions thay vì tự bịa `sandbox:/mnt/data/...`.

## Hướng dẫn chi tiết

- [Hướng dẫn sử dụng từ đầu đến cuối, các tình huống thường gặp](references/usage-guide.md)
- [Mẫu prompt copy vào ChatGPT](CHAT_PROMPT.md)
- [Quy trình dành cho ChatGPT/agent](AGENTS.md)
- [Khóa duyệt HITL](references/hitl-approval.md)
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

# Giai đoạn 1, chỉ tạo đề xuất 20 slide
python scripts/new_deck.py my-topic --title "Tiêu đề bài thuyết trình" --slides 20
# Viết đủ storyboard.json, không để TODO
python scripts/check_storyboard.py decks/my-topic --proposals-only
python scripts/render_storyboard.py decks/my-topic

# Giai đoạn 2 CHỈ SAU KHI người dùng đã duyệt bản cuối
python scripts/check_storyboard.py decks/my-topic --approve-quoted "Duyệt storyboard cuối cùng này"
python scripts/new_deck.py my-topic --from-approved-plan
# Viết nội dung thật vào deck.json, thêm sources.json và assets
python scripts/run_pipeline.py --deck my-topic
```

Hướng dẫn trong repo là **quy trình cho ChatGPT đọc qua GitHub**, không phải Skill đã cài trong tài khoản. Luôn yêu cầu đọc `AGENTS.md` khi bắt đầu chat/bài mới. **Không tự merge vào `main`** chỉ vì CI xanh; cần sự đồng ý của chủ repo.