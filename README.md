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

## Bắt đầu trong 2 lượt chat: chọn prompt theo tier

Trước tiên, kết nối GitHub với ChatGPT và bảo đảm tài khoản có quyền đọc/ghi repo, tạo branch và xem GitHub Actions. Có thể làm ngay trong cuộc trò chuyện thường; mỗi khi bắt đầu bài mới, hãy gửi link repo và yêu cầu ChatGPT đọc [`AGENTS.md`](AGENTS.md).

**Lượt 1: Chọn một trong ba prompt dưới đây và gửi vào chat.** Đây đều là yêu cầu **đề xuất storyboard/wireframe, chưa dựng PPTX**. Số slide chỉ là ví dụ, không phải giới hạn: thay bằng **1 slide hoặc 3–80 slide** theo nhu cầu (bộ dựng hiện chưa hỗ trợ đúng 2 slide).

### Content: slide tĩnh, gọn và chỉnh sửa được

Dành cho bài đọc, báo cáo hoặc trình chiếu không cần nhịp click. Tier Content **không có Fade, On Click, Morph hay transition**, kể cả khi có biểu đồ.

```text
Dùng https://github.com/longnt27/chat-slide-studio.
Đọc AGENTS.md và các tài liệu liên quan trong repo.

Tao cần 12 slide về [CHỦ ĐỀ] cho [ĐỐI TƯỢNG], khoảng [THỜI LƯỢNG].
Chọn tier Content (tier=content, animation_mode=none).
Ưu tiên bố cục rõ ràng, nội dung chính xác, hình ảnh có nguồn,
biểu đồ PowerPoint chỉnh sửa được nếu có số liệu phù hợp,
và Speaker Notes. Toàn bộ nội dung hiện sẵn, không animation.

CHỈ đề xuất storyboard đủ 12 slide và render wireframe để tao duyệt.
Tạo branch riêng, commit storyboard.json, chạy preview qua CI.
Chưa tạo deck.json, approval.json, PPTX/PDF; dừng chờ tao duyệt.
```

### Presenter: điều khiển nhịp thuyết trình bằng click

Dành cho người trực tiếp đứng nói; chỉ các nhóm ý cần thuyết minh riêng mới xuất hiện bằng On Click. Morph **có thể không có** nếu không tìm được cặp slide hợp lý.

```text
Dùng https://github.com/longnt27/chat-slide-studio.
Đọc AGENTS.md và các tài liệu liên quan trong repo.

Tao cần 15 slide về [CHỦ ĐỀ] cho [ĐỐI TƯỢNG], khoảng [THỜI LƯỢNG].
Chọn tier Presenter (tier=presenter, animation_mode=presenter).
Đề xuất nhóm nội dung hiện bằng On Click ở những chỗ cần ngắt nhịp;
tiêu đề/ý đầu có thể Auto. Khung, ảnh và chữ của cùng một ý
phải hiện cùng lúc. Chỉ đề xuất Morph khi có cùng chủ thể
tiếp nối giữa hai slide kề nhau và thay đổi khung hình có ý nghĩa.
Cần ảnh có nguồn, caption tự nhiên và Speaker Notes kèm cue click.

CHỈ đề xuất storyboard đủ 15 slide, thứ tự reveal và wireframe.
Tạo branch riêng, commit storyboard.json, chạy preview qua CI.
Chưa tạo deck.json, approval.json, PPTX/PDF; dừng chờ tao duyệt.
```

### Studio: bố cục chuyên sâu, mục lục ảnh và điều hướng theo chương

Ví dụ dưới đây **chủ động yêu cầu** quay lại mục lục, không phải mọi bài Studio đều cần tính năng này. Với 20 slide nội dung độc nhất và 3 lượt quay lại mục lục, file sẽ có **23 trang PPTX/PDF vật lý**. Chart và Morph chỉ dùng khi thực sự có ích.

```text
Dùng https://github.com/longnt27/chat-slide-studio.
Đọc AGENTS.md và references/tiers-and-navigation.md.

Tao cần 20 slide nội dung độc nhất về [CHỦ ĐỀ] cho [ĐỐI TƯỢNG],
khoảng [THỜI LƯỢNG]. Chọn tier Studio
(tier=studio, animation_mode=presenter).
Đề xuất mục lục ảnh ở slide logic #2, quay lại mục lục sau
các slide logic #5, #9 và #14 (navigation.mode=hub_return).
Như vậy: 20 slide logic, 23 trang PPTX/PDF vật lý.
Chỉ đề xuất Morph ở những đoạn liền kề có cùng ảnh/chủ thể,
dùng đúng ảnh nguồn và đổi bố cục có ý nghĩa; nếu không
phù hợp thì dùng Fade. Dùng On Click theo nhóm ý khi cần.
Biểu đồ phải có dữ liệu kiểm chứng được và chỉnh sửa được.
Có Speaker Notes, nguồn ảnh, và giải thích sơ đồ slide-route.

CHỈ đề xuất đủ 20 slide logic, thứ tự trang vật lý,
các cặp Morph và wireframe để tao duyệt cả tier/navigation.
Tạo branch riêng, commit storyboard.json, chạy preview qua CI.
Chưa tạo deck.json, approval.json, PPTX/PDF; dừng chờ tao duyệt.
```

Nếu chỉ cần thiết kế/biểu đồ chuyên sâu nhưng không muốn hiệu ứng, **Studio cũng có thể dùng `animation_mode=none`** và bỏ điều hướng quay lại mục lục. Đừng nâng tier chỉ để thêm chuyển cảnh cho vui.

Ở cả ba tier, ChatGPT phải nêu rõ **từng slide gồm nội dung gì, các nhóm có quan hệ ngữ nghĩa ra sao, ảnh dự kiến và bố cục**. Với Presenter/Studio, trình bày thêm nhịp xuất hiện và Morph có lý do. Storyboard phải được duyệt trước khi dựng file; nếu có TOC quay lại, báo **cả số slide logic và trang vật lý**.

**Lượt 2: Chỉnh hoặc duyệt rõ ràng.** Ví dụ:

> Đổi slide 5 sang sơ đồ tương hỗ, đặt nhóm chính trị/kinh tế/xã hội đồng cấp ở bên phải và văn hóa bên trái, bỏ divider trang trí. Giữ các trang còn lại. Cho tao xem storyboard đã sửa, **chưa build**.

Khi đã hài lòng với **bản storyboard cuối**, trả lời:

> Duyệt storyboard cuối cùng này. Khóa bố cục đã duyệt rồi dựng PPTX/PDF chính xác theo đó. Chạy GitHub Actions, xem từng trang, sửa lỗi và gửi link artifact cùng báo cáo QA. Chưa merge `main` nếu chưa được tao cho phép.

**Không coi việc sửa một phần là duyệt toàn bộ**. Nếu bản bố cục đổi sau khi duyệt, hệ thống phải xin duyệt lại. Dữ liệu khóa duyệt nằm trong `approval.json` với hash của `storyboard.json`.

## Quy tắc quan trọng

- **Số slide là tham số:** 1 slide độc lập hoặc từ 3 đến 80 slide tùy đề bài (bộ dựng hiện chưa hỗ trợ bài đúng 2 slide). Storyboard và deck phải có đúng số slide logic người dùng yêu cầu. PPTX/PDF phải khớp số trang vật lý được tính từ route; không lặp TOC thì hai số bằng nhau. `decks/demo` có 15 trang chỉ để test.
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