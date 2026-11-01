# Skill DFD ER With Mangkon

Skill สำหรับออกแบบ Data Flow Diagram และ ER Diagram ตามหลักข้อมูลต้องมีที่มาที่ไป ใช้กับ Cursor และตัวช่วยเขียนโค้ดที่รองรับ Agent Skills

## ติดตั้งจาก URL

คำสั่งนี้ติดตั้ง skill `dfd-er-design` ให้ Cursor ทั้งเครื่อง โดยไม่ต้องตอบคำถามเพิ่ม

```bash
npx skills add https://github.com/mangkon1/Skill-DFD-ER-With-Mangkon --skill dfd-er-design -g -a cursor -y
```

เปิดแชทใหม่หลังติดตั้ง แล้วบอกให้ช่วยออกแบบหรือตรวจ DFD, ER Diagram หรือ Data Dictionary

ใน Cursor ติดตั้งจากหน้าจอได้เช่นกัน

1. เปิด Customize
2. เลือกนำเข้าจาก GitHub repository
3. วาง `https://github.com/mangkon1/Skill-DFD-ER-With-Mangkon`
4. กดติดตั้ง plugin `dfd-er-design`

ติดตั้งเฉพาะโปรเจกต์ปัจจุบัน โดยไม่ใส่ `-g`

```bash
npx skills add https://github.com/mangkon1/Skill-DFD-ER-With-Mangkon --skill dfd-er-design -a cursor -y
```
