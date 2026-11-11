# Repo guide

Đây là repo profile của **noName25**: file `README.md` của nó được GitHub hiển thị trên trang [github.com/banhxuanphuc](https://github.com/banhxuanphuc).

GitHub lọc bỏ CSS trong README, nên mọi phần giao diện được làm thành **ảnh SVG động**. Các ảnh này do script Python sinh ra.

## Cấu trúc

| File | Vai trò |
|---|---|
| `README.md` | Trang profile: xếp các ảnh SVG bên dưới theo thứ tự |
| **assets/** | *Ảnh đầu ra: không sửa tay, hãy chạy lại script tương ứng* |
| `assets/header.svg` | Banner khởi động: `System.init()` → NEURAL LINK → *call me noName25* |
| `assets/ascii-avatar.svg` | Avatar bằng ký tự ASCII, có glitch ERROR mỗi 15 giây |
| `assets/about.svg` | DOSSIER: thông tin cá nhân |
| `assets/skills.svg` | INSTALLED MODULES: các badge kỹ năng |
| `assets/footer.svg` | Dòng kết `END_OF_TRANSMISSION` |
| **scripts/** | *Mã nguồn sinh ảnh* |
| `scripts/theme.py` | Màu, font, khung và mốc thời gian dùng chung cho mọi panel |
| `scripts/build_header.py` | Sinh `header.svg` |
| `scripts/ascii_avatar.py` | Sinh `ascii-avatar.svg` từ `avatar.txt` (hoặc từ một ảnh) |
| `scripts/avatar.txt` | Mã ASCII gốc của avatar |
| `scripts/build_about.py` | Sinh `about.svg` |
| `scripts/build_skills.py` | Sinh `skills.svg` (logo lấy từ Simple Icons) |
| `scripts/build_footer.py` | Sinh `footer.svg` |
| `scripts/build_stats.py` | Sinh thẻ ACTIVITY từ dữ liệu GitHub thật (GraphQL API) |
| `.github/workflows/profile-stats.yml` | Chạy `build_stats.py` mỗi 6 giờ và đưa `stats.svg` lên nhánh `output` |
| `.gitignore` | Bỏ qua file build tạm và ghi chú riêng |

## Build lại

Cần Python 3.9+, chạy trong thư mục repo:

```bash
python scripts/build_header.py
python scripts/ascii_avatar.py --text scripts/avatar.txt
python scripts/build_about.py
python scripts/build_skills.py
python scripts/build_footer.py
python scripts/build_stats.py --mock -o dist/stats.svg   # xem thử thẻ activity bằng số giả
```

Thẻ activity thật được GitHub Actions tự cập nhật, không cần build tay.
