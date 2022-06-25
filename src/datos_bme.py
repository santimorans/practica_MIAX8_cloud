# Este archivo de python descarga de la web de BME los datos que requerimos sobre el futuro del IBEX y las opciones
# call y put para el cálculo de la volatilidad implícita.

# Primero importamos las librerías

from bs4 import BeautifulSoup
import pandas as pd
import requests
import mibian
from datetime import datetime, date

# Ahora, a través de pandas, leemos el html y obtenemos la primera tabla de la página para obtener los datos del futuro más cercano
# Posteriormente, modificamos los datos para poder operar con ellos.

dfs = pd.read_html("https://www.meff.es/esp/Derivados-Financieros/Ficha/FIEM_MiniIbex_35")
df_futuros = dfs[0]
df_futuros = df_futuros.drop(["Tipo", "Compra", "Venta", "Últ.", "Vol.", "Aper.", "Máx.", "Min."], axis = 1)
df_futuros.columns = df_futuros.columns.droplevel()
datos_futuro = df_futuros.iloc[0]
datos_futuro["Ant."] = datos_futuro["Ant."].replace(".", "")
datos_futuro["Ant."] = datos_futuro["Ant."].replace(",", ".")
datos_futuro["Ant."] = float(datos_futuro["Ant."])

# Dado que con la vía de pandas no podíamos obener los datos de la table de las opciones, los obtenemos con la librería de webscrapping
# beautiful soup. Con este primer codigo, nos fijamos en la cantidad de valores en los que nos vamos a tener que fijar.

url = 'https://www.meff.es/esp/Derivados-Financieros/Ficha/FIEM_MiniIbex_35'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
detail_title = soup.find(id="OpStrike")

ls = []

for x in detail_title:
    ls.append(x.text)

ls.pop()

valores_fechas = soup.find_all("option")

codigos_fechas = []
for i in range(len(ls)):
    if i in codigos_fechas:
        pass
    else:
        codigos_fechas.append(valores_fechas[i]["value"])

# Una vez descargados, nos quedamos únicamente con las columnas que necesitamos para nuestro cálculo

codificados = {}
for i in codigos_fechas:
    codificados[i] = pd.DataFrame(soup.find_all("tr", {"data-tipo": i})).drop([0,2,3,4,5,6,7,8,9,10,11,12,14], axis=1)

# Viendo el formato html de los datos obtenidos, tenemos que poder identificarlos de alguna manera para saber su dia de vencimiento y también su 
# tipo de opcion, y eso lo conseguimos con los codigos OPE y OCE

test_puts = "OPE"
test_calls = "OCE"
puts = {key:val for key, val in codificados.items() if key.startswith(test_puts)}
calls = {key:val for key, val in codificados.items() if key.startswith(test_calls)}

final_calls = dict(zip(ls,list(calls.values())))
final_puts = dict(zip(ls,list(puts.values())))

suma = 0
for i in range(len(final_puts)):
    suma = suma + len(list(final_puts.values())[i])

# Ya con los datos obtenidos, creamos dos dataframes, uno para calls y otro para puts

df_cols = ["date", "strike", "precio"]
datos_options_puts = pd.DataFrame(columns = df_cols, index= range(suma))
datos_options_calls = pd.DataFrame(columns = df_cols, index= range(suma))

datos_options_puts_total = pd.DataFrame(columns = ["date", "strike", "precio"])
for i in range(0, len(final_puts)):
    sec_i = list(final_puts.items())[i]
    sec_dataframe_i = pd.DataFrame(columns = ["date", "strike", "precio"])
    sec_dataframe_i["strike"] = sec_i[1].iloc[:,0]
    sec_dataframe_i["precio"] = sec_i[1].iloc[:,1]
    sec_dataframe_i["date"] = sec_i[0]
    datos_options_puts_total = datos_options_puts_total.append([sec_dataframe_i])

datos_options_calls_total = pd.DataFrame(columns = ["date", "strike", "precio"])
for i in range(0, len(final_calls)):
    sec_i = list(final_calls.items())[i]
    sec_dataframe_i = pd.DataFrame(columns = ["date", "strike", "precio"])
    sec_dataframe_i["strike"] = sec_i[1].iloc[:,0]
    sec_dataframe_i["precio"] = sec_i[1].iloc[:,1]
    sec_dataframe_i["date"] = sec_i[0]
    datos_options_calls_total = datos_options_calls_total.append([sec_dataframe_i])

datos_options_puts_total = datos_options_puts_total.reset_index(drop=True)
datos_options_calls_total = datos_options_calls_total.reset_index(drop=True)

# Asimismo, debemos modificar los datos para poder operar con ellos

for i in range(0,len(datos_options_puts_total)):
    datos_options_puts_total["strike"].iloc[i] = datos_options_puts_total["strike"].iloc[i].text.strip().replace("[", "").replace("]", "").replace(".", "").replace(",", ".")
    datos_options_puts_total["precio"].iloc[i] = datos_options_puts_total["precio"].iloc[i].text.strip().replace("[", "").replace("]", "").replace(".", "").replace(",", ".").replace("-", "0")

for i in range(0,len(datos_options_calls_total)):
    datos_options_calls_total["strike"].iloc[i] = datos_options_calls_total["strike"].iloc[i].text.strip().replace("[", "").replace("]", "").replace(".", "").replace(",", ".")
    datos_options_calls_total["precio"].iloc[i] = datos_options_calls_total["precio"].iloc[i].text.strip().replace("[", "").replace("]", "").replace(".", "").replace(",", ".").replace("-", "0")

# Incluimos los datos que necesitamos para el cálculo de la volatilidad implícita

datos_options_puts_total["interest_rate"] = 0
datos_options_calls_total["interest_rate"] = 0

datos_options_puts_total["underlying_price"] = datos_futuro["Ant."]
datos_options_calls_total["underlying_price"] = datos_futuro["Ant."]

datos_options_puts_total["fecha_actual"] = datetime.today().strftime("%d/%m/%Y")
datos_options_calls_total["fecha_actual"] = datetime.today().strftime("%d/%m/%Y")

datos_options_puts_total["fecha_actual"] = pd.to_datetime(datos_options_puts_total["fecha_actual"])
datos_options_puts_total["date"] = pd.to_datetime(datos_options_puts_total["date"])

datos_options_calls_total["fecha_actual"] = pd.to_datetime(datos_options_calls_total["fecha_actual"])
datos_options_calls_total["date"] = pd.to_datetime(datos_options_calls_total["date"])

datos_options_puts_total["dias_vencimiento"] = datos_options_puts_total["date"] - datos_options_puts_total["fecha_actual"]
datos_options_calls_total["dias_vencimiento"] = datos_options_calls_total["date"] - datos_options_calls_total["fecha_actual"]

for i in range(0,len(datos_options_puts_total)):
    datos_options_puts_total["dias_vencimiento"][i] = datos_options_puts_total["dias_vencimiento"][i].days

for i in range(0,len(datos_options_calls_total)):
    datos_options_calls_total["dias_vencimiento"][i] = datos_options_calls_total["dias_vencimiento"][i].days

datos_options_puts_total["volatility"] = 0
datos_options_calls_total["volatility"] = 0

# Calculamos la volatilidad implícita

vols_puts = []
for i in range(0,len(datos_options_puts_total)):
    try:
        date, strike, precio, interest_rate, underlying_price, fecha_actual, dias_vencimiento, volatility = datos_options_puts_total.iloc[i]
        c_i = mibian.BS([underlying_price, strike, 0, dias_vencimiento], putPrice=float(precio))
        vols_puts.append(c_i.impliedVolatility)
    except ZeroDivisionError:
        vols_puts.append("0")

vols_calls = []
for i in range(0,len(datos_options_calls_total)):
    try:
        date, strike, precio, interest_rate, underlying_price, fecha_actual, dias_vencimiento, volatility = datos_options_calls_total.iloc[i]
        c_i = mibian.BS([underlying_price, strike, 0, dias_vencimiento], callPrice=float(precio))
        vols_calls.append(c_i.impliedVolatility)
    except ZeroDivisionError:
        vols_calls.append("0")

datos_options_puts_total["volatility"] = vols_puts
datos_options_calls_total["volatility"] = vols_calls

datos_options_puts_total["volatility"] = datos_options_puts_total["volatility"].fillna(0)
datos_options_calls_total["volatility"] = datos_options_calls_total["volatility"].fillna(0)

datos_options_puts_total.to_csv("datos_puts.csv", index = False)
datos_options_calls_total.to_csv("datos_calls.csv", index = False)