# Toolchain: 3 ส่วนเสริมที่ต้องมีก่อนเริ่มงาน (และ 1 ตัวที่ห้ามลง)

ที่มา: คู่มือ "ลง Claude Code แล้ว ติดตั้ง 3 ตัวนี้ก่อน (และ 1 ตัวที่ไม่ควรลง)" โดย AI Smart Work
<https://aismartworkth.com/guide/claude-code-first-3> (อัปเดตล่าสุด 20 ต.ค. 2569) เอกสารนี้สรุปและอ้างอิงจากหน้านั้น
ร่วมกับ README ทางการของแต่ละโครงการ (ตรวจ 4 พ.ย. 2569) **ไม่ได้คัดลอกซอร์สของเครื่องมือใดมาไว้ใน skill นี้** ให้ติดตั้งจากแหล่งทางการเท่านั้น

| เครื่องมือ | ทำอะไร | ผู้พัฒนา / สัญญาอนุญาต | ลิงก์ทางการ |
|---|---|---|---|
| Ponytail | ให้ AI ใช้ของที่มีอยู่ก่อน เขียนโค้ดน้อยที่สุดที่ยังใช้งานได้ | Dietrich Gebert / MIT | <https://github.com/DietrichGebert/ponytail> |
| Graphify | ทำแผนที่ความรู้ (knowledge graph) ของโฟลเดอร์งาน ให้ AI ถามจากแผนที่ | Graphify Labs / Apache-2.0 | <https://github.com/Graphify-Labs/graphify> |
| Anthropic Skills (document-skills) | สร้าง/แก้ Word, Excel, PowerPoint, PDF | Anthropic / docx-pdf-pptx-xlsx เป็น source-available (ไม่ใช่ open source) | <https://github.com/anthropics/skills> |

ทั้ง 3 ตัวฟรี (Graphify มีบริการคลาวด์เสียเงินแยก ไม่จำเป็นต้องใช้) ต้องมี Claude Code ที่ติดตั้งแล้ว (แพ็กเกจ Claude แบบเสียเงิน)

---

## 1. Ponytail: ใช้ของที่มีอยู่ก่อน เขียนใหม่ทีหลัง

**ทำอะไร** ชุดกฎที่สั่งให้ AI ใช้ของที่มีอยู่แล้วก่อน (ในโปรเจกต์ ในภาษา ในเบราว์เซอร์/แพลตฟอร์ม) ค่อยเขียนใหม่หรือลงไลบรารีเพิ่ม
ตาม README: ก่อนเขียนโค้ดให้หยุดที่ขั้นแรกที่ใช้ได้ 1) สิ่งนี้จำเป็นต้องมีไหม 2) มีในโปรเจกต์แล้วหรือยัง 3) standard library ทำได้ไหม
4) ฟีเจอร์ของแพลตฟอร์ม 5) dependency ที่ลงไว้แล้ว 6) ทำในบรรทัดเดียวได้ไหม 7) จึงเขียนขั้นต่ำที่ใช้งานได้ + test เล็ก ๆ ถ้ามี logic
และต้องอ่านโค้ดที่เกี่ยวข้องให้เข้าใจก่อนเสมอ ("ขี้เกียจเรื่องวิธีแก้ ไม่ขี้เกียจเรื่องการอ่าน") ไม่ตัดเรื่องความปลอดภัยหรือการตรวจข้อมูล

**ตัวเลขจริง** ผู้พัฒนาเคยอ้างว่าโค้ดลดลง 80–94% แล้วถอนตัวเลขเองหลังมีคนท้วง ผลรีวิวภายนอกที่หน้าคู่มืออ้างถึงอยู่ราว
**โค้ดน้อยลง ~54% และโทเคนน้อยลง ~22%** (README รุ่น 5 อ้าง benchmark ของผู้พัฒนาเองว่า −53% code, −45% tokens ถือเป็นตัวเลขจากผู้พัฒนา)

**ใช้เมื่อไร** ทุกงานที่เขียนหรือแก้โค้ด/สคริปต์ รวมทั้งงานเอกสารที่ทำด้วยสคริปต์

**ติดตั้ง (Claude Code)** พิมพ์ทีละบรรทัด ส่งแยกกัน:
```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```
- ติดตั้งจาก `DietrichGebert/ponytail` (GitHub) หรือ `@dietrichgebert/ponytail` (npm) **เท่านั้น** ตัวที่ชื่อคล้ายกันไม่ใช่ของจริง; ของจริงไม่มีไฟล์ `.exe`/`.dll`
- การเปิดใช้อัตโนมัติต้องมี **Node.js** ถ้าไม่มี ใช้ได้โดยพิมพ์ `/ponytail` เอง หรือให้ AI ติดตั้ง Node.js ให้

**ถอนการติดตั้ง** พิมพ์ `/plugin` ใน Claude Code แล้วเลือกปิดหรือถอนการติดตั้ง

## 2. Graphify: แผนที่โปรเจกต์ให้ AI อ่าน

**ทำอะไร** แปลงโฟลเดอร์งาน (โค้ด เอกสาร PDF ภาพ SQL config) เป็น knowledge graph ให้ AI ถามจากแผนที่แทนการเปิดไล่ทีละไฟล์

**ใช้เมื่อไร** โปรเจกต์ใหญ่ ไฟล์เยอะ (เช่น โฟลเดอร์รายงานทั้งเล่ม + โค้ดระบบ) ถ้าโปรเจกต์เล็ก **ข้ามได้**
ครั้งแรก AI ต้องอ่านทั้งโปรเจกต์ **กินโทเคนพอสมควร**

**ติดตั้ง** ต้องมี `uv` หรือ `pipx` (หรือ Python 3.10+) แพ็กเกจของจริงชื่อ **`graphifyy` (y สองตัว)** ตัวที่ชื่อ graphify อย่างอื่นไม่เกี่ยวข้อง
```bash
uv tool install graphifyy      # หรือ pipx install graphifyy / pip install graphifyy
graphify install
```
แล้วเปิด Claude Code ในโฟลเดอร์งาน พิมพ์ `/graphify .`

**ติดปัญหา** `graphify` ไม่พบคำสั่ง: รัน `uv tool update-shell` แล้วปิดเปิดเทอร์มินัลใหม่ ถ้ายังไม่ได้ ใช้ `pipx install graphifyy`
(Windows: เพิ่ม `%APPDATA%\Python\Python3xx\Scripts` ใน PATH ตาม README ของ Graphify)

**ถอนการติดตั้ง** `uv tool uninstall graphifyy` (หรือ `pipx uninstall graphifyy`)

## 3. Anthropic Skills: Word, Excel, PowerPoint, PDF

**ทำอะไร** สกิลทางการของ Anthropic ให้สร้างและแก้ไฟล์เอกสาร เช่น "ทำ Excel สรุปยอดจากไฟล์นี้" "ดึงช่องในฟอร์ม PDF นี้ออกมา"

**ติดตั้ง (Claude Code)** ทีละบรรทัด:
```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```
แล้วสั่งงานโดยเอ่ยชนิดไฟล์ได้เลย เช่น "ใช้ PDF skill ดึงช่องในฟอร์มจาก path/to/file.pdf"

**สัญญาอนุญาต** สกิล docx / pdf / pptx / xlsx เป็น source-available ไม่ใช่ open source: **ห้ามคัดลอกมาใส่ skill นี้หรือแจกต่อ** ให้ติดตั้งจาก anthropics/skills เท่านั้น

**ถอนการติดตั้ง** `/plugin` แล้วเลือกปิดหรือถอนการติดตั้ง

## ห้ามลง: OmniRoute

ดังเพราะ "ใช้ AI ฟรีเมื่อโควตาหมด" โดยเป็นตัวกลาง (proxy) ส่งงานของ Claude Code ไปให้ AI เจ้าอื่น แต่ตัวกลางนี้
- ต้อง **ถือ API key ของทุกเจ้า**
- **เห็นทุกข้อความและโค้ด** ที่ส่ง และ **แก้ข้อมูลระหว่างทางได้**
- สลับโมเดลกลางงาน ทำให้ **คุณภาพไม่คงที่**

ถ้าโควตาหมดบ่อย ทางที่ปลอดภัยกว่าคือใช้ Ponytail ลดโทเคน หรืออัปแพ็กเกจ (Pro / Max) งานรายงานและข้อมูลของผู้ใช้ห้ามส่งผ่าน proxy แบบนี้

## ติดตรงนี้ ทำยังไง

| อาการ | วิธีแก้ |
|---|---|
| พิมพ์ `/plugin` แล้วไม่มีอะไรเกิดขึ้น | `claude update` ในเทอร์มินัล เปิด Claude Code ใหม่ แล้วส่งคำสั่ง **ทีละบรรทัด** |
| ลง Ponytail แล้วไม่เห็นว่าทำงาน | ต้องมี Node.js สำหรับเปิดอัตโนมัติ ไม่งั้นพิมพ์ `/ponytail` เอง |
| `graphify` ไม่พบคำสั่ง | `uv tool update-shell` แล้วเปิดเทอร์มินัลใหม่ หรือ `pipx install graphifyy` |
| อยากเลิกใช้ | `/plugin` → ปิด/ถอน; Graphify: `uv tool uninstall graphifyy` |

---

## ใช้กับงานของเราอย่างไร

| เครื่องมือ | ในงาน DFD/ER และรายงาน |
|---|---|
| Ponytail (reuse-first) | = กฎเหล็กข้อ "เริ่มจากต้นฉบับที่แพ็กไว้": ใช้ `templates/generator` + `examples/spare_part.json` + `templates/vsdx` ก่อน แก้ spec แทนการวาดใหม่หรือเขียนโค้ดใหม่; ใช้ `dd_to_docx.py`, `dd_to_sql.py`, `check_*.py` ที่มีอยู่ก่อนเขียนสคริปต์เอง |
| Graphify | ทำแผนที่โฟลเดอร์รายงานของผู้ใช้ (บท 1–3, บรรณานุกรม, Final, โค้ดระบบ) เพื่อหาว่าคำ/ชื่อ process/ตารางอยู่ที่ไหนบ้าง ก่อนตรวจความสอดคล้องทั้งเล่ม; ใช้เมื่อโฟลเดอร์ใหญ่ ไม่ต้องใช้กับงานแก้ไฟล์เดียว |
| document-skills (docx/xlsx/pptx/pdf) | เปิด/แก้ .docx ของรายงาน, ทำ CRUD matrix ใน Excel, สไลด์นำเสนอ, อ่าน/รวม PDF — ยังต้องทำตาม `docs/report-insertion.md` (ฟอนต์ cs flag caption เลขหน้า) |

## เครื่องมืออื่นที่ไม่ใช่ Claude Code

| ตัวช่วย | Ponytail | Graphify | งานเอกสาร (docx/xlsx/pptx/pdf) |
|---|---|---|---|
| Codex | `codex plugin marketplace add DietrichGebert/ponytail` แล้ว `codex plugin add ponytail@ponytail` จากนั้นเปิด `/hooks` trust 2 hooks แล้วเริ่ม thread ใหม่ | ติดตั้ง `graphifyy` เหมือนกัน แล้วดูวิธีผูกกับ Codex ใน README ของ Graphify | `npx skills add https://github.com/anthropics/skills --skill docx` (ตามที่ตัวติดตั้งรองรับ; ใช้ส่วนตัว ห้ามแจกต่อ) หรือใช้ python-docx / openpyxl / python-pptx / pypdf |
| Cursor | ทำตาม INSTALL.md ของ Ponytail (rule file หรือ hooks) หรือคัดลอก `AGENTS.md` ของ Ponytail ลงโปรเจกต์ | ดู README ของ Graphify (รองรับ Cursor) | เหมือน Codex |
| ตัวที่รองรับ Agent Skills อื่น ๆ (Gemini CLI, Copilot, Windsurf, Cline, Grok Bot ฯลฯ) | `npx skills add https://github.com/DietrichGebert/ponytail` หรือให้ AI ติดตั้ง `skills/ponytail/SKILL.md` เป็น skill | ตาม README ของ Graphify | ใช้สกิลเอกสารที่ตัวช่วยมีอยู่แล้วก่อน (เช่น Grok Bot มี docx/xlsx/pptx/pdf skill ในตัว) |

ถ้าคำสั่งใดใช้ไม่ได้ในตัวช่วยนั้น ให้เปิด README/INSTALL.md ทางการของเครื่องมือ แล้วทำตามนั้น อย่าเดาคำสั่ง และ **อย่าติดตั้งโดยไม่ได้รับอนุญาตจากผู้ใช้** เมื่อเป็นเครื่องของผู้ใช้
