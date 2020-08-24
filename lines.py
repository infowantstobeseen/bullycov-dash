"""lines.py

Generates some sparklines or simple line chart as a Canvas2D plot
(sparkline) or a Pillow image (line chart).
"""
import math

style = "color: rgb(44,160,44)"
style = "color: #C33"
style = "color: #900; font-weight: bold"

def bank_data(data):
    """Using the median approach, bank to 45 degrees the data.  

    Returns the aspect ratio (w/h) for banking.
    """
    min_x = min(x for (x,y) in data)
    min_y = min(y for (x,y) in data)
    max_x = max(x for (x,y) in data)
    max_y = max(y for (x,y) in data)
    slopes = [math.fabs((data[i][1] - data[i-1][1])/(data[i][0] - data[i-1][0]))
              for i in range(1,len(data)) 
                if data[i][1] != data[i-1][1]
                and data[i][0] - data[i-1][0]]
    slopes.sort()
    if len(slopes) % 2 != 0:
        median_slope = slopes[len(slopes) // 2]
    else:
        median_slope = 0.5 * sum(slopes[len(slopes) // 2], slopes[len(slopes) // 2 - 1])
    return median_slope * (max_x - min_x) / (max_y - min_y)

def generate_canvas(canvas_id, data, colors, height, width=None):
    aspect = bank_data(data)
    min_x = min(x for (x,y) in data)
    min_y = min(y for (x,y) in data)
    max_x = max(x for (x,y) in data)
    max_y = max(y for (x,y) in data)
    h = height
    if max_y < 0.5:
        h = max_y * height / 0.5
    x_mapper = lambda x: (x - min_x) / (max_x - min_x) * width + 0.5
    y_mapper = lambda y: (max_y - y) / (max_y - min_y) * h + 0.5 + (height - h)

    if width is None:
        # Sparkline: Fit given line height
        width = round(height * aspect)
    else:
        # Fit best into given image
        if aspect <= 1:
            height = round(width / aspect)
        else:
            width = round(height * aspect)

    script = f"const canvas_{canvas_id} = document.getElementById('{canvas_id}');\n"
    script += f"const context_{canvas_id} = canvas_{canvas_id}.getContext('2d');\n"
    for index in range(1,len(data)):
        prev, prev_color = data[index-1], colors[index-1]
        curr, curr_color = data[index], colors[index]
        if index == 1 or prev_color != curr_color:
            if index != 1:
                script += f"context_{canvas_id}.stroke();\n"
            script += f"context_{canvas_id}.beginPath();\n context_{canvas_id}.strokeStyle = \"{curr_color}\";\n"
            script += f"context_{canvas_id}.moveTo({x_mapper(prev[0])}, {y_mapper(prev[1])});\n"
        script += f"context_{canvas_id}.lineTo({x_mapper(curr[0])}, {y_mapper(curr[1])});\n"
    script += f"context_{canvas_id}.stroke();\n"

    return f'<canvas id="{canvas_id}" height={height} width={width}></canvas><script>{script}</script>'

def generate_image(data, colors, width, height):
    pass
