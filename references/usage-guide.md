# Hướng dẫn dùng Chat Slide Studio trong ChatGPT thường

Repo chính: https://github.com/longnt27/chat-slide-studio

## 1. Chuẩn bị một lần

1. Kết nối GitHub trong ChatGPT và cấp quyền cần thiết cho repo (đọc nội dung, tạo/sửa branch/file, xem Actions và tải artifact nếu connector hỗ trợ).
2. Kiểm tra GitHub Actions được bật cho repo. Không cần cài skill ZIP hoặc chuyển sang Work.
3. Khi bắt đầu một chat mới, dán **link repo + yêu cầu đọc `AGENTS.md` + nội dung bài**. ChatGPT sẽ phải lấy đúng hướng dẫn từ repo, không dựa vào quy tắc tự nhớ từ cuộc trò chuyện cũ.

Nếu connector không có quyền ghi hoặc không thể thao tác CI, phải báo rõ giới hạn; không được tuyên bố đã tạo commit hoặc có artifact khi chưa xác minh.

## 2. Quy trình sản xuất có 2 chặng

### Chặng A: đề xuất và duyệt (HITL)

Gửi chủ đề, **số slide chính xác** (hiện hỗ trợ 1 slide đơn hoặc 3–80 slide; trường hợp đúng 2 slide cần thay đổi công cụ), đối tượng nghe, thời lượng và nội dung/tài liệu nguồn. ChatGPT:

- Tạo branch theo bài, đọc `AGENTS.md`, đề xuất **đúng số lượng slide** (gồm mở đầu/cảm ơn nếu đã yêu cầu).
- Mỗi slide trong `storyboard.json` nêu title, takeaway, `layout`, `composition`, `visual`, `content_units`, `reveal_sequence` và Morph từ slide trước nếu có.
- Với sơ đồ khái niệm, nêu `diagram_relationship`: `peers`, `hierarchy` hoặc `reciprocal`. Chỉ chọn sau khi hiểu quan hệ cần truyền đạt, không dựa vào số ô.
- Chạy `check_storyboard.py --proposals-only` và xuất ảnh wireframe bằng `render_storyboard.py`.
- Trình bày storyboard và wireframe để user sửa/duyệt. **Dừng**, không được tạo `deck.json`, `approval.json` hay PPTX trước khi được duyệt.

Nếu user sửa một vài slide, cập nhật đề xuất rồi **đưa bản chỉnh sửa cuối để duyệt lại**. Người dùng có thể duyệt bằng một tin nhắn rõ ràng như "Duyệt storyboard phiên bản vừa trình bày"; im lặng không phải phê duyệt.

### Chặng B: dựng bài đã duyệt

Chỉ khi đã duyệt bản cuối, ChatGPT mới:

1. Ghi `approval.json` bằng câu phê duyệt thật và SHA-256 của storyboard.
2. Tạo `deck.json` từ bản đã duyệt, viết nội dung/notes, truy xuất ảnh có nguồn và credit.
3. Chạy `check_spec.py`, build PPTX, animation, PDF, montage và `qa_pptx.py`.
4. Kiểm tra **từng slide**. Phát hiện lỗi thì sửa ở nguồn, không chỉ vá tạm file .pptx.
5. Gửi PPTX/PDF, credits/QA và link run GitHub Actions; báo rõ chưa thử native PowerPoint nếu mới xem PDF.

Không được tự đổi layout/quan hệ/nhịp click/Morph đã duyệt để chữa lỗi: nếu sửa kết cấu thì phải xin duyệt storyboard mới. Các sửa nhỏ về alignment, chính tả, spacing không đổi cấu trúc thường không cần duyệt lại.

## 3. Chọn bố cục một cách có ý nghĩa

| Loại quan hệ | Bố cục gợi ý | Tránh |
|---|---|---|
| `peers` (đồng cấp) | Các phần tử cùng cỡ; hàng không đủ ô vẫn cân trục | 2 ô trên + 1 ô ở góc trái nếu ba ô thật sự ngang hàng |
| `hierarchy` (phân cấp) | Trên → dưới theo quan hệ cha/con | Bố cục ngang hàng làm người xem hiểu nhầm là đồng cấp |
| `reciprocal` (tác động qua lại) | Hai phía, liên kết hai chiều; các yếu tố cùng cấp thành nhóm cân đối | Xếp chồng dọc hàm ý một chiều hoặc cấp trên/cấp dưới |
| Timeline / process | Trục thời gian hoặc chuỗi có hướng | Những card rời rạc không có thứ tự |
| Comparison | Hai cột thẳng hàng, trục so sánh rõ | Nội dung trái/phải không cùng mốc |

**Đây là heuristics, không phải template cứng.** Khi quá nhiều nội dung, chia thành hai slide hoặc đổi bố cục có chủ đích, thay vì ép ô cho vừa.

**Divider:** mặc định không có đường kẻ ngang để trang trí. Đường kẻ có chức năng (trục timeline, connector, ranh giới thật) được phép khi có lý do. Không thêm đồng thời viền trên, line giữa card và line trên footer chỉ để lấp chỗ trống.

## 4. Animation, Morph và Speaker Notes

**On Click:** các nhóm ý cần thuyết trình lần lượt xuất hiện do người nói quyết định. Một card là một đơn vị gồm nền/khung, text, hình và caption, tất cả hiện cùng lúc. Các card cùng vai trò phải dùng hiệu ứng nhất quán. Title và ý đầu có thể Fade tự động nếu đã duyệt.

**Morph:** không ép dùng; chỉ tạo khi có cùng đối tượng được theo dõi giữa hai slide liền nhau và việc thay vị trí/scale giúp hiểu hơn. Khi yêu cầu Morph, storyboard phải giải thích rõ chủ thể, vị trí/khung cũ và mới, lợi ích cho người xem. Không Morph page number, nhãn trống hoặc khung trang trí cho có.

**Quan trọng:** CI xác nhận cấu trúc native OOXML và hình học, không thể bảo đảm hiệu ứng chạy mượt trên Microsoft PowerPoint desktop. Ảnh PNG/PDF chỉ cho thấy kết quả tĩnh; muốn đánh giá On Click/Morph hãy trình chiếu thực tế.

## 5. Lấy artifact qua GitHub Actions

Mở https://github.com/longnt27/chat-slide-studio/actions, chọn workflow `Build and QA PowerPoint decks`, tìm run trên đúng branch của bài. Nếu run **Success**, xem mục **Artifacts** phía cuối run. Tải gói bài (PPTX/PDF, ảnh preview, nguồn ảnh/credits, QA report khi có).

Workflow push branch chạy theo các file thay đổi; **chưa duyệt** thì chỉ storyboard preview, **đã duyệt hợp lệ** mới build. Có thể dùng `workflow_dispatch` chọn `deck_id` cho một bài nếu cần chạy lại; `all` sẽ áp dụng các bộ deck phù hợp quy trình. Không dùng artifact của demo 15 slide thay cho bài thật.

## 6. Khi có sự cố

| Triệu chứng | Kiểm tra / hướng xử lý |
|---|---|
| Đã ghi 20 slide nhưng PowerPoint chỉ có 15 | `requested_slide_count`, `len(slides)`, số trang PDF. Build sai thì CI phải fail. Demo 15 slide không phải output của bài bạn. |
| CI xanh nhưng không thấy PPTX | Xem bài đã được duyệt HITL chưa; trước duyệt chỉ có wireframe. Kiểm tra run đang ở branch của bài. |
| Thấy ảnh/tài liệu nhưng không có animation | PDF, PNG, montage không chạy animation. Xem PPTX bằng Microsoft PowerPoint Slide Show và kiểm tra trigger `On Click`. |
| Morph có nhưng trông như crossfade hoặc không thấy | Kiểm tra một chủ thể duy nhất, asset gốc và thay đổi framing đã duyệt; mở bằng PowerPoint desktop. Không tuyên bố đã thử playback chỉ từ CI. |
| Sơ đồ xếp 2+1 lệch | Kiểm tra `diagram_relationship` và bố cục đã duyệt. Phải cân đối theo quan hệ khái niệm, không tùy tiện đổi ý nghĩa. |
| Slide đầy divider | Loại bỏ line trang trí, giữ connector/timeline có chức năng và giải thích rõ. |
| Ảnh bị cắt mất đầu hoặc vật | Dùng chế độ preserve, điều chỉnh khung hoặc chọn ảnh khác có nguồn, chạy lại visual QA. |
| Đổi bố cục sau duyệt bị CI chặn | Đây là hành vi đúng. Sửa storyboard, lấy phê duyệt mới và tạo hash mới. |
| ChatGPT không truy cập được GitHub | Kiểm tra connector/quyền repo; không yêu cầu mô hình đoán source hoặc bịa kết quả CI. |

## 7. Kỹ thuật dành cho developer

```bash
npm install
python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema
python -m unittest discover -s tests -p 'test_*.py' -v

python scripts/new_deck.py my-topic --title "Bài thuyết trình" --slides 20
# Điền storyboard.json đủ chi tiết, chưa có deck.json
python scripts/check_storyboard.py decks/my-topic --proposals-only
python scripts/render_storyboard.py decks/my-topic
# Dừng để xin duyệt

python scripts/check_storyboard.py decks/my-topic --approve-quoted "Duyệt storyboard này"
python scripts/new_deck.py my-topic --from-approved-plan
# Điền deck.json và sources.json, chuẩn bị ảnh có nguồn
python scripts/run_pipeline.py --deck my-topic
```

- [`AGENTS.md`](../AGENTS.md): hướng dẫn bắt buộc cho ChatGPT khi user paste repo.
- [`references/hitl-approval.md`](hitl-approval.md): yêu cầu duyệt thật và khóa hash.
- [`references/semantic-layout.md`](semantic-layout.md): sơ đồ theo ngữ nghĩa và divider restraint.
- [`references/animation-direction.md`](animation-direction.md): nhịp click, native animation và Morph.
- [`references/design-qa.md`](design-qa.md): máy và người kiểm tra trước khi phát hành.