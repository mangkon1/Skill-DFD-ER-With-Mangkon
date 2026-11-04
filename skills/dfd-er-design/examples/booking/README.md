# ตัวอย่าง: ระบบจองสนามกีฬาขนาดเล็ก (แก้จากผลทดสอบ AI อื่น 5 พ.ย. 2569)

AI อีกตัวใช้ skill v3.0 สร้างรูปของระบบนี้แล้วได้ลูกศรลอยใน Context, store D1–D5 ถูกวาดซ้ำ 19 กล่องใน Level 1
และสระ/วรรณยุกต์เพี้ยน (ดู `docs/checklist.md` ส่วน E) โฟลเดอร์นี้คือผลที่ถูกจาก generator v3.1

```bash
cd ../../templates/generator
python build.py ../../examples/booking/booking.json --out ../../examples/booking
python ../tools/check_vsdx.py ../../examples/booking/vsdx/*.vsdx
```

| รูป | ผล |
|---|---|
| `png/01_Context_Diagram.png` | ลูกศรทุกเส้นติดขอบกล่อง 0 และ entity (กล่อง 0 ขยายให้ครอบ ผู้จัดการ) |
| `png/02_DFD_Level1.png` | store_mode single: 10 กล่อง (เดิม 19) แต่ละ store ซ้ำไม่เกิน 1 สำเนา มีขีดซ้ำ; ถ้าห้ามซ้ำจะมีเส้นตัด 76 จุด จึงซ้ำเท่าที่จำเป็น เหลือ 5 จุดเป็น line jump; เส้นทุกเส้น glue ทั้งสองปลาย |

spec: `booking.json` (ER ไม่อยู่ในตัวอย่างนี้ ใช้ spec ER ของผู้ทดสอบได้ตามเดิม)
