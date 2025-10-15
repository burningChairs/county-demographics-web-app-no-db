from flask import Flask, request, render_template, flash
from markupsafe import Markup

import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    states = get_state_options()
    return render_template('home.html', state_options=states)

@app.route('/showFact')
def render_fact():
    states = get_state_options()
    state = request.args.get('state')
    county_selected = request.args.get('county')

    county = county_most_under_18(state)
    education_county = county_most_bachelors(state)
    counties = get_counties_for_state(state)

    fact = f"In {state}, the county with the highest percentage of under 18 year olds is {county}."
    edu_fact = f"In {state}, the county with the highest percentage of people with a Bachelor's degree or higher is {education_county}."

    county_fact = ""
    if county_selected:
        county_fact = get_county_population(state, county_selected)

    return render_template(
        'home.html',
        state_options=states,
        counties=Markup(counties),
        selected_state=state,
        selected_county=county_selected,
        funFact=fact,
        educationFact=edu_fact,
        countyFact=county_fact
    )

def get_state_options():
    with open('demographics.json') as demographics_data:
        counties = json.load(demographics_data)
    states = sorted({c["State"] for c in counties})
    options = ""
    for s in states:
        options += Markup(f'<option value="{s}">{s}</option>')
    return options

def county_most_under_18(state):
    with open('demographics.json') as demographics_data:
        counties = json.load(demographics_data)
    highest = 0
    county = ""
    for c in counties:
        if c["State"] == state:
            percent = c["Age"].get("Percent Under 18 Years", 0)
            if percent > highest:
                highest = percent
                county = c["County"]
    return county

def county_most_bachelors(state):
    with open('demographics.json') as demographics_data:
        counties = json.load(demographics_data)
    highest = 0
    county = ""
    for c in counties:
        if c["State"] == state:
            percent = c["Education"].get("Bachelor's Degree or Higher", 0)
            if percent > highest:
                highest = percent
                county = c["County"]
    return county

def get_counties_for_state(state):
    """Returns the HTML <option> elements for all counties in the given state."""
    with open('demographics.json') as demographics_data:
        counties = json.load(demographics_data)
    county_list = [c["County"] for c in counties if c["State"] == state]
    county_list = sorted(set(county_list))
    options = ""
    for c in county_list:
        options += Markup(f'<option value="{c}">{c}</option>')
    return options

def get_county_population(state, county_name):
    """Returns a fact string about the selected county."""
    with open('demographics.json') as demographics_data:
        counties = json.load(demographics_data)
    for c in counties:
        if c["State"] == state and c["County"] == county_name:
            population = c["Population"].get("2014 Population", "unknown")
            return f"The 2014 population of {county_name} is {population}."
    return "County data not found."

if __name__ == '__main__':
    app.run(debug=False)
