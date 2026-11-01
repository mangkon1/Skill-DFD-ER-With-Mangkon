# Skill DFD ER With Mangkon

Skill สำหรับออกแบบ Data Flow Diagram และ ER Diagram ตามหลักข้อมูลต้องมีที่มาที่ไป ใช้รูปแบบ [Agent Skills](https://agentskills.io) จึงติดตั้งจาก URL เดียวกันได้กับตัวช่วย AI ที่รองรับสกิล เช่น Cursor, Claude Code, Codex, Gemini CLI, GitHub Copilot, Windsurf, Cline และตัวอื่นที่ตัวติดตั้งรองรับ

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
