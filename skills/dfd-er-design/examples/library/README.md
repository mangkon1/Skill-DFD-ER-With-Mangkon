# ตัวอย่าง: ระบบยืม-คืนหนังสือห้องสมุด (ทดสอบ Level 1 แบบกะทัดรัด v3.4)

ถอดจากรูปที่ผู้ใช้ส่งมา (รูปเดิมวาง store เยื้องหลายคอลัมน์ หน้ายืดออกข้าง) แล้ววาดใหม่ด้วย generator

| รูป | ผล |
|---|---|
| `png/01_Context_Diagram.png` | 3 entity: บรรณารักษ์ หัวหน้าห้องสมุด สมาชิก |
| `png/02_DFD_Level1.png` | 11.9 x 14.7 in, 7 process, store คอลัมน์เดียวชิด process เส้นเข้าขอบบน/ล่าง store; 7 กล่อง store (ซ้ำ D2 D4 ตัวละ 1 สำเนา มีขีดซ้ำ), entity กล่องเดี่ยว 3 กล่อง, เส้นตัด 0 ไม่มี line jump |

spec: `library.json`  ทดสอบ: `python ../../templates/generator/test_examples.py`
