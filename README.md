# Skill DFD ER With Mangkon

Skill สำหรับออกแบบ วาด ตรวจ และใส่รูปเล่ม **Context Diagram, DFD Level 1/2, ER Diagram (Crow's Foot), Data Dictionary และ MariaDB DDL**
ตามหลัก "ข้อมูลต้องมีที่มาที่ไป" สำหรับรายงานโครงงาน/ปริญญานิพนธ์ภาษาไทย ใช้รูปแบบ [Agent Skills](https://agentskills.io)
จึงติดตั้งจาก URL เดียวกันได้กับตัวช่วย AI ที่รองรับสกิล เช่น Cursor, Claude Code, Codex, Gemini CLI, GitHub Copilot, Windsurf, Cline และตัวอื่นที่ตัวติดตั้งรองรับ

![ตัวอย่าง DFD Level 1, Context Diagram และ ER Diagram ที่สร้างจาก skill นี้](skills/dfd-er-design/assets/preview.png)

## มีอะไรบ้าง

- **กฎทั้งหมด** ที่ใช้ทำรายงานจริงจนผ่านการตรวจของอาจารย์: ตรรกะข้อมูล ลำดับ process ขนาดกรอบ เส้น ฟอนต์ การโยงเส้น สี caption เลขหน้า
- **ไฟล์ต้นฉบับ** Visio (.vsdx) และ PNG ของ Context, DFD Level 1, Level 2 (2 รูป) และ ER ที่แก้แล้ว (กล่องกลวงไม่บังตัวอักษร หัวตาราง ER สีฟ้า)
- **ตัวสร้างรูป** (Python) ที่อ่าน spec JSON แล้วสร้าง .vsdx + .png ตรงกับต้นฉบับทุกไบต์ พร้อม test
- **เครื่องมือตรวจ**: CRUD matrix, balancing, black hole/miracle, FK ↔ เส้น ER, ไฟล์ Visio
- **Data Dictionary** แม่แบบ .docx รูปแบบเดียวกับเล่ม และตัวสร้าง SQL DDL สำหรับ MariaDB

```
skills/dfd-er-design/
  SKILL.md                     คำสั่งหลักของ skill (workflow)
  docs/                        principles, dfd-style, er-style, report-insertion, checklist
  templates/                   vsdx/ png/ generator/ dd/ sql/ tools/  (ดู templates/README.md)
  examples/spare_part_design.md   สรุปการออกแบบตัวอย่าง (14 ตาราง)
  references/chapter3_example.docx บทที่ 3 ฉบับจริง
  evals/                       test prompts
```

## ติดตั้งให้ทุก AI

คำสั่งนี้ติดตั้ง skill `dfd-er-design` ทั้งเครื่อง ให้ทุกตัวช่วยที่ตรวจพบ โดยไม่ต้องตอบคำถามเพิ่ม

```bash
npx skills add https://github.com/mangkon1/Skill-DFD-ER-With-Mangkon --skill dfd-er-design --agent '*' -g -y
```

เปิดแชทใหม่หลังติดตั้ง แล้วบอกให้ช่วยออกแบบหรือตรวจ DFD, ER Diagram หรือ Data Dictionary

ติดตั้งเฉพาะโปรเจกต์ปัจจุบัน โดยไม่ใส่ `-g`

```bash
npx skills add https://github.com/mangkon1/Skill-DFD-ER-With-Mangkon --skill dfd-er-design --agent '*' -y
```

ใน Cursor ติดตั้งจากหน้าจอได้เช่นกัน เปิด Customize แล้วเลือกนำเข้าจาก GitHub repository จากนั้นวาง `https://github.com/mangkon1/Skill-DFD-ER-With-Mangkon` แล้วติดตั้ง plugin `dfd-er-design`

ติดตั้งเอง: คัดลอกโฟลเดอร์ `skills/dfd-er-design` ไปไว้ในโฟลเดอร์ skills ของเครื่องมือที่ใช้ (เช่น `~/.cursor/skills/`, `~/.claude/skills/`)

## ใช้ตัวสร้างรูปโดยตรง

```bash
pip install pillow lxml python-docx          # และติดตั้งฟอนต์ TH Sarabun New
cd skills/dfd-er-design/templates/generator
python test_reproduce.py                     # ต้องได้ PASS
python build.py examples/spare_part.json --out out
```

แก้ `examples/spare_part.json` เป็นระบบของคุณ แล้วรันใหม่ รายละเอียดใน [templates/README.md](skills/dfd-er-design/templates/README.md)

## ตัวอย่าง

ระบบบริหารจัดการอุปกรณ์อะไหล่และติดตามสถานะการส่งซ่อม: 5 External Entity, 8 Data Store, 8 Process (Level 2 ของ process 6 และ 8), 14 ตาราง, 23 ความสัมพันธ์
ดู [examples/spare_part_design.md](skills/dfd-er-design/examples/spare_part_design.md)
