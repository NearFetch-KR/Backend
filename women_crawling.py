import requests, json, math
from bs4 import BeautifulSoup

category_dict = {
    "clothing" : ["coats","dresses","jackets","jeans","knitwear","lingerie & swimwear","shirts","skirts","t-shirts","pants"],
    "shoes": ["boots","flats","heels","lace-up shoes","loafers","sandals","sneakers","wedges"],
    "bags": ["backpacks","belt bags","clutches","handbags","shopping bags","shoulder bags","travel bags"],
    "accessories": ["belts e braces","jewelry","glasses","gloves","hats","scarves and foulards","wallets"]
}

category_urls = [
    "https://www.mclabels.com/collections/coats-woman",
    "https://www.mclabels.com/collections/dresses",
    "https://www.mclabels.com/collections/jackets-woman",
    "https://www.mclabels.com/collections/jeans-woman",
    "https://www.mclabels.com/collections/knitwear-woman",
    "https://www.mclabels.com/collections/lingerie-swimwear",
    "https://www.mclabels.com/collections/shirts-woman",
    "https://www.mclabels.com/collections/skirts",
    "https://www.mclabels.com/collections/t-shirts-woman",
    "https://www.mclabels.com/collections/pants-woman",
    "https://www.mclabels.com/collections/boots-woman",
    "https://www.mclabels.com/collections/flats",
    "https://www.mclabels.com/collections/heels",
    "https://www.mclabels.com/collections/lace-up-shoes-woman",
    "https://www.mclabels.com/collections/loafers-woman",
    "https://www.mclabels.com/collections/sandals-woman",
    "https://www.mclabels.com/collections/sneakers-woman",
    "https://www.mclabels.com/collections/wedges",
    "https://www.mclabels.com/collections/backpacks-woman",
    "https://www.mclabels.com/collections/belt-bags-woman",
    "https://www.mclabels.com/collections/clutches-woman",
    "https://www.mclabels.com/collections/handbags-woman",
    "https://www.mclabels.com/collections/shopping-bags-woman",
    "https://www.mclabels.com/collections/shoulder-bags",
    "https://www.mclabels.com/collections/travel-bags-woman",
    "https://www.mclabels.com/collections/belts-e-braces-woman",
    "https://www.mclabels.com/collections/jewelry-woman",
    "https://www.mclabels.com/collections/glasses-woman",
    "https://www.mclabels.com/collections/gloves-woman",
    "https://www.mclabels.com/collections/hats-woman",
    "https://www.mclabels.com/collections/scarves-and-foulards-woman",
    "https://www.mclabels.com/collections/wallets-woman",
]
itemInfos = []  
product_links = []
for category_url in category_urls:
    for pageNo in range(1,6):
        url = f"{category_url}?page={pageNo}"
        result = requests.get(url = url)
        bs_obj = BeautifulSoup(result.content, "html.parser")
        articles = bs_obj.findAll("article", {"class":"product--root"})
        for article in articles:
            product_links.append('https://www.mclabels.com'+article.find("a")['href'])


for product_link in product_links:
    url = product_link
    result = requests.get(url = url)
    bs_obj = BeautifulSoup(result.content, "html.parser")
    if bs_obj.findAll("div", {"class":"product-page--thumbs-container"}) == []:
        continue

    thumbs_container = bs_obj.findAll("div", {"class":"product-page--thumbs-container"})[1]
    thumbs = thumbs_container.findAll("div", {"class":"product-page--thumb"})

    div_cart_form = bs_obj.find("div", {"class":"product-page--cart-form-block"})

    ul_breadcrumbs = bs_obj.find("ul", {"class":"breadcrumbs colored-links"})

    options = div_cart_form.findAll("option")

    div_description = bs_obj.find("div", {"class":"product-page--description"})
    lis = div_description.select('ul > li')


    itemImg = [('https:'+thumb.find("img")['data-src']).replace("{width}", "700") for thumb in thumbs]
    itemBrand = div_cart_form.find("a").text
    itemName = div_cart_form.find("h2", {"class":"product-page--title"}).text.replace(itemBrand,"").strip()
    if div_cart_form.find("span", {"class":"compare-price"}).text != "":
        price = div_cart_form.find("span", {"class":"compare-price"}).text.lstrip(" €").replace(".", "").replace(",", ".")
        sale_price = math.ceil(float(div_cart_form.find("span", {"class":"money"}).text.lstrip(" €").replace(".", "").replace(",", "."))*1330)
    else:
        price = div_cart_form.find("span", {"class":"money"}).text.lstrip(" €").replace(".", "").replace(",", ".")
        sale_price = None
    gender = lis[-1].text
    categorySmall = ul_breadcrumbs.findAll("li")[2].text.replace('woman',"").replace('man',"").strip()
    for i in category_dict:
        if categorySmall in category_dict[i]:
            categoryMedium = i
    itemOption = []
    for option in options:
        if option.text.split("/")[0].strip() == '-UNI-':
            itemOption.append("ONE SIZE")
        else:
            itemOption.append(option.text.split("/")[0].strip())

    materials = []
    for li in lis:
        if "%" in li.text:
            materials.append(li.text.strip())
    skuNum = lis[-2].text.strip('product code')


    itemInfo = {
        "itemImg":itemImg,
        "itemName":itemName,
        "itemBrand":itemBrand,
        "price":math.ceil(float(price)*1330),
        "sale_price":sale_price,
        "gender":gender,
        "categoryMedium":categoryMedium,
        "categorySmall":categorySmall,
        "itemOption":itemOption,
        "materials":materials,
        "skuNum":skuNum
    }
    itemInfos.append(itemInfo)

with open("./women_products.json", 'w', encoding='utf-8') as file:
    json.dump(itemInfos, file, indent="\t", ensure_ascii=False)