## Cities

apucarana_zip = [
  "86800-007", "86800-030", "86800-040", "86800-060", "86800-070", "86800-090",
  "86800-110", "86800-140", "86800-200", "86800-260", "86800-285", "86800-704"
]

arapongas_zip = [
  "86700-005", "86700-010", "86700-015", "86700-020", "86700-025", "86700-030",
  "86700-035", "86700-040"
]
ibipora_zip = ["86200-000", "86200-970","86200-981"]
londrina_zip = [
  "86010-000", "86010-050", "86010-100", "86010-150", "86010-200", "86010-800",
  "86010-250", "86010-300", "86010-350", "86010-400", "86010-450", "86010-500",
  "86010-550", "86010-600", "86010-650", "86010-700", "86010-750", "86082-580"
]
cambe_zip = [
  "86181-000", "86181-010", "86181-020", "86181-030", "86181-040"
]
maringa_zip = [
  "87010-000", "87010-050", "87010-100", "87010-150", "87010-200",
  "87010-250", "87010-300", "87010-350", "87010-400", "87010-450",
  "87010-500", "87010-550", "87010-600"
]
manaus_zip = ["69020-060"]

address = {"Apucarana":apucarana_zip, "Arapongas":arapongas_zip,"Ibiporã":ibipora_zip, "Londrina":londrina_zip,
            "Cambé":cambe_zip,"Maringá":maringa_zip, "Manaus": manaus_zip}

cities = ["Apucarana", "Arapongas", "Ibiporã", "Londrina", "Cambé", "Maringá", "Manaus"]
all_zips = sum(address.values(), [])
###  londrina_outlier = "86082-580"


# Products
camisa_sub_m = ["Camisa social", "Camisa polo"]
camiseta_sub_m = ["Básica", "Estampada", "Manga longa", "Regata"]
calcas_sub_m = ["Jeans", "Sarja", "Moletom", "Social"]
bermudas_sub_m = ["Jeans", "Sarja", "Moletom", "Praia"]
sport_sub_m = ["Shorts", "Camisetas dry fit", "Jaquetas esportivas"]

male = {"Camisas": camisa_sub_m, "Camisetas": camiseta_sub_m, "Calças": calcas_sub_m, "Bermudas": bermudas_sub_m,
        "Sport": sport_sub_m}

blusas_sub_f = ["Regata", "Manga curta", "Manga longa", "Bata", "Cropped"]
camiseta_sub_f = ["Social", "Casual", "Jeans"]
calcas_sub_f = ["Jeans", "Legging", "Pantalona", "Moletom"]
saias_sub_f = ["Curta", "Midi", "Longa", "Jeans"]
vestidos_sub_f = ["Curto", "Midi", "Longo", "Casual", "Festa"]
shorts_sub_f = ["Jeans", "Alfaiataria", "Moletom"]
jaquetas_sub_f = [	"Jeans", "Couro", "Corta-vento", "Moletom"]
sport_sub_f = ["Top", "Legging", "Shorts", "Jaqueta esportiva"]

female = {"Blusas": blusas_sub_f, "Camisetas": camiseta_sub_f, "Calças": calcas_sub_f, "Saias": saias_sub_f,
          "Vestidos": vestidos_sub_f, "Shorts": shorts_sub_f, "Jaquetas": jaquetas_sub_f, "Sport": sport_sub_f}

products = {"masculino": male, "feminino": female}

all_gender = ["masculino", "feminino"]
all_categories = list(female.keys()) + list(male.keys())
all_subcategories = sum(female.values(), []) + sum(male.values(), [])

# dataframe columns
df_cols = ["id", "pedido", "cliente", "cidade", "cep", "genero", "categoria", "subcategoria", "preço un.", "quantidade", "valor total"]