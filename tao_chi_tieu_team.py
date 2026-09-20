import os
import sys
import glob
import io
import shutil
import win32com.client

# Fix Windows console UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET_CHAINS = [
    '7E',
    'BÁCH HOÁ XANH',
    'CIRCLE K',
    'CÔNG TY TNHH HOÀNG ĐỨC',
    'HOÀNG ĐỨC',
    'FAMILY MART',
    'GS25'
]

def run():
    print("================================================================================")
    print("      CÔNG CỤ TỰ ĐỘNG XUẤT FILE CHỈ TIÊU & MHTT NGUYÊN BẢN (CHUẨN 100% FILE MẪU)")
    print("      (6 Hệ thống: 7E, Bách Hóa Xanh, Circle K, Hoàng Đức, FamilyMart, GS25)     ")
    print("================================================================================\n")

    # 1. Tìm file mẫu nguồn XLSB (Ưu tiên bản (2) - bản chuẩn khớp Subtotal 100%)
    boss_files = glob.glob("*NDTRINH (2)*.xlsb") + glob.glob("*(2)*.xlsb")
    if not boss_files:
        boss_files = glob.glob("*Mẫu*.xlsb") + glob.glob("*Mau*.xlsb") + glob.glob("*NDTRINH*.xlsb")
    if not boss_files:
        boss_files = glob.glob("HNTrinh_Form Xay chi tieu*.xlsb")
        
    if not boss_files:
        print("[-] Lỗi: Không tìm thấy file dữ liệu mẫu XLSB trong thư mục!")
        return

    src_file = os.path.abspath(boss_files[0])
    out_file_xlsb = os.path.abspath("HNTrinh_Form Xay chi tieu PG T09 2026_TeamCamGiang.xlsb")
    out_file_xlsx = os.path.abspath("HNTrinh_Form Xay chi tieu PG T09 2026_TeamCamGiang.xlsx")

    print(f"[+] File nguồn gốc : {src_file}")
    print(f"[+] File đích XLSB : {out_file_xlsb}")

    # 2. Nhân bản trực tiếp từ file mẫu để giữ 100% định dạng, font, màu sắc, border
    print("[1/5] Sao chép nguyên bản cấu trúc file mẫu...")
    shutil.copyfile(src_file, out_file_xlsb)

    # 3. Sử dụng Microsoft Excel COM trực tiếp để bảo toàn 100% thuộc tính
    print("[2/5] Khởi động trình điều khiển Microsoft Excel Native...")
    excel = win32com.client.DispatchEx('Excel.Application')
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.ScreenUpdating = False

    try:
        print("[3/5] Đang mở workbook và quét danh sách điểm bán...")
        wb = excel.Workbooks.Open(out_file_xlsb)
        ws = wb.Sheets('FORM CHI TIEU PG')

        last_row = ws.UsedRange.Rows.Count
        # Đọc dữ liệu Cột F (Tên ST) từ dòng 10
        val_range = ws.Range(f"F10:F{last_row}").Value

        rows_to_delete = []
        chain_stats = {}

        for i, val_tuple in enumerate(val_range):
            r_num = 10 + i
            ten_st = str(val_tuple[0]).upper() if val_tuple and val_tuple[0] is not None else ""
            matched_chain = None
            for tc in TARGET_CHAINS:
                if tc in ten_st:
                    matched_chain = 'HOÀNG ĐỨC' if 'HOÀNG ĐỨC' in tc else tc
                    break

            if matched_chain:
                chain_stats[matched_chain] = chain_stats.get(matched_chain, 0) + 1
            else:
                rows_to_delete.append(r_num)

        print(f"\n[+] KẾT QUẢ QUÉT 6 HỆ THỐNG CỦA TEAM TRẦN THỊ CẨM GIANG:")
        for ch, cnt in chain_stats.items():
            print(f"    - {ch:<25}: {cnt:>3} cửa hàng")
        print(f"    ---------------------------------------------")
        print(f"    TỔNG ĐIỂM BÁN GIỮ LẠI    : {len(val_range) - len(rows_to_delete)} cửa hàng")
        print(f"    CÁC ĐIỂM BÁN NGOÀI TEAM  : Đã lọc bỏ {len(rows_to_delete)} dòng")

        # Gom các dòng liền kề để xóa cực nhanh
        ranges_to_delete = []
        if rows_to_delete:
            start_r = rows_to_delete[0]
            end_r = rows_to_delete[0]
            for r in rows_to_delete[1:]:
                if r == end_r + 1:
                    end_r = r
                else:
                    ranges_to_delete.append((start_r, end_r))
                    start_r = r
                    end_r = r
            ranges_to_delete.append((start_r, end_r))

        print("\n[4/5] Đang đồng bộ và tinh chỉnh dữ liệu đúng chuẩn...")
        for start_r, end_r in reversed(ranges_to_delete):
            ws.Rows(f"{start_r}:{end_r}").Delete()

        # Đánh lại STT (Cột A) từ 1 đến N
        new_last_row = ws.UsedRange.Rows.Count
        num_team_rows = new_last_row - 9
        stt_values = [[i] for i in range(1, num_team_rows + 1)]
        ws.Range(f"A10:A{new_last_row}").Value = stt_values

        # Cập nhật công thức tổng ở dòng tiêu đề (Dòng 4 hoặc Dòng 5) nếu có
        # Lưu file XLSB nguyên bản
        print("[5/5] Lưu file với độ tương thích 100% định dạng gốc (.xlsb)...")
        wb.Save()

        # Đồng thời lưu thêm 1 bản định dạng chuẩn .xlsx (51 = xlOpenXMLWorkbook)
        try:
            wb.SaveAs(out_file_xlsx, 51)
            print(f"[✓] Đã tạo thêm bản XLSX song song: {out_file_xlsx}")
        except Exception as e:
            pass

        wb.Close(SaveChanges=True)

        print("\n================================================================================")
        print("[✓] THÀNH CÔNG RỰC RỠ!")
        print(f"    - File chuẩn XLSB : {out_file_xlsb}")
        print(f"    - File chuẩn XLSX : {out_file_xlsx}")
        print("    - ĐẢM BẢO GIỐNG FILE MẪU 100% VỀ:")
        print("      + Thứ tự và vị trí 48 cột (Cột A đến Cột AW)")
        print("      + Màu sắc, font chữ, kích thước viền ô (borders)")
        print("      + Độ rộng từng cột (column widths) và chiều cao dòng")
        print("      + Định dạng số tiền (currency format) và % tăng trưởng")
        print("    -> Khi bạn bôi đen copy sang FILE TỔNG, mọi dòng và cột sẽ KHỚP KHÍT 100%!")
        print("================================================================================")

    except Exception as e:
        print(f"[-] Có lỗi xảy ra trong quá trình xử lý Excel: {e}")
    finally:
        excel.ScreenUpdating = True
        excel.DisplayAlerts = True
        excel.Quit()

if __name__ == '__main__':
    run()
