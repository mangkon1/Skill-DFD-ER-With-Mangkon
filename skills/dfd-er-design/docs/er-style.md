# ER Diagram style (Crow's Foot): ค่าที่ใช้จริง

ค่าทั้งหมดมาจาก `templates/generator/d_er.py`, `draw.py`, `vsdx.py` และ spec `er` ใน `examples/spare_part.json`

## 1. กล่องตาราง

| รายการ | ค่า |
|---|---|
| ความกว้างตาราง (TW) | **2.05 in** ทุกตาราง (เท่ากันทั้งรูป) |
| ความสูงแถว (RH) | **0.24 in** ทั้งหัวและแถวฟิลด์; ความสูงตาราง = RH × (จำนวนฟิลด์ + 1) ห้ามยืดกล่องเกินจำนวนแถว |
| หัวตาราง | ชื่อตาราง (ภาษาอังกฤษ snake_case) ตัวหนา กึ่งกลาง, layout 13 pt (19.9 pt จริง), **พื้น `#BDD7EE`** (ฟ้าอ่อน) เส้นดำ |
| ตัวตาราง | พื้นขาว `#FFFFFF`, เส้นดำ 0.75 pt |
| คอลัมน์คีย์ | กว้าง **0.42 in** มีเส้นตั้งคั่น; "PK"/"FK" ตัวหนา layout 11 pt กึ่งกลางที่ 0.21 in |
| ชื่อฟิลด์ | layout 11 pt (16.8 pt จริง) ชิดซ้ายที่ 0.50 in จากขอบซ้าย; ฟิลด์ PK ขีดเส้นใต้ |
| ฟอนต์ | TH Sarabun New |
| Visio | group `DisplayMode = 1` (ไม่งั้นพื้นขาวของ group ทับสีหัวตาราง), หัว = shape แยกที่มี `FillForegnd #BDD7EE` |

ลำดับฟิลด์: **PK ก่อน → FK → ฟิลด์อื่น** (ยกเว้นฟิลด์ที่อ่านง่ายกว่าเมื่อเรียงตามความหมาย เช่น `prev_status` ก่อน `status_code` ใน log) และต้องตรงกับลำดับใน Data Dictionary

## 2. เส้นความสัมพันธ์

- **1 เส้นต่อ 1 คู่ตาราง** แม้มี FK หลายตัวระหว่างคู่นั้น (generator จะ assert ถ้าซ้ำ; `tools/check_vsdx.py` ตรวจไฟล์ vsdx)
- เส้นตั้ง/นอน (orthogonal) หนา 0.75 pt สีดำ ไม่ตัดกัน ไม่ผ่านตาราง
- จุดต่อด้านซ้าย/ขวา: ที่ระดับแถวของฟิลด์ (`row_frac(table, attr)`): ฝั่ง parent ที่แถว PK, ฝั่ง child ที่แถว FK
- จุดต่อด้านบน/ล่าง: กลางกล่อง (0.5) หรือเลื่อนเพื่อหลบเส้นอื่น (0.3 / 0.7)
- เส้นที่อ้อมใช้ `via` (ช่องทางเดินแนวตั้ง x หรือแนวนอน y) วางในช่องว่างระหว่างคอลัมน์ตาราง

| ปลายเส้น | รหัส Visio (BeginArrow/EndArrow) | PNG |
|---|---|---|
| หนึ่งเท่านั้น (one and only one) | **25** | ขีด 2 ขีดที่ 0.10 และ 0.16 in |
| ศูนย์หรือหนึ่ง (zero or one) | **30** | ขีดที่ 0.10 + วงกลม r 0.045 ที่ 0.22 in |
| ศูนย์หรือหลาย (zero or many) | **29** | ตีนกา (กว้าง ±0.08 ยาว 0.16) + วงกลมที่ 0.25 in |
| หนึ่ง (one) | 24 | ขีดที่ 0.12 |
| หลาย (many) | 27 | ตีนกา |
| หนึ่งหรือหลาย (one or many) | 28 | ตีนกา + ขีดที่ 0.20 |

กติกาที่ใช้: ฝั่ง parent = 25 (FK NOT NULL) หรือ **30 ถ้า FK ว่างได้**; ฝั่ง child = **29** (หรือ 30 เมื่อเป็น 1:1 เช่น employees–users)

## 3. การจัดวาง (ตัวอย่าง 14 ตาราง)

- 6 คอลัมน์ x = 0.3 + TW/2 + i × **2.95 in**, แถวบนสุด y = 0.6 in
- วางตามกลุ่มเรื่อง ซ้าย→ขวา: ทีม/โซน/log → พนักงาน/ผู้ใช้ → ธุรกรรม (แจกจ่าย ใช้งาน) → อุปกรณ์/ประวัติสถานะ → lookup (ประเภท รุ่น สถานะ)
- ตารางที่อ้างหลายกลุ่ม (เช่น `kpi_settings`) วางล่างสุดกลางรูป ต่ำกว่าตารางที่ลึกที่สุด 0.75 in
- parent อยู่บนหรือซ้ายของ child เท่าที่ทำได้ ทำให้เส้นสั้นและไม่ตัด
- ER ทั้งหมดอยู่ใน **รูปเดียว** (หลังตัดขอบ 17.34×10.05 in) ใส่ในหน้ากระดาษแนวนอน

## 4. การได้ตารางจาก Data Store

1. เขียน `store_tables` ใน spec: D1 → [product_types, products, spare_statuses, spares], D2 → [employees, roles, users], ...
2. ตาราง lookup (ประเภท สถานะ บทบาท) อยู่ใน store ของข้อมูลหลักที่ใช้มัน
3. ทุก store มีอย่างน้อย 1 ตาราง และทุกตารางอยู่ใน store เดียว (`check_spec.py` ตรวจ)
4. FK ทุกตัวใน DD ต้องมีเส้นใน ER (คู่ละเส้น) และทุกเส้นต้องมี FK อย่างน้อย 1 ตัว (`check_spec.py SPEC DD` ตรวจ)

## 5. Data Dictionary (รูปแบบในเล่ม ตารางที่ 3.1–3.14)

- 1 ตารางในฐานข้อมูล = 1 ตารางในเล่ม เรียงตามลำดับ store (D1.. หรือตามลำดับในเนื้อหา)
- คำบรรยาย **อยู่เหนือตาราง**: `ตารางที่ 3.x␣␣table_name (ชื่อภาษาไทย)` (เว้น 2 ช่องหลังเลข) ตัวปกติ ชิดซ้าย-ขวา (jc both) keepNext
- คอลัมน์ 8 ช่อง และความกว้าง (twips, รวม 8300 = กว้างเต็มบรรทัด, tblLayout fixed):

| Attribute Name | Description | Data Type | Size | Not Null | Unique | Key | References Table |
|---|---|---|---|---|---|---|---|
| 1750 | 1700 | 980 | 500 | 650 | 920 | 500 | 1300 |

- ฟอนต์ TH SarabunPSK **15 pt**; แถวหัวตัวหนา กึ่งกลาง และตั้ง "ทำซ้ำแถวหัวทุกหน้า" (tblHeader); ทุกแถว cantSplit; cell margin ซ้าย-ขวา 57 twips; เส้นขอบเดี่ยว 4 (½ pt) สีดำทุกเส้น
- ค่าในเซลล์: ชื่อฟิลด์/คำอธิบาย/ตารางอ้างอิง ชิดซ้าย; ชนิด ขนาด Not Null Unique Key กึ่งกลาง
- Data Type ใช้ชนิดของ MariaDB ตัวเล็ก: `int`, `varchar`, `tinyint`, `date`, `datetime`, `text`; Size ใส่เฉพาะ varchar/char/decimal
- Not Null / Unique = `Yes` / `No`; Key = `PK` / `FK` / ว่าง; References Table = ชื่อตาราง parent เมื่อเป็น FK
- สร้างอัตโนมัติ: `python templates/dd/dd_to_docx.py dd.json out.docx` (โคลนรูปแบบจาก `dd_template.docx`)

## 6. MariaDB DDL

- สร้างจาก DD ไฟล์เดียวกัน: `python templates/sql/dd_to_sql.py dd.json > schema_mariadb.sql`
- int PK → `INT NOT NULL AUTO_INCREMENT`; varchar PK = รหัสธรรมชาติ (เช่น `status_code`, `role_code`)
- `Unique = Yes` (ที่ไม่ใช่ PK) → `UNIQUE KEY`; FK → `CONSTRAINT fk_<table>_<col> FOREIGN KEY ... REFERENCES parent(pk)`
- `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`, คำอธิบายภาษาไทยเป็น `COMMENT`
- เรียงตาราง parent ก่อน child อัตโนมัติ; ตรวจโดย import เข้า MariaDB / HeidiSQL / MySQL Workbench แล้ว Reverse Engineer เทียบกับ ER
- ตัวอย่าง: `templates/sql/schema_mariadb.sql` (14 ตาราง)
