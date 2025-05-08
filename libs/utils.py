import os
import re
import time
import colorsys
from pathlib import Path
from datetime import datetime

from postgrest.exceptions import APIError
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def retry_on_db_error(retries: int = 3, delay: int = 60):
    """
    Decorator to retry a function upon encountering a database error.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except (APIError) as e:
                    attempt += 1
                    if attempt < retries:
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator


def generate_contract_pdf(concert: dict, paid_in_full: bool = False) -> str:
    if concert["total"] == concert["advance"]:
        paid_in_full = True
    
    file_path = get_filepath(concert['date'], concert['city'])
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Register fonts
    pdfmetrics.registerFont(TTFont("Lato-Black", "assets/fonts/Lato-Black.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-BlackItalic", "assets/fonts/Lato-BlackItalic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Bold", "assets/fonts/Lato-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-BoldItalic", "assets/fonts/Lato-BoldItalic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Heavy", "assets/fonts/Lato-Heavy.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-HeavyItalic", "assets/fonts/Lato-HeavyItalic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Italic", "assets/fonts/Lato-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Light", "assets/fonts/Lato-Light.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-LightItalic", "assets/fonts/Lato-LightItalic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Medium", "assets/fonts/Lato-Medium.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-MediumItalic", "assets/fonts/Lato-MediumItalic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Regular", "assets/fonts/Lato-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Semibold", "assets/fonts/Lato-Semibold.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-SemiboldItalic", "assets/fonts/Lato-SemiboldItalic.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-Thin", "assets/fonts/Lato-Thin.ttf"))
    pdfmetrics.registerFont(TTFont("Lato-ThinItalic", "assets/fonts/Lato-ThinItalic.ttf"))


    # Title
    c.setFont("Lato-Bold", 12)
    c.drawCentredString(width / 2, height - 50, "CONTRACT FORM")

    # Band Info
    c.setFont("Lato-Black", 26)
    c.drawCentredString(width / 2, height - 80, "TANMAY KAR AND FRIENDS")
    c.setFont("Lato-Bold", 10)
    c.drawCentredString(width / 2, height - 100, "(A Folk-Based Urban Band)")
    c.setFont("Lato-BoldItalic", 10)
    c.drawCentredString(width / 2, height - 115, "91/11 J.K. Street, Uttarpara, Hooghly - 712258")
    c.setFont("Lato-Black", 10)
    c.drawCentredString(width / 2, height - 130, "Mobile No.: 9836860793 / 9433070936 | Email: tanmaykar1977@gmail.com")

    # Separator Line
    c.setLineWidth(2)
    c.setStrokeColorRGB(0, 0, 0)
    c.line(50, height - 140, 550, height - 140)

    # Contract Details
    c.setFont("Lato-Regular", 10)
    y = height - 170
    c.setLineWidth(1)
    c.drawString(50, y, "Organizer/Club")
    c.drawString(160, y, ":")
    c.line(170, y, 550, y)
    c.drawCentredString(360, y + 2, concert['organizer'])

    c.drawString(50, y - 20, "Address/Venue")
    c.drawString(160, y - 20, ":")
    c.line(170, y - 20, 550, y - 20)
    c.drawCentredString(360, y - 18, concert['venue'])

    c.drawString(50, y - 40, "Date of Program")
    c.drawString(160, y - 40, ":")
    c.line(170, y - 40, 550, y - 40)
    c.drawCentredString(360, y - 38, format_date(concert['date']))

    c.drawString(50, y - 60, "Stage Timing")
    c.drawString(160, y - 60, ":")
    c.line(170, y - 60, 550, y - 60)
    c.drawCentredString(360, y - 58, format_time(concert['time']))

    c.drawString(50, y - 80, "Total Contract Amount")
    c.drawString(160, y - 80, ":")
    c.line(170, y - 80, 550, y - 80)
    c.drawCentredString(
        360,
        y - 78,
        f"Rs. {format_indian_number(concert['total']) or 0}/- " +
        f"({number_to_words(concert['total'])}) " +
        f"{'With' if concert['is_sound_included'] else 'Without'} " +
        "Input Sound"
    )

    c.drawString(50, y - 100, "Advance Payment")
    c.drawString(160, y - 100, ":")
    c.line(170, y - 100, 550, y - 100)
    if paid_in_full:
        c.drawCentredString(
            360,
            y - 98,
            f"Rs. {format_indian_number(concert['total']) or 0}/- " +
            f"({number_to_words(concert['total'])})"
        )
    else:
        c.drawCentredString(
            360,
            y - 98,
            f"Rs. {format_indian_number(concert['advance']) or 0}/- " +
            f"({number_to_words(concert['advance'])})"
        )

    c.drawString(50, y - 120, "Remaining Payment")
    c.drawString(160, y - 120, ":")
    c.line(170, y - 120, 550, y - 120)
    if paid_in_full:
        c.drawCentredString(
            360,
            y - 118,
            "Rs. 0/- (Rupees Zero Only)"
        )
    else:
        c.drawCentredString(
            360,
            y - 118,
            f"Rs. {format_indian_number(concert['total'] - concert['advance']) or 0}/- " +
            f"({number_to_words(concert['total'] - concert['advance'])})"
        )

    c.setFont("Lato-Italic", 10)
    c.drawString(50, y - 140, "(To be received in full before stage)")

    # Signatures
    c.setFont("Lato-Semibold", 10)
    c.drawImage("assets/images/signature.jpg", 50, y - 200, width=150, height=50)
    c.line(50, y - 210, 200, y - 210)
    c.drawCentredString(125, y - 220, "For Tanmay Kar and Friends")
    c.line(400, y - 210, 550, y - 210)
    c.drawCentredString(475, y - 220, "Signature of the Party")

    # Paid in Full
    if paid_in_full:
        c.drawImage("assets/images/paid_in_full.png", (width - 150) / 2, y - 255, width=160, height=120, mask="auto")

    # Terms and Conditions
    c.setFont("Lato-BoldItalic", 12)
    c.drawString(50, y - 260, "Terms and Conditions:")
    c.setFont("Lato-Italic", 10)
    terms = [
        "1. Party/club is liable to pay the band 50% of the contract amount if they cancel the event on the day of the event.",
        "2. Advance will only be refunded if the band is unable to perform for any reason (except Force Majeure).",
        "3. The band will stop the program if offensive attitude or any harassment/malfunctioning is faced.",
        "4. Party/club is responsible for the security of all members and belongings (Instruments, Vehicles, etc.)."
    ]
    for i, term in enumerate(terms):
        c.drawString(60, y - 280 - i * 20, term)
    
    # Footer Line
    c.setLineWidth(2)
    c.line(50, y - 360, 550, y - 360)

    # For the Band
    c.setFont("Lato-Bold", 12)
    c.drawCentredString(width / 2, y - 380, "[FOR TANMAY KAR AND FRIENDS]")

    y = y - 420
    c.setFont("Lato-Regular", 10)
    c.setLineWidth(1)
    c.drawString(50, y, "Organizer/Club")
    c.drawString(160, y, ":")
    c.line(170, y, 550, y)
    c.drawCentredString(360, y + 2, concert['organizer'])

    c.drawString(50, y - 20, "Address/Venue")
    c.drawString(160, y - 20, ":")
    c.line(170, y - 20, 550, y - 20)
    c.drawCentredString(360, y - 18, concert['venue'])

    c.drawString(50, y - 40, "Date of Program")
    c.drawString(160, y - 40, ":")
    c.line(170, y - 40, 550, y - 40)
    c.drawCentredString(360, y - 38, format_date(concert['date']))

    c.drawString(50, y - 60, "Stage Timing")
    c.drawString(160, y - 60, ":")
    c.line(170, y - 60, 550, y - 60)
    c.drawCentredString(360, y - 58, format_time(concert['time']))

    c.drawString(50, y - 80, "Total Contract Amount")
    c.drawString(160, y - 80, ":")
    c.line(170, y - 80, 550, y - 80)
    c.drawCentredString(
        360,
        y - 78,
        f"Rs. {format_indian_number(concert['total']) or 0}/- " +
        f"({number_to_words(concert['total'])}) " +
        f"{'With' if concert['is_sound_included'] else 'Without'} " +
        "Input Sound"
    )

    c.drawString(50, y - 100, "Advance Payment")
    c.drawString(160, y - 100, ":")
    c.line(170, y - 100, 550, y - 100)
    if paid_in_full:
        c.drawCentredString(
            360,
            y - 98,
            f"Rs. {format_indian_number(concert['total']) or 0}/- " +
            f"({number_to_words(concert['total'])})"
        )
    else:
        c.drawCentredString(
            360,
            y - 98,
            f"Rs. {format_indian_number(concert['advance']) or 0}/- " +
            f"({number_to_words(concert['advance'])})"
        )

    c.drawString(50, y - 120, "Remaining Payment")
    c.drawString(160, y - 120, ":")
    c.line(170, y - 120, 550, y - 120)
    if paid_in_full:
        c.drawCentredString(
            360,
            y - 118,
            "Rs. 0/- (Rupees Zero Only)"
        )
    else:
        c.drawCentredString(
            360,
            y - 118,
            f"Rs. {format_indian_number(concert['total'] - concert['advance']) or 0}/- " +
            f"({number_to_words(concert['total'] - concert['advance'])})"
        )

    # Footer Signatures
    c.setFont("Lato-Semibold", 10)
    c.drawImage("assets/images/signature.jpg", 50, y - 180, width=150, height=50)
    c.line(50, y - 190, 200, y - 190)
    c.drawCentredString(125, y - 200, "For Tanmay Kar and Friends")
    c.line(400, y - 190, 550, y - 190)
    c.drawCentredString(475, y - 200, "Signature of the Party")

    c.save()\
    
    return file_path


def get_filepath(date: str, city: str) -> str:
    folder_name = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%B")
    full_folder_name = os.path.join(Path.home(), "Documents", "TK&F Contracts", folder_name)
    if not os.path.exists(full_folder_name):
        os.makedirs(full_folder_name)
    return f"{full_folder_name}\\{format_date(date, False)} {city}.pdf"


def get_ordinal_suffix(day: int) -> str:
    if 11 <= day <= 13:
        return 'th'
    last_digit = day % 10
    if last_digit == 1:
        return 'st'
    elif last_digit == 2:
        return 'nd'
    elif last_digit == 3:
        return 'rd'
    else:
        return 'th'

def format_date(input_date_str: str, include_year: bool = True) -> str:
    # Parse the input date string
    date_obj = datetime.strptime(input_date_str, "%Y-%m-%d")

    # Get parts
    day = date_obj.day
    month = date_obj.strftime("%B")  # Full month name
    year = date_obj.year

    # Get ordinal suffix
    suffix = get_ordinal_suffix(day)

    # Format final string
    if include_year:
        formatted_date = f"{day}{suffix} {month}, {year}"
    else:
        formatted_date = f"{day}{suffix} {month}"

    return formatted_date


def format_time(input_time: str) -> str:
    # Parse the input time string
    time_obj = datetime.strptime(input_time, "%H:%M:%S")

    # Format to 12-hour time without leading zero
    formatted_time = time_obj.strftime("%I:%M %p").lstrip('0')

    # Add 'From' prefix
    return f"From {formatted_time} (1 Hour 30 Minutes + Sound Check)"


def number_to_words(num: int) -> str:
    units = [
        "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"
    ]
    tens = [
        "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
    ]

    def convert_integer(n: int) -> str:
        if n < 20:
            return units[n]
        if n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        if n < 1000:
            return units[n // 100] + " Hundred" + (" And " + convert_integer(n % 100) if n % 100 != 0 else "")
        if n < 100000:
            return convert_integer(n // 1000) + " Thousand" + (" " + convert_integer(n % 1000) if n % 1000 != 0 else "")
        if n < 10000000:
            return convert_integer(n // 100000) + " Lakh" + (" " + convert_integer(n % 100000) if n % 100000 != 0 else "")
        if n < 1000000000:
            return convert_integer(n // 10000000) + " Crore" + (" " + convert_integer(n % 10000000) if n % 10000000 != 0 else "")
        return convert_integer(n // 1000000000) + " Arab" + (" " + convert_integer(n % 1000000000) if n % 1000000000 != 0 else "")

    try:
        return "Rupees " + convert_integer(num) + " Only"
    except ValueError:
        return ""


def format_indian_number(number: int | str) -> str:
    if not number:
        return ""
    
    if isinstance(number, int):
        number = str(number)

    number = re.sub(r"[^\d]", "", number)  # Remove non-digits
    if not number:
        return ""
    
    if len(number) <= 3:
        return number
    
    else:
        last_three = number[-3:]
        rest = number[:-3]
        # Add commas after every 2 digits from the right
        parts = []
        while len(rest) > 2:
            parts.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.append(rest)
        parts.reverse()
        return ",".join(parts) + "," + last_three


def lighten_color(hex_color, amount=0.1):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = min(1.0, l + amount)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))