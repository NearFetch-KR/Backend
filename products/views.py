import random
from string import ascii_uppercase
from django.db.models import Q
from difflib import SequenceMatcher

from django.views           import View

from products.models        import Largecategory, Mediumcategory, Product, ProductHits, Smallcategory
from users.models           import Like
from django.http            import JsonResponse

class MakeBrandListView(View):
    def get(self, request):
        alpha_list = list(ascii_uppercase)

        result = {}
        for alpha in alpha_list:
            result[alpha] = [product['brand'] for product in Product.objects.filter(brand__startswith=alpha).values('brand').distinct()]
      
        delete_by_keys = [k for k, v in result.items() if v == []]

        for delete_by_key in delete_by_keys:
            del result[delete_by_key]
        return JsonResponse({'message': 'success', 'result': result}, status=200)

class MakeFilterView(View):
    def get(self, request):
        large_categories = [large_category.name for large_category in Largecategory.objects.all()]
        brands = [product['brand'] for product in Product.objects.values('brand').distinct()]
        small_categories = [small_category['name'] for small_category in Smallcategory.objects.values('name').distinct()]

     
        result = {
            'gender' : large_categories,
            'brand' : brands,
            'categorySmall' : small_categories
        }
        return JsonResponse({'message': 'success', 'result': result}, status=200)

class MakeCategoryView(View):
    def get(self, request):
        medium_categories = Mediumcategory.objects.values('name').distinct()
        medium_category_dict = [medium_category['name'] for medium_category in medium_categories]
        men = {}
        women = {}
        for medium_category in medium_category_dict:
            men[medium_category] = [
                small_category.name for small_category in Smallcategory.objects.filter(
                    medium_category__name=medium_category,
                    medium_category__large_category__name="MEN"
                )
            ]

            women[medium_category] = [
                small_category.name for small_category in Smallcategory.objects.filter(
                    medium_category__name=medium_category,
                    medium_category__large_category__name="WOMEN"
                )
            ]
        
        return JsonResponse({'message': 'success', 'men': men, 'women': women}, status=200)

class MainHotItemView(View):
    def get(self, request):
        products = Product.objects.order_by('-hits')[:4]

        result = [{
            "itemImg"        : [image.url for image in product.image_set.all()],
            "itemBrand"      : product.brand,
            "itemName"       : product.name,
            "price"          : product.price,
            "sale_price"     : product.sale_price,
            "skuNum"         : product.sku_number,
            "product_id"     : product.id,
            "categorySmall"  : product.small_category.name,
            "categoryMedium" : product.small_category.medium_category.name,
            "gender"         : product.small_category.medium_category.large_category.name,
            "itemOption"     : [option.size for option in product.option_set.all()],
            "materials"      : [material.name for material in product.material_set.all()],
            'hits'           : product.hits
        } for product in products]

        return JsonResponse({'message': 'success', 'result': result}, status=200)

class MainRecommendView(View):
    def get(self, request):
        products = Product.objects.filter(small_category__medium_category__name='bags', small_category__medium_category__large_category__name="WOMEN")

        products = random.sample(list(products), 40)

        result = [{
            "itemImg"        : [image.url for image in product.image_set.all()],
            "itemBrand"      : product.brand,
            "itemName"       : product.name,
            "price"          : product.price,
            "sale_price"     : product.sale_price,
            "skuNum"         : product.sku_number,
            "product_id"     : product.id,
            "categorySmall"  : product.small_category.name,
            "categoryMedium" : product.small_category.medium_category.name,
            "gender"         : product.small_category.medium_category.large_category.name,
            "itemOption"     : [option.size for option in product.option_set.all()],
            "materials"      : [material.name for material in product.material_set.all()],
            'hits'           : product.hits
        } for product in products]

        return JsonResponse({'message': 'success', 'result': result}, status=200)

class ProductListView(View):
    def get(self, request):
        # offset = int(request.GET.get('offset', 0))
        # limit = int(request.GET.get('limit', 5))

        # 상단 카테고리 및 필터 부분
        large_category  = request.GET.getlist('gender', None)
        medium_category = request.GET.get('categoryMedium', None)
        small_category  = request.GET.getlist('categorySmall', None)
        print(small_category)
        sale  = request.GET.get('sale', None)
        brand = request.GET.getlist('brand', None)
        min_price = request.GET.get('min_price', 0)
        max_price = request.GET.get('max_price', 10000000)

        if brand == ['null']:
            brand = None   
     
        if sale == "null":
            sale = None      

        # 정렬 부분
        order_condition = request.GET.get('order', None)

        products = Product.objects.select_related(
            'small_category', 'small_category__medium_category', 'small_category__medium_category__large_category'
        ).all()

        if large_category:
            products = products.filter(small_category__medium_category__large_category__name__in=large_category)

        if medium_category:
            products = products.filter(small_category__medium_category__name__iexact=medium_category)

        if small_category:
            products = products.filter(small_category__name__in=small_category)

        if sale:
            products = products.exclude(sale_price=None)

        if brand:
            products = products.filter(brand__in=brand)

        if min_price or max_price:
            products = products.filter(price__range=(min_price, max_price))

        if order_condition == '높은 가격순':
            products = products.order_by('-price')

        if order_condition == '낮은 가격순':
            products = products.order_by('price')   

        if order_condition == '추천 상품':
            products = products.order_by('-hits') 
        print(len(products))

        # 가격바에 디폴트 값으로 쓰임(화면에 표시되는 상품 중에서의 가장 높은 가격, 가장 낮은 가격)
        price_bar = {
            "min" : products.order_by('price')[0].price,
            "max" : products.order_by('-price')[0].price
        }

        result = [{
            "itemImg"        : [image.url for image in product.image_set.all()],
            "itemBrand"      : product.brand,
            "itemName"       : product.name,
            "price"          : product.price,
            "sale_price"     : product.sale_price,
            "skuNum"         : product.sku_number,
            "product_id"     : product.id,
            "categorySmall"  : product.small_category.name,
            "categoryMedium" : product.small_category.medium_category.name,
            "gender"         : product.small_category.medium_category.large_category.name,
            "itemOption"     : [option.size for option in product.option_set.all()],    
            "materials"      : [material.name for material in product.material_set.all()],
            'hits'           : product.hits
        } for product in products]

        return JsonResponse({'message': 'success', 'result': result, 'price_bar': price_bar}, status=200)




def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ProductDetailView(View): # 상품상세페이지에 필요한 데이터: 브랜드이름,상품명,가격,할인가격,스큐넘버,소재,옵션(사이즈),상품사진
    # def get(self, request, product_id):
    def get(self, request, sku_number):
        try:
            product = Product.objects.get(sku_number=sku_number)
            # product = Product.objects.get(id=product_id)
            # images = product.image_set.all()

            ip = get_client_ip(request)

            if not ProductHits.objects.filter(client_ip=ip, product_id=product.id).exists():
                product.hits += 1 
                product.save()
                
                ProductHits.objects.create(
                    client_ip = ip,
                    product_id = product.id
                )

            detail = {
                "itemImg"        : [image.url for image in product.image_set.all()],
                "itemBrand"      : product.brand,
                "itemName"       : product.name,
                "price"          : product.price,
                "sale_price"     : product.sale_price,
                "skuNum"         : product.sku_number,
                "product_id"     : product.id,
                "categorySmall"  : product.small_category.name,
                "categoryMedium" : product.small_category.medium_category.name,
                "gender"         : product.small_category.medium_category.large_category.name,
                "itemOption"     : [option.size for option in product.option_set.all()],
                "materials"      : [material.name for material in product.material_set.all()],
                'hits'           : product.hits
            }   

            # 추천 상품(동일 성별이면서 동일 소카테고리인 거)
            same_small_category = product.small_category.name
            same_gender = product.small_category.medium_category.large_category.name
            
            recommend_products = Product.objects.filter(
                small_category__name = same_small_category,
                small_category__medium_category__large_category__name = same_gender
            ).exclude(id=product.id)

            number_of_samples = 20
            if len(recommend_products) < number_of_samples:
                number_of_samples = len(recommend_products)
            recommend_products = random.sample(list(recommend_products), number_of_samples)

            recommend = [{
                "itemImg"        : [image.url for image in recommend_product.image_set.all()],
                "itemBrand"      : recommend_product.brand,
                "itemName"       : recommend_product.name,
                "price"          : recommend_product.price,
                "sale_price"     : recommend_product.sale_price,
                "skuNum"         : recommend_product.sku_number,
                "product_id"     : recommend_product.id,
                "categorySmall"  : recommend_product.small_category.name,
                "categoryMedium" : recommend_product.small_category.medium_category.name,
                "gender"         : recommend_product.small_category.medium_category.large_category.name,
                "itemOption"     : [option.size for option in recommend_product.option_set.all()],
                "materials"      : [material.name for material in recommend_product.material_set.all()],
                'hits'           : recommend_product.hits
            } for recommend_product in recommend_products]

            return JsonResponse({'detail': detail, 'recommend': recommend}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({"message": "Product_DoesNotExist"}, status=404)


class LikeView(View):
    # @signin_decorator
    def post(self, request, product_id):
        try:
            like, is_like = Like.objects.get_or_create(product_id=product_id, user_id=request.user.id)
            
            if not is_like:
                like.delete()
            
            return JsonResponse({'massage':"ToggleSuccess"}, status=200)
                
        except Product.DoesNotExist:
            return JsonResponse({'massage':"DoesNotExist"}, status=401)

class ProductSearchView(View):
    def get(self, request):
        products = Product.objects.all()
        word_list  = request.GET.get('word', '').split()
        print(word_list)

        word_list = [word.replace(".","").replace("-","").replace(" ","").upper() for word in word_list]
        convert_word = {}

        brand_dict = {
            "VALENTINO":["발렌티노","발랜티노"],
            "3.1 PHILLIP LIM":["3.1 필립림","필림림"],
            "A-COLD-WALL":["어콜드월","콜드윌"],
            "A.P.C.":["아페쎄","아패쎄"],
            "A.S. 98":["A.S. 98","as98"],
            "A.TESTONI":["아테스토니","어테스토니"],
            "ACNE STUDIOS":["아크네 스튜디오","아크네스투디오"],
            "ADIDAS":["아디다스","아디다쓰"],
            "ADIDAS Y-3 YOHJI YAMAMOTO":["아디다스 Y-3 요지 야마모토","아디다스야마모토"],
            "AERONAUTICA MILITARE":["에어로노티카 밀리타레","에로노티카"],
            "ALANUI":["알라누이","알라누"],
            "ALDO CASTAGNA":["알도 카스타냐","알도카스타냐"],
            "ALEXANDER MCQUEEN":["알렉산더맥퀸","알랙산더맥퀸"],
            "ALEXANDER SMITH":["알렉산더 스미스","알랙산더스미스"],
            "ALEXANDER WANG":["알렉산더왕","알랙산더왕"],
            "ALEXANDRE VAUTHIER":["알렉산드레 보티에","알랙산더보티에"],
            "ALPHA INDUSTRIES":["알파 인더스트리","알파인더스트리스"],
            "ALYX":["알릭스","앨릭스"],
            "AMBUSH":["앰부쉬","앰부시"],
            "AMI ALEXANDRE MATTIUSSI":["아미 알렉산드레 마티우시","아미"],
            "AMIRI":["아미리","아마이리"],
            "ANCIENT GREEK SANDALS":["앤시언트 그릭 샌들",""],
            "ANDERSON'S":["앤더슨","엔더슨"],
            "ANDREA D'AMICO":["안드레아 다미코",""],
            "ANDRÈ MAURICE 1921":["ANDRÈ MAURICE 1921",""],
            "ANTONY MORATO":["안토니 모라토",""],
            "ANYA HINDMARCH":["안야힌드마치",""],
            "AQUASCUTUM":["아쿠아스큐텀",""],
            "AQUAZZURA":["아쿠아주라",""],
            "ARMANI EXCHANGE":["아르마니 익스체인지","알마니익스체인지"],
            "ARMANI JEANS":["아르마니진","알마니청바지"],
            "ASH":["아쉬","애쉬"],
            "ASPESI":["아스페시","애스페시"],
            "ATHLEISUREWEAR BY BOSS":["ATHLEISUREWEAR BY BOSS",""],
            "ATLANTIC STARS":["아틀란틱 스타",""],
            "AUA":["AUA",""],
            "AUTRY":["오트리","어트리"],
            "B-LOW THE BELT":["빌로우더벨트",""],
            "BAGUTTA":["바구타",""],
            "BALENCIAGA":["발렌시아가","발랜시아가"],
            "BALLANTYNE":["발란타인",""],
            "BALLY":["발리","밸리"],
            "BALMAIN":["발망","발만"],
            "BAO BAO ISSEY MIYAKE":["바오바오 이세이미야케","이쎄이미야케"],
            "BARBOUR":["바버","바보"],
            "BARROW":["BARROW",""],
            "BEST COMPANY":["BEST COMPANY",""],
            "BILLIONAIRE BOYS CLUB":["빌리어네어 보이즈 클럽",""],
            "BILLIONAIRE COUTURE":["BILLIONAIRE COUTURE",""],
            "BIRKENSTOCK":["버켄스탁","버캔스탁"],
            "BLAUER":["BLAUER",""],
            "BLUNDSTONE":["블런드스톤",""],
            "BOGLIOLI":["볼리올리",""],
            "BORBONESE":["보르보네제",""],
            "BORSALINO":["보르살리노",""],
            "BOTTEGA VENETA":["보테가베네타","베테가보네타"],
            "BOUTIQUE MOSCHINO":["부티크 모스키노",""],
            "BOY LONDON":["BOY LONDON",""],
            "BRIGLIA 1949":["브리글리아 1949",""],
            "BRUNELLO CUCINELLI":["브루넬로 쿠치넬리","쿠치넬리"],
            "BRUNO PREMI":["BRUNO PREMI",""],
            "BUFFALO LONDON":["버팔로 런던",""],
            "BULGARI":["불가리","불가리스"],
            "BURBERRY":["버버리","바바리"],
            "BUSCEMI":["부세미",""],
            "BUTTERO":["부테로","부태로"],
            "CALVIN KLEIN":["캘빈클라인","켈빈클라인"],
            "CALVIN KLEIN JEANS":["캘빈클라인 진",""],
            "CAMPER":["캠퍼","켐퍼"],
            "CANADA GOOSE":["캐나다구스","캐나다구쓰"],
            "CANALI":["까날리",""],
            "CAR SHOE":["카슈",""],
            "CARHARTT":["칼하트","찰하트"],
            "CARTIER":["까르띠에","카르티에"],
            "CASADEI":["까사데이",""],
            "CASTANER":["까스따네르",""],
            "CAZAL EYEWEAR":["CAZAL EYEWEAR",""],
            "CÉLINE":["셀린느","쎌린느"],
            "CHANEL":["샤넬","채널"],
            "CHIARA FERRAGNI":["키아라 페라그니",""],
            "CHLOÉ":["끌로에","끌로애"],
            "CHRISTIAN LOUBOUTIN":["크리스찬 루부탱","크리스티안루부탱"],
            "CHURCH'S":["처치스",""],
            "CIESSE":["CIESSE",""],
            "CLARKS":["클락스",""],
            "COACH":["코치",""],
            "COCCINELLE":["코치넬리","쿠치낼리"],
            "COLMAR ORIGINALS":["COLMAR ORIGINALS",""],
            "COMME DES GARÇONS":["COMME DES GARÇONS",""],
            "COMME DES GARÇONS PLAY":["COMME DES GARÇONS PLAY",""],
            "COMMON PROJECTS":["커먼프로젝트",""],
            "CONVERSE":["컨버스","캔버스"],
            "CORNELIANI":["꼬르넬리아니",""],
            "CP COMPANY":["CP컴퍼니","씨피컴퍼니"],
            "CRIME LONDON":["크라임런던",""],
            "CRUCIANI":["크루치아니",""],
            "CULT GAIA":["컬트가이아",""],
            "D.A.T.E.":["데이트",""],
            "DAMIR DOMA":["다미르 도마",""],
            "DAVIDSON":["DAVIDSON",""],
            "DESIGUAL":["DESIGUAL",""],
            "DIADORA":["디아도라",""],
            "DIADORA HERITAGE":["디아도라 헤리티지",""],
            "DIANE VON FURSTENBERG":["다이앤 본 퍼스텐버그",""],
            "DIOR":["디올","디오르"],
            "DITA":["디타",""],
            "DOLCE E GABBANA":["돌체 앤 가바나","돌체엔가바나"],
            "DOUCAL'S":["듀칼스",""],
            "DR. MARTENS":["닥터마틴",""],
            "DRIES VAN NOTEN":["드리스반노튼",""],
            "DRKSHDW BY RICK OWENS":["DRKSHDW BY RICK OWENS",""],
            "DRUMOHR":["드루모어",""],
            "DSQUARED2":["디스퀘어드2","디스케어드"],
            "DUVETICA":["듀베티카","두베티카"],
            "EASTPAK":["이스트팩",""],
            "EDWARD GREEN":["에드워드 그린",""],
            "ELISABETTA FRANCHI":["엘리자베타 프랑키",""],
            "EMPORIO ARMANI":["엠포리오 아르마니","앰포리오알마니"],
            "ENTRE AMIS":["ENTRE AMIS",""],
            "ERMENEGILDO ZEGNA":["에르메네질도 제냐","애르메네질도재냐"],
            "ETRO":["에트로","애트로"],
            "EYEPETIZER":["아이페타이저",""],
            "FABIANA FILIPPI":["파비아나 필리피",""],
            "FALIERO SARTI":["팔리에로 사르티",""],
            "FAY":["페이",""],
            "FEAR OF GOD":["피어오브갓","피어오브갇"],
            "FEDELI":["페델리",""],
            "FENDI":["펜디","팬디"],
            "FILA":["휠라",""],
            "FILLING PIECES":["필링피스",""],
            "FINAMORE":["FINAMORE",""],
            "FIORUCCI":["피오루치",""],
            "FORTE FORTE":["포르테포르테",""],
            "FRATELLI ROSSETTI":["프라텔리 로세띠",""],
            "FURLA":["훌라","퓰라"],
            "GALLO":["GALLO",""],
            "GANNI":["가니",""],
            "GANT":["간트",""],
            "GCDS":["GCDS",""],
            "GHOUD":["GHOUD",""],
            "GIADA BENINCASA":["지아다 베닌카사",""],
            "GIMO'S":["GIMO'S",""],
            "GIORGIO ARMANI":["조르지오 아르마니","조지오아르마니"],
            "GIUSEPPE ZANOTTI DESIGN":["쥬세페 자노티 디자인",""],
            "GIVENCHY":["지방시",""],
            "GOLDEN GOOSE":["골든구스","골든구쓰"],
            "GOSHA RUBCHINSKIY":["고샤 루브친스키",""],
            "G-SHOCK WATCHES BY CASIO":["지샥 와치 바이 카시오","지샥"],
            "GUCCI":["구찌","구치"],
            "GUESS":["게스",""],
            "HALMANERA":["할마네라",""],
            "HARMONT & BLAINE":["HARMONT & BLAINE",""],
            "HARRIS WHARF LONDON":["해리스워프런던",""],
            "HARTFORD":["하트포드",""],
            "HERNO":["에르노",""],
            "HERON PRESTON":["헤론 프레스턴",""],
            "HERSCHEL SUPPLY & CO":["HERSCHEL SUPPLY & CO",""],
            "HOMME PLISSÉ ISSEY MIYAKE":["HOMME PLISSÉ ISSEY MIYAKE",""],
            "HUGO BOSS":["휴고보스",""],
            "ICEBERG":["아이스버그",""],
            "IH NOM UH NIT":["이놈어닛","이놈우닛"],
            "INCOTEX":["인코텍스",""],
            "ISABEL MARANT":["이자벨마랑","이자밸마랑"],
            "J.W. ANDERSON":["JW앤더슨","엔더슨"],
            "JACK & JONES":["JACK & JONES",""],
            "JACOB COHEN":["야콥 코헨",""],
            "JACQUEMUS":["쟈크뮈스","자크미스"],
            "JAMES PERSE":["제임스펄스",""],
            "JANET SPORT":["JANET SPORT",""],
            "JANET&JANET":["자넷&자넷",""],
            "JECKERSON":["제커슨",""],
            "JEFFREY CAMPBELL":["제프리 캠벨",""],
            "JIL SANDER":["질샌더","질센더"],
            "JIMMY CHOO":["지미추",""],
            "JOHN LOBB":["존 롭",""],
            "JOHN SMEDLEY":["존스메들리",""],
            "JOSHUA SANDERS":["조슈아샌더스",""],
            "JUNYA WATANABE":["준야 와타나베","와타나배"],
            "K-WAY":["케이웨이",""],
            "KANGRA":["캉그라",""],
            "KAPPA":["카파",""],
            "KARL LAGERFELD":["칼 라거펠트",""],
            "KHRISJOY":["크리스조이",""],
            "KITON":["키톤",""],
            "L'AUTRE CHOSE":["로트레쇼즈",""],
            "LACOSTE":["라코스테","라코스떼"],
            "LANCASTER PARIS":["LANCASTER PARIS",""],
            "LANVIN":["랑방",""],
            "LE PARMENTIER":["르파라멘티",""],
            "LEATHER CROWN":["레더크라운",""],
            "LERZ":["LERZ",""],
            "LOEWE":["로에베","로애배"],
            "LOLA CRUZ":["로라 크루즈",""],
            "LONGHI":["LONGHI",""],
            "LORO PIANA":["로로피아나",""],
            "LOVE MOSCHINO":["러브모스키노",""],
            "LUIGI BORRELLI":["루이지 보렐리",""],
            "MAISON KITSUNÉ":["메종 키츠네","매종키츠네"],
            "MAISON MARGIELA":["메종마르지엘라","마르지앨라"],
            "MAJESTIC FILATURES":["마제스틱 필라쳐",""],
            "MALÌPARMI":["MALÌPARMI",""],
            "MALONE SOULIERS":["말론슐져",""],
            "MARC ELLIS":["MARC ELLIS",""],
            "MARC JACOBS":["마크제이콥스",""],
            "MARCELO BURLON":["마르셀로불론",""],
            "MARINE SERRE":["마린세르",""],
            "MARNI":["마르니","말니"],
            "MARSELL":["마르셀",""],
            "MAUI JIM":["마우이 짐",""],
            "MC2 SAINT BARTH":["MC2 SAINT BARTH",""],
            "MCM":["엠씨엠","앰씨앰"],
            "MCQ BY ALEXANDER MCQUEEN":["MCQ BY ALEXANDER MCQUEEN",""],
            "MICHAEL KORS":["마이클코어스",""],
            "MISSONI":["미쏘니","미써니"],
            "MIU MIU":["미우미우","미유미유"],
            "MOA":["모아",""],
            "MOMA":["모마",""],
            "MONCLER":["몽클레어","몽클래어"],
            "MOORER":["무레르",""],
            "MORESCHI":["모레스키",""],
            "MOSCHINO":["모스키노","모스치노"],
            "MOSCHINO UNDERWEAR":["모스키노 언더웨어",""],
            "MOU":["MOU",""],
            "MSGM":["엠에스지엠","앰에스지앰"],
            "NANUSHKA":["나누쉬카",""],
            "NAPAPIJRI":["나파피리",""],
            "NEIL BARRETT":["닐바렛","닐바랫"],
            "NERO GIARDINI":["NERO GIARDINI",""],
            "NEW BALANCE":["뉴발란스","뉴밸런스"],
            "NEW ERA":["NEW ERA",""],
            "NIKE":["나이키",""],
            "NORTH SAILS":["노스세일즈",""],
            "OAKLEY":["오클리",""],
            "OFF-WHITE":["오프 화이트",""],
            "OFFICINE CREATIVE":["오피시네 크리에이티브",""],
            "OLIVER PEOPLES":["올리버 피플스",""],
            "ONLY":["ONLY",""],
            "ONLY & SONS":["ONLY & SONS",""],
            "ORIGINAL VINTAGE":["오리지널 빈티지",""],
            "ORLEBAR BROWN":["올레바브라운",""],
            "PALM ANGELS":["팜앤젤스",""],
            "PALOMA BARCELÓ":["PALOMA BARCELÓ",""],
            "PANTANETTI":["판타네티",""],
            "PARABOOT":["파라부트",""],
            "PARAJUMPERS":["파라점퍼스",""],
            "PARIS TEXAS":["파리 텍사스",""],
            "PATAGONIA":["파타고니아","빠타고니아"],
            "PATRIZIA PEPE":["페트리지아페페",""],
            "PAUL & SHARK":["폴앤샤크",""],
            "PAUL SMITH":["폴스미스",""],
            "PÀNCHIC":["PÀNCHIC",""],
            "PEOPLE OF SHIBUYA":["PEOPLE OF SHIBUYA",""],
            "PERSOL":["페르솔",""],
            "PERSONA BY MARINA RINALDI":["페르소나 바이 마리나 리날디",""],
            "PEUTEREY":["페트레이",""],
            "PHILIPP PLEIN":["필립플레인",""],
            "PHILIPPE MODEL":["필립모델",""],
            "PINKO":["핀코",""],
            "PLEIN SPORT":["플레인 스포츠",""],
            "POMME D'OR":["POMME D'OR",""],
            "PONS QUINTANA":["뽄스낀따나",""],
            "PRADA":["프라다",""],
            "PREMIATA":["프리미아타",""],
            "PROENZA SCHOULER":["프로엔자슐러",""],
            "PS BY PAUL SMITH":["피에스바이폴스미스",""],
            "PUMA":["퓨마",""],
            "PYREX":["PYREX",""],
            "R13":["R13",""],
            "RAINS":["레인스",""],
            "RALPH LAUREN":["랄프로렌","폴로랄프로렌"],
            "RED VALENTINO":["레드 발렌티노",""],
            "RED WING":["레드윙",""],
            "REEBOK":["리복",""],
            "REPETTO":["레페토",""],
            "RHUDE":["루드",""],
            "RICK OWENS":["릭오웬스","리고웬스"],
            "RINASCIMENTO":["RINASCIMENTO",""],
            "ROBERT CLERGERIE":["로베르 끌레제리",""],
            "ROBERTA DI CAMERINO":["로베리타 디 까메리노",""],
            "ROSSIGNOL":["로시뇰",""],
            "ROY ROGER'S":["로이 로저스",""],
            "RRD":["라드",""],
            "RUSLAN BAGINSKIY":["RUSLAN BAGINSKIY",""],
            "S.W.O.R.D 6.6.44":["소드 6.6.44",""],
            "SAINT LAURENT":["생로랑","쌩로랑"],
            "SALVATORE FERRAGAMO":["살바토레 페라가모","파라가모"],
            "SALVATORE SANTORO":["살바토레 산토로",""],
            "SANTONI":["산토니","싼토니"],
            "SAUCONY":["써코니",""],
            "SAVE THE DUCK":["세이브 더 덕","새이브더덕"],
            "SCHUTZ":["슈츠",""],
            "SEBAGO":["세바고",""],
            "SEE BY CHLOÉ":["씨 바이 끌로에","씨바이클로에"],
            "SELF-PORTRAIT":["SELF-PORTRAIT",""],
            "SERENGETI":["SERENGETI",""],
            "SERGIO ROSSI":["세르지오 로시",""],
            "SILVANO SASSETTI":["실바노 사세티",""],
            "SIVIGLIA":["세비야",""],
            "SOPHIA WEBSTER":["소피아웹스터",""],
            "SOPHIE HULME":["소피휼미",""],
            "STAND":["STAND",""],
            "STELLA MCCARTNEY":["스텔라맥카트니",""],
            "STOKTON":["스탁턴",""],
            "STONE ISLAND":["스톤아일랜드","돌섬"],
            "STUART WEITZMAN":["스튜어트 와이츠먼",""],
            "STUSSY":["스투시","스투씨"],
            "SUICOKE":["수이코크",""],
            "SUNDEK":["SUNDEK",""],
            "SUPER BY RETROSUPERFUTURE":["SUPER BY RETROSUPERFUTURE",""],
            "SUPERGA":["슈페르가",""],
            "TAGLIATORE":["딸리아토레",""],
            "TELFAR":["텔파","탤파"],
            "THE ATTICO":["THE ATTICO",""],
            "THE NORTH FACE":["더 노스페이스",""],
            "THOM BROWNE":["톰브라운",""],
            "THOM KROM":["톰크롬",""],
            "TIMBERLAND":["팀버랜드",""],
            "TOM FORD":["톰포드",""],
            "TOMMY HILFIGER":["타미힐피거",""],
            "TORY BURCH":["토리버치",""],
            "TRICKER'S":["트리커즈",""],
            "TRIPPEN":["트리픈",""],
            "TRUSSARDI":["트루사르디",""],
            "UGG":["어그",""],
            "UNRAVEL PROJECT":["언레이블 프로젝트",""],
            "VALENTINO GARAVANI":["VALENTINO GARAVANI",""],
            "VALSPORT":["발스포츠",""],
            "VANS":["반스",""],
            "VEJA":["베자",""],
            "VERSACE":["베르사체","베르사채"],
            "VERSACE COLLECTION":["베르사체컬렉션",""],
            "VERSACE JEANS":["베르사체 진",""],
            "VERSUS VERSACE":["베르수스 베르사체",""],
            "VETEMENTS":["베트멍","배트멍"],
            "VIA ROMA 15":["VIA ROMA 15",""],
            "VISION OF SUPER":["비전오브 슈퍼",""],
            "VOILE BLANCHE":["보일브랑쉐",""],
            "WINDSOR SMITH":["윈드솔스미스",""],
            "WOOLRICH":["울리치",""],
            "YEEZY":["YEEZY",""],
            "Z ZEGNA":["지제냐",""],
            "ZANELLATO":["자넬라토",""],
            "ZANONE":["자논",""],
        }

        small_category_dict = {
            "Coats":["코트",""],
            "Dresses":["드레스","원피스"],
            "Jackets":["자켓","재킷"],
            "Jeans":["진","청바지"],
            "Knitwear":["니트웨어",""],
            "Lingerie & Swimwear":["란제리&수영복","속옷"],
            "Shirts":["셔츠","남방"],
            "Skirts":["스커트","치마"],
            "T-shirts":["티셔츠",""],
            "Pants":["팬츠","바지"],
            "Boots":["부츠",""],
            "Flats":["플랫",""],
            "Heels":["힐",""],
            "Lace-Up Shoes":["레이스업 슈즈",""],
            "Loafers":["로퍼",""],
            "Sandals":["샌들","샌달"],
            "Sneakers":["스니커즈","운동화"],
            "Wedges":["웨지","가보시"],
            "Backpacks":["백팩","책가방"],
            "Belt Bags":["벨트백",""],
            "Clutches":["클러치",""],
            "Handbags":["핸드백","손가방"],
            "Shopping Bags":["쇼핑백",""],
            "Shoulder Bags":["숄더백",""],
            "Travel Bags":["트래블백",""],
            "Belts & Braces":["벨트&멜빵","허리띠"],
            "Jewelry":["주얼리","쥬얼리"],
            "Glasses":["안경","선글라스"],
            "Gloves":["장갑","글로브"],
            "Hats":["모자","햇"],
            "Scarves & Foulards":["스카프","머플러"],
            "Wallets":["지갑",""],
            "Suits":["수트","정장"],
            "Underwear & Swimwear":["언더웨어&수영복","속옷"],
            "Briefcases":["브리프케이스",""],
            "Messenger Bags":["메신저백",""],
            "Ties & Bowties":["넥타이",""],
        }

        medium_category_dict = {
            "clothing":["의류"],
            "shoes":["신발"],
            "bags":["가방"],
            "accessories":["액세서리"],
        }

        large_category_dict = {
            "WOMEN":["여성","여자"],
            "MEN":["남성","남자"]
        }



        for word in word_list:
            if word.encode().isalpha(): # 입력이 영어인 경우
                for key in brand_dict:
                    if word == key.replace(".","").replace("-","").replace(" ",""):
                        convert_word["brand"] = key
                        break
                    else:
                        if SequenceMatcher(None, key.replace(".","").replace("-","").replace(" ",""), word).ratio() >= 0.6:
                            convert_word["brand"] = key
                            break

                for key in small_category_dict:
                    if word == key.replace(".","").replace("-","").replace(" ",""):
                        convert_word["small_category"] = key
                        break
                    else:
                        if SequenceMatcher(None, key.replace(".","").replace("-","").replace(" ",""), word).ratio() >= 0.6:
                            convert_word["small_category"] = key
                            break

                for key in medium_category_dict:
                    if word == key.replace(".","").replace("-","").replace(" ",""):
                        convert_word["medium_category"] = key
                        break
                    else:
                        if SequenceMatcher(None, key.replace(".","").replace("-","").replace(" ",""), word).ratio() >= 0.6:
                            convert_word["medium_category"] = key
                            break

                for key in large_category_dict:
                    if word == key.replace(".","").replace("-","").replace(" ",""):
                        convert_word["large_category"] = key
                        break
                    else:
                        if SequenceMatcher(None, key.replace(".","").replace("-","").replace(" ",""), word).ratio() >= 0.6:
                            convert_word["large_category"] = key
                            break
            else: # 입력이 한글인 경우
                for key in brand_dict:
                    if word in brand_dict[key]:
                        convert_word["brand"] = key
                        break
                    else:
                        if SequenceMatcher(None, brand_dict[key][0].replace(" ",""), word).ratio() >= 0.6:
                            convert_word["brand"] = key
                            break

                for key in small_category_dict:
                    if word in small_category_dict[key]:
                        convert_word["small_category"] = key
                        break
                    else:
                        if SequenceMatcher(None, small_category_dict[key][0].replace(" ",""), word).ratio() >= 0.6:
                            convert_word["small_category"] = key
                            break
                
                for key in medium_category_dict:
                    if word in medium_category_dict[key]:
                        convert_word["medium_category"] = key
                        break
                    else:
                        if SequenceMatcher(None, medium_category_dict[key][0].replace(" ",""), word).ratio() >= 0.6:
                            convert_word["medium_category"] = key
                            break

                for key in large_category_dict:
                    if word in large_category_dict[key]:
                        convert_word["large_category"] = key
                        break
                    else:
                        if SequenceMatcher(None, large_category_dict[key][0].replace(" ",""), word).ratio() >= 0.6:
                            convert_word["large_category"] = key
                            break
        print(convert_word)

        if convert_word:
            if convert_word.get('brand'):
                products = products.filter(brand__icontains=convert_word["brand"])

            if convert_word.get('small_category'):
                products = products.filter(small_category__name__icontains=convert_word['small_category'])

            if convert_word.get('medium_category'):
                products = products.filter(small_category__medium_category__name__icontains=convert_word['medium_category'])

            if convert_word.get('large_category'):
                products = products.filter(small_category__medium_category__large_category__name__icontains=convert_word['large_category'])

        else:
            products = products.filter(brand__icontains=word)

        result = [{
            "itemImg"        : [image.url for image in product.image_set.all()],
            "itemBrand"      : product.brand,
            "itemName"       : product.name,
            "price"          : product.price,
            "sale_price"     : product.sale_price,
            "skuNum"         : product.sku_number,
            "product_id"     : product.id,
            "categorySmall"  : product.small_category.name,
            "categoryMedium" : product.small_category.medium_category.name,
            "gender"         : product.small_category.medium_category.large_category.name,
            "itemOption"     : [option.size for option in product.option_set.all()],
            "materials"      : [material.name for material in product.material_set.all()],

        } for product in products]

        return JsonResponse({'message': 'success', 'result': result, 'convert_word': convert_word}, status=200)