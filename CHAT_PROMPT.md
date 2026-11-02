# Mẫu prompt dùng với ChatGPT thường

Repo: https://github.com/longnt27/chat-slide-studio

Cần kết nối GitHub với ChatGPT và cấp quyền phù hợp. Các prompt bên dưới áp dụng cho **ChatGPT thường, không cần Work hoặc Skill ZIP**. Số slide chỉ là ví dụ: thay 20 bằng 1 slide đơn hoặc 3–80 slide theo yêu cầu (hiện chưa hỗ trợ bài đúng 2 slide).

## 1. Đề xuất bố cục trước (HITL)

```text
Dùng https://github.com/longnt27/chat-slide-studio.
Đọc AGENTS.md và toàn bộ tài liệu liên quan trong repo.
Tao cần bài PowerPoint 20 slide về [CHỦ ĐỀ], dành cho [ĐỐI TƯỢNG],
trình bày trong [THỜI LƯỢNG]. Nội dung chính: [BRIEF/TÀI LIỆU].

Giai đoạn này CHỈ đề xuất storyboard đủ 20 slide và wireframe:
- Ý chính và tiêu đề mỗi slide, thông tin/ảnh cần minh họa
- Bố cục thực sự thể hiện mối quan hệ nội dung
- Nhịp Auto/On Click và các Morph có lý do (nếu phù hợp)
- Speaker Notes dự kiến

Giảm divider và slogan thừa. Chưa tạo deck.json/PPTX.
Tạo branch, commit storyboard, chạy preview CI và gửi tao xem để duyệt.
```

## 2. Yêu cầu chỉnh storyboard, vẫn chưa build

```text
Sửa bản storyboard đang đề xuất:
- Slide [N]: đổi thành [BỐ CỤC/QUAN HỆ], bởi vì [LÝ DO]
- Slide [M]: đổi ảnh/chú thích/nhịp click theo [YÊU CẦU]
- Giữ nguyên những slide còn lại.
Cập nhật storyboard và wireframe, đưa bản cuối cho tao duyệt.
CHƯA build PPTX và CHƯA tự đánh dấu đã duyệt.
```

## 3. Duyệt bản cuối và triển khai

```text
Tao duyệt storyboard cuối cùng vừa trình bày.
Khóa đúng phiên bản đó qua approval.json rồi tạo deck.json
bám sát từng slide, bố cục, quan hệ giữa các khối,
On Click và Morph đã duyệt.
Chạy GitHub Actions, kiểm tra PPTX/PDF, render và soát 100% slide.
Sửa lỗi tại source, chạy CI lại. Gửi file, link artifact, QA report.
Không merge vào main nếu chưa được tao yêu cầu.
```

## 4. Rà soát một deck đã build

```text
Rà soát bài [DECK/BRANCH] trong repo chat-slide-studio.
Kiểm tra từng slide ở kích thước đầy đủ: ảnh crop, text overlap,
căn giữa thật, mật độ divider, quan hệ bố cục, nhịp click,
nhóm khung+chữ+ảnh, và Morph giữa các slide kề nhau.
Sửa source trong branch rồi chạy CI; nếu thay đổi bố cục đã duyệt,
hãy đưa storyboard mới để tao duyệt trước khi build.
Đừng coi PDF/preview tĩnh là bằng chứng animation hoạt động.
```

## 5. Khi cần Morph có chủ đích

```text
Tao muốn có Morph nhưng chỉ ở chỗ làm rõ mạch nội dung.
Trong storyboard, đề xuất từng cặp slide và chỉ ra chính xác
chủ thể nào được giữ lại, từ vị trí/tỷ lệ nào sang vị trí/tỷ lệ nào,
người xem hiểu thêm điều gì. Nếu không có cặp phù hợp, nói rõ.
Không morph số trang, title trang trí hoặc object không liên quan.
```

## Những điều dễ nhầm

- `decks/demo` có 15 slide **không có nghĩa** bài mới phải 15. Số lượng do user đặt trong prompt.
- Khi chưa có duyệt HITL, CI chỉ tạo storyboard preview; không có PPTX là **đúng**.
- Không gọi trang cảm ơn là cơ hội thêm slogan kiểu “Lịch sử là mạch nối”.
- Khác biệt quan trọng: `peers` = đồng cấp; `hierarchy` = phân cấp; `reciprocal` = hai chiều. Không xếp bố cục chỉ để lấp ô.
- Đường ngang thực sự là trục timeline có thể hợp lý; divider trang trí thì bỏ.
- PowerPoint bản PDF và ảnh tĩnh không hiển thị animation. Chỉ xác nhận phát Morph/On Click sau khi thử Slide Show trong Microsoft PowerPoint.
- Người dùng có quyền duyệt storyboard, **không đồng nghĩa** đã cho phép merge branch lên `main`.