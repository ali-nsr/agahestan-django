# fix_fixture.py
import json

PATH = '../ad/fixtures/vehicle_fields.json'

with open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# اضافه کردن یک } به انتهای entryهای دارای models
content = content.replace('"سایر": []}}},', '"سایر": []}}}},')

# اعتبارسنجی
try:
    data = json.loads(content)
    print(f"✅ Valid JSON — {len(data)} entries")
    with open(PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved")
except json.JSONDecodeError as e:
    print(f"❌ Still invalid at line {e.lineno}, col {e.colno}")
    print(f"   {e.msg}")
    print(f"   near: ...{content[max(0,e.pos-80):e.pos+80]}...")