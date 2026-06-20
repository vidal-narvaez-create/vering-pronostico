"""
build_pronostico.py
Descarga el fixture actualizado del Mundial 2026 (fuente publica, sin API key)
y regenera index.html a partir de template.html con los datos frescos.

Ejecutar: python3 build_pronostico.py
"""
import urllib.request, json, os, re

print("Descargando datos...")
url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
with urllib.request.urlopen(url, timeout=15) as r:
    data = json.loads(r.read())

matches = [m for m in data['matches'] if m.get('group', '').startswith('Group')]

NAME = {
    'Mexico': 'México', 'USA': 'Estados Unidos', 'Canada': 'Canadá', 'Brazil': 'Brasil',
    'Argentina': 'Argentina', 'Spain': 'España', 'France': 'Francia', 'Germany': 'Alemania',
    'Japan': 'Japón', 'Netherlands': 'Países Bajos', 'Portugal': 'Portugal', 'England': 'Inglaterra',
    'Croatia': 'Croacia', 'Morocco': 'Marruecos', 'Senegal': 'Senegal', 'Ecuador': 'Ecuador',
    'Uruguay': 'Uruguay', 'Colombia': 'Colombia', 'Paraguay': 'Paraguay', 'Switzerland': 'Suiza',
    'Belgium': 'Bélgica', 'Denmark': 'Dinamarca', 'Australia': 'Australia',
    'South Korea': 'Corea del Sur', 'Iran': 'Irán', 'Saudi Arabia': 'Arabia Saudita',
    'Tunisia': 'Túnez', 'Ghana': 'Ghana', 'Ivory Coast': 'Costa de Marfil', 'Egypt': 'Egipto',
    'Algeria': 'Argelia', 'Norway': 'Noruega', 'Turkey': 'Turquía', 'Scotland': 'Escocia',
    'Panama': 'Panamá', 'Haiti': 'Haití', 'South Africa': 'Sudáfrica',
    'Czech Republic': 'Rep. Checa', 'Bosnia & Herzegovina': 'Bosnia', 'Qatar': 'Qatar',
    'Curacao': 'Curaçao', 'Sweden': 'Suecia', 'New Zealand': 'Nueva Zelanda',
    'Cape Verde': 'Cabo Verde', 'Iraq': 'Irak', 'Jordan': 'Jordania', 'DR Congo': 'Congo DR',
    'Uzbekistan': 'Uzbekistán', 'Austria': 'Austria'
}
MONTHS = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
          '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}

def es(n):
    return NAME.get(n, n)

def fD(s):
    if not s:
        return ''
    p = s.split('-')
    return str(int(p[2])) + ' ' + MONTHS.get(p[1], p[1])

def fCity(ground):
    if not ground:
        return ''
    g = ground.lower()
    city_map = {
        'lumen field': 'Seattle', 'sofi stadium': 'Los Angeles (Inglewood)',
        "levi's stadium": 'San Francisco Bay Area (Santa Clara)', 'bc place': 'Vancouver',
        'at&t stadium': 'Dallas (Arlington)', 'arrowhead stadium': 'Kansas City',
        'nrg stadium': 'Houston', 'azteca stadium': 'Mexico City',
        'estadio akron': 'Guadalajara (Zapopan)', 'estadio bbva': 'Monterrey (Guadalupe)',
        'mercedes-benz stadium': 'Atlanta', 'hard rock stadium': 'Miami (Miami Gardens)',
        'gillette stadium': 'Boston (Foxborough)', 'metlife stadium': 'New York/New Jersey (East Rutherford)',
        'lincoln financial field': 'Philadelphia', 'bmo field': 'Toronto',
    }
    for key, city in city_map.items():
        if key in g:
            return city
    return ground

def fT_py(time_str):
    # JSON trae hora base, +4 = hora Paraguay
    if not time_str:
        return ''
    try:
        parts = time_str.split(':')
        local_h = int(parts[0])
        local_m = int(parts[1][:2]) if len(parts) > 1 else 0
        py_h = (local_h + 4) % 24
        return f"{py_h:02d}:{local_m:02d}"
    except Exception:
        return time_str

out = []
for i, m in enumerate(matches):
    sc = m.get('score', {}).get('ft')
    goals1 = [{'name': g.get('name', ''), 'minute': str(g.get('minute', ''))} for g in (m.get('goals1') or [])]
    goals2 = [{'name': g.get('name', ''), 'minute': str(g.get('minute', ''))} for g in (m.get('goals2') or [])]
    ground = m.get('ground', '')
    city = fCity(ground)
    time_py = fT_py(m.get('time', ''))

    out.append({
        'id': i,
        'g': m['group'].replace('Group ', ''),
        'a': es(m.get('team1', '')),
        'b': es(m.get('team2', '')),
        'date': fD(m.get('date', '')),
        'dateRaw': m.get('date', ''),
        'time': time_py,
        'city': city,
        'ga': sc[0] if sc else None,
        'gb': sc[1] if sc else None,
        'goals1': goals1,
        'goals2': goals2,
        'round': m.get('round', '')
    })

jugados = sum(1 for m in out if m['ga'] is not None)
print(f"Partidos jugados: {jugados} de {len(out)}")

with open('template.html', encoding='utf-8') as f:
    tmpl = f.read()

DATA = 'const REAL_MATCHES = ' + json.dumps(out, ensure_ascii=False) + ';'

result = re.sub(
    r'const REAL_MATCHES = \[.*?\];',
    lambda m: DATA,
    tmpl, count=1, flags=re.DOTALL
)

if result == tmpl:
    print("ERROR: no se encontro el marcador const REAL_MATCHES en template.html")
else:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"Listo! {jugados} jugados de {len(out)} -> index.html actualizado")
