# -*- coding: utf-8 -*-
"""Proyek Akhir: Sistem Rekomendasi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iyf26HkvYTWQfLWMkzMxwP5Fb0qOFlkH

**Proyek Akhir**
- **Nama:** Aulia Afifah
- **Email:** auliaafifah2205@gmail.com
- **ID Dicoding:** auliaafifah253

# Data Understanding

Import semua library yang dibutuhkan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

""" baca data dengan menggunakan fungsi pandas.read_csv"""

df= pd.read_csv('/content/IMDB Top 250 Movies.csv')
df

"""# Univariate Exploratory Data Analysis"""

df.info()

"""Berdasarkan output di atas, dapat mengetahui bahwa file df memiliki 250 entri"""

print(df.shape)

"""jumlah kolom dan baris pada df

Untuk melihat ada berapa banyak entri yang unik berdasarkan variable-variable yang ada

**Rating Variable**
"""

print('Jumlah data: ', len(df.rating.unique()))
print('Jenis rating: ', df.rating.unique())

sns.histplot(df['rating'], bins=20)
plt.title('Distribution of Ratings')
plt.show()

"""**Certificate Variable**"""

print('Jumlah data: ', len(df.certificate.unique()))
print('Jenis certificate: ', df.certificate.unique())

"""**Year Variable**"""

print('Jumlah data: ', len(df.year.unique()))
print('Jenis tahun: ', df.year.unique())

sns.histplot(df['year'], bins=20)
plt.title('Distribution of Release Years')
plt.show()

"""**Genre Variable**"""

print('Jumlah data: ', len(df.genre.unique()))
print('Jenis genre: ', df.genre.unique())

"""**Run Time Variable**"""

print('Jumlah data: ', len(df.run_time.unique()))
print('Jenis run time: ', df.run_time.unique())

"""Terdapat isi entri yaitu Not Available yang akan diperbaiki pada data preprocessing"""

not_available_rows = df[df['run_time'] == 'Not Available']

not_available_rows

"""**Budget Variable**"""

print('Jumlah data: ', len(df.budget.unique()))
print('Jenis budget: ', df.budget.unique())

""" * Terdapat berbagai format ada beberapa nilai yang disertai dengan simbol dollar ('$')."""

not_budgets_rows = df[df['budget'] == '$3300000']

not_budgets_rows

not_budgets_rows = df[df['budget'] == '$8240000']

not_budgets_rows

"""# Data Preprocessing"""

df.isna().sum()

"""Dari output di atas, terlihat bahwa tidak ada missing value

**Certificate Variable**:
Menggabungkan 'Not Rated' dan 'Unrated' menjadi satu kategori, mengganti 'Not Available' dengan 'Unknown', dan mengganti 'Passed' dengan 'Approved' agar lebih mudah diinterpretasi saat analisis.
"""

df['certificate'] = df['certificate'].replace({
    'Not Rated': 'Unrated',
    'Passed': 'Approved',
    'Not Available': 'Unknown'
})

print('Jenis certificate: ', df.certificate.unique())

"""**Run Time Variable**: Terlihat bahwa terdapat film The Boat run time yang berisi not available, maka akan diganti sesuai run time film yaitu 2 Jam 29 Menit"""

df.loc[df['name'] == 'The Boat', 'run_time'] = '2h 29m'

df[df['name'] == 'The Boat']

"""**Budget Variable**: Menghapus simbol '$'"""

df.loc[df['name'] == 'City of God', 'budget'] = '3300000'

df[df['name'] == 'City of God']

df.loc[df['name'] == 'Mary and Max', 'budget'] = '8240000'

df[df['name'] == 'Mary and Max']

"""# Data Preparation

Melihat informasi pada file df
"""

df.info()

"""Melihat statistik deskriptif dengan semua variable"""

df.describe(include="all")

"""# Model Development dengan Content Based Filtering

cek lagi data yang dimiliki
"""

data = df
data.sample(3)

"""akan membangun sistem rekomendasi sederhana berdasarkan jenis genre yang disediakan dalam film tersebut

## TF-IDF Vectorizer

menggunakan fungsi tfidfvectorizer() dari library sklearn
"""

# Inisialisasi TfidfVectorizer
tf = TfidfVectorizer()

# Melakukan perhitungan idf pada data genre
tf.fit(data['genre'])

# Mapping array dari fitur index integer ke fitur nama
tf.get_feature_names_out()

"""melakukan fit dan transformasi ke dalam bentuk matriks"""

# Melakukan fit lalu ditransformasikan ke bentuk matrix
tfidf_matrix = tf.fit_transform(data['genre'])

# Melihat ukuran matrix tfidf
tfidf_matrix.shape

"""matriks yang kita miliki berukuran (250, 23). Nilai 250 merupakan ukuran data dan 23 merupakan matrik kategori genre.

Untuk menghasilkan vektor tf-idf dalam bentuk matriks, menggunakan fungsi todense()
"""

# Mengubah vektor tf-idf dalam bentuk matriks dengan fungsi todense()
tfidf_matrix.todense()

"""lihat matriks tf-idf untuk beberapa nama film (name) dan kategori genre (genre)."""

# Membuat dataframe untuk melihat tf-idf matrix
# Kolom diisi dengan jenis genre
# Baris diisi dengan nama film

pd.DataFrame(
    tfidf_matrix.todense(),
    columns=tf.get_feature_names_out(),
    index=data.name
).sample(23, axis=1).sample(10, axis=0)

"""## Cosine Similarity

menghitung derajat kesamaan (similarity degree) antar film dengan teknik cosine similarity
"""

# Menghitung cosine similarity pada matrix tf-idf
cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim

"""melihat matriks kesamaan setiap film dengan menampilkan nama film dalam 5 sampel kolom (axis = 1) dan 10 sampel baris (axis=0)."""

# Membuat dataframe dari variabel cosine_sim dengan baris dan kolom berupa nama film
cosine_sim_df = pd.DataFrame(cosine_sim, index=data['name'], columns=data['name'])
print('Shape:', cosine_sim_df.shape)

# Melihat similarity matrix pada setiap film
cosine_sim_df.sample(5, axis=1).sample(10, axis=0)

"""## Mendapatkan Rekomendasi

Di sini, membuat fungsi film_recommendations dengan beberapa parameter sebagai berikut:

* Nama_film : Nama film.
* Similarity_data : Dataframe mengenai similarity yang telah didefinisikan sebelumnya.
* Items : Nama dan fitur yang digunakan untuk mendefinisikan kemiripan, dalam hal ini adalah ‘name’ dan ‘genre’.
* k : Banyak rekomendasi yang ingin diberikan.
"""

def film_recommendations(nama_film, similarity_data=cosine_sim_df, items=data[['name', 'genre']], k=5):
    """
    Rekomendasi film berdasarkan kemiripan dataframe

    Parameter:
    ---
    nama_film : tipe data string (str)
                Nama film (index kemiripan dataframe)
    similarity_data : tipe data pd.DataFrame (object)
                      Kesamaan dataframe, simetrik, dengan film sebagai
                      indeks dan kolom
    items : tipe data pd.DataFrame (object)
            Mengandung kedua nama dan fitur lainnya yang digunakan untuk mendefinisikan kemiripan
    k : tipe data integer (int)
        Banyaknya jumlah rekomendasi yang diberikan
    ---

    Pada index ini, kita mengambil k dengan nilai similarity terbesar
    pada index matrix yang diberikan (i).
    """

    # Mengambil data dengan menggunakan argpartition untuk melakukan partisi secara tidak langsung sepanjang sumbu yang diberikan
    # Dataframe diubah menjadi numpy
    # Range(start, stop, step)
    index = similarity_data.loc[:, nama_film].to_numpy().argpartition(range(-1, -k-1, -1))

    # Mengambil data dengan similarity terbesar dari index yang ada
    closest = similarity_data.columns[index[-1:-(k+2):-1]]

    # Drop nama_film agar nama film yang dicari tidak muncul dalam daftar rekomendasi
    closest = closest.drop(nama_film, errors='ignore')

    return pd.DataFrame(closest).merge(items).head(k)

"""menerapkan kode di atas untuk menemukan rekomendasi film yang mirip dengan film 'the dark knight'"""

data[data.name.eq('The Dark Knight')]

"""mendapatkan film recommendation dengan memanggil fungsi yang telah didefinisikan sebelumnya"""

# Mendapatkan rekomendasi film yang mirip dengan nama film tersebut
film_recommendations('The Dark Knight')

"""# Model evaluations

Menilai kinerja model rekomendasi menggunakan metrik evaluasi

menghitung seberapa banyak genre dari rekomendasi yang beneran sama dengan genre asli film yang direkomendasiin
"""

def evaluate_recommendations(recommendations, actual_genre):
    matches = recommendations['genre'].apply(lambda x: actual_genre in x)
    precision = matches.sum() / len(matches)
    return precision

"""memanggil film_recommendations buat dapetin rekomendasi film mirip 'The Dark Knight' dan ambil genre asli dari 'The Dark Knight'"""

recs = film_recommendations('The Dark Knight')
actual_genre = df[df['name'] == 'The Dark Knight']['genre'].values[0]

"""menghitung precision dengan munakan fungsi evaluasi buat hitung seberapa akurat rekomendasi kita"""

precision = evaluate_recommendations(recs, actual_genre)
print(f'Precision: {precision:.2f}')

"""Precision 0.80: Dari 5 film yang direkomendasiin, 4 film genrenya cocok sama genre 'The Dark Knight' yaitu Action, Crime, dan Drama."""