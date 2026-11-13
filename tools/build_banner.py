#!/usr/bin/env python3
"""Build the README banner image in assets/."""
from PIL import Image, ImageDraw, ImageFont

import doc_template as T

W, H, PAD = 1600, 460, 90


def main():
    img = Image.new("RGB", (W, H), f"#{T.ACCENT}")
    draw = ImageDraw.Draw(img)
    font = lambda face, size: ImageFont.truetype(face, size)
    logo = Image.open(T.MONOGRAM_WHITE).convert("RGBA").resize((96, 96), Image.LANCZOS)
    img.paste(logo, (PAD, 70), logo)
    draw.text((PAD + 124, 78), "Jahangir Shukurov", font=font(T.ARIAL_BOLD, 40), fill="white")
    draw.text((PAD + 124, 128), "Governance, Risk and Compliance portfolio", font=font(T.ARIAL, 28), fill="#CFE3E8")
    draw.text((PAD, 218), "Threat-informed GRC", font=font(T.ARIAL_BOLD, 64), fill="white")
    draw.text((PAD, 300), "Would this control actually stop or detect a real attack?", font=font(T.ARIAL, 30), fill="#DCEBEE")
    x = PAD
    for chip in ("ISO/IEC 27001:2022", "ISO/IEC 27005", "DORA", "GDPR", "PCI DSS v4.0.1", "NIST CSF 2.0", "MITRE ATT&CK"):
        width = draw.textlength(chip, font=font(T.ARIAL_BOLD, 22)) + 36
        draw.rounded_rectangle((x, 368, x + width, 412), radius=22, fill="#2B7385")
        draw.text((x + 18, 378), chip, font=font(T.ARIAL_BOLD, 22), fill="white")
        x += width + 14
    img.save(T.ASSETS / "banner.png")
    print("Banner saved")


if __name__ == "__main__":
    main()
