
"""
                                          İŞ PROBLEMİ
FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranış öbeklenmelerine göre gruplar oluşturulacak..


                                         VERİ SETİ HİKAYESİ
# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi
"""

                                             #GÖREVLER


                    # GÖREV 1: Veriyi Anlama (Data Understanding) ve Hazırlama

#Öncelikle kütüphanelerimizi import edelim.
import seaborn as sns
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
import matplotlib.pyplot as plt


df_ = pd.read_csv(r"C:\Users\sevim\Desktop\MIUUL\HAFTA 3\CASE STUDY-1\FLOMusteriSegmentasyonu\flo_data_20k.csv")
df = df_.copy()

#Veri Okuma ve İnceleme gerçekleştirelim.
df.head()

df.shape   #(19945, 12)   19945 adet müşteri idm ve 12 adet değişkenim var.

df.nunique()

df["master_id"].nunique() #master_id  19945 çıktı, tüm datam unique olduğunu anlıyorum, gruplama yapmama gerek yok.

df.info()
#burada değişkenlerin özelliklerini inceliyorum, date içeren değişkenlerim time olmasına rağmen object olduğunu fark ettim.

#Şimdi dataframeimin transpozunu alarak standart sapma, çeyreklik değerleri , ortalamaları ve max min değerlerini inceleyeceğim.
df.describe().T


#daha detaylı bir describe istiyorsam istediğim değerleri ben belirleyebilirim.
df.describe([0, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99, 1]).T
"""
Describea bakıldıgında "order_num_total_ever_online " değişkeninde %75 ve max değerleri arasında ciddi bir değer farkı
gözlemledim. Bunu grafiğe döktüğümde sağdan çarpık olduğunu gördüm ve bu değişkende outlier var dedik.
"""

for col in df.describe().columns:
    df.hist(column=col,bins=100)
    plt.title("Histogram"+" "+col)
    plt.show(block=True)


# Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir.
# Herbir müşterinin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

#Yeni bir değişken oluşturup online ve offline alışveriş sayısını ve ödediği toplam ücreti birleştireceğim.
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df.head()
#head atarak durumu gözlemledim.



# Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.
df.info()
#Daha önce de gözlemlediğimiz gibi tarih ifade eden değişkenlerimiz object formatta.type dönüşümü yapmamız gerek.
#Date iceren değişkenleri bul ve bu değişkenlere pd.to_datetime uygula dedik.
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()



# Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısı ve toplam harcamaların dağılımına bakınız.
df.groupby("order_channel").agg({"master_id":"count",
                                 "order_num_total":"sum",
                                 "customer_value_total":"sum"})
# 6. En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.
df.sort_values("customer_value_total", ascending=False)[:10]



# 7. En fazla siparişi veren ilk 10 müşteriyi sıralayınız. 3 farklı gösterimini de belirtiyorum.
df.sort_values("order_num_total", ascending=False)[:10]
df.sort_values("order_num_total", ascending=False).head(10)
df.nlargest(10,columns="order_num_total")




# 8. Veri ön hazırlık sürecini fonksiyonlaştırınız.
def data_prep(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
    return dataframe





                             # GÖREV 2: RFM Metriklerinin Hesaplanması


# Veri setindeki en son alışverişin yapıldığı tarihten 2 gün sonrasını analiz tarihi
#Bunu yapmamızın sebebi veri setinin eski oluşundan kaynaklanmaktadır. Günümüzü baz alınca veri setini
#yorumlarken yanılgıya düşebiliriz. O sebeple verilerin toplandığı tarihe yakın bir tarih seçmek mantıklı olacaktır.
#analysis date adında yeni bir değişken tanımlıyorum


df["last_order_date"].max() # 2021-05-30
analysis_date = dt.datetime(2021,6,1)



# customer_id, recency, frequnecy ve monetary değerlerinin yer aldığı yeni bir rfm dataframe
#master_id unique değerlere sahip olduğu için customer_id değişkenine eşitliyoruz.
#recency değeri müşterinin en son alışveriş yaptığı tarihten geçen süreyi ifade eder.
#frequency müşterinin alışveriş frekansıdır.
#monetary müşterinin bıraktığı değerdir.


rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[ns]').dt.days
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]

rfm.head()


                # GÖREV 3: RF ve RFM Skorlarının Hesaplanması (Calculating RF and RFM Scores)


#  Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çevrilmesi ve
# Bu skorları recency_score, frequency_score ve monetary_score olarak kaydedilmesi
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] =pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


#Describe atarak RFM değerlerini gözlemleyelim.
rfm.describe([0, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99, 1]).T
#frequency değerinde outliers değerleri tespit ettik. Grafikte gözlemleyelim.

plt.hist(rfm["frequency"],bins=50)
plt.show(block=True)
#Aykırı değer söz konusu.


rfm["frequency"].value_counts()
rfm["frequency_score"].value_counts()


#RFM Score için monetary değeri bir şey ifade etmemektedir. O sebeple recency ve frequency değerlerini string formata
#çevirerek birleştirdik.
# recency_score ve frequency_score’u tek bir değişken olarak ifade edilmesi ve RF_SCORE olarak kaydedilmesi
rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

# 3. recency_score ve frequency_score ve monetary_score'u tek bir değişken olarak ifade edilmesi ve RFM_SCORE olarak kaydedilmesi
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))

rfm.head()


                     # GÖREV 4: RF Skorlarının Segment Olarak Tanımlanması


# Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlama ve  tanımlanan seg_map yardımı ile RF_SCORE'u segmentlere çevirme
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

rfm.head()





# 1. Segmentlerin recency, frequency ve monetary ortalamalarını inceleyiniz.
#Burada Segmente göre groupbya alıp istenilen değerlerin mean ve countunu alıyoruz. 2 yöntemi de bırakıyorum.

rfm[["segment","recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm.groupby("segment").agg({"recency":["mean", "count"],
                            "frequency":["mean", "count"],
                            "monetary":["mean", "count"]})



#                          recency       frequency       monetary
#                        mean count      mean count     mean count
# segment
# about_to_sleep       113.79  1629      2.40  1629   359.01  1629
# at_Risk              241.61  3131      4.47  3131   646.61  3131
# cant_loose           235.44  1200     10.70  1200  1474.47  1200
# champions             17.11  1932      8.93  1932  1406.63  1932
# hibernating          247.95  3604      2.39  3604   366.27  3604
# loyal_customers       82.59  3361      8.37  3361  1216.82  3361
# need_attention       113.83   823      3.73   823   562.14   823
# new_customers         17.92   680      2.00   680   339.96   680
# potential_loyalists   37.16  2938      3.30  2938   533.18  2938
# promising             58.92   647      2.00   647   335.67   647



# 2. RFM analizi yardımı ile 2 case için ilgili profildeki müşterileri bulunuz ve müşteri id'lerini csv ye kaydediniz.

# a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri tercihlerinin üstünde. Bu nedenle markanın
# tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak iletişime geçeilmek isteniliyor. Bu müşterilerin sadık  ve
# kadın kategorisinden alışveriş yapan kişiler olması planlandı. Müşterilerin id numaralarını csv dosyasına yeni_marka_hedef_müşteri_id.cvs
# olarak kaydediniz.

"""
Burada yeni bir hedef değişken tanımlıyorum. target_segments_customer_ids değişkenine atama gerçekleştiriyorum.
rfm dataframeinde segment kategorisinde champions ve loyal customer seçenekleri varsa isin metodu kullanarak boolean döndürüyoruz.
Tanımladığım hedef değişkenş master_id ile seçip benden beklenen yeni kategorilere meraklı ve kadın olan master_idleri sınıflandırarak
seçim islemini gerçekletiriyorum.
"""
target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) &(df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_marka_hedef_müşteri_id.csv", index=False)
cust_ids.shape ##(2497,) totalde benden beklenen göreve dahil olabilecek müşteri sayısı


# b. Erkek ve Çoçuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte iyi müşterilerden olan ama uzun süredir
# alışveriş yapmayan ve yeni gelen müşteriler özel olarak hedef alınmak isteniliyor. Uygun profildeki müşterilerin id'lerini csv dosyasına indirim_hedef_müşteri_ids.csv
# olarak kaydediniz.
target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","at_Risk","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)
df.head()



                     # Tüm süreci fonksiyonlaştıralım.


def create_rfm(dataframe):
    # Veriyi Hazırlma
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)


    # RFM METRIKLERININ HESAPLANMASI
    dataframe["last_order_date"].max()  # 2021-05-30
    analysis_date = dt.datetime(2021, 6, 1)
    rfm = pd.DataFrame()
    rfm["customer_id"] = dataframe["master_id"]
    rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[ns]').dt.days
    rfm["frequency"] = dataframe["order_num_total"]
    rfm["monetary"] = dataframe["customer_value_total"]

    # RF ve RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }
    rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

    return rfm[["customer_id", "recency","frequency","monetary","RF_SCORE","RFM_SCORE","segment"]]

rfm_df = create_rfm(df)
rfm_df.head()



