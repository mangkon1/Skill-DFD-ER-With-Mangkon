---
name: dfd-er-design
description: "MUST be loaded and read FIRST, at the start of EVERY task of any kind (coding, documents, reports, research, files, chat), before any other work or any other skill, in every session. Holds the user's global working rules (reply in Thai, back up before replacing, never overwrite the user's edits, check ~$ lock files, verify results, reuse before you build) and the toolchain check (Ponytail, Graphify, Anthropic document-skills; never OmniRoute). Also the full rules, Visio/PNG templates and generator for Context Diagram, DFD Level 1/2, ER (Crow's Foot), Data Dictionary and MariaDB DDL in Thai project reports. ต้องโหลดก่อนเริ่มงานทุกงาน: กฎการทำงานของผู้ใช้ + ชุดเครื่องมือ + กฎ DFD/ER"
compatibility: Any agent that supports the Agent Skills standard. The generator needs Python 3.9+, Pillow (with raqm), lxml, python-docx and the TH Sarabun New font; Microsoft Visio is optional for hand edits.
metadata:
  author: mangkon
  version: "3.0"
---

# กฎการทำงานของผู้ใช้ + DFD & ER Design

> **อ่านไฟล์นี้ก่อนเริ่มงานทุกงาน ทุก session** ไม่ใช่แค่งาน DFD/ER ส่วนที่ 1 (กฎทั่วไป + Step 0) ใช้กับทุกงาน
> ส่วนที่ 2 ใช้เฉพาะงานแผนภาพ ฐานข้อมูล และรายงาน

## ส่วนที่ 1: กฎทั่วไป ใช้กับทุกงาน

1. **ตอบเป็นภาษาไทย** กระชับ ชัดเจน (ศัพท์เทคนิค/ชื่อไฟล์/คำสั่ง คงภาษาอังกฤษได้) ใช้คำที่ผู้ใช้กำหนด เช่น ชำรุด (ไม่ใช่ เสีย), ทีม (ไม่ใช่ สายงาน), MariaDB
2. **สำรองก่อนแทนที่** ทุกครั้งที่จะเขียนทับ ย้าย หรือลบไฟล์ของผู้ใช้ ให้สำรองฉบับเดิมไว้ในโฟลเดอร์สำรอง (เช่น `ขยะ/` หรือ `backup/` พร้อมวันเวลา) ห้ามลบไฟล์ของผู้ใช้โดยไม่มีเหตุผล
3. **ห้ามทับงานที่ผู้ใช้แก้เอง** ก่อนวางไฟล์ ตรวจเวลาแก้ไขว่าผู้ใช้แก้หลังเราหรือไม่ ถ้าใช่ ให้ต่อยอดจากฉบับของผู้ใช้ แก้เฉพาะส่วนที่ได้รับมอบหมาย
4. **ตรวจไฟล์ล็อก `~$`** (ไฟล์ที่ Word/Excel เปิดค้าง) ก่อนแก้/วางไฟล์ Office ถ้ามี ให้แจ้งผู้ใช้ปิดไฟล์ก่อน อย่าฝืนเขียนทับ
5. **ตรวจผลทุกครั้ง** หลังทำ: เปิดดูผลจริง (render PDF/ภาพ, รัน test) และยืนยันว่าไฟล์ที่วางตรงกับที่ตั้งใจ (เช่นเทียบ MD5) โฟลเดอร์ส่งงาน (Final) เก็บเฉพาะฉบับล่าสุด
6. **ใช้ของที่มีอยู่ก่อนสร้างใหม่ (reuse-first)** ตามแนวคิด Ponytail: มีในโปรเจกต์/ต้นฉบับ/เทมเพลตแล้วหรือยัง → standard library → ฟีเจอร์แพลตฟอร์ม → dependency ที่มีอยู่ → ค่อยเขียนใหม่ให้น้อยที่สุด และอ่านงานเดิมให้เข้าใจก่อนเสมอ
7. **ถามแทนการเดา** เมื่อข้อกำหนดไม่ชัด และไม่ทำสิ่งที่ผู้ใช้ไม่ได้ขอ (ส่งข้อความ ลบไฟล์ ติดตั้งโปรแกรมบนเครื่องผู้ใช้) โดยไม่ได้รับอนุญาต
8. **ความปลอดภัย** ห้ามดึงหรือใช้รหัสผ่าน/token ผิดวัตถุประสงค์ ห้ามหลบการยืนยันตัวตน ห้ามใช้ proxy อย่าง OmniRoute กับงานของผู้ใช้

## Step 0: ตรวจชุดเครื่องมือก่อนเริ่มงาน

รายละเอียด คำสั่งติดตั้ง ข้อควรระวัง และวิธีถอน: `docs/toolchain.md` (สรุปจาก <https://aismartworkth.com/guide/claude-code-first-3>)

1. **ตรวจว่ามี 3 ตัวนี้หรือยัง** ใน agent ที่ใช้อยู่
   - Ponytail (`/plugin` ดูรายการ หรือมี skill `ponytail`)
   - Graphify (`graphify --help` ได้ผล หรือ `uv tool list` มี `graphifyy`)
   - Anthropic document-skills (`/plugin` มี `document-skills@anthropic-agent-skills`) หรือ skill งานเอกสารที่เทียบเท่าของ agent นั้น
2. **ถ้าขาดตัวใด** เสนอคำสั่งติดตั้งจาก `docs/toolchain.md` ติดตั้งเองได้เฉพาะเมื่อผู้ใช้อนุญาต หรือเป็นเครื่อง/sandbox ของ agent เอง ถ้าติดตั้งไม่ได้ ให้ทำงานต่อด้วยหลักการเดียวกัน (ข้อ 6 ด้านบน) และแจ้งผู้ใช้
3. **Reuse-first ทุกงาน**: งาน DFD/ER เริ่มจาก `templates/` และ generator ที่แพ็กไว้ ห้ามวาดใหม่จากศูนย์
4. **โฟลเดอร์ใหญ่** (รายงานทั้งเล่ม, โค้ดทั้งระบบ): ใช้ Graphify ทำแผนที่ก่อนค้น/ตรวจความสอดคล้อง โฟลเดอร์เล็กหรือไฟล์เดียวข้ามได้
5. **งาน docx / xlsx / pptx / pdf**: ใช้ document-skills (หรือ skill เอกสารของ agent) ร่วมกับ `docs/report-insertion.md`
6. **ห้ามติดตั้ง OmniRoute** หรือ proxy ที่ถือ key และเห็นข้อมูลทั้งหมด

---

## ส่วนที่ 2: DFD & ER Design: ข้อมูลต้องมีที่มาที่ไป (ใช้เฉพาะงานแผนภาพ/ฐานข้อมูล/รายงาน)
Skill นี้รวมกฎทั้งหมดที่ใช้ทำ DFD/ER ของรายงานจริงจนผ่านการตรวจของอาจารย์ ทั้งตรรกะ ขนาดกรอบ เส้น ฟอนต์ การโยงเส้น
และการใส่รูปเล่ม พร้อมไฟล์ต้นฉบับและตัวสร้างรูปที่สร้างรูปชุดเดิมได้ตรงทุกไบต์

### ใช้เมื่อไร

- ออกแบบระบบใหม่: Context Diagram, DFD Level 1/2, ER, Data Dictionary, SQL
- แก้หรือตรวจแผนภาพที่มีอยู่ (ตามข้อเสนอแนะอาจารย์/กรรมการ)
- ตรวจความสอดคล้อง DFD ↔ ER ↔ DD ↔ เนื้อหา (CRUD matrix, balancing)
- นำรูปและตาราง DD ใส่ไฟล์ .docx ของรายงาน และตรวจเลขหน้า/สารบัญ

### กฎเหล็ก (DFD/ER)

1. **เริ่มจากต้นฉบับที่แพ็กไว้เสมอ** อย่าวาดใหม่จากศูนย์ และอย่าคิดค่าสไตล์ขึ้นเอง
   - คัดลอก `templates/generator/examples/spare_part.json` แล้วแก้เป็นระบบใหม่ จากนั้นรัน `build.py`
   - หรือเปิด `templates/vsdx/*.vsdx` ใน Visio แล้วแก้/คัดลอกสัญลักษณ์ (สไตล์ถูกต้องแล้ว)
2. **ทำตามเอกสารสไตล์ทุกตัวเลข**: `docs/dfd-style.md`, `docs/er-style.md`, `docs/report-insertion.md`
3. **ตรรกะก่อนรูป**: ทำตาม `docs/principles.md` และผ่าน `tools/check_spec.py` ก่อนวาด
4. **ถามแทนการเดา** เมื่อกฎธุรกิจหรือ cardinality ไม่ชัด
5. **ไฟล์ของผู้ใช้สำคัญที่สุด**: สำรองก่อนแก้ ตรวจว่าผู้ใช้แก้ไฟล์หลังเราหรือไม่ (เวลาแก้ไข, ไฟล์ล็อก `~$`) แล้วต่อยอดจากฉบับของผู้ใช้ แก้เฉพาะส่วนที่ได้รับมอบหมาย

### Workflow

#### 1. เก็บความต้องการ
ขอข้อมูลตาม `docs/principles.md` ข้อ 9: ชื่อโครงการ ผู้ใช้/บทบาท ขั้นตอนงานจริง ข้อมูลที่บันทึก รายงาน/แจ้งเตือนและผู้รับ
กฎ/KPI หน่วยงานนอกระบบ ข้อเสนอแนะอาจารย์ และไฟล์ตัวอย่างสไตล์ของอาจารย์ (ถ้ามี ให้สไตล์อาจารย์ชนะ)

#### 2. ออกแบบ (ยังไม่วาด)
1. External Entity และข้อมูลเข้า/ออกของแต่ละตัว
2. Data Store (D1..Dn) และตารางของแต่ละ store (`store_tables`)
3. Process Level 1 เรียง **Master → ค่าที่กำหนด (KPI) → Transaction → Report** ชื่อเป็นวลีกริยา
4. Data flow ทุกเส้น `[ต้นทาง, ปลายทาง, ชื่อข้อมูล]` ทิศละ 1 ลูกศรต่อคู่
5. เลือก process ที่ต้องมี Level 2 (หลายขั้นตอน/หลายผู้กระทำ/หลาย store) และเขียน flow ให้สมดุล
6. ตาราง ER + Data Dictionary (`templates/dd/dd_spare_part.json` เป็นแบบ) ระบุ PK/FK/nullable
7. รัน `python templates/tools/check_spec.py spec.json dd.json` แก้จน `OK` และอ่าน WARN ทุกบรรทัด

#### 3. วาด
```bash
cd templates/generator
python test_reproduce.py                 # ตรวจว่าเครื่องพร้อม (ต้อง PASS)
python build.py my_system.json --out out --lo
```
- ปรับตำแหน่งด้วย spec (`entries`, `store_order`, `shared_store`, `placement`, `relations.via`) ไม่ใช่แก้โค้ด
- รายละเอียด spec: `templates/README.md`

#### 4. ตรวจ
- ผล finalize ต้องเป็น 0 ทั้ง 5 ค่าในทุกรูป
- `python templates/tools/check_vsdx.py out/vsdx/*.vsdx` ต้องผ่าน (DisplayMode = 1, ER 1 เส้นต่อคู่)
- เปิด PNG ดูด้วยตาทุกรูป: กล่องกลวง ตัวอักษรไม่ถูกบัง หัว ER สีฟ้า `#BDD7EE` ป้ายไม่ทับ
- ไล่ `docs/checklist.md` ส่วน A และ B

#### 5. ใส่รูปเล่ม
- ทำตาม `docs/report-insertion.md`: แทน `word/media` ของรูปเดิม คงขนาดในเล่ม (Context 5.76 in, L1 4.28×7.74, L2 5.5, ER 8.30 แนวนอน)
  คำบรรยายรูปใต้รูปตัวหนา ตารางเหนือตาราง
- สร้าง DD ด้วย `templates/dd/dd_to_docx.py` และ SQL ด้วย `templates/sql/dd_to_sql.py` จากไฟล์ DD เดียวกัน
- render PDF ใหม่ ตรวจเลขหน้า สารบัญ สารบัญภาพ สารบัญตาราง และไล่ `docs/checklist.md` ส่วน C

### ไฟล์ใน skill

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `docs/toolchain.md` | Ponytail, Graphify, Anthropic document-skills: ติดตั้ง ใช้เมื่อไร ข้อควรระวัง ถอน; คำเตือน OmniRoute |
| `templates/bootstrap/` | CLAUDE.md, AGENTS.md, Cursor rule และสคริปต์ติดตั้ง ที่บังคับให้อ่าน skill นี้ก่อนทุกงาน |
| `docs/principles.md` | ตรรกะ: ที่มาที่ไปของข้อมูล ลำดับ process สถานะ KPI ประวัติ กฎ DFD/ER |
| `docs/dfd-style.md` | ขนาด ฟอนต์ เส้น ลูกศร การจัดวาง ป้าย ข้อห้าม ของ Context/L1/L2 |
| `docs/er-style.md` | กล่องตาราง สีหัว Crow's Foot การจัดวาง DD MariaDB DDL |
| `docs/report-insertion.md` | ใส่รูป/ตารางในเล่ม caption หัวข้อ ฟอนต์ เลขหน้า สารบัญ |
| `docs/checklist.md` | checklist ก่อนส่ง + ข้อผิดพลาดที่พบบ่อย + บทเรียนทางเทคนิค |
| `templates/` | vsdx/png ต้นฉบับ, generator, DD template, SQL, tools (ดู `templates/README.md`) |
| `examples/spare_part_design.md` | สรุปการออกแบบตัวอย่าง (5 entity, 8 store, 8 process, 14 ตาราง, 23 ความสัมพันธ์) |
| `references/chapter3_example.docx` | บทที่ 3 ฉบับจริง: Process Description, ER หน้าแนวนอน, DD 14 ตาราง |

### สิ่งที่ส่งมอบให้ผู้ใช้

1. รายการ entity / store / process (พร้อมเหตุผลของลำดับ) / process ที่ทำ Level 2
2. ไฟล์ .vsdx + .png ของทุกรูป และผลตรวจ (finalize, check_vsdx)
3. CRUD matrix และปัญหาที่พบ
4. Data Dictionary (.docx) และ SQL DDL
5. คำถามที่ผู้ใช้ต้องตอบ
