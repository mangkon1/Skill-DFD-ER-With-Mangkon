---
name: dfd-er-design
description: "ออกแบบ DFD และ ER Diagram ตามหลักข้อมูลต้องมีที่มาที่ไป สำหรับเอกสารโครงงานวิจัย. Use when designing Data Flow Diagrams, Entity-Relationship diagrams, data dictionaries, or checking research document consistency for Thai university projects."
type: workflow
lifecycle: active
---

# DFD & ER Design — ข้อมูลต้องมีที่มาที่ไป

Skill สำหรับออกแบบ Data Flow Diagram (DFD) และ Entity-Relationship (ER) Diagram ให้สอดคล้องกับหลักการ "ข้อมูลต้องมีที่มาที่ไป" ตามมาตรฐานเอกสารโครงงานวิจัยมหาวิทยาลัยไทย

ใช้เมื่อต้องการออกแบบระบบใหม่, ตรวจสอบความสอดคล้องของ DFD/ER/Data Dictionary, หรือจัดทำเอกสารบทวิเคราะห์ระบบ

## หลักการหลัก (Core Principles)

1. **ข้อมูลต้องมีที่มาที่ไป**: ข้อมูลต้องเกิดก่อนถูกใช้ ทุก data flow มีต้นทางและปลายทางชัดเจน
2. **ข้อมูลเข้า-ออกต้องสมดุล**: จำนวนและชนิดของข้อมูลที่ไหลเข้า-ออกแต่ละ process ต้องตรงกัน
3. **ความสอดคล้อง 3 ส่วน**: DFD + ER + Data Dictionary ต้องตรงกันทุกจุด
4. **ใช้ Visio จากต้นฉบับเท่านั้น**: ห้ามใช้เครื่องมืออื่นหรือวาดเองนอกจากไฟล์ Visio แม่แบบ

## กฎการออกแบบ DFD

- ใช้สัญลักษณ์ Gane & Sarson
- เส้นห้ามตัดกัน
- Data Store / Entity ไม่ซ้ำ (ถ้าซ้ำให้ใช้สัญลักษณ์เดียวกับที่ใช้ในเอกสาร)
- ทำ Context Diagram + Level 1 เป็นหลัก
- Level 2 ทำเฉพาะ process ที่ซับซ้อนจริง ๆ (มีหลายขั้นตอนต่อเนื่อง)
- แต่ละ process ต้องระบุ: External Entity, Data Flow เข้า-ออก, Data Store ที่เกี่ยวข้อง

## กฎการออกแบบ ER

- ใช้สัญลักษณ์ Crow's Foot
- แต่ละคู่ตารางมีเส้นเพียงเส้นเดียว (ห้ามเส้นซ้ำ)
- เส้นห้ามตัดกัน
- ทุก FK ต้องมีที่มาจาก DFD
- ตารางต้องรองรับทุก Data Store ใน DFD

## กฎเอกสารทั่วไป

- ย่อหน้าและขนาดตัวอักษรตามแม่แบบมหาวิทยาลัย
- สารบัญ / เลขหน้า / สารบัญภาพ ต้องอัปเดตทุกครั้ง
- บรรณานุกรมรูปแบบถูกต้องและอ้างอิงตรงกับเนื้อหา
- รูปภาพ DFD/ER ต้องมาจากไฟล์ Visio ต้นฉบับ

## Workflow การออกแบบ

1. ระบุ External Entities และ Data Stores หลัก
2. วาด Context Diagram
3. แตกเป็น DFD Level 1 (process ตามลำดับการเกิดข้อมูล)
4. ตรวจสอบความสมดุลข้อมูลเข้า-ออกทุก process
5. ออกแบบ ER ให้รองรับ Data Stores ทั้งหมด
6. สร้าง Data Dictionary
7. ตรวจสอบความสอดคล้องทั้ง 3 ส่วน
8. วาดด้วย Visio จากแม่แบบเท่านั้น

## Checklist ก่อนส่งเอกสาร

- [ ] ข้อมูลทุกตัวมีที่มาที่ไป
- [ ] เส้นใน DFD และ ER ไม่ตัดกัน
- [ ] ไม่มี entity/data store ซ้ำโดยไม่มีสัญลักษณ์อ้างอิง
- [ ] ข้อมูลเข้า-ออกสมดุลทุก process
- [ ] ER รองรับทุก Data Store
- [ ] ใช้ไฟล์ Visio จากต้นฉบับ
- [ ] สารบัญและเลขหน้าถูกต้อง
- [ ] ฟอนต์เป็น TH Sarabun New หรือ Angsana New
- [ ] สีและเส้นตรงกับรูปใน assets/style-reference/
- [ ] ขนาดตัวอักษรและย่อหน้าตามแม่แบบ

## สไตล์และรูปแบบที่ต้องปฏิบัติตามอย่างเคร่งครัด

**อ้างอิงรูปใน `assets/style-reference/` ทุกครั้งก่อนวาด**

### ฟอนต์ (สำคัญมาก)
- ใช้ฟอนต์ **TH Sarabun New** หรือ **Angsana New** เท่านั้น (ขนาด 14–16 pt สำหรับข้อความทั่วไป, 12 pt สำหรับ attribute ในตาราง)
- ห้ามใช้ Arial, Calibri, หรือฟอนต์อังกฤษอื่น ๆ
- ตัวหนาสำหรับชื่อตาราง / ชื่อ process
- ตัวปกติสำหรับ attribute และ data flow

### สีและเส้น
- ตาราง ER: พื้นหลังหัวตารางสีฟ้าอ่อน, เส้นสีดำหนา
- Process ใน DFD: กรอบสี่เหลี่ยมขอบมนสีดำ, พื้นขาว
- External Entity: สี่เหลี่ยมขอบดำ
- Data Store: เส้นคู่ขนานสีดำ
- เส้นเชื่อม: สีดำ, ไม่ตัดกัน, ใช้ Crow's Foot ชัดเจน
- ไม่มีสีสันอื่นนอกจากฟ้าอ่อนในหัวตาราง ER

### Layout
- จัดวางให้โปร่ง ไม่ทับเส้น
- แต่ละคู่ตารางมีเส้นเดียวเท่านั้น
- ชื่อ data flow เขียนชัดเจนข้างเส้น
- ดูรูปตัวอย่างใน `assets/style-reference/` เป็นหลัก

### ไฟล์อ้างอิงสไตล์
- `ER_Diagram_style.png`
- `Context_Diagram_style.png`
- `DFD_Level1_style.png`
- `DFD_Level2_P6_style.png`
- `DFD_Level2_P8_style.png`

**เมื่อใช้ Skill นี้:** ต้องเปิดไฟล์ Visio แม่แบบ แล้วปรับสี เส้น ฟอนต์ และ layout ให้ตรงกับรูปอ้างอิงก่อนนำไปใส่เอกสาร

## ไฟล์แม่แบบและตัวอย่าง

### Visio Templates (ใช้เป็นต้นฉบับเท่านั้น)
ไฟล์ใน `assets/templates/` คือแม่แบบ Visio ที่ต้องใช้:
- `01_Context_Diagram.vsdx` — Context Diagram
- `02_DFD_Level1.vsdx` — DFD Level 1
- `03_ER_Diagram.vsdx` — ER Diagram
- `04_DFD_Level2_P6.vsdx` — DFD Level 2 Process 6
- `04_DFD_Level2_P8.vsdx` — DFD Level 2 Process 8

**กฎ:** ต้องเปิดไฟล์เหล่านี้ใน Visio แล้วแก้ไข/คัดลอกสัญลักษณ์เท่านั้น ห้ามสร้างใหม่จากศูนย์หรือใช้เครื่องมืออื่น

### ตัวอย่างบทที่ 3
ดู `references/chapter3_example.docx` สำหรับโครงสร้างจริงของ:
- Process Description (ตารางรูปแบบมาตรฐาน)
- Data Dictionary (14 ตาราง)
- การจัดวางภาพ DFD/ER
- รูปแบบย่อหน้าและหัวข้อ

## Checklist ก่อนส่งเอกสาร