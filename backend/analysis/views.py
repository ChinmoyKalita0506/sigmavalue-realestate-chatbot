import os
import re
import pandas as pd
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Load and normalize once
excel_path = os.path.join(settings.BASE_DIR, 'data', 'realestate_data.xlsx')
df = pd.read_excel(excel_path)
df.columns = [col.strip() for col in df.columns]

# Column constants
AREA_COL    = 'final location'
YEAR_COL    = 'year'
DEMAND_COL  = 'total_sales - igr'  # or whichever demand column you prefer

@api_view(['POST'])
def analyze_area(request):
    query = request.data.get('query', '').strip().lower()

    # 1) Compare two areas demand trends
    if query.startswith('compare'):
        # Regex to extract “area1 and area2”
        m = re.search(r'compare\s+(.+?)\s+and\s+(.+?)\s+demand', query)
        if not m:
            return Response({
                'summary': "Sorry, I couldn't parse those two areas. Please say: \"Compare A and B demand trends.\"",
                'chart': {'labels': [], 'series': []},
                'table': []
            })

        area1, area2 = m.group(1), m.group(2)

        # Filter each
        def series_for(area):
            sub = df[df[AREA_COL].str.lower() == area.lower()]
            return (
                sub.groupby(YEAR_COL)[DEMAND_COL]
                   .mean()
                   .reset_index()
                   .sort_values(YEAR_COL)
            )

        s1 = series_for(area1)
        s2 = series_for(area2)

        # Build common x‑axis of years
        years = sorted(set(s1[YEAR_COL]).union(s2[YEAR_COL]))

        # Map year→value (filling missing with 0 or NaN)
        def map_vals(series_df):
            return {int(r[YEAR_COL]): r[DEMAND_COL] for _, r in series_df.iterrows()}

        map1, map2 = map_vals(s1), map_vals(s2)
        vals1 = [round(map1.get(y, 0), 2) for y in years]
        vals2 = [round(map2.get(y, 0), 2) for y in years]

        summary = f"Demand trends for {area1.title()} vs {area2.title()} from {min(years)} to {max(years)}."
        return Response({
            'summary': summary,
            'chart': {
                'labels': [str(y) for y in years],
                'series': [
                  {'name': area1.title(), 'values': vals1},
                  {'name': area2.title(), 'values': vals2}
                ]
            },
            'table': []  # you can also return combined tables if desired
        })

    # 2) Last‑N‑years price growth (e.g. “Show price growth for Akurdi over last 3 years”)
    if 'last' in query and 'year' in query:
        m = re.search(r'for\s+(.+?)\s+over\s+last\s+(\d+)\s+years', query)
        if m:
            area, n_years = m.group(1), int(m.group(2))
            sub = df[df[AREA_COL].str.lower() == area.lower()]

            max_year = int(sub[YEAR_COL].max())
            cutoff   = max_year - n_years + 1
            filtered = sub[sub[YEAR_COL] >= cutoff]

            if filtered.empty:
                return Response({
                    'summary': f"No data for {area.title()} in the last {n_years} years.",
                    'chart': {'labels': [], 'values': []},
                    'table': []
                })

            # Price column for growth—choose whichever makes sense
            PRICE_COL = 'flat - weighted average rate'
            chart_df = (
                filtered.groupby(YEAR_COL)[PRICE_COL]
                        .mean()
                        .reset_index()
                        .sort_values(YEAR_COL)
            )

            summary = (
                f"{area.title()} price growth over the last {n_years} years "
                f"({cutoff}–{max_year})."
            )
            return Response({
                'summary': summary,
                'chart': {
                    'labels': chart_df[YEAR_COL].astype(str).tolist(),
                    'values': chart_df[PRICE_COL].round(2).tolist()
                },
                'table': filtered.to_dict(orient='records')
            })

    # 3) Single‑area analysis (“Analyze Wakad”)
    if AREA_COL in df.columns and 'analyze' in query:
        area = query.replace('analyze', '').strip()
        sub  = df[df[AREA_COL].str.lower() == area]

        if sub.empty:
            return Response({
                'summary': f"No data found for {area.title()}.",
                'chart': {'labels': [], 'values': []},
                'table': []
            })

        PRICE_COL = 'flat - weighted average rate'
        chart_df = (
            sub.groupby(YEAR_COL)[PRICE_COL]
               .mean()
               .reset_index()
               .sort_values(YEAR_COL)
        )
        summary = (
            f"{area.title()} has {len(sub)} records from "
            f"{int(sub[YEAR_COL].min())}–{int(sub[YEAR_COL].max())}. "
            "Average flat rate shows an upward trend."
        )
        return Response({
            'summary': summary,
            'chart': {
                'labels': chart_df[YEAR_COL].astype(str).tolist(),
                'values': chart_df[PRICE_COL].round(2).tolist()
            },
            'table': sub.to_dict(orient='records')
        })

    # 4) Fallback
    return Response({
        'summary': "Sorry, I couldn't understand that query.",
        'chart': {'labels': [], 'series': [], 'values': []},
        'table': []
    })
