# Mẫu câu ngắn để dùng lại trong ChatGPT thường

```
https://github.com/longnt27/chat-slide-studio
Dùng AGENTS.md trong repo này. Tạo một bài PowerPoint hoàn chỉnh [SỐ] slide về [CHỦ ĐỀ] từ [NỘI DUNG]. Tự tìm ảnh đúng nguồn, viết notes, điều phối Auto / On Click / Morph có ý nghĩa. Commit branch, chạy GitHub CI, tải artifact, xem montage từng slide, sửa các lỗi rồi gửi PPTX + PDF + preview.
```

**Cam kết số slide:** Nếu câu lệnh nói `15 slide`, Chat bắt buộc khai báo `requested_slide_count: 15` và xuất đúng 15 slide. CI không chấp nhận 8 slide dù render đẹp và không lỗi. Demo trong repo cũng phải được kiểm chứng với 15 slide để thử trọn quy trình.

**Không phải Work.** ChatGPT sẽ đọc file hướng dẫn từ GitHub connector trong cuộc chat khi nhận đường link và yêu cầu này. Link repo không tự cài skill vào tài khoản; có thể ghim mẫu prompt trong chat hoặc Custom Instructions để khỏi gõ lại.
