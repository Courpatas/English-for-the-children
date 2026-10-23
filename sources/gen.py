import sys, json, re
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from data1 import S
from data2 import S2

def parse(t):
    return [l.split("|") for l in t.strip("\n").split("\n")]

secdef = [
 ("v1", "Vocabulaire courant", "COM", S["1. Vocabulaire courant"]),
 ("v2", "Le corps humain", "BODY", S["2. Le corps humain"]),
 ("v3", "L'océan et la mer", "SEA", S["3. L'océan et la mer"]),
 ("v4", "Le surf", "SURF", S["4. Le surf"]),
 ("v5", "La maison", "HOME", S["5. La maison"]),
 ("v6", "Le sport", "SPORT", S["6. Le sport"]),
 ("v7", "Verbes irréguliers", "IRR", S2["7. Verbes irréguliers (infinitif | prétérit | participe passé | français)"]),
 ("v7b", "Verbes réguliers et modaux", "VERB", S2["7bis. Verbes réguliers et modaux (+ « -ed » au prétérit)"]),
 ("v8a", "Mots de liaison", "LINK", S2["8a. Mots de liaison"]),
 ("v8b", "Prépositions", "PREP", S2["8b. Prépositions"]),
 ("v8c", "Pronoms, questions, quantité", "WHO", S2["8c. Pronoms, questions et quantité"]),
 ("v9", "Famille et personnes", "FAM", S2["9. Famille et personnes"]),
 ("v10", "Nourriture et boissons", "FOOD", S2["10. Nourriture et boissons"]),
 ("v11", "L'école et les études", "SCHL", S2["11. L'école et les études"]),
 ("v12", "Vêtements", "WEAR", S2["12. Vêtements et accessoires"]),
 ("v13", "Temps, dates, nombres", "TIME", S2["13. Le temps, les dates et les nombres"]),
 ("v14", "Adjectifs et adverbes", "ADJ", S2["14. Adjectifs et adverbes courants"]),
 ("v15", "Nature, météo, animaux", "NATR", S2["15. Nature, météo et animaux"]),
 ("v16", "Ville et transports", "CITY", S2["16. Ville, transports et voyage"]),
 ("v17", "Technologie et médias", "TECH", S2["17. Technologie, médias et réseaux sociaux"]),
 ("v18", "Sentiments et expressions", "TALK", S2["18. Sentiments, opinions et expressions utiles"]),
]
colors = ["#ff6a4d","#19d3c5","#3d9bff","#ffd23f","#b07cff","#35e08f","#ff6fae","#ff9f43","#4dd0e1","#9ccc65","#f78fb3",
          "#5ea8ff","#ffb142","#7bed9f","#ff7f7f","#70a1ff","#eccc68","#a29bfe","#55efc4","#fd9644","#ff8aa1"]

DAYS = {"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"}
MONTHS = {"January","February","March","April","May","June","July","August","September","October","November","December"}
SEASONS = {"spring","summer","autumn","winter"}
NUMS = {"zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","thirteen","fourteen",
        "fifteen","sixteen","seventeen","eighteen","nineteen","twenty","thirty","forty","fifty","sixty","seventy","eighty",
        "ninety","a hundred","a thousand","a million"}
COLORS = {"red","blue","green","yellow","black","white","grey","brown","pink","purple"}
HUMAN = {"shy","lazy","brave","proud","clever / smart","stupid","polite","rude","generous","kind","tired","busy","ready",
         "famous","popular","strong","weak","young","old","fit","healthy"}
VERBX = {"be","have","do","get","let","set","mean","cost","lay","lie","ring","hang","lead","rise","happen","miss","kill",
         "tear","feed","shine","hit","shoot","shake","steal","show","hold","put","keep","fall"}
GEN = {
 "v5": {"neighbour","home","house","furniture","electricity","air conditioning","television","remote control"},
 "v2": {"blood","sweat","breath","voice","skeleton","freckle"},
 "v11": {"pupil / student","university","career","future job","canteen","playground","library","school","class / classroom","break","oral"},
 "v6": {"injury","cramp","stamina","strength","speed","fair play","warm-up","training","sport","competition","tournament"},
 "v16": {"traffic","journey","luggage","tourist","address","flight","map","traffic light"},
 "v15": {"weather","temperature","climate","environment","soil","fire","earth","nature"},
 "v4": {"beginner","instructor","lesson","forecast","stance","spot"},
 "v17": {"like","post","comment"},
 "v3": {"sea level","depth","salt","pollution","plastic"},
 "v12": {"clothes"},
 "v10": {"food","meal","tap water"},
}
NOSENT_PHRASE = set()

def classify(sid, e, f, idx):
    el = e.lower()
    if sid in ("v7", "v7b"):
        if el in ("need to / have to", "can / could", "must", "should"):
            return ""
        if el in VERBX and sid == "v7":
            return "verbx"
        if el in VERBX:
            return "verbx"
        return "verb"
    if sid in ("v8a", "v8b", "v8c", "v18"):
        if sid == "v18":
            if el in {"happy","sad","angry","afraid / scared","worried","nervous","surprised","bored","excited","jealous",
                      "lonely","embarrassed","disappointed"}:
                return "emotion"
        return ""
    if sid == "v13":
        if e in DAYS: return "day"
        if e in MONTHS: return "month"
        if e in SEASONS: return "season"
        if el in NUMS: return "number"
        return ""
    if sid == "v14":
        if el in COLORS: return "color"
        if el in HUMAN: return "human"
        if el in {"very","quite","too","enough","well","badly","quickly","slowly"}: return ""
        return "adj"
    if e.startswith("to "):
        return "verb"
    if sid == "v6":
        if idx in range(1, 27) and el not in {"sport"}: return "sportname"
        if el in {"fit", "healthy"}: return "human"
        if el in GEN["v6"]: return "gen"
        return "noun"
    if sid == "v3":
        if el in {"deep", "shallow", "salty"}: return "adj"
        if el in GEN["v3"]: return "gen"
        return "noun"
    if sid == "v4":
        if el in {"glassy", "choppy", "crowded"}: return "adj"
        if el in {"regular", "goofy", "left", "right"}: return ""
        if el in GEN["v4"]: return "gen"
        return "noun"
    if sid == "v10":
        if el in {"hungry", "thirsty"}: return "hungry"
        if el in {"delicious","tasty","sweet","sour","spicy","bitter","raw","fresh"}: return "taste"
        if el in GEN["v10"]: return "gen"
        return "noun"
    if sid == "v11":
        if el in {"maths","science","history","geography","french","english","art","pe"}: return "subject"
        if el in GEN["v11"]: return "gen"
        return "noun"
    if sid == "v15":
        if el in {"sunny","cloudy","rainy","windy","humid"}: return "wadj"
        if el in {"endangered"}: return ""
        if el in GEN["v15"]: return "gen"
        return "noun"
    if sid == "v16":
        if el in {"left","right","straight on","turn left","far","near"}: return ""
        if el in GEN["v16"]: return "gen"
        return "noun"
    if sid == "v17":
        if el in GEN["v17"]: return "gen"
        return "noun"
    if sid == "v1":
        return "noun"
    if sid in GEN and el in GEN[sid]:
        return "gen"
    return "noun"

secs = []
for i, (sid, name, tag, raw) in enumerate(secdef):
    rows = parse(raw)
    items = []
    for j, r in enumerate(rows):
        e, f = r[0], r[-1]
        it = {"e": e, "f": f}
        if sid == "v7":
            it["p"] = [r[1], r[2]]
        k = classify(sid, e, f, j)
        if k: it["k"] = k
        items.append(it)
    secs.append({"id": sid, "name": name, "tag": tag, "color": colors[i % len(colors)], "items": items})

cx = {}
for line in open(os.path.join(HERE,"cx.txt"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line: continue
    k, v = line.split("|", 1)
    cx[k] = v

# sanity: every cx key must match an entry
keys = {s["id"] + ":" + it["e"] for s in secs for it in s["items"]}
for k in cx:
    if k not in keys:
        print("CX KEY NOT FOUND:", k)

total = sum(len(s["items"]) for s in secs)
with_sent = 0
print("sections", len(secs), "entries", total)
data = {"secs": secs}
tpl = open(os.path.join(HERE,"template.html"), encoding="utf-8").read()
out = tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":"))) \
         .replace("/*CX*/null", json.dumps(cx, ensure_ascii=False, separators=(",", ":")))
open(sys.argv[1], "w", encoding="utf-8").write(out)
print("bytes", len(out.encode("utf-8")))
