"""bullycov-dash.py

Processes scraped data to summarize last week's change in cases and the
history of test positivity since the beginning of Fall 2020. Uses
my scaper: https://github.com/infowantstobeseen/bullycov-scrape 
"""
import json

import requests

# Data location
data_url = "https://raw.githubusercontent.com/infowantstobeseen/bullycov-scrape/main/bullycov.json"

# Our template we'll format w/ Python string formatting
base_html = """<p style="font-size: 21px; margin: none; padding: none;">Last week, the Longest Health Center tested and processed 
    <span id="total">{total}</span> students and employees for COVID. Of those, 
    <span id="student_positive">{student_positive}</span> came back positive 
    (<span id="student_trend">{student_trend}</span> from last week) and 
    <span id="employee_positive">{employee_positive}</span> came back positive
    (<span id="employee_trend">{employee_trend}</span> from last week). The 
    <canvas id="positivity_total" width="1" height="1">{positivity_total}</canvas>overall positivity rate is 
    <span id="overall_positivity" style="{overall_positivity_style}">{overall_positivity}</span> whereas the 
    <canvas id="positivity_student" width="1" height="1">{positivity_student}</canvas>student and 
    <canvas id="positivity_employee" width="1" height="1">{positivity_employee}</canvas>employee 
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

def format_trend(data, base):
    if len(data) < 2:
        return "unchanged"
    else:
        # TODO
        pass

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
        style = "color: rgb(44,160,44)"
    elif value < 0.15:
        style = "color: #C33"
    else:
        style = "color: #900; font-weight: bold"
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
    to_format["student_trend"]=format_trend(data, "student")
    to_format["employee_positive"]=format_plural(last["employees_positive"], "employee")
    to_format["employee_trend"]=format_trend(data, "employee")
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
    return "\n".join(line.strip() for line in base_html.format(positivity_total="", 
                                                               positivity_student="", 
                                                               positivity_employee="", 
                                                               **to_format).split('\n'))

if __name__ == "__main__":
    data = pull_data()
    html = format_data(data)
    with open("bullycov-dash.html", "w") as htmlfile:
        htmlfile.write(html)
