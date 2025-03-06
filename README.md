
# AI-Makruk-Board


## Engine
#### การใช้คำสั่งเพื่อสื่อสารกับ Engine

1.คำสั่งตัวอย่างคำสั่งส่งตำเเหน่ง
```http
  python3 makruk_cli.py --fen "rnsmksnr/8/pppppppp/8/8/PPPPPPPP/8/RNSKMS1R w - - 0 1"
```

2.คำสั่งตัวอย่างการส่งตำเเหน่ง + เลือก Level Engine
```http
  python3 makruk_cli.py --fen "rnsmksnr/8/pppppppp/8/8/PPPPPPPP/8/RNSKMS1R w - - 0 1" --skill 20
```

3.คำสั่งที่ใช้ทดสอบว่า Engine Level เปลี่ยนจริงๆ (เข้าไปเปลี่ยนใน Level source code ก่อน)
```http
  python3 makruk_cli.py --test-skill 
```
