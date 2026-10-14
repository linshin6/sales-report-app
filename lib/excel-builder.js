const ExcelJS = require("exceljs");
const { FM_CATEGORIES, DEFAULT_FM_STORES } = require("./fm-data.js");

function openpyxlColLetter(colIdx) {
      let temp = colIdx;
      let letter = '';
      while (temp > 0) {
        let mod = (temp - 1) % 26;
        letter = String.fromCharCode(65 + mod) + letter;
        temp = Math.floor((temp - mod) / 26);
      }
      return letter;
    }

    async function buildExcelWorkbook(p) {
      const wb = new ExcelJS.Workbook();
        wb.creator = 'Team Lead ' + p.team_lead;
        wb.created = new Date();

        const thinBorder = {
          top: { style: 'thin', color: { argb: 'FFB4B4B4' } },
          left: { style: 'thin', color: { argb: 'FFB4B4B4' } },
          bottom: { style: 'thin', color: { argb: 'FFB4B4B4' } },
          right: { style: 'thin', color: { argb: 'FFB4B4B4' } }
        };

        // -------------------------------------------------------------
        // SHEET 1: DASHBOARD
        // -------------------------------------------------------------
        const ws1 = wb.addWorksheet('Dashboard', { properties: { tabColor: { argb: 'FF1F4E78' } } });
        ws1.columns = [
          { width: 4 }, { width: 10 }, { width: 25 }, { width: 18 },
          { width: 18 }, { width: 18 }, { width: 18 }, { width: 14 }
        ];

        // Banner Title B2:H2
        ws1.mergeCells('B2:H2');
        const b2 = ws1.getCell('B2');
        b2.value = '📊 THEO DÕI DOANH SỐ TEAM - ' + p.team_lead.toUpperCase();
        b2.font = { name: 'Calibri', size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
        b2.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        b2.alignment = { horizontal: 'center', vertical: 'middle' };
        ws1.getRow(2).height = 35;

        // Metadata B3:H3
        const setMeta = (c, val, isLbl, isRed) => {
          const cell = ws1.getCell(c);
          cell.value = val;
          cell.font = { name: 'Calibri', bold: true, color: { argb: isRed ? 'FFC00000' : 'FF000000' } };
          cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: isLbl ? 'FFFFF2CC' : 'FFFFF9E6' } };
          cell.alignment = { horizontal: 'center', vertical: 'middle' };
          cell.border = thinBorder;
        };
        setMeta('B3', 'Tháng:', true, false);
        setMeta('C3', p.month + '/' + p.year, false, true);
        setMeta('D3', 'Team Lead:', true, false);
        setMeta('E3', p.team_lead, false, false);
        setMeta('F3', '% Timegone:', true, false);
        setMeta('G3', p.timegone / 100, false, true);
        ws1.getCell('G3').numFmt = '0.0%';
        const nowD = new Date();
        setMeta('H3', 'Cập nhật: ' + String(nowD.getDate()).padStart(2,'0') + '/' + String(nowD.getMonth()+1).padStart(2,'0') + '/' + nowD.getFullYear(), false, false);
        ws1.getRow(3).height = 24;

        // Section Title B5:G5
        ws1.mergeCells('B5:G5');
        const b5 = ws1.getCell('B5');
        b5.value = '🎯 TỔNG QUAN DOANH SỐ TEAM';
        b5.font = { name: 'Calibri', size: 13, bold: true, color: { argb: 'FF1F4E78' } };
        b5.alignment = { horizontal: 'center', vertical: 'middle' };
        ws1.getRow(5).height = 26;

        // Row 6 & 7: Thẻ KPI Doanh Số Thực Tế (B to G)
        const kpiDef = [
          { col: 'B', lbl: 'Thực Hiện BHX', val: p.total_actual_bhx, fmt: '#,##0', bg: 'FF70AD47', fg: 'FFFFFFFF' },
          { col: 'C', lbl: 'Thực Hiện CVS', val: p.total_cvs, fmt: '#,##0', bg: 'FFED7D31', fg: 'FFFFFFFF' },
          { col: 'D', lbl: 'Tổng Thực Hiện', val: p.total_actual, fmt: '#,##0', bg: 'FF2E75B6', fg: 'FFFFFFFF' },
          { col: 'E', lbl: 'Tổng CH BHX Team', val: (p.total_stores_bhx_team || 178) + ' CH', fmt: null, bg: 'FF4472C4', fg: 'FFFFFFFF' },
          { col: 'F', lbl: 'TB Doanh Số/CH BHX', val: p.bhx_per_store, fmt: '#,##0', bg: 'FF70AD47', fg: 'FFFFFFFF' },
          { col: 'G', lbl: 'Số Nhân Viên', val: (p.employees || []).length + ' NV', fmt: null, bg: 'FF595959', fg: 'FFFFFFFF' }
        ];

        kpiDef.forEach(k => {
          const lCell = ws1.getCell(k.col + '6');
          lCell.value = k.lbl;
          lCell.font = { name: 'Calibri', size: 10, bold: true, color: { argb: k.fg } };
          lCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: k.bg } };
          lCell.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
          lCell.border = thinBorder;

          const vCell = ws1.getCell(k.col + '7');
          vCell.value = k.val;
          if (k.fmt) vCell.numFmt = k.fmt;
          vCell.font = { name: 'Calibri', size: 12, bold: true };
          vCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF2F2F2' } };
          vCell.alignment = { horizontal: 'center', vertical: 'middle' };
          vCell.border = thinBorder;
        });
        ws1.getRow(6).height = 30;
        ws1.getRow(7).height = 28;

        // Row 9: Status Bar B9:G9
        ws1.mergeCells('B9:G9');
        const b9 = ws1.getCell('B9');
        b9.value = '📊 BẢNG THEO DÕI DOANH SỐ CHI TIẾT - TEAM ' + p.team_lead.toUpperCase() + ' - THÁNG ' + p.month + '/' + p.year;
        b9.font = { name: 'Calibri', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
        b9.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        b9.alignment = { horizontal: 'center', vertical: 'middle' };
        ws1.getRow(9).height = 25;

        // Row 11: Header Bảng Xếp Hạng
        ws1.mergeCells('B11:G11');
        const b11 = ws1.getCell('B11');
        b11.value = 'XẾP HẠNG DOANH SỐ NHÂN VIÊN';
        b11.font = { name: 'Calibri', size: 13, bold: true, color: { argb: 'FF1F4E78' } };
        b11.alignment = { horizontal: 'center', vertical: 'middle' };
        ws1.getRow(11).height = 26;

        // Row 12: Headers B12:G12 (Bỏ Target và % Đạt)
        const rHeaders = ['Hạng', 'Nhân Viên', 'Doanh Số BHX', 'Doanh Số CVS', 'Tổng Thực Hiện', 'Tỷ Trọng DS'];
        const rCols = ['B', 'C', 'D', 'E', 'F', 'G'];
        rHeaders.forEach((h, i) => {
          const c = ws1.getCell(rCols[i] + '12');
          c.value = h;
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws1.getRow(12).height = 26;

        const sortedEmps = (p.employees || []).slice().sort((a, b) => (b.total_actual || 0) - (a.total_actual || 0));
        const rankTotRow = 13 + sortedEmps.length;
        sortedEmps.forEach((e, idx) => {
          const rowNum = 13 + idx;
          const setCell = (col, val, fmt, isBold, align) => {
            const c = ws1.getCell(col + rowNum);
            c.value = val;
            if (fmt) c.numFmt = fmt;
            c.font = { name: 'Calibri', bold: !!isBold };
            c.alignment = { horizontal: align || 'left', vertical: 'middle' };
            c.border = thinBorder;
            return c;
          };
          setCell('B', idx + 1, null, true, 'center');
          setCell('C', e.name, null, true, 'left');
          setCell('D', e.bhx_actual || 0, '#,##0', false, 'right');
          setCell('E', e.cvs_total || 0, '#,##0', false, 'right');
          setCell('F', { formula: `D${rowNum}+E${rowNum}`, result: e.total_actual || 0 }, '#,##0', true, 'right');
          const pctShare = p.total_actual > 0 ? ((e.total_actual || 0) / p.total_actual) : 0;
          setCell('G', { formula: `F${rowNum}/$F$${rankTotRow}`, result: pctShare }, '0.0%', false, 'center');
          ws1.getRow(rowNum).height = 22;
        });

        // Row Total for Rank table
        ws1.mergeCells(`B${rankTotRow}:C${rankTotRow}`);
        const rTotLbl = ws1.getCell(`B${rankTotRow}`);
        rTotLbl.value = 'TỔNG CỘNG TEAM';
        rTotLbl.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
        rTotLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        rTotLbl.alignment = { horizontal: 'center', vertical: 'middle' };
        rTotLbl.border = thinBorder;
        ws1.getCell(`C${rankTotRow}`).border = thinBorder;

        const setTotCell = (col, formula, result, fmt) => {
          const c = ws1.getCell(`${col}${rankTotRow}`);
          c.value = { formula, result };
          c.numFmt = fmt;
          c.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
          c.alignment = { horizontal: 'right', vertical: 'middle' };
          c.border = thinBorder;
        };
        setTotCell('D', `SUM(D13:D${rankTotRow-1})`, p.total_actual_bhx, '#,##0');
        setTotCell('E', `SUM(E13:E${rankTotRow-1})`, p.total_cvs, '#,##0');
        setTotCell('F', `SUM(F13:F${rankTotRow-1})`, p.total_actual, '#,##0');
        const rTotG = ws1.getCell(`G${rankTotRow}`);
        rTotG.value = { formula: `SUM(G13:G${rankTotRow-1})`, result: 1 };
        rTotG.numFmt = '0.0%';
        rTotG.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFF00' } };
        rTotG.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        rTotG.alignment = { horizontal: 'center', vertical: 'middle' };
        rTotG.border = thinBorder;
        ws1.getRow(rankTotRow).height = 25;

        // -------------------------------------------------------------
        // SHEET 2: TIẾN ĐỘ TEAM
        // -------------------------------------------------------------
        const ws2 = wb.addWorksheet('Tiến độ Team', { properties: { tabColor: { argb: 'FF70AD47' } } });
        ws2.columns = [
          { width: 3 }, { width: 6 }, { width: 24 }, { width: 16 },
          { width: 14 }, { width: 14 }, { width: 14 }, { width: 14 },
          { width: 14 }, { width: 14 }, { width: 20 }
        ];

        // Banner B2:K2
        ws2.mergeCells('B2:K2');
        const wb2 = ws2.getCell('B2');
        wb2.value = 'THEO DÕI DOANH SỐ - TEAM ' + p.team_lead.toUpperCase() + ' - THÁNG ' + p.month + '/' + p.year;
        wb2.font = { name: 'Calibri', size: 14, bold: true, color: { argb: 'FFFFFFFF' } };
        wb2.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        wb2.alignment = { horizontal: 'center', vertical: 'middle' };
        ws2.getRow(2).height = 30;

        // Info Row B3:K3
        const setInfo = (col, val, isLbl, isRed) => {
          const c = ws2.getCell(col + '3');
          c.value = val;
          c.font = { name: 'Calibri', bold: true, color: { argb: isRed ? 'FFC00000' : 'FF000000' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: isLbl ? 'FFFFF2CC' : 'FFFFF9E6' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        };
        setInfo('B', 'Tháng:', true, false);
        setInfo('C', p.month + '/' + p.year, false, true);
        setInfo('D', 'Tổng CH BHX:', true, false);
        setInfo('E', p.total_stores_bhx_team || p.total_stores_bhx, false, true);
        setInfo('F', 'TB BHX/CH:', true, false);
        setInfo('G', p.bhx_per_store, false, true);
        ws2.getCell('G3').numFmt = '#,##0';
        setInfo('H', 'Cập nhật:', true, false);
        setInfo('I', String(nowD.getDate()).padStart(2,'0') + '/' + String(nowD.getMonth()+1).padStart(2,'0') + '/' + nowD.getFullYear(), false, false);
        setInfo('J', '% Timegone:', true, false);
        setInfo('K', p.timegone / 100, false, true);
        ws2.getCell('K3').numFmt = '0.0%';
        ws2.getRow(3).height = 24;

        // Group headers
        ws2.mergeCells('D5:J5');
        const g1 = ws2.getCell('D5');
        g1.value = 'THỰC HIỆN (chi tiết theo từng kênh)';
        g1.font = { name: 'Calibri', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
        g1.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
        g1.alignment = { horizontal: 'center', vertical: 'middle' };

        const g2 = ws2.getCell('K5');
        g2.value = 'TỔNG CỘNG';
        g2.font = { name: 'Calibri', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
        g2.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        g2.alignment = { horizontal: 'center', vertical: 'middle' };
        ws2.getRow(5).height = 22;

        // Subheaders Row 6 (Bỏ Target và % Đạt)
        const teamHeaders = [
          'STT', 'Nhân Viên', 'BHX\n(cố định)', 'GS25', '7-Eleven',
          'FamilyMart', 'Circle K', 'Hoàng Đức', 'WinMart+', 'Tổng TH\n(BHX+CVS)'
        ];
        const teamCols = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'];
        teamHeaders.forEach((th, idx) => {
          const c = ws2.getCell(teamCols[idx] + '6');
          c.value = th;
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
          c.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true };
          c.border = thinBorder;
        });
        ws2.getRow(6).height = 40;

        // 10 Employee rows
        p.employees.forEach((emp, k) => {
          const r = 7 + k;
          const setC = (col, val, fmt, isBold, align) => {
            const cell = ws2.getCell(col + r);
            cell.value = val;
            if (fmt) cell.numFmt = fmt;
            cell.font = { name: 'Calibri', bold: !!isBold };
            cell.alignment = { horizontal: align || 'left', vertical: 'middle' };
            cell.border = thinBorder;
            return cell;
          };

          setC('B', k + 1, null, false, 'center');
          setC('C', emp.name, null, true, 'left');
          setC('D', emp.bhx_actual, '#,##0', false, 'right');
          setC('E', emp.gs25_actual, '#,##0', false, 'right');
          setC('F', emp.se_actual, '#,##0', false, 'right');
          setC('G', emp.fm_actual, '#,##0', false, 'right');
          setC('H', emp.ck_actual, '#,##0', false, 'right');
          setC('I', emp.hd_actual, '#,##0', false, 'right');
          setC('J', emp.wmp_actual, '#,##0', false, 'right');

          // Tổng TH formula =SUM(D..:J..)
          setC('K', { formula: `SUM(D${r}:J${r})`, result: emp.total_actual }, '#,##0', true, 'right');
          ws2.getRow(r).height = 22;
        });

        // Row Total TỔNG TEAM
        const totalR = 7 + p.employees.length;
        ws2.mergeCells(`B${totalR}:C${totalR}`);
        const totLbl = ws2.getCell(`B${totalR}`);
        totLbl.value = 'TỔNG TEAM';
        totLbl.font = { name: 'Calibri', size: 12, bold: true, color: { argb: 'FFFFFFFF' } };
        totLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        totLbl.alignment = { horizontal: 'center', vertical: 'middle' };
        totLbl.border = thinBorder;
        ws2.getCell(`C${totalR}`).border = thinBorder;

        const sumCols = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'];
        const sumResults = [
          p.total_actual_bhx,
          p.employees.reduce((a,x)=>a+x.gs25_actual,0),
          p.employees.reduce((a,x)=>a+x.se_actual,0),
          p.employees.reduce((a,x)=>a+x.fm_actual,0),
          p.employees.reduce((a,x)=>a+x.ck_actual,0),
          p.employees.reduce((a,x)=>a+x.hd_actual,0),
          p.employees.reduce((a,x)=>a+x.wmp_actual,0),
          p.total_actual
        ];
        sumCols.forEach((col, idx) => {
          const sc = ws2.getCell(`${col}${totalR}`);
          sc.value = { formula: `SUM(${col}7:${col}${totalR-1})`, result: sumResults[idx] };
          sc.numFmt = '#,##0';
          sc.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
          sc.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
          sc.alignment = { horizontal: 'right', vertical: 'middle' };
          sc.border = thinBorder;
        });
        ws2.getRow(totalR).height = 28;

        // Freeze Panes at D7
        ws2.views = [{ state: 'frozen', xSplit: 3, ySplit: 6 }];

        // -------------------------------------------------------------
        // SHEET 3: CHI TIẾT CVS
        // -------------------------------------------------------------
        const ws3 = wb.addWorksheet('Chi tiết CVS', { properties: { tabColor: { argb: 'FFED7D31' } } });
        ws3.columns = [
          { width: 6 }, { width: 22 }, { width: 14 }, { width: 16 }, { width: 45 }, { width: 18 }
        ];

        ws3.mergeCells('A1:F1');
        const t3 = ws3.getCell('A1');
        t3.value = 'CHI TIẾT DOANH SỐ CVS - TỪNG CỬA HÀNG';
        t3.font = { name: 'Calibri', size: 14, bold: true, color: { argb: 'FFFFFFFF' } };
        t3.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        t3.alignment = { horizontal: 'center', vertical: 'middle' };
        ws3.getRow(1).height = 30;

        const cvsHeaders = ['STT', 'Nhân Viên', 'Chuỗi', 'Mã CH', 'Địa Chỉ', 'Thực Hiện'];
        cvsHeaders.forEach((ch, idx) => {
          const colLetter = String.fromCharCode(65 + idx);
          const c = ws3.getCell(colLetter + '3');
          c.value = ch;
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws3.getRow(3).height = 25;

        let curR3 = 4;
        let sttCounter = 1;
        const chainColors = {
          'GS25': 'FF4472C4', '7-Eleven': 'FF00B050', '7E': 'FF00B050', 'FamilyMart': 'FFED7D31',
          'Circle K': 'FFC00000', 'Hoàng Đức': 'FF70AD47', 'Hoàng Đức Long Khánh': 'FF70AD47',
          'Hoàng Đức Gia Kiệm': 'FF008080', 'WinMart+': 'FFD9534F', 'WMP': 'FFD9534F'
        };

        p.employees.forEach(emp => {
          const empStores = p.stores.filter(s => s.employee_name === emp.name);
          if (empStores.length === 0) return;

          // Subheader row
          ws3.mergeCells(`A${curR3}:D${curR3}`);
          const sHead = ws3.getCell(`A${curR3}`);
          sHead.value = '👤 ' + emp.name + ' (' + empStores.length + ' cửa hàng CVS)';
          sHead.font = { name: 'Calibri', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
          sHead.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
          sHead.alignment = { horizontal: 'left', vertical: 'middle', indent: 1 };
          sHead.border = thinBorder;

          const sLbl = ws3.getCell(`E${curR3}`);
          sLbl.value = 'TỔNG CVS:';
          sLbl.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
          sLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
          sLbl.alignment = { horizontal: 'right', vertical: 'middle' };
          sLbl.border = thinBorder;

          const sTot = ws3.getCell(`F${curR3}`);
          const empTotVal = empStores.reduce((a,x)=>a+(x.actual||0), 0);
          sTot.value = empTotVal;
          sTot.numFmt = '#,##0';
          sTot.font = { name: 'Calibri', size: 11, bold: true, color: { argb: 'FFFFFF00' } };
          sTot.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
          sTot.alignment = { horizontal: 'right', vertical: 'middle' };
          sTot.border = thinBorder;
          ws3.getRow(curR3).height = 24;
          curR3++;

          empStores.forEach(st => {
            const setS = (col, val, fmt, isBold, align) => {
              const c = ws3.getCell(col + curR3);
              c.value = val;
              if (fmt) c.numFmt = fmt;
              c.font = { name: 'Calibri', size: 10, bold: !!isBold };
              c.alignment = { horizontal: align || 'left', vertical: 'middle' };
              c.border = thinBorder;
              return c;
            };

            setS('A', sttCounter, null, false, 'center');
            setS('B', emp.name, null, false, 'left');

            const chCell = setS('C', st.chain, null, true, 'center');
            chCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: chainColors[st.chain] || 'FF70AD47' } };
            chCell.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };

            setS('D', st.store_code || '', null, false, 'left');
            setS('E', st.store_address || '', null, false, 'left');
            setS('F', st.actual || 0, '#,##0', false, 'right');

            ws3.getRow(curR3).height = 20;
            curR3++;
            sttCounter++;
          });
        });

        // Grand Total Row
        ws3.mergeCells(`A${curR3}:E${curR3}`);
        const gtLbl = ws3.getCell(`A${curR3}`);
        gtLbl.value = '🎯 TỔNG CVS TOÀN TEAM';
        gtLbl.font = { name: 'Calibri', size: 12, bold: true, color: { argb: 'FFFFFFFF' } };
        gtLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        gtLbl.alignment = { horizontal: 'center', vertical: 'middle' };
        gtLbl.border = thinBorder;

        const gtVal = ws3.getCell(`F${curR3}`);
        gtVal.value = p.total_cvs;
        gtVal.numFmt = '#,##0';
        gtVal.font = { name: 'Calibri', size: 12, bold: true, color: { argb: 'FFFFFF00' } };
        gtVal.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        gtVal.alignment = { horizontal: 'right', vertical: 'middle' };
        gtVal.border = thinBorder;
        ws3.getRow(curR3).height = 28;

        ws3.views = [{ state: 'frozen', ySplit: 3 }];

        // -------------------------------------------------------------
        // SHEET 4: DATA BHX
        // -------------------------------------------------------------
        const ws4 = wb.addWorksheet('Data BHX', { properties: { tabColor: { argb: 'FF4472C4' } } });
        ws4.columns = [
          { width: 6 }, { width: 24 }, { width: 14 }, { width: 16 }, { width: 18 }, { width: 14 }
        ];

        ws4.mergeCells('A1:F1');
        const t4 = ws4.getCell('A1');
        t4.value = 'PHÂN BỔ DOANH SỐ BHX (' + p.total_stores_bhx + ' CỬA HÀNG)';
        t4.font = { name: 'Calibri', size: 13, bold: true, color: { argb: 'FFFFFFFF' } };
        t4.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        t4.alignment = { horizontal: 'center', vertical: 'middle' };
        ws4.getRow(1).height = 28;

        const setBhxTop = (row, lbl, val, fmt, isRed) => {
          const a = ws4.getCell('A' + row);
          a.value = lbl;
          a.font = { name: 'Calibri', bold: true };
          a.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF2CC' } };
          a.border = thinBorder;

          const b = ws4.getCell('B' + row);
          b.value = val;
          if (fmt) b.numFmt = fmt;
          b.font = { name: 'Calibri', bold: true, color: { argb: isRed ? 'FFC00000' : 'FF000000' } };
          b.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF9E6' } };
          b.border = thinBorder;
        };
        setBhxTop(3, 'Tổng DS 5 Hubs Hệ Thống:', p.total_actual_bhx_hubs || p.total_actual_bhx, '#,##0', true);
        setBhxTop(4, 'Tổng số CH hệ thống:', p.total_stores_bhx, null, false);
        setBhxTop(5, 'TB doanh số/CH:', { formula: 'B3/B4', result: p.bhx_per_store }, '#,##0', true);

        const bhxHeaders = ['STT', 'Nhân Viên', 'Số CH BHX', 'TB/CH', 'Doanh Số BHX', '% BHX/Team'];
        bhxHeaders.forEach((bh, idx) => {
          const colLetter = String.fromCharCode(65 + idx);
          const c = ws4.getCell(colLetter + '7');
          c.value = bh;
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws4.getRow(7).height = 25;

        const bhxTotRow = 8 + p.employees.length;

        p.employees.forEach((emp, idx) => {
          const r = 8 + idx;
          const setB = (col, val, fmt, isBold, align) => {
            const cell = ws4.getCell(col + r);
            cell.value = val;
            if (fmt) cell.numFmt = fmt;
            cell.font = { name: 'Calibri', bold: !!isBold };
            cell.alignment = { horizontal: align || 'left', vertical: 'middle' };
            cell.border = thinBorder;
            return cell;
          };

          setB('A', idx + 1, null, false, 'center');
          setB('B', emp.name, null, true, 'left');
          setB('C', emp.bhx_stores, null, false, 'center');
          setB('D', { formula: '$B$5', result: p.bhx_per_store }, '#,##0', false, 'right');
          setB('E', { formula: `C${r}*D${r}`, result: emp.bhx_actual }, '#,##0', true, 'right');
          setB('F', { formula: `E${r}/$E$${bhxTotRow}`, result: p.total_actual_bhx > 0 ? (emp.bhx_actual / p.total_actual_bhx) : 0 }, '0.0%', false, 'center');
          ws4.getRow(r).height = 20;
        });

        ws4.mergeCells(`A${bhxTotRow}:B${bhxTotRow}`);
        const bTotLbl = ws4.getCell(`A${bhxTotRow}`);
        bTotLbl.value = 'TỔNG CỘNG TEAM';
        bTotLbl.font = { name: 'Calibri', bold: true };
        bTotLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        bTotLbl.alignment = { horizontal: 'center', vertical: 'middle' };
        bTotLbl.border = thinBorder;

        const bTotC = ws4.getCell(`C${bhxTotRow}`);
        bTotC.value = { formula: `SUM(C8:C${bhxTotRow-1})`, result: p.employees.reduce((a,x)=>a+x.bhx_stores,0) };
        bTotC.font = { name: 'Calibri', bold: true };
        bTotC.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        bTotC.alignment = { horizontal: 'center', vertical: 'middle' };
        bTotC.border = thinBorder;

        const bTotD = ws4.getCell(`D${bhxTotRow}`);
        bTotD.value = { formula: '$B$5', result: p.bhx_per_store };
        bTotD.numFmt = '#,##0';
        bTotD.font = { name: 'Calibri', bold: true };
        bTotD.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        bTotD.alignment = { horizontal: 'right', vertical: 'middle' };
        bTotD.border = thinBorder;

        const bTotE = ws4.getCell(`E${bhxTotRow}`);
        bTotE.value = { formula: `SUM(E8:E${bhxTotRow-1})`, result: p.total_actual_bhx };
        bTotE.numFmt = '#,##0';
        bTotE.font = { name: 'Calibri', bold: true };
        bTotE.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        bTotE.alignment = { horizontal: 'right', vertical: 'middle' };
        bTotE.border = thinBorder;

        const bTotF = ws4.getCell(`F${bhxTotRow}`);
        bTotF.value = { formula: `SUM(F8:F${bhxTotRow-1})`, result: 1 };
        bTotF.numFmt = '0.0%';
        bTotF.font = { name: 'Calibri', bold: true };
        bTotF.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        bTotF.alignment = { horizontal: 'center', vertical: 'middle' };
        bTotF.border = thinBorder;
        ws4.getRow(bhxTotRow).height = 24;


        // -------------------------------------------------------------
        // SHEET 5: CONFIG
        // -------------------------------------------------------------
        const ws5 = wb.addWorksheet('Config', { properties: { tabColor: { argb: 'FF595959' } } });
        ws5.columns = [{ width: 35 }, { width: 35 }];

        ws5.mergeCells('A1:B1');
        const t5 = ws5.getCell('A1');
        t5.value = 'THÔNG SỐ CẤU HÌNH HỆ THỐNG';
        t5.font = { name: 'Calibri', size: 12, bold: true, color: { argb: 'FFFFFFFF' } };
        t5.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        t5.alignment = { horizontal: 'center', vertical: 'middle' };
        ws5.getRow(1).height = 28;

        const nowStr = new Date().toLocaleDateString('vi-VN') + ' ' + new Date().toLocaleTimeString('vi-VN');
        const cfgItems = [
          ['Team Lead', p.team_lead],
          ['Tháng Báo Cáo', p.month],
          ['Năm Báo Cáo', p.year],
          ['% Timegone Thực Tế', p.timegone + '%'],
          ['Tổng Cửa Hàng BHX Hệ Thống', p.total_stores_bhx || 240],
          ['Tổng Cửa Hàng GS25 Hệ Thống', 72],
          ['Hệ Số Phân Bổ GS25 (2 DC)', '20.46%'],
          ['Tổng Cửa Hàng 7-Eleven Phụ Trách', 5],
          ['Hệ Số Phân Bổ 7-Eleven (2 DC)', '3.62%'],
          ['Thời Gian Xuất Báo Cáo', nowStr]
        ];

        cfgItems.forEach((item, idx) => {
          const r = 3 + idx;
          const ca = ws5.getCell('A' + r);
          ca.value = item[0];
          ca.font = { name: 'Calibri', bold: true };
          ca.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF2F2F2' } };
          ca.border = thinBorder;

          const cb = ws5.getCell('B' + r);
          cb.value = item[1];
          cb.alignment = { horizontal: 'center', vertical: 'middle' };
          cb.border = thinBorder;
          ws5.getRow(r).height = 22;
        });

        // -------------------------------------------------------------
        // SHEET 6: CHI TIẾT HUBS & PHÂN BỔ FAMILYMART (HIỂN THỊ GIỐNG BÁCH HÓA XANH)
        // -------------------------------------------------------------
        const ws6 = wb.addWorksheet('Chi tiết FamilyMart', { properties: { tabColor: { argb: 'FFED7D31' } } });
        ws6.columns = [
          { width: 8 },  // A: STT
          { width: 50 }, // B: Tên Hub / Nhân viên
          { width: 22 }, // C: Doanh số Hub / Số CH
          { width: 22 }, // D: Ghi chú / TB CH
          { width: 26 }, // E: Doanh số phân bổ
          { width: 16 }  // F: % Tỷ trọng
        ];

        // Row 1: Title Banner
        ws6.mergeCells('A1:F1');
        const t6 = ws6.getCell('A1');
        t6.value = '🏪 BÁO CÁO CHI TIẾT HUBS & PHÂN BỔ DOANH SỐ - CHUỖI FAMILYMART';
        t6.font = { name: 'Calibri', size: 12, bold: true, color: { argb: 'FFFFFFFF' } };
        t6.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E78' } };
        t6.alignment = { horizontal: 'center', vertical: 'middle' };
        ws6.getRow(1).height = 28;

        const fmHubsList = p.fm_hubs || [
          { name: '125 Điện Biên Phủ, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 543750 },
          { name: '18A Lưu Trọng Lư, P. Tân Thuận, TP. HCM', code: 'PNTU', amount: 141921000 },
          { name: '34, Hiệp Bình, KP 8, Phường Hiệp Bình Phước, Quận Thủ Đức, TP. Hồ Chí Minh', code: 'PNTU', amount: 483600 },
          { name: '97/99 Nguyễn Hữu Cầu, Phường Tân Định, TP.Hồ Chí Minh', code: 'PNTU', amount: 608100 },
          { name: 'Kho Anpha AG – Lô E02, đường số 2, khu công nghiệp Long Hậu, xã Cần Giuộc, tỉnh Tây Ninh', code: 'PNTU', amount: 589017600 },
          { name: 'G05, Tầng trệt, Block CT2, Thửa đất số 351, Đại lộ Bình Dương, Khu phố Hưng Lộc, Phường Thuận An, Thành Phố Hồ Chí Minh', code: 'PNTU', amount: 633600 }
        ];
        const totFmHubs = p.total_actual_fm_hubs || fmHubsList.reduce((a, b) => a + (b.amount || 0), 0);
        const totStoresFmSys = p.total_stores_fm || 196;
        const fmUnitPrice = p.fm_per_store || Math.round(totFmHubs / totStoresFmSys);

        const setFmTop = (row, lbl, val, fmt, isRed) => {
          const a = ws6.getCell('A' + row);
          a.value = lbl;
          a.font = { name: 'Calibri', bold: true };
          a.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF2CC' } };
          a.border = thinBorder;

          const b = ws6.getCell('B' + row);
          b.value = val;
          if (fmt) b.numFmt = fmt;
          b.font = { name: 'Calibri', bold: true, color: { argb: isRed ? 'FFC00000' : 'FF000000' } };
          b.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF9E6' } };
          b.border = thinBorder;
        };

        setFmTop(3, 'Tổng DS 6 Hubs Hệ Thống:', totFmHubs, '#,##0', true);
        setFmTop(4, 'Tổng số CH hệ thống:', totStoresFmSys, null, false);
        setFmTop(5, 'TB doanh số/CH:', { formula: 'B3/B4', result: fmUnitPrice }, '#,##0', true);

        // BẢNG 1: 6 HUBS FAMILYMART
        ws6.mergeCells('A7:D7');
        const hFm1 = ws6.getCell('A7');
        hFm1.value = '1. CHI TIẾT 6 HUBS XUẤT HÀNG FAMILYMART (PNTU / GIA ĐÌNH VIỆT NAM)';
        hFm1.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
        hFm1.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
        hFm1.alignment = { horizontal: 'left', vertical: 'middle' };
        ws6.getRow(7).height = 22;

        const hubHdrs = ['STT', 'Tên Hub / Địa Chỉ Hub FamilyMart', 'Doanh Số Thực Tế (VNĐ)', 'Ghi Chú'];
        ['A', 'B', 'C', 'D'].forEach((col, idx) => {
          const c = ws6.getCell(col + '8');
          c.value = hubHdrs[idx];
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF333F48' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws6.getRow(8).height = 22;

        fmHubsList.forEach((h, idx) => {
          const r = 9 + idx;
          const ca = ws6.getCell('A' + r); ca.value = idx + 1; ca.alignment = { horizontal: 'center' }; ca.border = thinBorder;
          const cb = ws6.getCell('B' + r); cb.value = h.name; cb.border = thinBorder;
          const cc = ws6.getCell('C' + r); cc.value = h.amount; cc.numFmt = '#,##0'; cc.font = { bold: true }; cc.alignment = { horizontal: 'right' }; cc.border = thinBorder;
          const cd = ws6.getCell('D' + r); cd.value = 'Mã GS: ' + (h.code || 'PNTU'); cd.alignment = { horizontal: 'center' }; cd.border = thinBorder;
          ws6.getRow(r).height = 20;
        });

        const hubTotR = 9 + fmHubsList.length;
        ws6.mergeCells(`A${hubTotR}:B${hubTotR}`);
        const cTotHubLbl = ws6.getCell(`A${hubTotR}`);
        cTotHubLbl.value = 'TỔNG 6 HUBS FAMILYMART (HỆ THỐNG)';
        cTotHubLbl.font = { name: 'Calibri', bold: true };
        cTotHubLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        cTotHubLbl.alignment = { horizontal: 'center' };
        cTotHubLbl.border = thinBorder;
        ws6.getCell(`B${hubTotR}`).border = thinBorder;

        const cTotHubVal = ws6.getCell(`C${hubTotR}`);
        cTotHubVal.value = { formula: `SUM(C9:C${hubTotR-1})`, result: totFmHubs };
        cTotHubVal.numFmt = '#,##0';
        cTotHubVal.font = { name: 'Calibri', bold: true, color: { argb: 'FFC00000' } };
        cTotHubVal.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        cTotHubVal.alignment = { horizontal: 'right' };
        cTotHubVal.border = thinBorder;

        const cTotHubNote = ws6.getCell(`D${hubTotR}`);
        cTotHubNote.value = `Đơn giá: ${fmUnitPrice.toLocaleString('vi-VN')} đ/CH`;
        cTotHubNote.font = { name: 'Calibri', bold: true };
        cTotHubNote.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        cTotHubNote.alignment = { horizontal: 'center' };
        cTotHubNote.border = thinBorder;
        ws6.getRow(hubTotR).height = 22;

        // BẢNG 2: PHÂN BỔ FAMILYMART THEO NHÂN VIÊN (36 CH)
        const distStartR = hubTotR + 3;
        ws6.mergeCells(`A${distStartR-1}:F${distStartR-1}`);
        const hFm2 = ws6.getCell(`A${distStartR-1}`);
        hFm2.value = '2. PHÂN BỔ DOANH SỐ FAMILYMART THEO NHÂN VIÊN (36 CỬA HÀNG KHU VỰC)';
        hFm2.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
        hFm2.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
        hFm2.alignment = { horizontal: 'left', vertical: 'middle' };
        ws6.getRow(distStartR-1).height = 22;

        const distHdrs = ['STT', 'Nhân Viên / Điểm Bán', 'Số CH FM', 'TB/CH', 'Doanh Số FM Phân Bổ', '% FM/Team'];
        distHdrs.forEach((bh, idx) => {
          const colLetter = String.fromCharCode(65 + idx);
          const c = ws6.getCell(colLetter + distStartR);
          c.value = bh;
          c.font = { name: 'Calibri', size: 10, bold: true, color: { argb: 'FFFFFFFF' } };
          c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2E75B6' } };
          c.alignment = { horizontal: 'center', vertical: 'middle' };
          c.border = thinBorder;
        });
        ws6.getRow(distStartR).height = 22;

        const fmDistList = [
          { name: 'Nguyễn Đức Hoà', count: 24, amount: Math.round(fmUnitPrice * 24) },
          { name: 'Nguyễn Thị Thanh Thủy', count: 7, amount: Math.round(fmUnitPrice * 7) },
          { name: 'Não Thị Anh Đào', count: 3, amount: Math.round(fmUnitPrice * 3) },
          { name: 'Kim Hoàng Khang', count: 1, amount: Math.round(fmUnitPrice * 1) },
          { name: 'Chưa phân bổ nhân sự (Căn 03 Marina Swanbay)', count: 1, amount: fmUnitPrice }
        ];

        const fmDistTotR = distStartR + 1 + fmDistList.length;

        fmDistList.forEach((d, idx) => {
          const r = distStartR + 1 + idx;
          const ca = ws6.getCell('A' + r); ca.value = idx + 1; ca.alignment = { horizontal: 'center' }; ca.border = thinBorder;
          const cb = ws6.getCell('B' + r); cb.value = d.name; cb.font = { bold: true }; cb.border = thinBorder;
          const cc = ws6.getCell('C' + r); cc.value = d.count; cc.alignment = { horizontal: 'center' }; cc.border = thinBorder;
          const cd = ws6.getCell('D' + r); cd.value = { formula: '$B$5', result: fmUnitPrice }; cd.numFmt = '#,##0'; cd.alignment = { horizontal: 'right' }; cd.border = thinBorder;
          const ce = ws6.getCell('E' + r); ce.value = { formula: `C${r}*D${r}`, result: d.amount }; ce.numFmt = '#,##0'; ce.font = { bold: true }; ce.alignment = { horizontal: 'right' }; ce.border = thinBorder;
          const cf = ws6.getCell('F' + r); cf.value = { formula: `E${r}/$E$${fmDistTotR}`, result: d.count / 36 }; cf.numFmt = '0.0%'; cf.alignment = { horizontal: 'center' }; cf.border = thinBorder;
          ws6.getRow(r).height = 20;
        });

        ws6.mergeCells(`A${fmDistTotR}:B${fmDistTotR}`);
        const fTotLbl = ws6.getCell(`A${fmDistTotR}`);
        fTotLbl.value = 'TỔNG CỘNG KHU VỰC (36 CỬA HÀNG)';
        fTotLbl.font = { name: 'Calibri', bold: true };
        fTotLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotLbl.alignment = { horizontal: 'center' };
        fTotLbl.border = thinBorder;
        ws6.getCell(`B${fmDistTotR}`).border = thinBorder;

        const fTotC = ws6.getCell(`C${fmDistTotR}`);
        fTotC.value = { formula: `SUM(C${distStartR+1}:C${fmDistTotR-1})`, result: 36 };
        fTotC.font = { name: 'Calibri', bold: true };
        fTotC.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotC.alignment = { horizontal: 'center' };
        fTotC.border = thinBorder;

        const fTotD = ws6.getCell(`D${fmDistTotR}`);
        fTotD.value = { formula: '$B$5', result: fmUnitPrice };
        fTotD.numFmt = '#,##0';
        fTotD.font = { name: 'Calibri', bold: true };
        fTotD.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotD.alignment = { horizontal: 'right' };
        fTotD.border = thinBorder;

        const fTotE = ws6.getCell(`E${fmDistTotR}`);
        const totFmDistAmt = fmDistList.reduce((a, b) => a + b.amount, 0);
        fTotE.value = { formula: `SUM(E${distStartR+1}:E${fmDistTotR-1})`, result: totFmDistAmt };
        fTotE.numFmt = '#,##0';
        fTotE.font = { name: 'Calibri', bold: true, color: { argb: 'FFC00000' } };
        fTotE.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotE.alignment = { horizontal: 'right' };
        fTotE.border = thinBorder;

        const fTotF = ws6.getCell(`F${fmDistTotR}`);
        fTotF.value = { formula: `SUM(F${distStartR+1}:F${fmDistTotR-1})`, result: 1 };
        fTotF.numFmt = '0.0%';
        fTotF.font = { name: 'Calibri', bold: true };
        fTotF.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD9E1F2' } };
        fTotF.alignment = { horizontal: 'center' };
        fTotF.border = thinBorder;
        ws6.getRow(fmDistTotR).height = 24;

        return wb;
    }

module.exports = { buildExcelWorkbook, openpyxlColLetter };
