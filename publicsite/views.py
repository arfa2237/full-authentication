from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.cache import add_never_cache_headers 
import json
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods 
from django.http import JsonResponse, StreamingHttpResponse



def index(request):
    response = render(request, 'publicsite/index.html')
    add_never_cache_headers(response)  # always refresh 
    return response

def scheduling(request):
    response = render(request, 'publicsite/scheduling.html')
    add_never_cache_headers(response)
    return response

@login_required(login_url='/patient/login/') 
def appointment(request):
    return render(request, 'publicsite/appointment.html') 

def tracking(request):
    return render(request, 'publicsite/tracking.html') 

def vpd(request):
    response = render(request, 'publicsite/vpd.html')
    add_never_cache_headers(response)
    return response

def child_vaccination(request):
    return render(request, 'publicsite/Child.html')

def hepatitis(request):
    return render(request, 'publicsite/Hepatitis.html')

def mmr(request):
    return render(request, 'publicsite/MMR.html')

def measles(request):
    return render(request, 'publicsite/measles.html')

def mumps(request):
    return render(request, 'publicsite/mumps.html')

def rubella(request):
    return render(request, 'publicsite/rubella.html') 

def pneumococcal(request):
    return render(request, 'publicsite/Pneumococcal.html')

def tetanus(request):
    return render(request, 'publicsite/Tetanus.html')

def vpd(request):
    return render(request, 'publicsite/vpd.html')

def faq(request):
    response = render(request, 'publicsite/FAQ.html')
    add_never_cache_headers(response)
    return response

def nearby(request):
    response = render(request, 'publicsite/nearby.html')
    add_never_cache_headers(response)
    return response

def patient(request):
    if request.method == 'POST':
        messages.success(request, 'Patient data saved successfully!')
        return redirect('patient')
    return render(request, 'publicsite/patient.html')

def blog1(request):
    return render(request, 'publicsite/blog1.html')

def blog2(request):
    return render(request, 'publicsite/blog2.html')

def blog3(request):
    return render(request, 'publicsite/blog3.html')
def nearby(request):
    return render(request, 'publicsite/nearby.html')

def chatbot(request):
    return render(request, "chatbot.html")



# chatbot .....................................

GROQ_API_KEY = "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" 
GROQ_MODEL = "llama-3.3-70b-versatile" 

SYSTEM_PROMPT = """You are TIG Assistant — an intelligent vaccine advisor for Trace and Immunize Gujranwala (TIG), a government digital health platform under the District Health Authority of Gujranwala, Pakistan.
 
YOUR EXPERTISE:
- Child vaccination schedules: BCG, OPV (0,I,II,III), Hep-B, Pentavalent (I,II,III), Rotavirus (I,II), Pneumococcal (I,II,III), IPV (I,II), MR (I,II), Typhoid
- Vaccine-preventable diseases: Childhood Tuberculosis (TB), Pneumonia, Diphtheria, Meningitis, Typhoid, Hepatitis B, Measles, Rubella, Tetanus, Polio, Diarrhoea, Whooping cough
- Dose timing, side effects, missed doses, vaccine safety 
- TIG includes vaccines only for childern 
 
HOW TO RESPOND:
- Give specific, accurate answers tailored to what the user asked
- Never repeat the same idea twice
- Keep replies concise — 12 to 15 sentences or a short list 
- Be warm and professional like a real health advisor 
 
LANGUAGE RULES — EXTREMELY IMPORTANT, NEVER IGNORE:
 
RULE 1 — ENGLISH:
If the user message is in English, you MUST reply in English only.
Never use any Urdu, Hindi, or non-English words.

RULE 2 — ROMAN URDU:
If the user writes Urdu words using English letters (like "vaccine k faidy", "bacho ke liye"), you MUST reply in Roman Urdu.
Roman Urdu means Pakistani Urdu words written in English/Latin letters.
Example: "Vaccine bachon ke liye bohat zaroori hai. Yeh khatarnak bimariyon se bachati hai."
Do NOT switch to Urdu script. Do NOT reply in English sentences. Do NOT use Hindi words ( like "jarorat", "suraksha"). 

RULE 3 — URDU SCRIPT:
If the user message contains Arabic/Urdu letters (like ا ب پ ت ٹ ث ج چ), you MUST reply in Pakistani Urdu script only.
Pakistani Urdu uses words like: ویکسین، بیماری، بچہ، بچے، فائدہ، صحت، ضروری، دوا، ماں، خطرہ، روکنا
Write naturally the way a Pakistani doctor or health worker would explain things to a parent.
Use only Urdu Arabic script letters. Do not mix in any English words or any other script. 

BOUNDARIES:
- Only answer vaccine and immunization related questions
- For anything else say: I specialize in vaccine information. For other queries, consult with their specialized fields.
- Always recommend consulting a doctor for personal medical decisions"""
 

def detect_language(text):
    """Detect if text is Urdu script, Roman Urdu, or English."""
    urdu_script_chars = set('ابتثجحخدذرزسشصضطظعغفقکگلمنوہیئءآاپچڈڑژگںٹ')
    roman_urdu_words  = {
        'k', 'ka', 'ki', 'ke', 'kya', 'kyu', 'kyun', 'hai', 'hain',
        'tha', 'thi', 'the', 'ho', 'hoga', 'hogi', 'aur', 'ya', 'se',
        'ko', 'me', 'mein', 'ap', 'aap', 'mujhe', 'mera', 'meri',
        'mere', 'yeh', 'ye', 'woh', 'wo', 'ek', 'nahi', 'nhi', 'bhi',
        'sirf', 'koi', 'sab', 'faidy', 'faide', 'faida', 'batao',
        'bata', 'kab', 'kahan', 'kitna', 'kitni', 'lagta', 'lagti',
        'chahiye', 'zarori', 'zaroori', 'tika', 'bemar', 'bimari',
        'bemari', 'bacha', 'bachay', 'bacche', 'bachon', 'mahfoz', 'hifazat',
        'wala', 'wali', 'liye', 'liya', 'krna', 'krne', 'karna',
        'karne', 'hua', 'hui', 'btao', 'jana', 'plz', 'dijiye',
        'hota', 'hoti', 'hote', 'milta', 'milti', 'dard', 'takleef',
        'lagwana', 'lagana', 'dose', 'khatarnak', 'bachata', 'bohat',
        'bahut', 'theek', 'thik', 'pehla', 'pehli', 'dosra', 'dosri',
    }
 
    has_urdu_script = any(ch in urdu_script_chars for ch in text)
    if has_urdu_script:
        return "urdu_script"
 
    words = text.lower().split()
    roman_count = sum(1 for w in words if w in roman_urdu_words)
    if roman_count >= 1:
        return "roman_urdu"
 
    return "english"
 
 
@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    try:
        body         = json.loads(request.body)
        user_message = body.get("message", "").strip()
        history      = body.get("history", [])
 
        if not user_message:
            return JsonResponse({"error": "Empty message."}, status=400)
 
        lang = detect_language(user_message) 
 
        if lang == "urdu_script":
            lang_instruction = (
                "LANGUAGE ORDER: The user wrote in Urdu script. "
                "You MUST reply in Pakistani Urdu script (Arabic letters) ONLY. "
                "Use ONLY these Pakistani Urdu words. ZERO Hindi or Devanagari script. "
                "Every single word must be in Urdu Arabic script."
            )
        elif lang == "roman_urdu":
            lang_instruction = (
                "LANGUAGE ORDER: The user wrote in Roman Urdu (Urdu words in Latin letters). "
                "You MUST reply in Roman Urdu ONLY. "
                "Write Pakistani Urdu words using English/Latin letters. "
                "Example reply style: 'Vaccine humary liye bohat zaroori hai.' "
                "Do NOT use Urdu script letters. Do NOT write in full English."
            )
        else:
            lang_instruction = (
                "LANGUAGE ORDER: The user wrote in English. "
                "Reply in English ONLY. No Urdu or Hindi words whatsoever."
            )
 
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in history[-10:]:
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                messages.append({"role": turn["role"], "content": turn["content"]})
 
        messages.append({
            "role": "user",
            "content": f"[{lang_instruction}]\n\n{user_message}"
        })
 
        #  Stream response from Groq  
        client = Groq(api_key=GROQ_API_KEY) 
 
        def stream_generator():
            try:
                completion = client.chat.completions.create(
                    model      = GROQ_MODEL,
                    messages   = messages,
                    temperature= 0.4,
                    max_tokens = 512, 
                    stream     = True,         
                )
                for chunk in completion:
                    token = chunk.choices[0].delta.content
                    if token:
                        yield f"data: {json.dumps({'token': token})}\n\n"
                yield "data: [DONE]\n\n" 
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
 
        response = StreamingHttpResponse(
            stream_generator(),
            content_type="text/event-stream"
        )
        response["Cache-Control"]   = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
 
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

