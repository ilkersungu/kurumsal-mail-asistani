import streamlit as st
from huggingface_hub import InferenceClient

# --- 1. AYARLAR ---
# Hugging Face token'ını buraya yapıştır:
HF_TOKEN = st.secrets["HF_TOKEN"]
repo_id = "Qwen/Qwen2.5-7B-Instruct"
client = InferenceClient(model=repo_id, token=HF_TOKEN)

# --- 2. SAYFA YAPISI VE GÖRSELLİK ---
st.set_page_config(
    page_title="Kurumsal Asistan Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. GENİŞLETİLMİŞ VERİTABANI (Senaryolar) ---
sirket_senaryolari = {
    "👥 İnsan Kaynakları (İK)": [
        "Yıllık izin talebi", "Mazeret izni", "Maaş zammı/Promosyon talebi", 
        "İstifa dilekçesi", "Mobbing bildirimi", "Personel alım duyurusu", 
        "Eğitim talebi", "Bordro hatası", "Referans mektubu isteği"
    ],
    "💻 Bilgi İşlem (IT)": [
        "Bilgisayar/Donanım çok yavaş", "İnternet bağlantı sorunu", "VPN/Uzak erişim yetkisi", 
        "Lisans/Program satın alma talebi", "Siber güvenlik şüphesi", "Şifremi unuttum",
        "Yazıcı arızası", "Yeni monitör/ekipman talebi"
    ],
    "💰 Muhasebe & Finans": [
        "Maaş ödemesi gelmedi", "Avans talebi", "Masraf formu teslimi", 
        "Fatura onay süreci", "Yol/Yemek ücreti eksikliği", "Cari hesap mutabakatı",
        "Bütçe aşımı uyarısı"
    ],
    "🤝 Satış & Pazarlama": [
        "Müşteri toplantı özeti", "Yeni kampanya duyurusu", "Fiyat teklifi (Resmi)", 
        "Müşteri şikayeti yanıtlama", "Aylık satış raporu sunumu", "Bayram/Özel gün tebriği",
        "Sponsorluk talebi"
    ],
    "⚖️ Hukuk & Sözleşmeler": [
        "Sözleşme taslağı inceleme", "Gizlilik sözleşmesi (NDA) talebi", 
        "Telif hakkı ihlali uyarısı", "Resmi ihtarname taslağı"
    ],
    "📦 Lojistik & Depo": [
        "Stok yetersizliği uyarısı", "Sevkiyat gecikmesi bildirimi", 
        "Hasarlı ürün tutanağı", "Araç tahsis talebi"
    ],
    "🏢 İdari İşler & Genel": [
        "Ofis temizliği/Hijyen sorunu", "Klima/Isıtma arızası", "Servis aracı saat değişikliği", 
        "Yemekhane menüsü şikayeti", "Otopark sorunu", "Genel şirket duyurusu"
    ]
}

# --- 4. SOL MENÜ (Kişisel Ayarlar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=100)
    st.header("👤 Gönderen Bilgileri")
    st.info("Bu bilgiler imza kısmına otomatik eklenir.")
    
    gonderen_ad = st.text_input("Adınız Soyadınız", placeholder="Örn: İlker Yılmaz")
    unvan = st.text_input("Unvanınız", placeholder="Örn: Proje Yöneticisi")
    sirket_adi = st.text_input("Şirket Adı", placeholder="Örn: Yılmaz Teknoloji A.Ş.")
    
    st.markdown("---")
    st.header("🎨 Üslup Ayarı")
    ton = st.select_slider(
        "Mailin dili nasıl olsun?",
        options=["Çok Resmi", "Standart Kurumsal", "Nazik ve Ilımlı", "Net ve Sert", "Arkadaşça (Şirket İçi)"],
        value="Standart Kurumsal"
    )

# --- 5. ANA EKRAN ---
st.title("🏢 Kurumsal İletişim Asistanı v3.0")
st.markdown(f"Merhaba **{gonderen_ad if gonderen_ad else 'Misafir'}**, bugün ne yazmak istiyorsun?")

# Sekmeler (Tabs) ekliyoruz: İster Mail yazdır, İster Mesaj
tab1, tab2 = st.tabs(["📧 E-Posta Oluştur", "💬 Teams/Slack Mesajı"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        secilen_departman = st.selectbox("Departman Seç:", list(sirket_senaryolari.keys()))
        kime = st.text_input("Kime Gönderilecek (Alıcı):", placeholder="Örn: İnsan Kaynakları Müdürü")
    with col2:
        secilen_konu = st.selectbox("Konu Seç:", sirket_senaryolari[secilen_departman])
        # Tarih seçici ekleyelim (Görsellik)
        tarih_var_mi = st.checkbox("Tarih belirtilecek mi?")
        tarih_detayi = ""
        if tarih_var_mi:
            tarih = st.date_input("İlgili Tarih:")
            tarih_detayi = f"Tarih: {tarih}"

    detaylar = st.text_area("✍️ Ekstra Detaylar (İsteğe bağlı):", 
                            placeholder="Örn: Konu çok acil, dönüş bekliyorum, ekte dosya var vb.", height=100)

    if st.button("🚀 Maili Oluştur", key="mail_btn", use_container_width=True):
        if not gonderen_ad or not sirket_adi:
            st.error("⚠️ Lütfen sol menüden Adınızı ve Şirket Adınızı girin! İmza için gerekli.")
        elif not kime:
            st.warning("⚠️ Lütfen alıcı ismini girin.")
        else:
            # Yapay Zeka Emri (Prompt)
            messages = [
                {
                    "role": "system",
                    "content": f"""Sen {sirket_adi} şirketinde çalışan {unvan} pozisyonundaki {gonderen_ad} isimli kişisin.
                    Görevin: '{ton}' bir üslupla Türkçe kurumsal e-posta yazmak.
                    
                    KURALLAR:
                    1. Asla [Şirket Adı] veya [Ad Soyad] gibi yer tutucu kullanma.
                    2. Sana verilen Şirket Adı: '{sirket_adi}' ve Gönderen Adı: '{gonderen_ad}' bilgilerini AYNEN kullan.
                    3. Başka bir şirket ismi uydurma.
                    4. Konu başlığı (Subject) yaz.
                    5. Sadece mail içeriğini ver."""
                },
                {
                    "role": "user",
                    "content": f"""
                    Alıcı: {kime}
                    Departman: {secilen_departman}
                    Konu: {secilen_konu}
                    Ekstra Detay: {detaylar} {tarih_detayi}
                    
                    Lütfen bu bilgilerle '{ton}' tonunda maili yaz."""
                }
            ]
            
            with st.spinner('Yapay zeka kelimeleri düzenliyor...'):
                try:
                    response = client.chat_completion(messages, max_tokens=800)
                    mail_metni = response.choices[0].message.content
                    st.success("✅ Mail Hazırlandı!")
                    st.text_area("Kopyalanabilir Metin:", value=mail_metni, height=500)
                except Exception as e:
                    st.error(f"Hata: {e}")

with tab2:
    st.write("Daha kısa, anlık mesajlaşma uygulamaları için metin oluşturur.")
    msg_konu = st.text_input("Mesajın Konusu:", placeholder="Örn: Toplantı gecikmesi")
    if st.button("💬 Kısa Mesaj Oluştur", key="msg_btn"):
        # Kısa mesaj için ayrı prompt
        prompt_msg = f"""Sen {gonderen_ad}. {kime} kişisine Teams/Slack üzerinden '{msg_konu}' hakkında kısa bir mesaj atıyorsun. 
        Üslup: {ton}. Şirket: {sirket_adi}.
        Kısa, net ve profesyonel bir mesaj yaz. Merhaba diyerek başla."""
        
        try:
             res = client.text_generation(prompt_msg, max_new_tokens=200)
             st.info("Kısa Mesaj Taslağı:")
             st.code(res, language="text")
        except:
            st.error("Bağlantı hatası.")