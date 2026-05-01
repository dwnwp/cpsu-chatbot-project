import re

def normalize_llm_markdown(text: str) -> str:
    if not text:
        return ""

    # ลบ Backslash ที่ใช้ Escape อักขระพิเศษ (เช่น \_, \*, \[, \]) 
    # ให้เหลือแค่อักขระปกติ
    text = re.sub(r'\\([_*\[\]()~`>#+\-=|{}.!])', r'\1', text)
    
    # ลบเครื่องหมาย Header (#, ##, ###) ออกจากต้นบรรทัด
    text = re.sub(r'^[#]+\s*', '', text, flags=re.MULTILINE)

    # แปลง Markdown Link [Text](URL) ให้เหลือแค่ Text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    return text.strip()