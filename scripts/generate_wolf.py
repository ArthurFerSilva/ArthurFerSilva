import os
import json
import urllib.request
from pathlib import Path
from html import escape

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
            weekday
          }
        }
      }
    }
  }
}
"""

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({
        "query": query,
        "variables": {"login": USERNAME}
    }).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "wolf-contributions"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

if "errors" in result:
    raise RuntimeError(result["errors"])

weeks = result["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 40
TOP = 30

width = LEFT + len(weeks) * STEP + 30
height = TOP + 7 * STEP + 35

colors = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}

# Caminho que o lobo percorre
points = []
position = {}

index = 0

for row in range(7):
    columns = (
        range(len(weeks))
        if row % 2 == 0
        else range(len(weeks) - 1, -1, -1)
    )

    for week_index in columns:
        x = LEFT + week_index * STEP + CELL / 2
        y = TOP + row * STEP + CELL / 2

        points.append((x, y))
        position[(week_index, row)] = index
        index += 1

path = ""

for i, (x, y) in enumerate(points):
    if i == 0:
        path += f"M {x} {y}"
    else:
        path += f" L {x} {y}"

total_steps = max(1, len(points) - 1)

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}">'''
)

svg.append("""
<defs>

  <filter id="greenGlow"
          x="-100%"
          y="-100%"
          width="300%"
          height="300%">

    <feGaussianBlur stdDeviation="2.5"
                    result="blur"/>

    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>

  </filter>

</defs>
""")

# Fundo
svg.append(
    f'<rect width="{width}" height="{height}" rx="10" fill="#0d1117"/>'
)

# Grade de contribuições
for week_index, week in enumerate(weeks):

    for day in week["contributionDays"]:

        row = day["weekday"]

        x = LEFT + week_index * STEP
        y = TOP + row * STEP

        level = day["contributionLevel"]
        count = day["contributionCount"]
        date = escape(day["date"])

        fill = colors.get(level, "#161b22")

        animation = ""

        # Os commits "somem" quando o lobo passa
        if count > 0:

            step_index = position.get((week_index, row), 0)

            t = step_index / total_steps

            before = max(0, min(0.96, t))
            after = max(before + 0.005, min(0.97, t + 0.01))

            animation = f'''
            <animate
                attributeName="opacity"
                dur="18s"
                repeatCount="indefinite"
                values="1;1;0.12;0.12;1"
                keyTimes="0;{before:.4f};{after:.4f};0.98;1"
            />
            '''

        svg.append(
            f'''
            <rect
                x="{x}"
                y="{y}"
                width="{CELL}"
                height="{CELL}"
                rx="2"
                fill="{fill}">
                <title>{date}: {count} contribuições</title>
                {animation}
            </rect>
            '''
        )

# Lobo
svg.append(f'''
<g>

  <animateMotion
      dur="18s"
      repeatCount="indefinite"
      rotate="auto"
      path="{path}"
  />

  <g transform="translate(-19 -10)">

    <!-- sombra -->
    <ellipse
        cx="18"
        cy="16"
        rx="17"
        ry="4"
        fill="#000000"
        opacity="0.35"
    />

    <!-- cauda -->
    <path
        d="M7 11
           C0 5 -5 8 -8 5
           C-5 12 0 15 7 15 Z"
        fill="#272c32"
    />

    <!-- corpo -->
    <ellipse
        cx="16"
        cy="10"
        rx="14"
        ry="7"
        fill="#30363d"
        stroke="#111418"
        stroke-width="1"
    />

    <!-- parte escura do corpo -->
    <path
        d="M5 7
           C10 1 20 2 28 6
           C21 5 15 8 10 13
           Z"
        fill="#171b20"
    />

    <!-- pernas -->
    <path
        d="M10 14 L7 22 L11 22 L15 15 Z"
        fill="#20252b"
    >
      <animateTransform
          attributeName="transform"
          type="rotate"
          values="-15 12 14;15 12 14;-15 12 14"
          dur="0.35s"
          repeatCount="indefinite"/>
    </path>

    <path
        d="M22 14 L25 22 L29 22 L26 13 Z"
        fill="#171b20"
    >
      <animateTransform
          attributeName="transform"
          type="rotate"
          values="15 24 14;-15 24 14;15 24 14"
          dur="0.35s"
          repeatCount="indefinite"/>
    </path>

    <!-- pescoço -->
    <path
        d="M25 5
           L31 0
           L37 4
           L34 14
           L25 14 Z"
        fill="#292e34"
    />

    <!-- cabeça -->
    <path
        d="M28 3
           L29 -5
           L34 -1
           L38 -6
           L40 3
           L37 10
           L30 10
           L26 6 Z"
        fill="#343a40"
        stroke="#101418"
        stroke-width="1"
    />

    <!-- focinho -->
    <path
        d="M37 4
           L44 7
           L38 10
           L34 7 Z"
        fill="#181c20"
    />

    <!-- nariz -->
    <circle
        cx="43"
        cy="7"
        r="1.8"
        fill="#050708"
    />

    <!-- olhos verdes -->
    <circle
        cx="34"
        cy="3"
        r="1.6"
        fill="#39ff88"
        filter="url(#greenGlow)"
    />

    <circle
        cx="37"
        cy="3.5"
        r="1.2"
        fill="#39ff88"
        filter="url(#greenGlow)"
    />

    <!-- brilho extra -->
    <circle
        cx="34"
        cy="3"
        r="3"
        fill="#39ff88"
        opacity="0.12"
    />

  </g>

</g>
''')

svg.append("</svg>")

output = Path("assets/wolf-contributions.svg")
output.parent.mkdir(parents=True, exist_ok=True)

output.write_text(
    "\n".join(svg),
    encoding="utf-8"
)

print(f"Arquivo criado: {output}")
