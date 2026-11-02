# Templates และ generator

ไฟล์ในโฟลเดอร์นี้คือ **ต้นฉบับที่ถูกต้อง** ของรูปในรายงานจริง ให้เริ่มงานใหม่จากที่นี่เสมอ (คัดลอกแล้วแก้)

```
templates/
  vsdx/        01_Context_Diagram, 02_DFD_Level1, 03_ER_Diagram, 04_DFD_Level2_P6, 04_DFD_Level2_P8 (.vsdx, แก้ต่อใน Visio ได้)
  png/         รูปเดียวกัน 220 dpi (ใส่รูปเล่มได้ทันที)
  generator/   โค้ดสร้าง .vsdx + .png จาก spec JSON
    build.py            จุดเริ่ม: python build.py SPEC.json --out OUT
    model.py            โหลด spec; สร้าง Context จาก Level 1 อัตโนมัติ (สมดุลเสมอ)
    d_ctx.py d_l1.py d_l2.py d_er.py   วาดแต่ละชนิด
    draw.py             รูปทรง, การเดินเส้น, PNG renderer (ฟอนต์ TH Sarabun New, K = 1.5295)
    lay.py              ตัวช่วยจัดวาง H / V / R / store_rows
    finalize.py         ดันเส้นขนานไม่ให้ทับ วางป้าย และนับ overlap/cross/through_shape/label_hits/label_label
    vsdx.py             เขียน Visio XML (DisplayMode=1, NoFill, หัว ER #BDD7EE)
    assets/visio_document.xml   stylesheet + FaceName ของ Visio
    examples/spare_part.json    spec ที่สร้างรูปทั้ง 5 ของตัวอย่าง
    test_reproduce.py   ทดสอบว่า spec ตัวอย่างสร้างรูปตรงกับ vsdx/ และ png/ ทุกไบต์
  dd/          dd_template.docx (รูปแบบตาราง DD ของเล่ม), dd_spare_part.json, dd_to_docx.py
  sql/         dd_to_sql.py, schema_mariadb.sql (14 ตาราง)
  tools/       check_spec.py (CRUD matrix + กฎตรรกะ), check_vsdx.py (ตรวจไฟล์ Visio)
```

## ติดตั้ง

- Python 3.9+; `pip install pillow lxml python-docx` (Pillow ต้องมี libraqm สำหรับจัดสระ/วรรณยุกต์ไทย: Linux `apt install libraqm0`; Windows/macOS wheel ของ Pillow มีให้แล้ว)
- ฟอนต์ **TH Sarabun New** (SIPA, แจกฟรี) ติดตั้งในเครื่อง หรือชี้ `DFDER_FONT_DIR` ไปโฟลเดอร์ที่มี `THSarabunNew.ttf` และ `THSarabunNew Bold.ttf`
- ไม่บังคับ: LibreOffice (`soffice`) สำหรับ render .vsdx เป็น PNG เพื่อตรวจ (`--lo`), Microsoft Visio สำหรับแก้ต่อ

## คำสั่ง

```bash
cd templates/generator
python test_reproduce.py                                   # ต้องได้ PASS ก่อนเริ่ม
python ../tools/check_spec.py examples/spare_part.json ../dd/dd_spare_part.json
python build.py examples/spare_part.json --out out          # ทั้ง 5 รูป
python build.py my_system.json --out out --only l1,er --lo  # เฉพาะบางรูป + render ด้วย LibreOffice
python ../tools/check_vsdx.py out/vsdx/*.vsdx
python ../dd/dd_to_docx.py ../dd/dd_spare_part.json out/dd.docx
python ../sql/dd_to_sql.py ../dd/dd_spare_part.json > out/schema.sql
```

## เริ่มระบบใหม่

1. คัดลอก `examples/spare_part.json` เป็น `my_system.json`
2. แก้ `system`, `entities`, `stores`, `store_tables`, `processes`, `process_breaks`, `level1_flows`
   (flow = `[ต้นทาง, ปลายทาง, ชื่อข้อมูล]`; ทิศเดียวกันหลายรายการจะถูกรวมเป็นลูกศรเดียวอัตโนมัติ)
3. `level1.store_order` = store ของแต่ละ process เรียงบนลงล่าง; `level1.entries` = ทางเข้าด้านซ้ายของแต่ละ process
   `[entity, "in"|"out", "side"|"lane"]` หรือ `null` เพื่อเว้นช่อง; `shared_store` = ใช้กล่อง store ของ process ก่อนหน้าแทนการวาดซ้ำ
4. `context.entities` = ตำแหน่ง entity; `horizontal` = เชื่อมแนวนอน, `vertical` = entity ใต้ process 0
5. `level2.diagrams` = เฉพาะ process ที่ต้องแตก: `subprocesses`, `breaks`, `flows` (ขอบนอกต้องตรงกับ Level 1)
6. `er.tables` = ฟิลด์ `[PK|FK|"", ชื่อ]`; `er.placement` = จุดกึ่งกลาง x, y ของตาราง (นิ้ว);
   `er.relations` = parent, child, ด้าน (L/R/T/B), ta/tb = ตำแหน่งบนด้านเป็นสัดส่วน 0–1
   (ด้าน L/R ใช้ `d_er.row_frac(table, field)`), `via` = ช่องทางเดิน `[["x", 6.2]]` หรือ `[["y", 0.18]]`, ปลาย 25/30 และ 29/30
7. รัน `check_spec.py` → `build.py` จนผลเป็น 0 ทุกตัว → ดูรูปด้วยตา → `check_vsdx.py`
8. ถ้าต้องขยับนิดหน่อย เปิด .vsdx ใน Visio แก้ได้ (shape เป็น group ที่ DisplayMode = 1 แล้ว) แต่ให้แก้ spec ด้วยเพื่อสร้างซ้ำได้
