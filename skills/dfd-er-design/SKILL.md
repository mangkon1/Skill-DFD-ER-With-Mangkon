---
name: dfd-er-design
description: "ออกแบบ วาด ตรวจ และใส่รูปเล่ม Context Diagram, DFD Level 1/2, ER Diagram (Crow's Foot), Data Dictionary และ MariaDB DDL ตามหลัก 'ข้อมูลต้องมีที่มาที่ไป' สำหรับรายงานโครงงาน/ปริญญานิพนธ์ภาษาไทย. Use when the user asks to design, draw, fix, review, or check consistency of a Data Flow Diagram, Context Diagram, ER diagram, data dictionary, CRUD matrix, or database schema for a Thai university project report, or to insert those diagrams into the report (.docx/Visio .vsdx). Includes packed Visio/PNG templates, a JSON-driven generator that reproduces them, and exact style rules (sizes, fonts, lines, colors, captions)."
compatibility: Any agent that supports the Agent Skills standard. The generator needs Python 3.9+, Pillow (with raqm), lxml, python-docx and the TH Sarabun New font; Microsoft Visio is optional for hand edits.
metadata:
  author: mangkon
  version: "2.0"
---

# DFD & ER Design: ข้อมูลต้องมีที่มาที่ไป

Skill นี้รวมกฎทั้งหมดที่ใช้ทำ DFD/ER ของรายงานจริงจนผ่านการตรวจของอาจารย์ ทั้งตรรกะ ขนาดกรอบ เส้น ฟอนต์ การโยงเส้น
และการใส่รูปเล่ม พร้อมไฟล์ต้นฉบับและตัวสร้างรูปที่สร้างรูปชุดเดิมได้ตรงทุกไบต์

## ใช้เมื่อไร

- ออกแบบระบบใหม่: Context Diagram, DFD Level 1/2, ER, Data Dictionary, SQL
- แก้หรือตรวจแผนภาพที่มีอยู่ (ตามข้อเสนอแนะอาจารย์/กรรมการ)
- ตรวจความสอดคล้อง DFD ↔ ER ↔ DD ↔ เนื้อหา (CRUD matrix, balancing)
- นำรูปและตาราง DD ใส่ไฟล์ .docx ของรายงาน และตรวจเลขหน้า/สารบัญ

## กฎเหล็ก

1. **เริ่มจากต้นฉบับที่แพ็กไว้เสมอ** อย่าวาดใหม่จากศูนย์ และอย่าคิดค่าสไตล์ขึ้นเอง
   - คัดลอก `templates/generator/examples/spare_part.json` แล้วแก้เป็นระบบใหม่ จากนั้นรัน `build.py`
   - หรือเปิด `templates/vsdx/*.vsdx` ใน Visio แล้วแก้/คัดลอกสัญลักษณ์ (สไตล์ถูกต้องแล้ว)
2. **ทำตามเอกสารสไตล์ทุกตัวเลข**: `docs/dfd-style.md`, `docs/er-style.md`, `docs/report-insertion.md`
3. **ตรรกะก่อนรูป**: ทำตาม `docs/principles.md` และผ่าน `tools/check_spec.py` ก่อนวาด
4. **ถามแทนการเดา** เมื่อกฎธุรกิจหรือ cardinality ไม่ชัด
5. **ไฟล์ของผู้ใช้สำคัญที่สุด**: สำรองก่อนแก้ ตรวจว่าผู้ใช้แก้ไฟล์หลังเราหรือไม่ (เวลาแก้ไข, ไฟล์ล็อก `~$`) แล้วต่อยอดจากฉบับของผู้ใช้ แก้เฉพาะส่วนที่ได้รับมอบหมาย

## Workflow

### 1. เก็บความต้องการ
ขอข้อมูลตาม `docs/principles.md` ข้อ 9: ชื่อโครงการ ผู้ใช้/บทบาท ขั้นตอนงานจริง ข้อมูลที่บันทึก รายงาน/แจ้งเตือนและผู้รับ
กฎ/KPI หน่วยงานนอกระบบ ข้อเสนอแนะอาจารย์ และไฟล์ตัวอย่างสไตล์ของอาจารย์ (ถ้ามี ให้สไตล์อาจารย์ชนะ)

### 2. ออกแบบ (ยังไม่วาด)
1. External Entity และข้อมูลเข้า/ออกของแต่ละตัว
2. Data Store (D1..Dn) และตารางของแต่ละ store (`store_tables`)
3. Process Level 1 เรียง **Master → ค่าที่กำหนด (KPI) → Transaction → Report** ชื่อเป็นวลีกริยา
4. Data flow ทุกเส้น `[ต้นทาง, ปลายทาง, ชื่อข้อมูล]` ทิศละ 1 ลูกศรต่อคู่
5. เลือก process ที่ต้องมี Level 2 (หลายขั้นตอน/หลายผู้กระทำ/หลาย store) และเขียน flow ให้สมดุล
6. ตาราง ER + Data Dictionary (`templates/dd/dd_spare_part.json` เป็นแบบ) ระบุ PK/FK/nullable
7. รัน `python templates/tools/check_spec.py spec.json dd.json` แก้จน `OK` และอ่าน WARN ทุกบรรทัด

### 3. วาด
```bash
cd templates/generator
python test_reproduce.py                 # ตรวจว่าเครื่องพร้อม (ต้อง PASS)
python build.py my_system.json --out out --lo
```
- ปรับตำแหน่งด้วย spec (`entries`, `store_order`, `shared_store`, `placement`, `relations.via`) ไม่ใช่แก้โค้ด
- รายละเอียด spec: `templates/README.md`

### 4. ตรวจ
- ผล finalize ต้องเป็น 0 ทั้ง 5 ค่าในทุกรูป
- `python templates/tools/check_vsdx.py out/vsdx/*.vsdx` ต้องผ่าน (DisplayMode = 1, ER 1 เส้นต่อคู่)
- เปิด PNG ดูด้วยตาทุกรูป: กล่องกลวง ตัวอักษรไม่ถูกบัง หัว ER สีฟ้า `#BDD7EE` ป้ายไม่ทับ
- ไล่ `docs/checklist.md` ส่วน A และ B

### 5. ใส่รูปเล่ม
- ทำตาม `docs/report-insertion.md`: แทน `word/media` ของรูปเดิม คงขนาดในเล่ม (Context 5.76 in, L1 4.28×7.74, L2 5.5, ER 8.30 แนวนอน)
  คำบรรยายรูปใต้รูปตัวหนา ตารางเหนือตาราง
- สร้าง DD ด้วย `templates/dd/dd_to_docx.py` และ SQL ด้วย `templates/sql/dd_to_sql.py` จากไฟล์ DD เดียวกัน
- render PDF ใหม่ ตรวจเลขหน้า สารบัญ สารบัญภาพ สารบัญตาราง และไล่ `docs/checklist.md` ส่วน C

## ไฟล์ใน skill

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `docs/principles.md` | ตรรกะ: ที่มาที่ไปของข้อมูล ลำดับ process สถานะ KPI ประวัติ กฎ DFD/ER |
| `docs/dfd-style.md` | ขนาด ฟอนต์ เส้น ลูกศร การจัดวาง ป้าย ข้อห้าม ของ Context/L1/L2 |
| `docs/er-style.md` | กล่องตาราง สีหัว Crow's Foot การจัดวาง DD MariaDB DDL |
| `docs/report-insertion.md` | ใส่รูป/ตารางในเล่ม caption หัวข้อ ฟอนต์ เลขหน้า สารบัญ |
| `docs/checklist.md` | checklist ก่อนส่ง + ข้อผิดพลาดที่พบบ่อย + บทเรียนทางเทคนิค |
| `templates/` | vsdx/png ต้นฉบับ, generator, DD template, SQL, tools (ดู `templates/README.md`) |
| `examples/spare_part_design.md` | สรุปการออกแบบตัวอย่าง (5 entity, 8 store, 8 process, 14 ตาราง, 23 ความสัมพันธ์) |
| `references/chapter3_example.docx` | บทที่ 3 ฉบับจริง: Process Description, ER หน้าแนวนอน, DD 14 ตาราง |

## สิ่งที่ส่งมอบให้ผู้ใช้

1. รายการ entity / store / process (พร้อมเหตุผลของลำดับ) / process ที่ทำ Level 2
2. ไฟล์ .vsdx + .png ของทุกรูป และผลตรวจ (finalize, check_vsdx)
3. CRUD matrix และปัญหาที่พบ
4. Data Dictionary (.docx) และ SQL DDL
5. คำถามที่ผู้ใช้ต้องตอบ
