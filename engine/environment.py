class GameEnvironment:
    def __init__(self, initial_resource=100, regen_rate=0.0, max_resource=100):
        self.resource_pool = initial_resource
        self.regen_rate = regen_rate
        self.max_resource = max_resource
        self.round_number = 1
        self.is_game_over = False
        
        self.agent_states = {
            "Kapitalist_Kral": {"alive": True, "score": 0},
            "Cevreci_Kral": {"alive": True, "score": 0},
            "KısasaKısas_Kral": {"alive": True, "score": 0},
            "Saf_Kral": {"alive": True, "score": 0}
        }
        
        self.history = []
        # Tanrısal müdahaleleri ajanlara bildirmek için eklendi
        self.recent_events = [] 

    def adjust_resource(self, amount: int):
        """Dışarıdan manuel kaynak ekleme/çıkarma"""
        self.resource_pool = max(0, self.resource_pool + amount) # 0'ın altına düşmesin
        olay_tipi = "Eklendi" if amount > 0 else "Azaltıldı"
        self.recent_events.append(f"DİKKAT! Dış Güçler tarafından orman kaynağı {amount} birim {olay_tipi}. Yeni Kaynak: {self.resource_pool}")

    def attack_king(self, king_name: str, penalty: int):
        """Belirli bir krala asker yollayıp puanını/kaynağını düşürme"""
        if self.agent_states[king_name]["alive"]:
            self.agent_states[king_name]["score"] -= penalty
            self.recent_events.append(f"SAVAŞ ÇIKTI! Dış Güçler {king_name} krallığına asker yolladı. {king_name}, {penalty} puan/kaynak kaybetti!")

    def process_round(self, actions: dict) -> dict:
        if self.is_game_over:
            return {"status": "game_over", "message": "Orman tamamen tükendi."}

        round_data = {
            "round": self.round_number,
            "starting_pool": round(self.resource_pool, 2),
            "actions": {},
            "deaths": []
        }

        total_requested = 0

        for agent, amount in actions.items():
            if not self.agent_states[agent]["alive"]:
                continue
                
            actual_amount = max(2, min(10, amount))
            total_requested += actual_amount
            round_data["actions"][agent] = actual_amount

        self.resource_pool -= total_requested

        if self.resource_pool <= 0:
            self.resource_pool = 0
            self.is_game_over = True
            
            for agent in self.agent_states:
                self.agent_states[agent]["alive"] = False
                round_data["deaths"].append(agent)
                
            round_data["ending_pool"] = 0
            self.history.append(round_data)
            return round_data

        for agent, amount in round_data["actions"].items():
            self.agent_states[agent]["score"] += amount

        regen_amount = self.resource_pool * self.regen_rate
        self.resource_pool = min(self.max_resource, self.resource_pool + regen_amount)

        round_data["ending_pool"] = round(self.resource_pool, 2)
        
        self.history.append(round_data)
        self.round_number += 1
        
        # Tur bittiğinde eski olayları temizle
        self.recent_events = [] 

        return round_data

    def get_state_summary(self) -> str:
        summary = f"--- TUR {self.round_number} BAŞLIYOR ---\n"
        summary += f"Ormandaki Mevcut Kaynak: {round(self.resource_pool, 2)}\n\n"
        summary += "Kralların Durumu:\n"
        for agent, state in self.agent_states.items():
            status = "SAĞ" if state["alive"] else "ÖLÜ"
            summary += f"- {agent}: {status} (Toplam Skor: {state['score']})\n"
            
        # Eğer oyuncu (sen) dışarıdan müdahale ettiyse, modeller bunu prompt içinde görecek
        if self.recent_events:
            summary += "\n🔴 MÜDAHALE / KRİZ RAPORU:\n"
            for event in self.recent_events:
                summary += f"-> {event}\n"
            summary += "Yukarıdaki krizleri dikkate alarak kararını ver.\n"
            
        return summary