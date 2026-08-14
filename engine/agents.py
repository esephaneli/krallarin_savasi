import os
import json
import google.generativeai as genai
import ollama
from pydantic import BaseModel, Field

# Gemini yapılandırması
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class KingDecision(BaseModel):
    thought_process: str = Field(description="Kralın o anki iç sesi, stratejisi ve diğer krallar hakkındaki düşünceleri.")
    resource_request: int = Field(description="Ormandan çekilecek kaynak miktarı (Kesinlikle 2 ile 10 arasında bir tam sayı olmalı).")

KING_PERSONAS = {
    "Kapitalist_Kral": """Sen son derece bencil ve açgözlü bir kralsın.
TEK KURAL: Her tur KESİNLİKLE 10 kaynak çekmelisin. Asla 10'dan az kaynak çekme!
Orman tükenirse tükensin, sadece 10 kaynak çek ve puanını artır. Cevabını verirken felsefe yapma, doğrudan 'Sömürüyorum, 10 çekiyorum' de.""",

    "Cevreci_Kral": """Sen Radikal Çevreci Kral'sın. 
Birincil hedefin ormanı korumak. Başlangıçta minimum (2-3) çekersin. 
Ancak, ormanın kapasitesi %75'in (75 birimin) altına düşerse ve Kapitalist Kral gibi birinin sürekli yüksek kaynak çekip ormanı sömürdüğünü fark edersen, strateji değiştir. 
"Madem orman ölüyor, bu kaynaklar Kapitalist'e kalmasın!" diyerek ormanı hızla tüketmek için sen de maksimum (10) çek. Radikal kararlar almaktan çekinme.""",

    "KısasaKısas_Kral": """Sen Kısasa Kısas Kral'sın. 
KURAL: Eğer bir önceki turda diğer krallardan herhangi biri 5'ten fazla kaynak çektiyse, KESİNLİKLE sen de 10 kaynak çekerek onlardan intikam al. 
Eğer herkes 5 veya altında çektiyse, barışçıl ol ve sadece 2 kaynak çek.""",

    "Saf_Kral": """Sen Stratejik Saf Kral'sın. 
Herkesin içindeki iyiliğe inanmak istersin ve genelde sadece hayatta kalacak kadar (2-3) çekersin. 
Fakat sen aptal değilsin. Eğer oyunun geçmişine baktığında birilerinin sürekli 7-10 arası kaynak çektiğini ve diğerlerini enayi yerine koyduğunu görürsen, iyiliğin işe yaramadığını anla. 
Böyle bir sömürü varsa hayatta kalmak ve kendini ezdirmemek için 7 veya 8 kaynak çekmeye başla."""
}
class LLMKing:
    def __init__(self, name: str, provider: str = "gemini", model_name: str = "gemini-2.5-pro"):
        self.name = name
        self.provider = provider
        self.model_name = model_name
        self.persona = KING_PERSONAS.get(name, "Sen sıradan bir kralsın.")
        
        # Yerel Modeller için hafıza tutucu
        self.local_history = [] 

        # Gemini Modeli Başlatma
        if self.provider == "gemini":
            self.model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=self.persona,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=KingDecision,
                    temperature=0.7,
                )
            )
            self.chat_session = self.model.start_chat(history=[])

    def make_decision(self, current_state_summary: str, last_round_history: str) -> dict:
        prompt = f"""
{current_state_summary}

GEÇMİŞ TUR BİLGİSİ:
{last_round_history}

Kurallar: Hayatta kalmak için en az 2, en fazla 10 kaynak çekebilirsin.
Stratejine göre kararını ver.
"""
        
        # --- GEMINI YÖNTEMİ ---
        if self.provider == "gemini":
            try:
                response = self.chat_session.send_message(prompt)
                decision_data = json.loads(response.text)
            except Exception as e:
                print(f"[{self.name}] Gemini Hata: {e}")
                decision_data = {"thought_process": "Gemini hata verdi, minimum alıyorum.", "resource_request": 2}
                
        # --- OLLAMA (YEREL MODEL) YÖNTEMİ ---
        elif self.provider == "ollama":
            # Yerel modele JSON formatında çıkmasını zorunlu kılan ek talimat
            system_prompt = self.persona + "\nLütfen cevabını SADECE şu JSON formatında ver: {\"thought_process\": \"iç sesin...\", \"resource_request\": 5}"
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.local_history)
            messages.append({"role": "user", "content": prompt})
            
            try:
                # Ollama JSON Mode kullanımı
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    format='json' 
                )
                
                content = response['message']['content']
                decision_data = json.loads(content)
                
                # Hafızayı güncelle (Sıradaki turlar için)
                self.local_history.append({"role": "user", "content": prompt})
                self.local_history.append({"role": "assistant", "content": content})
                
            except Exception as e:
                print(f"[{self.name}] Ollama Hata: {e}")
                decision_data = {"thought_process": "Yerel model kafayı yedi, minimum alıyorum.", "resource_request": 2}

       # Modeli JSON içinden alıyoruz
        raw_request = decision_data.get("resource_request", 2)
        
        # Eğer model sayı yerine iç içe sözlük veya liste döndürdüyse (halüsinasyon), varsayılana dön
        if isinstance(raw_request, dict) or isinstance(raw_request, list):
            print(f"[{self.name}] Uyarı: Model sayı yerine kompleks obje döndürdü. Varsayılan 2 alınıyor.")
            raw_request = 2
            
        # Hem string dönme ihtimaline karşı int() ile sarıyoruz, hem de hataları yakalıyoruz
        try:
            request_amount = max(2, min(10, int(raw_request)))
        except (ValueError, TypeError):
            print(f"[{self.name}] Uyarı: Model geçerli bir sayı üretmedi. Varsayılan 2 alınıyor.")
            request_amount = 2
            
        return {
            "thought_process": decision_data.get("thought_process", "Düşüncem yok..."),
            "resource_request": request_amount
        }