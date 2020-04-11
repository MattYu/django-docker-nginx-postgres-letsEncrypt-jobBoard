from django.test import TestCase

from django.core.mail import EmailMessage
from matching import games as ranking
# Create your tests here.

def sendEmail():
    resident_prefs = {
        "A": ["C"],
        "S": ["C", "M"],
        "D": ["M", "C", "G"],
        "J": ["C", "G", "M"],
        "L": ["M", "C", "G"],
    }

    hospital_prefs = {
        "M": ["D", "J", "S", "L"],
        "C": ["D", "A", "S", "L", "J"],
        "G": ["D", "J", "L"],
    }

    capacities = {hosp: 2 for hosp in hospital_prefs}
    game = ranking.HospitalResident.create_from_dictionaries( resident_prefs, hospital_prefs, capacities)
    print(game.solve(optimal="hospital"))


sendEmail()