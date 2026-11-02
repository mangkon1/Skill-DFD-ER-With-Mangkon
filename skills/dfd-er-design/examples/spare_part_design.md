# ตัวอย่าง: ระบบบริหารจัดการอุปกรณ์อะไหล่และติดตามสถานะการส่งซ่อม

สรุปการออกแบบที่ผ่านการตรวจของอาจารย์ ใช้เป็นตัวอย่างอ้างอิง ข้อมูลทั้งหมดอยู่ใน `templates/generator/examples/spare_part.json` (แผนภาพ) และ `templates/dd/dd_spare_part.json` (Data Dictionary)

## External Entities

| รหัส | ชื่อ |
|---|---|
| ADM | ผู้ดูแลระบบ |
| ENG | ช่าง |
| SUP | หัวหน้างาน |
| AST | ผู้ช่วยผู้จัดการ |
| MGR | ผู้จัดการ |

## Data Stores และตาราง

| Store | ชื่อ | ตาราง |
|---|---|---|
| D1 | ข้อมูลอุปกรณ์ | `product_types`, `products`, `spare_statuses`, `spares` |
| D2 | ข้อมูลพนักงาน | `employees`, `roles`, `users` |
| D3 | ข้อมูลโซน | `zones` |
| D4 | ข้อมูลทีม | `teams`, `team_supervisor_logs` |
| D5 | ข้อมูลการแจกจ่ายอุปกรณ์ | `spare_assignments` |
| D6 | ประวัติสถานะอุปกรณ์ | `spare_status_logs` |
| D7 | ข้อมูลการใช้งานอุปกรณ์ | `spare_usages` |
| D8 | ข้อมูลเกณฑ์ KPI | `kpi_settings` |

## Processes (Level 1 ตามลำดับการเกิดข้อมูล)

| เลข | ชื่อ | เขียน store | อ่าน store | ประเภท |
|---|---|---|---|---|
| 1 | จัดการข้อมูลอุปกรณ์ | D1 | - | Master |
| 2 | จัดการข้อมูลพนักงาน | D2 | - | Master |
| 3 | จัดการข้อมูลโซน | D3 | D2 D4 | Master |
| 4 | จัดการข้อมูลทีม | D4 | D2 | Master |
| 5 | แจกจ่ายอุปกรณ์ให้ช่าง | D1 D5 D6 | D1 D2 D5 | Transaction |
| 6 | บันทึกการใช้งานและปรับสถานะอุปกรณ์ | D1 D6 D7 | D1 D7 | Transaction |
| 7 | กำหนดเกณฑ์ KPI | D8 | D4 | ค่าที่กำหนด (KPI) |
| 8 | ติดตามสถานะและออกรายงาน | - | D1 D2 D3 D4 D6 D8 | Report / แจ้งเตือน |

Level 2 ทำเฉพาะ process ที่มีหลายขั้นตอน:

- **6 บันทึกการใช้งานและปรับสถานะอุปกรณ์**: 6.1 บันทึกการใช้งานหน้างาน → 6.2 ปรับสถานะและบันทึกอาการชำรุด → 6.3 รับคืนและส่งซ่อมอุปกรณ์
- **8 ติดตามสถานะและออกรายงาน**: 8.1 คำนวณระยะเวลาในสถานะ → 8.2 ตรวจสอบเกณฑ์ KPI และแจ้งเตือน → 8.3 ออกรายงานตามสิทธิ์

## ตาราง (14 ตาราง)

| ตารางที่ | ตาราง | ความหมาย | PK | FK |
|---|---|---|---|---|
| 3.1 | `employees` | ข้อมูลพนักงาน | emp_id | - |
| 3.2 | `roles` | บทบาทผู้ใช้ | role_code | - |
| 3.3 | `users` | บัญชีผู้ใช้ | user_id | emp_id→employees, role_code→roles |
| 3.4 | `zones` | โซน | zone_id | team_id→teams, emp_id→employees |
| 3.5 | `teams` | ทีม | team_id | sup_emp_id→employees |
| 3.6 | `team_supervisor_logs` | ประวัติการย้ายทีมของหัวหน้างาน | log_id | emp_id→employees, prev_team_id→teams, new_team_id→teams |
| 3.7 | `product_types` | ประเภทอุปกรณ์ | type_id | - |
| 3.8 | `products` | รุ่นอุปกรณ์ | product_id | type_id→product_types |
| 3.9 | `spare_statuses` | สถานะอุปกรณ์ | status_code | - |
| 3.10 | `spares` | อุปกรณ์อะไหล่รายเครื่อง | spare_id | product_id→products, status_code→spare_statuses, emp_id→employees |
| 3.11 | `spare_assignments` | การแจกจ่ายอุปกรณ์ให้ช่าง | sa_id | spare_id→spares, emp_id→employees |
| 3.12 | `spare_usages` | การใช้งานอุปกรณ์หน้างาน | usage_id | spare_id→spares, removed_spare_id→spares, emp_id→employees |
| 3.13 | `spare_status_logs` | ประวัติสถานะอุปกรณ์ | log_id | spare_id→spares, usage_id→spare_usages, status_code→spare_statuses, actor_id→users |
| 3.14 | `kpi_settings` | เกณฑ์ KPI | kpi_id | team_id→teams, type_id→product_types, status_code→spare_statuses, set_by→users |

## ความสัมพันธ์ (23 เส้น, 1 เส้นต่อคู่)

| Parent | Child | ฝั่ง parent | ฝั่ง child |
|---|---|---|---|
| `teams` | `zones` | 1 (หนึ่งเท่านั้น) | 0..N |
| `employees` | `zones` | 1 (หนึ่งเท่านั้น) | 0..1 |
| `roles` | `users` | 1 (หนึ่งเท่านั้น) | 0..N |
| `employees` | `users` | 1 (หนึ่งเท่านั้น) | 0..N |
| `employees` | `spare_assignments` | 1 (หนึ่งเท่านั้น) | 0..N |
| `employees` | `spare_usages` | 1 (หนึ่งเท่านั้น) | 0..N |
| `employees` | `spares` | 0..1 | 0..N |
| `spares` | `spare_assignments` | 1 (หนึ่งเท่านั้น) | 0..N |
| `spares` | `spare_usages` | 1 (หนึ่งเท่านั้น) | 0..N |
| `spares` | `spare_status_logs` | 1 (หนึ่งเท่านั้น) | 0..N |
| `spare_usages` | `spare_status_logs` | 0..1 | 0..N |
| `products` | `spares` | 1 (หนึ่งเท่านั้น) | 0..N |
| `product_types` | `products` | 1 (หนึ่งเท่านั้น) | 0..N |
| `spare_statuses` | `spares` | 1 (หนึ่งเท่านั้น) | 0..N |
| `spare_statuses` | `spare_status_logs` | 1 (หนึ่งเท่านั้น) | 0..N |
| `users` | `spare_status_logs` | 1 (หนึ่งเท่านั้น) | 0..N |
| `users` | `kpi_settings` | 1 (หนึ่งเท่านั้น) | 0..N |
| `spare_statuses` | `kpi_settings` | 1 (หนึ่งเท่านั้น) | 0..N |
| `product_types` | `kpi_settings` | 0..1 | 0..N |
| `teams` | `kpi_settings` | 0..1 | 0..N |
| `employees` | `teams` | 1 (หนึ่งเท่านั้น) | 0..N |
| `teams` | `team_supervisor_logs` | 1 (หนึ่งเท่านั้น) | 0..N |
| `employees` | `team_supervisor_logs` | 1 (หนึ่งเท่านั้น) | 0..N |

## จุดที่ควรสังเกต

- สถานะอุปกรณ์ (เช่น ชำรุด ส่งซ่อม) เป็นแถวใน `spare_statuses` ไม่ใช่ process
- เกณฑ์ KPI มี process 7 และ store D8 ของตัวเอง process 8 อ่านเกณฑ์จาก D8 เพื่อแจ้งเตือนหัวหน้างาน
- ประวัติเก็บเฉพาะ 2 เรื่องที่ต้องใช้: การย้ายทีมของหัวหน้างาน (`team_supervisor_logs`: ทีมเดิม ทีมใหม่ เวลา) และการเปลี่ยนสถานะอุปกรณ์ (`spare_status_logs`)
- อุปกรณ์ผูกกับช่างผู้ถือครอง (`spares.emp_id`, nullable) ไม่ผูกกับโซน
- `team_supervisor_logs` มี FK 2 ตัวไป `teams` (prev/new) แต่วาดเส้นเดียว
- `check_spec.py` เตือนว่า process 3 (โซน) อ่าน D4 (ทีม) ก่อน process 4 สร้างทีม เพราะ `zones.team_id` เป็น NOT NULL
  ลำดับนี้คงไว้ตามที่อาจารย์กำหนดในข้อเสนอแนะ ถ้าออกแบบใหม่โดยไม่มีข้อกำหนด ควรให้ "จัดการข้อมูลทีม" มาก่อน "จัดการข้อมูลโซน"
