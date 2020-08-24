"""bullycov-dash.py

Processes scraped data to summarize last week's change in cases and the
history of test positivity since the beginning of Fall 2020. Uses
my scaper: https://github.com/infowantstobeseen/bullycov-scrape 
"""
import json

import requests

from lines import generate_canvas

# Data location
data_url = "https://raw.githubusercontent.com/infowantstobeseen/bullycov-scrape/main/bullycov.json"

# Our template we'll format w/ Python string formatting
base_html = """<p style="font-size: 21px; margin: none; padding: none;">Last week, the Longest Health Center tested and processed 
    <span id="total">{total}</span> students and employees for COVID. Of those, 
    <span id="student_positive">{student_positive}</span> came back positive 
    (<span id="student_trend">{student_trend}</span> from last week) and 
    <span id="employee_positive">{employee_positive}</span> came back positive
    (<span id="employee_trend">{employee_trend}</span> from last week). The 
    {positivity_total}overall positivity rate is 
    <span id="overall_positivity" style="{overall_positivity_style}">{overall_positivity}</span> whereas the 
    {positivity_student}student and {positivity_employee}employee 
    positivity rates are <span id="student_positivity" style="{student_positivity_style}">{student_positivity}</span> 
    and <span id="employee_positivity" style="{employee_positivity_style}">{employee_positivity}</span> 
    respectively.</p>
    """

def pull_data():
    """Pull the JSON from the github repository."""
    page = requests.get(data_url)
    page.raise_for_status()
    return json.loads(page.content)

def format_plural(value, base):
    """Format English purals: No for values of 1, yes for everything else."""
    if value != 1:
        return f"{value} {base}s"
    else:
        return f"1 {base}"

def format_trend(data, key):
    if len(data) < 2:
        return "unchanged"
    else:
        penultimate, last = [d[key] for d in data[-2:]]
        if penultimate < last:
            return "increased"
        elif penultimate == last:
            return "unchanged"
        else:
            return "decreased"

def color(value):
    if value < 0.05:
        return "rgb(44,160,44)"
    elif value < 0.15:
        return "#C33"
    else:
        return "#900"
     
def format_positivity(value):
    """Format positivity.

    Color is based upon the positivity value:
        - Less than 5% is green
        - More then 5% but less then 15 is red 
        - 15% or more is bold, dark red
    These thresholds are from the World Health Organization (for the 5%)
    for a worrisome value and Johns Hopkins (for the 15%) for a very
    worrisome value.
    """
    positivity = f"{value:.1%}"
    if value < 0.05:
        style = f"color: {color(value)}"
    elif value < 0.15:
        style = f"color: {color(value)}"
    else:
        style = f"color: {color(value)}; font-weight: bold"
    return positivity, style

def format_data(data):
    """Given the data, summarize the latest week's tests and overall trend of 
       positivity."""
    last = data[-1]
    employees_total = last["employees_positive"] + last["employees_negative"]
    students_total  = last["students_positive"]  + last["students_negative"]
    to_format = {}
    to_format["total"]=employees_total + students_total
    to_format["student_positive"]=format_plural(last["students_positive"], "student")
    to_format["student_trend"]=format_trend(data, "students_positive")
    to_format["employee_positive"]=format_plural(last["employees_positive"], "employee")
    to_format["employee_trend"]=format_trend(data, "employees_positive")
    positivity, style = format_positivity((last["students_positive"] + last["employees_positive"])
                                         /(employees_total + students_total))
    to_format["overall_positivity_style"]=style
    to_format["overall_positivity"]=positivity
    positivity, style = format_positivity(last["students_positive"] / students_total)
    to_format["student_positivity_style"]=style
    to_format["student_positivity"]=positivity
    positivity, style = format_positivity(last["employees_positive"] / employees_total)
    to_format["employee_positivity_style"]=style
    to_format["employee_positivity"]=positivity
    to_format["positivity_total"]=generate_canvas(
        "positivity_total", 
        [(i, (data[i]["employees_positive"] + data[i]["students_positive"]) 
             / (data[i]["employees_positive"] + data[i]["students_positive"] + data[i]["employees_negative"] + data[i]["students_negative"])) 
        for i in range(len(data))],
        [color((datum["employees_positive"] + datum["students_positive"]) 
             / (datum["employees_positive"] + datum["students_positive"] + datum["employees_negative"] + datum["students_negative"])) 
        for datum in data],
        21)
    to_format["positivity_student"]=generate_canvas(
        "positivity_student", 
        [(i, data[i]["students_positive"] / (data[i]["students_positive"] + data[i]["students_negative"])) 
        for i in range(len(data))],
        [color(datum["students_positive"] / (datum["students_positive"] +  datum["students_negative"])) 
        for datum in data],
        21)
    to_format["positivity_employee"]=generate_canvas(
        "positivity_employee", 
        [(i, data[i]["employees_positive"] / (data[i]["employees_positive"] + data[i]["employees_negative"])) 
        for i in range(len(data))],
        [color(datum["employees_positive"] / (datum["employees_positive"] +  datum["employees_negative"])) 
        for datum in data],
        21)
    return "\n".join(line.strip() for line in base_html.format(**to_format).split('\n'))

if __name__ == "__main__":
    data = pull_data()
    html = format_data(data)
    with open("bullycov-dash.html", "w") as htmlfile:
        htmlfile.write(html)
