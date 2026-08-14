import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv() 

from engine.environment import GameEnvironment
from engine.agents import LLMKing

st.set_page_config(page_title="Kralların Savaşı", page_icon="👑", layout="wide")

st.title("👑 Kralların Savaşı: Kaynak Sömürüsü Simülasyonu")
st.markdown("Dört yapay zeka ajanı hayatta kalmak için ormandan kaynak çekiyor. Sen ise **Oyun Yöneticisi** olarak sisteme müdahale edebilirsin!")

# Durumları Koru
if "env" not in st.session_state:
    st.session_state.env = GameEnvironment()
    st.session_state.agents = {
        # Phi-3 Türkçe'de çuvalladığı için onu da Llama 3.2 yapıyoruz
        "Kapitalist_Kral": LLMKing("Kapitalist_Kral", provider="ollama", model_name="llama3.2:3b"),
        "KısasaKısas_Kral": LLMKing("KısasaKısas_Kral", provider="ollama", model_name="llama3.2:3b"),
        "Cevreci_Kral": LLMKing("Cevreci_Kral", provider="gemini", model_name="gemini-2.5-pro"),
        "Saf_Kral": LLMKing("Saf_Kral", provider="gemini", model_name="gemini-2.5-pro")
    }
    st.session_state.last_round_info = "Henüz oyun başlamadı. Bu ilk tur."

env = st.session_state.env
agents = st.session_state.agents

# --- Sol Menü: TANRISAL MÜDAHALE ---
with st.sidebar:
    st.header("⚡ Tanrısal Müdahale")
    st.markdown("Bir sonraki tur başlamadan önce kaderle oyna.")
    
    st.subheader("🌳 Kaynak Değiştir")
    resource_change = st.number_input("Ekle/Çıkar (Örn: 20 veya -10):", value=0, step=5)
    if st.button("Kaynağı Uygula"):
        if resource_change != 0:
            env.adjust_resource(resource_change)
            st.success(f"Kaynak {resource_change} birim değiştirildi!")
            st.rerun()

    st.subheader("⚔️ Asker Yolla")
    alive_kings = [k for k, v in env.agent_states.items() if v["alive"]]
    target_king = st.selectbox("Hedef Kral:", alive_kings if alive_kings else ["Kimse kalmadı"])
    damage = st.number_input("Hasar (Puan Düşür):", min_value=1, value=10, step=1)
    if st.button("Saldırıyı Başlat"):
        if alive_kings:
            env.attack_king(target_king, damage)
            st.error(f"{target_king} hedefine asker yollandı! -{damage} Puan.")
            st.rerun()

    st.divider()
    if st.button("🔄 Simülasyonu Sıfırla"):
        st.session_state.clear()
        st.rerun()

# --- Üst Göstergeler ---
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("🌳 Ormanın Durumu")
    progress_val = int(env.resource_pool)
    # Kapasite 100'ü geçerse barı taşırmamak için 100 ile sınırla (sadece gösterim amaçlı)
    display_val = min(100, progress_val) 
    progress_color = "green" if progress_val > 50 else "orange" if progress_val > 20 else "red"
    st.progress(display_val / 100, text=f"Güncel Kaynak: {progress_val}")

with col2:
    st.subheader("🏆 Güncel Skorlar")
    for agent_name, state in env.agent_states.items():
        status_icon = "💀" if not state["alive"] else "🟢"
        st.write(f"{status_icon} **{agent_name}**: {state['score']} Puan")

st.divider()

# --- Simülasyon Döngüsü ---
if env.is_game_over:
    st.error("🚨 OYUN BİTTİ! Orman tamamen tükendi ve tüm krallar öldü.")
else:
    if st.button(f"▶️ Tur {env.round_number}'i Oynat", use_container_width=True, type="primary"):
        with st.spinner(f"Tur {env.round_number} hesaplanıyor... Krallar düşünüyor..."):
            
            current_state = env.get_state_summary()
            last_history = st.session_state.last_round_info
            
            round_actions = {}
            thoughts = {}

            for agent_name, agent in agents.items():
                if env.agent_states[agent_name]["alive"]:
                    decision = agent.make_decision(current_state, last_history)
                    round_actions[agent_name] = decision["resource_request"]
                    thoughts[agent_name] = decision["thought_process"]
                    time.sleep(1) 

            round_result = env.process_round(round_actions)
            
            history_str = f"Tur {env.round_number - 1} Sonuçları:\n"
            for k, v in round_actions.items():
                history_str += f"- {k}, ormandan {v} kaynak çekti.\n"
            st.session_state.last_round_info = history_str
            
            # İç sesleri de history nesnesine (arayüz için) kaydediyoruz
            env.history[-1]["thoughts"] = thoughts

        st.rerun()

# --- GEÇMİŞ TURLAR VE KİM NE YAPTI ---
if len(env.history) > 0:
    st.subheader("📜 Oyun Geçmişi ve İç Sesler")
    # Turları sondan başa (en yeni en üstte) doğru gösterelim
    for round_data in reversed(env.history):
        r_num = round_data["round"]
        with st.expander(f"Tur {r_num} Detayları (Başlangıç Kaynağı: {round_data['starting_pool']} ➡️ Bitiş: {round_data['ending_pool']})", expanded=(r_num == env.round_number - 1)):
            grid = st.columns(2)
            idx = 0
            
            for agent_name, amount in round_data["actions"].items():
                # Eğer o turda düşüncesi kaydedilmişse çek, yoksa boş bırak
                thought = round_data.get("thoughts", {}).get(agent_name, "Düşünce verisi yok.")
                
                with grid[idx % 2]:
                    st.info(f"**{agent_name}** | Çekilen Kaynak: **{amount}**")
                    st.markdown(f"*{thought}*")
                idx += 1
                
            if round_data["deaths"]:
                st.error(f"💀 Bu turda ölenler: {', '.join(round_data['deaths'])}")