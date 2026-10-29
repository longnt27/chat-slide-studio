# Mẫu dùng trong chat bình thường

**Lần đầu, trước khi duyệt, đừng tạo PowerPoint ngay:**

> https://github.com/longnt27/chat-slide-studio
>
> Đọc `AGENTS.md`. Tao cần bài thuyết trình 15 slide về **[chủ đề]**, với nội dung **[...]**. **Trước tiên đề xuất bố cục chi tiết 15 slide và wireframe**, bao gồm hình minh họa và thứ tự On Click/Morph. Chưa làm PPTX. Tao sẽ duyệt bố cục trước; sau khi duyệt mới build theo bản chốt, chạy CI và gửi PPTX/PDF/preview.

**Sau khi Chat trình bày storyboard cuối cùng:**

> Duyệt bố cục 15 slide này. Triển khai đúng storyboard đã chốt, tự chạy CI, xem QA và gửi artifact.

**Nếu muốn sửa:** "Slide 5 chuyển thành sơ đồ; slide 9 dùng ảnh tư liệu; những cái khác giữ nguyên. Đề xuất lại bản cuối để tao duyệt." Chat phải cập nhật storyboard và xin duyệt lại, không tự build.

## Tránh hiểu nhầm

- Repo hướng dẫn ChatGPT qua GitHub connector; **không tự biến thành Skill cài đặt trong tài khoản**.
- Preview trước duyệt là **wireframe bố cục**, không phải PPTX. Sau khi duyệt, QA kiểm tra build có bám đúng bố cục và reveal plan.
- Slide cảm ơn mặc định là lời cảm ơn + Q&A, không thêm slogan.
- PowerPoint animations cần thử trong Microsoft PowerPoint; ảnh PDF/web không hiển thị hiệu ứng.
