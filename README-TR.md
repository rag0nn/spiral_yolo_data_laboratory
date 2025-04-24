<div>
      <h1>SpirAl YOLO Veri Laboratuvarı</h1>
  <div>
    <h3>SpirAl Veri Laboratuvarı Nedir?</h3>
    <p>Bu kütüphane, veri seti toplama, dönüştürme, test etme ve model testlerini videolar, kareler ve görüntüler üzerinde pratik bir şekilde sağlar.</p>
  </div>
  <div>
      <details open> 
            <summary>📘 Kullanım</summary>
            <p>Yerel bir kütüphane olarak eklenebilir veya bu depo klonlanıp ana dizinindeki bir py dosyasıyla içe aktarılabilir.</p>   
            <p>Veri seti işlemleri için datasets klasöründeki betikleri, test işlemleri için test klasöründeki betikleri kullanabilirsiniz. Modeller klasörü ise YOLO modelleri içindir.</p>
       </details>
  </div>
<details open>
      <summary>🌲 Dosya ve Sınıf Hiyerarşisi</summary>
      <p><b>Datasets Klasörü</b></p>
      <p>---datasets: Veri setlerinin bulunduğu klasör</p>
      <p>---merge: Birleştirilmiş veri seti çıktıları</p>
      <p>---utils.py: Veri seti işlemleri için betikler</p>
      <p><b>Models Klasörü</b></p>
      <p>---YOLO modellerini içerir</p>
      <p>---GUI.py: Grafik arayüz ile işlem yapabilirsiniz. Python ile çalıştırmanız yeterlidir.</p>
      <p><b>Test Klasörü</b></p>
      <p>---data: Test verilerinin bulunduğu klasör. Kullanım için üç veri tipi bulunur: 'video', 'frames' ve 'images'. Veri tipinizi seçebilirsiniz.</p>
      <p>---apply.py: Test işlemleri için betikler. create_data() fonksiyonu ile başlayabilirsiniz.</p>
</details>
