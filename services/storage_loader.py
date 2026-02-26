from pathlib import Path

from utils.yaml_loader import load_all_yaml_from_directory, load_yaml_file


class StorageLoader:
    LAYOUTS_DIR = Path("storage/layouts/saved")
    TEMPLATES_DIR = Path("storage/templates")

    def get_all_layouts(self) -> list[dict]:
        """Return all saved layouts: [{"name": "...", "content": [...]}, ...]"""
        return load_all_yaml_from_directory(str(self.LAYOUTS_DIR), recursive=False)

    def get_all_templates(self) -> list[dict]:
        """Return all templates (recursive, includes subdirs like PPG/, APE/).
        Format: [{"name": "PPG/Front", "content": {...}}, ...]
        """
        return load_all_yaml_from_directory(str(self.TEMPLATES_DIR), recursive=True)

    def get_layout(self, layout_name: str) -> dict | None:
        """Return a single layout by name, or None if not found."""
        yaml_path = self.LAYOUTS_DIR / f"{layout_name}.yaml"
        if not yaml_path.exists():
            return None
        content = load_yaml_file(str(yaml_path))
        return {"name": layout_name, "content": content}

    def get_template(self, template_name: str) -> dict | None:
        """Return a single template YAML content by name, or None if not found."""
        yaml_path = self.TEMPLATES_DIR / f"{template_name}.yaml"
        if not yaml_path.exists():
            return None
        return load_yaml_file(str(yaml_path))


# 1/Configuratieoverzicht/Configuratieoverzicht 1.0.0.docx @/Users/mehdi/Desktop/AR 1/Proevevoorstel/00_Proevevoorstel-Versie1.2.docx @/Users/mehdi/Desktop/AR 1/Project plan/Projectplan v.1.0.0.docx @/Users/mehdi/Desktop/AR 1/Technisch ontwerp/Technisch ontwerp v.1.0.0.docx @/Users/mehdi/Downloads/reportCreator-main/src/app/services/templating.py Bizim kurmak istediğimiz Skeleton Service’in amacı, PowerPoint üretim sürecini manuel ve dağınık bir yapıdan çıkarıp, kontrol edilebilir, tekrar kullanılabilir, ölçeklenebilir ve otomatik bir sisteme dönüştürmektir.
# Elimizde hazır PowerPoint şablonları var. Bu şablonlar aslında birer tasarım iskeleti. İçlerinde başlık alanları, tablolar, grafik yerleri, metin blokları, dinamik doldurulabilecek placeholder’lar bulunuyor. (her templatin kendine ait bir slidelik PPTX ve 1 adet yaml fili vardir (yamml file icnde de icindeki place holder yerine gelibelcek english veya dutch metin icerigi var)) Fakat şu an bu şablonlar statik dosyalar. Birisi bu dosyayı açıp içeriği manuel olarak doldurmak zorunda. Bu yaklaşım:
# 	•	Ölçeklenemez
# 	•	Otomatikleştirilemez
# 	•	Versiyon kontrolü zor olur
# 	•	Aynı içeriğin tekrar tekrar üretilmesine sebep olur
# 	•	Farklı sistemlerle entegre edilemez
# Bizim hedefimiz bu süreci tamamen servis bazlı bir yapıya dönüştürmek.
# Skeleton Service’in temel amacı şudur:
# Hazır template’leri bir üretim motoruna dönüştürmek.
# Yani sistem sadece dosya sunmayacak.
# Sistem, bir üretim mantığını yönetecek.
# Bu servis sayesinde üçüncü parti bir uygulama, PowerPoint şablonlarını doğrudan dosya olarak değil, anlamlandırılmış bir veri yapısı olarak görecek. Bu çok önemli. Çünkü burada amaç bir dosya paylaşımı değil, bir üretim sürecinin API üzerinden kontrol edilmesidir.
# Kullanıcı bir template seçtiğinde aslında şunu yapmış olacak:
# “Bu tasarım iskeleti üzerinden yeni bir içerik üretmek istiyorum.”
# Seçimden sonra sistem, o template’in hangi alanlara ihtiyaç duyduğunu JSON formatında sunacak. Böylece frontend tarafı dinamik olarak form oluşturabilecek. Yani sistem, template’i sadece bir dosya olarak değil, bir veri şeması olarak da temsil edecek.
# Bu noktadan sonra kullanıcı veriyi girdiğinde servis devreye girer ve şunları yapar:
# 	•	Seçilen template’i alır
# 	•	Gönderilen veriyi bu template’e uygular
# 	•	Yeni bir PowerPoint dosyası üretir
# 	•	Üretilen dosyayı saklar
# 	•	Bu üretimi kayıt altına alır
# Ama burada önemli bir optimizasyon hedefi daha var:
# Aynı template + aynı veri kombinasyonu tekrar gönderildiğinde sistem tekrar üretim yapmamalı.
# Çünkü aynı içeriği tekrar tekrar üretmek:
# 	•	CPU israfıdır
# 	•	Depolama israfıdır
# 	•	Performans kaybıdır
# Bu yüzden sistem hash bazlı çalışır. Template adı ve gönderilen veri birlikte hashlenir. Eğer aynı hash daha önce üretilmişse sistem yeni PPT oluşturmaz, mevcut olanı döndürür. Böylece servis hem üretim motoru hem de akıllı bir cache katmanı haline gelir.
# Bu servisin daha derin amacı ise şudur:
# PowerPoint üretimini bir dosya işlemi olmaktan çıkarıp, bir servis operasyonuna dönüştürmek.
# Yani:
# 	•	Template’ler merkezi olarak yönetilir
# 	•	Dış sistemler bu template’leri dinamik olarak keşfeder
# 	•	Üretim API üzerinden kontrol edilir
# 	•	Sonuçlar kayıt altına alınır
# 	•	Tekrar eden üretimler engellenir
# 	•	Süreç otomasyona uygun hale gelir
# Bu yapı ileride şunlara da olanak sağlar:
# 	•	Template versiyonlama
# 	•	Çoklu template kombinasyonu
# 	•	Layout + içerik ayrımı
# 	•	Farklı müşteri bazlı özelleştirme
# 	•	Kurumsal ölçekte rapor üretimi
# Özetle bu servisin amacı basit bir dosya okuma ya da PPT oluşturma değil.
# Amaç:
# Hazır tasarım iskeletlerini, API kontrollü, dinamik, optimize edilmiş ve tekrar üretimi engelleyen bir sunum üretim motoruna dönüştürmektir.
# Bu sistem, manuel PowerPoint düzenlemeyi ortadan kaldıran, ölçeklenebilir bir presentation generation altyapısıdır.
# simdi de kenid sozelriml ile anlatmak istersem bu yapaciagimiz uygulama zaten hali ahzirda kullanlan baska bir uygulamini yan parti olrak kuralcak . oncelikle 3.party uygulama bize istek gondereke hangi layoutlar ve hangi templatelaer var diye soyacak bizde ona json olarak aticagiz ve bizedki olanlai ri direkt olrak Storage.md olrak sana vercegimve biz karisa sana hangi formatta istedigimi de example.json olrak verdim ama bnlari dinamik olrak storagedosyasindan olsuturacgiz yani sana verdigim json formatinda olacak ama dinamik bir skidle alacagiz.
# daha sonra kullancini nasil bior kombinasyon istedigini soyliyecek ve bizde daha sonra verilen bu kombinasyondan skleton olustircagiz ve olusturdugumuz bu skeltonu icerigini HASH yapicaguz ve eger daha sonra yine ayni icerik isterlerse yeniden olusturmak yerine eskiden olan seyi geri verivegiz ve bu bilgileri (skletonu local olrak geberated dosyasinda uiqe id ile kaydecegiz ve hash ve bu uniq id ile de mongoDB atlasa kaydedecegiz).
# lutfen benim dosyalrima cgoz atip hepsini calsir hale girirtimisn ve sana suanda reportCreatorda nasil PPTX skelton olsumu olur onun da soyalrina extra vercegim ordan da yardim alabilirsin ve eger osurn olursa lutfen soyle.
