#!/usr/bin/env python3
"""
Copa do Mundo 2026 — Auto-update script
Roda via GitHub Actions a cada 2 horas.
Busca resultados da ESPN API, atualiza data.json e os arquivos .ics de assinatura.
"""
import urllib.request, json, os, base64, subprocess, sys, re
from datetime import datetime, timezone, timedelta

# ──────────────────────────────────────────────
# MATCHES (mesma lista do index.html)
# [id, date, timeBRT, phase, group, homeCode, awayCode, venue]
# ──────────────────────────────────────────────
MATCHES = [
  [1,'2026-06-11','16:00','GS','A','MX','ZA','Cidade do México'],
  [2,'2026-06-11','23:00','GS','A','KR','CZ','Guadalajara'],
  [3,'2026-06-12','16:00','GS','B','CA','BA','Toronto'],
  [4,'2026-06-12','22:00','GS','D','US','PY','Los Angeles'],
  [5,'2026-06-13','16:00','GS','B','QA','CH','San Francisco'],
  [6,'2026-06-13','19:00','GS','C','BR','MA','Nova York/NJ'],
  [7,'2026-06-13','22:00','GS','C','HT','GB-SCT','Boston'],
  [8,'2026-06-14','01:00','GS','D','AU','TR','Vancouver'],
  [9,'2026-06-14','14:00','GS','E','DE','CW','Houston'],
  [10,'2026-06-14','17:00','GS','F','NL','JP','Dallas'],
  [11,'2026-06-14','20:00','GS','E','CI','EC','Philadelphia'],
  [12,'2026-06-14','23:00','GS','F','SE','TN','Monterrey'],
  [13,'2026-06-15','13:00','GS','H','ES','CV','Atlanta'],
  [14,'2026-06-15','16:00','GS','G','BE','EG','Seattle'],
  [15,'2026-06-15','19:00','GS','H','SA','UY','Miami'],
  [16,'2026-06-15','22:00','GS','G','IR','NZ','Los Angeles'],
  [17,'2026-06-16','16:00','GS','I','FR','SN','Nova York/NJ'],
  [18,'2026-06-16','19:00','GS','I','IQ','NO','Boston'],
  [19,'2026-06-16','22:00','GS','J','AR','DZ','Kansas City'],
  [20,'2026-06-17','01:00','GS','J','AT','JO','San Francisco'],
  [21,'2026-06-17','14:00','GS','K','PT','CD','Houston'],
  [22,'2026-06-17','17:00','GS','L','GB-ENG','HR','Dallas'],
  [23,'2026-06-17','20:00','GS','L','GH','PA','Toronto'],
  [24,'2026-06-17','23:00','GS','K','UZ','CO','Cidade do México'],
  [25,'2026-06-18','13:00','GS','A','CZ','ZA','Atlanta'],
  [26,'2026-06-18','16:00','GS','B','CH','BA','Los Angeles'],
  [27,'2026-06-18','19:00','GS','B','CA','QA','Vancouver'],
  [28,'2026-06-18','22:00','GS','A','MX','KR','Guadalajara'],
  [29,'2026-06-19','16:00','GS','D','US','AU','Seattle'],
  [30,'2026-06-19','19:00','GS','C','GB-SCT','MA','Boston'],
  [31,'2026-06-19','21:30','GS','C','BR','HT','Philadelphia'],
  [32,'2026-06-20','00:00','GS','D','TR','PY','San Francisco'],
  [33,'2026-06-20','14:00','GS','F','NL','SE','Houston'],
  [34,'2026-06-20','17:00','GS','E','DE','CI','Toronto'],
  [35,'2026-06-20','21:00','GS','E','EC','CW','Kansas City'],
  [36,'2026-06-21','01:00','GS','F','TN','JP','Monterrey'],
  [37,'2026-06-21','13:00','GS','H','ES','SA','Atlanta'],
  [38,'2026-06-21','16:00','GS','G','BE','IR','Los Angeles'],
  [39,'2026-06-21','19:00','GS','H','UY','CV','Miami'],
  [40,'2026-06-21','22:00','GS','G','NZ','EG','Vancouver'],
  [41,'2026-06-22','14:00','GS','J','AR','AT','Dallas'],
  [42,'2026-06-22','18:00','GS','I','FR','IQ','Philadelphia'],
  [43,'2026-06-22','21:00','GS','I','NO','SN','Nova York/NJ'],
  [44,'2026-06-23','00:00','GS','J','JO','DZ','San Francisco'],
  [45,'2026-06-23','14:00','GS','K','PT','UZ','Houston'],
  [46,'2026-06-23','17:00','GS','L','GB-ENG','GH','Boston'],
  [47,'2026-06-23','20:00','GS','L','PA','HR','Toronto'],
  [48,'2026-06-23','23:00','GS','K','CO','CD','Guadalajara'],
  [49,'2026-06-24','16:00','GS','B','CH','CA','Vancouver'],
  [50,'2026-06-24','16:00','GS','B','BA','QA','Seattle'],
  [51,'2026-06-24','19:00','GS','C','GB-SCT','BR','Miami'],
  [52,'2026-06-24','19:00','GS','C','MA','HT','Atlanta'],
  [53,'2026-06-24','22:00','GS','A','CZ','MX','Cidade do México'],
  [54,'2026-06-24','22:00','GS','A','ZA','KR','Monterrey'],
  [55,'2026-06-25','17:00','GS','E','CW','CI','Philadelphia'],
  [56,'2026-06-25','17:00','GS','E','EC','DE','Nova York/NJ'],
  [57,'2026-06-25','20:00','GS','F','JP','SE','Dallas'],
  [58,'2026-06-25','20:00','GS','F','TN','NL','Kansas City'],
  [59,'2026-06-25','23:00','GS','D','TR','US','Los Angeles'],
  [60,'2026-06-25','23:00','GS','D','PY','AU','San Francisco'],
  [61,'2026-06-26','16:00','GS','I','NO','FR','Boston'],
  [62,'2026-06-26','16:00','GS','I','SN','IQ','Toronto'],
  [63,'2026-06-26','21:00','GS','H','CV','SA','Houston'],
  [64,'2026-06-26','21:00','GS','H','UY','ES','Guadalajara'],
  [65,'2026-06-27','00:00','GS','G','EG','IR','Seattle'],
  [66,'2026-06-27','00:00','GS','G','NZ','BE','Vancouver'],
  [67,'2026-06-27','18:00','GS','L','PA','GB-ENG','Nova York/NJ'],
  [68,'2026-06-27','18:00','GS','L','HR','GH','Philadelphia'],
  [69,'2026-06-27','20:30','GS','K','CO','PT','Miami'],
  [70,'2026-06-27','20:30','GS','K','CD','UZ','Atlanta'],
  [71,'2026-06-27','23:00','GS','J','DZ','AT','Kansas City'],
  [72,'2026-06-27','23:00','GS','J','JO','AR','Dallas'],
  [73,'2026-06-28','16:00','R32','','','','Los Angeles'],
  [74,'2026-06-29','14:00','R32','','','','Houston'],
  [75,'2026-06-29','17:30','R32','','','','Boston'],
  [76,'2026-06-29','22:00','R32','','','','Monterrey'],
  [77,'2026-06-30','14:00','R32','','','','Dallas'],
  [78,'2026-06-30','18:00','R32','','','','Nova York/NJ'],
  [79,'2026-06-30','22:00','R32','','','','Cidade do México'],
  [80,'2026-07-01','13:00','R32','','','','Atlanta'],
  [81,'2026-07-01','17:00','R32','','','','Seattle'],
  [82,'2026-07-01','21:00','R32','','','','San Francisco'],
  [83,'2026-07-02','16:00','R32','','','','Los Angeles'],
  [84,'2026-07-02','20:00','R32','','','','Toronto'],
  [85,'2026-07-03','00:00','R32','','','','Vancouver'],
  [86,'2026-07-03','15:00','R32','','','','Dallas'],
  [87,'2026-07-03','17:00','R32','','','','Atlanta'],
  [88,'2026-07-03','22:30','R32','','','','Kansas City'],
  [89,'2026-07-04','14:00','R16','','','','Houston'],
  [90,'2026-07-04','18:00','R16','','','','Philadelphia'],
  [91,'2026-07-05','17:00','R16','','','','Nova York/NJ'],
  [92,'2026-07-05','21:00','R16','','','','Cidade do México'],
  [93,'2026-07-06','15:00','R16','','','','Dallas'],
  [94,'2026-07-06','20:00','R16','','','','Seattle'],
  [95,'2026-07-07','13:00','R16','','','','Atlanta'],
  [96,'2026-07-07','17:00','R16','','','','Vancouver'],
  [97,'2026-07-09','17:00','QF','','','','Boston'],
  [98,'2026-07-10','16:00','QF','','','','Los Angeles'],
  [99,'2026-07-11','18:00','QF','','','','Miami'],
  [100,'2026-07-11','21:00','QF','','','','Kansas City'],
  [101,'2026-07-14','16:00','SF','','','','Dallas'],
  [102,'2026-07-15','16:00','SF','','','','Dallas'],
  [103,'2026-07-18','18:00','3P','','','','Miami'],
  [104,'2026-07-19','16:00','F','','','','Nova York/NJ'],
]

FLAGS = {
  'BR':'🇧🇷','MX':'🇲🇽','ZA':'🇿🇦','KR':'🇰🇷','CZ':'🇨🇿','CA':'🇨🇦','BA':'🇧🇦',
  'US':'🇺🇸','PY':'🇵🇾','QA':'🇶🇦','CH':'🇨🇭','HT':'🇭🇹','AU':'🇦🇺','TR':'🇹🇷',
  'DE':'🇩🇪','CW':'🇨🇼','NL':'🇳🇱','JP':'🇯🇵','CI':'🇨🇮','EC':'🇪🇨','SE':'🇸🇪',
  'TN':'🇹🇳','ES':'🇪🇸','CV':'🇨🇻','BE':'🇧🇪','EG':'🇪🇬','SA':'🇸🇦','UY':'🇺🇾',
  'IR':'🇮🇷','NZ':'🇳🇿','FR':'🇫🇷','SN':'🇸🇳','IQ':'🇮🇶','NO':'🇳🇴','AR':'🇦🇷',
  'DZ':'🇩🇿','AT':'🇦🇹','JO':'🇯🇴','PT':'🇵🇹','CD':'🇨🇩','HR':'🇭🇷','GB-ENG':'🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'GH':'🇬🇭','PA':'🇵🇦','UZ':'🇺🇿','CO':'🇨🇴','MA':'🇲🇦','GB-SCT':'🏴󠁧󠁢󠁳󠁣󠁴󠁿',
}

# ESPN team name → our code
ESPN_MAP = {
  'Mexico':'MX','South Africa':'ZA','South Korea':'KR','Czech Republic':'CZ',
  'Canada':'CA','Bosnia and Herzegovina':'BA','Bosnia-Herzegovina':'BA','Czech Republic':'CZ','Czechia':'CZ',
  'United States':'US','USA':'US','Paraguay':'PY','Qatar':'QA','Switzerland':'CH',
  'Haiti':'HT','Scotland':'GB-SCT','Australia':'AU','Turkey':'TR','Germany':'DE',
  'Curacao':'CW','Netherlands':'NL','Japan':'JP',"Ivory Coast":"CI","Cote d'Ivoire":'CI',
  "Côte d'Ivoire":'CI','Ecuador':'EC','Sweden':'SE','Tunisia':'TN','Spain':'ES',
  'Cape Verde':'CV','Belgium':'BE','Egypt':'EG','Saudi Arabia':'SA','Uruguay':'UY',
  'Iran':'IR','New Zealand':'NZ','France':'FR','Senegal':'SN','Iraq':'IQ',
  'Norway':'NO','Argentina':'AR','Algeria':'DZ','Austria':'AT','Jordan':'JO',
  'Portugal':'PT','DR Congo':'CD','Congo DR':'CD','DRC':'CD','Croatia':'HR',
  'England':'GB-ENG','Ghana':'GH','Panama':'PA','Uzbekistan':'UZ','Colombia':'CO',
  'Morocco':'MA','Brazil':'BR',
}

NAMES_PT = {
  'BR':'Brasil','MX':'México','ZA':'África do Sul','KR':'Coreia do Sul',
  'CZ':'Rep. Tcheca','CA':'Canadá','BA':'Bósnia-Herz.','US':'Estados Unidos',
  'PY':'Paraguai','QA':'Qatar','CH':'Suíça','HT':'Haiti','GB-SCT':'Escócia',
  'AU':'Austrália','TR':'Turquia','DE':'Alemanha','CW':'Curaçao','NL':'Países Baixos',
  'JP':'Japão','CI':'Costa do Marfim','EC':'Equador','SE':'Suécia','TN':'Tunísia',
  'ES':'Espanha','CV':'Cabo Verde','BE':'Bélgica','EG':'Egito','SA':'Arábia Saudita',
  'UY':'Uruguai','IR':'Irã','NZ':'Nova Zelândia','FR':'França','SN':'Senegal',
  'IQ':'Iraque','NO':'Noruega','AR':'Argentina','DZ':'Argélia','AT':'Áustria',
  'JO':'Jordânia','PT':'Portugal','CD':'Congo (RD)','HR':'Croácia',
  'GB-ENG':'Inglaterra','GH':'Gana','PA':'Panamá','UZ':'Uzbequistão','CO':'Colômbia',
  'MA':'Marrocos',
}

NAMES_IT = {
  'BR':'Brasile','MX':'Messico','ZA':'Sudafrica','KR':'Corea del Sud',
  'CZ':'Rep. Ceca','CA':'Canada','BA':'Bosnia-Erz.','US':'Stati Uniti',
  'PY':'Paraguay','QA':'Qatar','CH':'Svizzera','HT':'Haiti','GB-SCT':'Scozia',
  'AU':'Australia','TR':'Turchia','DE':'Germania','CW':'Curaçao','NL':'Paesi Bassi',
  'JP':'Giappone','CI':"Costa d'Avorio",'EC':'Ecuador','SE':'Svezia','TN':'Tunisia',
  'ES':'Spagna','CV':'Capo Verde','BE':'Belgio','EG':'Egitto','SA':'Arabia Saudita',
  'UY':'Uruguay','IR':'Iran','NZ':'Nuova Zelanda','FR':'Francia','SN':'Senegal',
  'IQ':'Iraq','NO':'Norvegia','AR':'Argentina','DZ':'Algeria','AT':'Austria',
  'JO':'Giordania','PT':'Portogallo','CD':'Congo (RD)','HR':'Croazia',
  'GB-ENG':'Inghilterra','GH':'Ghana','PA':'Panama','UZ':'Uzbekistan','CO':'Colombia',
  'MA':'Marocco',
}

RAI_IDS = set([1,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,
               89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104])

def name(code, lang):
    d = NAMES_IT if lang == 'it' else NAMES_PT
    return d.get(code, code) if code else ('A definire' if lang == 'it' else 'A definir')

def flag(code):
    return FLAGS.get(code, '🏳️')

# ──────────────────────────────────────────────
# ESPN API
# ──────────────────────────────────────────────
def fetch_espn():
    """Fetch current scoreboard from ESPN."""
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        return data.get("events", [])
    except Exception as e:
        print(f"ESPN fetch error: {e}", file=sys.stderr)
        return []

def parse_espn(events):
    """Parse ESPN events into results dict."""
    results = {}
    for ev in events:
        try:
            comps = ev.get("competitions", [{}])[0]
            competitors = comps.get("competitors", [])
            status_obj = comps.get("status", {})
            status_type = status_obj.get("type", {})
            status = status_type.get("shortDetail", "")
            state = status_type.get("state", "")  # pre / in / post

            if len(competitors) < 2:
                continue

            # Determine home/away
            home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

            home_name = home.get("team", {}).get("displayName", "")
            away_name = away.get("team", {}).get("displayName", "")
            home_code = ESPN_MAP.get(home_name, "")
            away_code = ESPN_MAP.get(away_name, "")

            if not home_code or not away_code:
                # Try abbreviation
                home_abbr = home.get("team", {}).get("abbreviation", "")
                away_abbr = away.get("team", {}).get("abbreviation", "")
                # Skip if still unknown
                if not home_code:
                    print(f"  Unknown team: {home_name} ({home_abbr})", file=sys.stderr)
                if not away_code:
                    print(f"  Unknown team: {away_name} ({away_abbr})", file=sys.stderr)
                continue

            home_score = home.get("score", "")
            away_score = away.get("score", "")

            # Map to our match id
            match_id = find_match_id(home_code, away_code)
            if match_id:
                results[str(match_id)] = {
                    "hs": int(home_score) if home_score != "" else None,
                    "as": int(away_score) if away_score != "" else None,
                    "status": "FT" if state == "post" else ("LIVE" if state == "in" else "NS"),
                    "detail": status,
                }
        except Exception as e:
            print(f"  parse error: {e}", file=sys.stderr)
    return results

def find_match_id(hc, ac):
    """Find our match ID given home and away codes."""
    for m in MATCHES:
        if m[5] == hc and m[6] == ac:
            return m[0]
        # also check reversed (in case ESPN has different home/away)
        if m[5] == ac and m[6] == hc:
            return m[0]
    return None

# ──────────────────────────────────────────────
# ICS GENERATION
# ──────────────────────────────────────────────
def fold(line):
    if len(line) <= 75:
        return line
    res, i = '', 0
    while i < line.length() if hasattr(line, 'length') else len(line):
        chunk_len = 75 if i == 0 else 74
        chunk = line[i:i+chunk_len]
        res += ('\r\n ' if i > 0 else '') + chunk
        i += len(chunk)
    return res

def fold_line(line):
    if len(line) <= 75:
        return line
    result = ''
    i = 0
    while i < len(line):
        chunk_len = 75 if i == 0 else 74
        chunk = line[i:i+chunk_len]
        result += ('\r\n ' if i > 0 else '') + chunk
        i += len(chunk)
    return result

def esc(s):
    return s.replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')

def brt_to_utc(date_str, time_str):
    y, mo, d = map(int, date_str.split('-'))
    h, mi = map(int, time_str.split(':'))
    dt = datetime(y, mo, d, h, mi, tzinfo=timezone(timedelta(hours=-3)))
    utc = dt.astimezone(timezone.utc)
    return utc.strftime('%Y%m%dT%H%M%SZ')

def brt_to_cest(time_str):
    h, mi = map(int, time_str.split(':'))
    ih = (h + 5) % 24
    nd = (h + 5) >= 24
    return ('+1 ' if nd else '') + f'{ih:02d}:{mi:02d}'

def gen_ics(lang, results, knockout):
    """Generate full ICS for subscription."""
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Copa2026//Auto-Update//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        f'X-WR-CALNAME:{"⚽ Mondiali FIFA 2026" if lang=="it" else "⚽ Copa do Mundo 2026"}',
        'X-WR-TIMEZONE:UTC',
        'X-APPLE-CALENDAR-COLOR:#C8A84B',
        f'REFRESH-INTERVAL;VALUE=DURATION:PT2H',
        f'X-PUBLISHED-TTL:PT2H',
    ]

    for m in MATCHES:
        mid, date, timeBRT, phase, group, hc_orig, ac_orig, venue = m

        # Use knockout override if available
        ko = knockout.get(str(mid), {})
        hc = ko.get('hc', hc_orig) or hc_orig
        ac = ko.get('ac', ac_orig) or ac_orig

        hName = name(hc, lang) if hc else ('A definire' if lang=='it' else 'A definir')
        aName = name(ac, lang) if ac else ('A definire' if lang=='it' else 'A definir')
        hFlag = flag(hc) if hc else '❓'
        aFlag = flag(ac) if ac else '❓'

        dtStart = brt_to_utc(date, timeBRT)
        # End +2h
        h, mi = map(int, timeBRT.split(':'))
        eh = (h + 2) % 24
        end_time = f'{eh:02d}:{mi:02d}'
        # If crosses midnight, advance date
        end_date = date
        if h + 2 >= 24:
            from datetime import datetime as dt2, timedelta as td
            d2 = dt2.strptime(date, '%Y-%m-%d') + td(days=1)
            end_date = d2.strftime('%Y-%m-%d')
        dtEnd = brt_to_utc(end_date, end_time)

        # Result info
        res = results.get(str(mid), {})
        hs = res.get('hs')
        as_ = res.get('as')
        status = res.get('status', 'NS')
        score_str = ''
        if status == 'FT' and hs is not None:
            score_str = f' [{hs}-{as_}]'
        elif status == 'LIVE' and hs is not None:
            score_str = f' 🔴 {hs}-{as_}'

        # Summary
        if hc:
            summary = f'{hFlag} {hName}{score_str} vs {aFlag} {aName}'
        else:
            phase_labels = {'R32':'Rodada de 32','R16':'Oitavas','QF':'Quartas','SF':'Semifinal','3P':'3º Lugar','F':'Final'}
            summary = f'🏆 Copa 2026 — {phase_labels.get(phase, phase)}'

        # Description
        watch_label = 'Dove vedere' if lang=='it' else 'Onde assistir'
        group_label = f'Grupo {group}' if group else {'R32':'Rodada de 32','R16':'Oitavas de Final','QF':'Quartas de Final','SF':'Semifinal','3P':'3º Lugar','F':'Grande Final'}.get(phase, phase)
        if lang == 'it':
            group_label = f'Gruppo {group}' if group else {'R32':'Turno dei 32','R16':'Ottavi di Finale','QF':'Quarti di Finale','SF':'Semifinale','3P':'Finale 3° Posto','F':'Finale'}.get(phase, phase)

        if lang == 'pt':
            bc = 'CazéTV (YouTube - grátis) + N Sports'
            if mid in {1,6,31,51} or phase in {'QF','SF','3P','F'}:
                bc += ' + Globo + SBT + SporTV + Globoplay'
        else:
            bc = 'DAZN'
            if mid in RAI_IDS:
                bc += ' + Rai 1 / RaiPlay (grátis)'

        desc = f'🏆 Copa do Mundo FIFA 2026\\n{group_label}\\n📍 {venue}\\n📺 {watch_label}: {bc}'
        if status == 'FT':
            desc += f'\\n✅ Resultado: {hs}-{as_}'
        elif status == 'LIVE':
            desc += f'\\n🔴 AO VIVO: {hs}-{as_}'

        lines.append('BEGIN:VEVENT')
        lines.append(fold_line(f'UID:wc2026-{mid}@copa2026.app'))
        lines.append(fold_line(f'DTSTART:{dtStart}'))
        lines.append(fold_line(f'DTEND:{dtEnd}'))
        lines.append(fold_line(f'SUMMARY:{esc(summary)}'))
        lines.append(fold_line(f'DESCRIPTION:{esc(desc)}'))
        lines.append(fold_line(f'LOCATION:{esc(venue)}'))
        lines.append('STATUS:CONFIRMED')
        lines.append('SEQUENCE:1')
        lines.append('END:VEVENT')

    lines.append('END:VCALENDAR')
    return '\r\n'.join(lines)

# ──────────────────────────────────────────────
# DATA.JSON
# ──────────────────────────────────────────────
def load_existing():
    if os.path.exists('data.json'):
        with open('data.json') as f:
            return json.load(f)
    return {"updated": "", "results": {}, "knockout": {}}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_ics(lang, content):
    fname = f'calendar-{"it" if lang=="it" else "pt"}.ics'
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  saved {fname}')

# ──────────────────────────────────────────────
# GIT COMMIT
# ──────────────────────────────────────────────
def git_commit():
    subprocess.run(['git', 'config', 'user.email', 'bot@copa2026.app'], check=True)
    subprocess.run(['git', 'config', 'user.name', 'Copa 2026 Bot 🤖'], check=True)
    subprocess.run(['git', 'add', 'data.json', 'calendar-pt.ics', 'calendar-it.ics'], check=True)
    result = subprocess.run(['git', 'diff', '--staged', '--quiet'])
    if result.returncode != 0:
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M')
        subprocess.run(['git', 'commit', '-m', f'update: resultados {now}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print('  ✓ pushed to GitHub')
    else:
        print('  no changes to commit')

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print(f'🔄 Copa 2026 Update — {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}')

    # Load existing data
    data = load_existing()

    # Fetch ESPN
    print('📡 Fetching ESPN API...')
    events = fetch_espn()
    print(f'  {len(events)} events found')

    new_results = parse_espn(events)
    print(f'  {len(new_results)} matches parsed')

    # Merge results (keep existing, update with new)
    for mid, res in new_results.items():
        data['results'][mid] = res

    data['updated'] = datetime.now(timezone.utc).isoformat()

    # Save data.json
    save_data(data)
    print('  saved data.json')

    # Generate ICS files
    print('📅 Generating ICS files...')
    save_ics('pt', gen_ics('pt', data['results'], data.get('knockout', {})))
    save_ics('it', gen_ics('it', data['results'], data.get('knockout', {})))

    # Commit and push
    print('📤 Pushing to GitHub...')
    git_commit()

    print('✅ Done!')

if __name__ == '__main__':
    main()
