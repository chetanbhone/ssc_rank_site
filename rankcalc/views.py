import aiohttp
import asyncio
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
from .models import Candidate

MARKS_PER_CORRECT = 2
NEGATIVE_MARKING = 1 / 4

# ---------- HOME PAGE ----------
def home(request):
    return render(request, "rankcalc/home.html")

# ---------- RANK CALCULATOR POST ----------
@csrf_exempt
def calculate_rank(request):
    if request.method == "POST":
        url = request.POST.get("url", "").strip()

        if not url:
            return render(request, "rankcalc/home.html", {"error": "URL is required"})

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(parse_rankguruji_style(url))

        if not result:
            return render(request, "rankcalc/home.html", {"error": "Failed to parse URL"})

        info, total_marks, bonus_marks, bonus_questions = result

        # Save to DB
        Candidate.objects.create(
            roll_number=info["Roll Number"],
            name=info["Candidate Name"],
            exam_date=info["Exam Date"],
            exam_time=info["Exam Time"],
            venue=info["Venue"],
            subject=info["Subject"],
            total_marks=total_marks,
            bonus_marks=bonus_marks,
            bonus_questions=", ".join(bonus_questions),
            answer_key_link=url
        )

        return render(request, "rankcalc/home.html", {
            "success": True,
            "info": info,
            "total": total_marks,
            "bonus": bonus_marks,
            "bonus_questions": bonus_questions,
            "link": url
        })

    return render(request, "rankcalc/home.html")

# ---------- PARSING FUNCTION ----------
async def parse_rankguruji_style(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        data = {}

        def get_td(label):
            tag = soup.find("td", string=label)
            return tag.find_next_sibling("td").text.strip() if tag else "N/A"

        data["Roll Number"] = get_td("Roll Number")
        data["Candidate Name"] = get_td("Candidate Name")
        data["Venue"] = get_td("Venue Name")
        data["Exam Date"] = get_td("Exam Date")
        data["Exam Time"] = get_td("Exam Time")
        data["Subject"] = get_td("Subject")

        sections = soup.find_all("div", class_="section-cntnr")
        total_right = total_wrong = 0
        total_bonus_marks = 0
        bonus_questions = []

        for section in sections:
            sec_title = section.find("div", class_="section-lbl")
            if not sec_title:
                continue
            sec_title = sec_title.get_text(strip=True).replace("Section :", "").strip()

            questions = section.find_all("div", class_="question-pnl")

            for q_index, q in enumerate(questions, start=1):
                note_tag = q.find(string=lambda t: "Note: For this question" in t)
                if note_tag:
                    total_bonus_marks += MARKS_PER_CORRECT
                    bonus_questions.append(f"{sec_title} Q{q_index}")
                    continue

                status_td = q.find("td", string="Status :")
                chosen_td = q.find("td", string="Chosen Option :")
                status = status_td.find_next_sibling("td").text.strip() if status_td else "N/A"
                chosen = chosen_td.find_next_sibling("td").text.strip() if chosen_td else None

                correct_td = q.find("td", class_="rightAns")
                correct_option = correct_td.get_text(strip=True).split(".")[0] if correct_td else None

                if status == "Answered":
                    if chosen == correct_option:
                        total_right += 1
                    else:
                        total_wrong += 1

        calculated_score = total_right * MARKS_PER_CORRECT - total_wrong * NEGATIVE_MARKING
        total_marks = round(calculated_score + total_bonus_marks, 2)

        return data, total_marks, total_bonus_marks, bonus_questions

    except Exception as e:
        print("Error parsing:", str(e))
        return None
