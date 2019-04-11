## Dokumentácia ku projektu IPP 2018/2019 - 2. časť - interpret.py a test.php</br> Meno a priezvisko: Tomáš Sasák </br> Login: xsasak01

Obe tieto pod časti, boli implementované použitím objektovo-orientovaného programovania. 

### interpret.py
Interpret sa skladá z nasledujúcich tried:
* `Stats` - abstrakcia počítania štatistík pre rozšírenie STATI
* `Nil` - abstrakcia dátového typu jazyka IPPcode19 `nil`
* `Stack` - implementácia abstraktnej dátovej štruktúry zásobník
* `Instruction` - abstrakcia jednej inštrukcie zo súbora XML, jazyka IPPcode19. Obsahuje kód inštrukcie a parametre
* `Interpret` - abstrakcia interepretu, vykonáva inštrukcie diktované zdrojovým XML súborom

#### Stats
Obsahuje atribúty slúžiace, pre počítanie jednotlivých elementov interpretovaného zdrojového súboru. Taktiež, vypisuje štatistiky na základe požiadavku od uživateľa.

#### Nil
Jednoduchá trieda, obsahujúca reťazec "nil". Používaná pre simuláciu dátového typu `nil`. Ukladaná do premenných.

#### Stack
Implementácia abstraktnej dátovej štruktúry zásboník. Táto trieda je využívaná, pre ukladanie návratov inštrukcie `CALL` a `RETURN` (atribút `callStack`), taktiež pre dátový zásobník, s ktorým uživateľ môže pracovať (atribút `dataStack`) a hlavne nakoniec pre ukladanie rámcov a prácu s nimi (atribút `frameStack`).

#### Interpret
Srdcie interpretu. Skladá sa z lexéra, ktorý načítava inštrukcie z XML zdrojového súboru a kontroluje ich správnosť. Syntaktické a sémantické kontroly sú striedané medzi sebou. Pred začiatkom interpretácie, sa ciele skokov (`LABEL` inštrukcia), prehľadávajú a ukladajú do slovníka určené pre tieto ciele. Zoradí sa poradie inštrukcí podľa XML atribútu `ORDER` a skontroluje sa správna číselná postupnosť. Interpret má atribút `order`, ktorý obsahuje číslo aktuálne vykonávanej inštrukcie vzhľadom na atribút XML `ORDER`. Inštrukcie sa začínajú vykonávať v cykle, dokým interpret nenarazí na `EOF` flag, `EXIT` inštrukciu alebo sémenaticku/syntaktickú chybu. Toto vykonáva metóda `execute`, ktorá pomocou podmienky `if`, rozhodne, aká inštrukcia sa má vykonať. Každá táto inštrukcia má implementovanú svoju metódu v tejto triede. V každej jednej metóde priliehajúcej príkazu z `IPPcode19`, sa vykonáva syntaktická a sémantická kontrola v rôznych poradiach podľa potreby. Väčšina syntaktických kontrol, využíva regulárne výrazy. Sémantické kontroly, sa vykonávajú rôznymi spôsobmi, napr. kontrolou skoku na existujúce náveštia, existencie premennej v zázname atď. Jeden rámec (frame), predstavuje jeden záznam (dictionary). Toto slúži ako asociatívne pole, pre ukladanie uživateľských premenných (názvov) a ich hodnôt. Podľa zadaných príkazov, sa s týmito záznammi pracuje (prekladanie na rámcový zásobník, dočasný rámec na lokálny rámec, odoberanie atď.).

### test.php
Tester sa skladá z jednej triedy `tester` ktorá, obsahuje zopár metód. Zo začiatku sa skontrolujú argumenty, zapamätajú sa nastavenia uživateľa a jeho požiadavky. Skontroluje sa existencia súborov (parse/interpret/testy) a nasledovne sa buď rekurzívne, alebo nerekurzívne po prehľadávajú zadané priečinky, pre súbory `.src` (testy). Nasledovne, sa spustí exekúcia programov `parse.php`, `interpret.py` alebo oboch na základe požiadavkov a ich skutočné výsledky sa uložia do medzisúbrov. Nasledovne sú tieto súbory porovnávané s očakávanými výstupmi a ukladajú sa výsledky. Porovnávanie prebieha pomocou nástroja `diff` (v prípade interpretu a návratových kódov) a `jexamxml` (v prípade parse). Tieto výsledky sú uložené do poľa. Ako ďalší krok, sa začne generácia výsledkovej stránky v jazyku `HTML`. Pracuje sa s poľom výsledkov testov a podľa hodnoty `true` alebo `false`, sa určí či sa vygeneruje danému testu výsledok Success alebo Failed. Sú 2 druhy výsledkov, jeden pre výstup `.out` (stdout) a druhý pre výstup `.rc` (návratový kód). Oba druhy sú vložené v `HTML` súbore. `HTML` výstupný súbor ma jednoduchú a čitateľnú štruktúru, obsahuje aktuálny čas, umiestnenie testov, názvy testov, ich výsledky a celkový počet úspešných testov ku neúspešným. Success výsledok nastáva, ak sa súbor `.out` alebo `.rc`, rovná výstupu programu, pri Failed platí presný opak.