"""Seed script: inserts IPL 2025 players and upcoming matches into the database."""

import asyncio
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from server.app.core.database import async_session_factory
from server.app.models.player import Player, PlayerRole
from server.app.models.match import Match, MatchStatus

MI = "Mumbai Indians"
CSK = "Chennai Super Kings"
DC = "Delhi Capitals"
GT = "Gujarat Titans"
KKR = "Kolkata Knight Riders"
LSG = "Lucknow Super Giants"
PBKS = "Punjab Kings"
RR = "Rajasthan Royals"
RCB = "Royal Challengers Bengaluru"
SRH = "Sunrisers Hyderabad"

PLAYERS = [
    # Mumbai Indians (IPL 2026 actual squad from ESPNcricinfo)
    # Batters
    ("Rohit Sharma", PlayerRole.BATSMAN, MI, 10.0),
    ("Suryakumar Yadav", PlayerRole.BATSMAN, MI, 10.0),
    ("Quinton de Kock", PlayerRole.WICKET_KEEPER, MI, 9.5),
    ("Ryan Rickelton", PlayerRole.WICKET_KEEPER, MI, 8.0),
    ("Robin Minz", PlayerRole.WICKET_KEEPER, MI, 7.0),
    ("Sherfane Rutherford", PlayerRole.BATSMAN, MI, 8.0),
    ("Danish Malewar", PlayerRole.BATSMAN, MI, 6.5),
    # Allrounders
    ("Hardik Pandya", PlayerRole.ALL_ROUNDER, MI, 10.5),
    ("Tilak Varma", PlayerRole.ALL_ROUNDER, MI, 9.0),
    ("Will Jacks", PlayerRole.ALL_ROUNDER, MI, 9.0),
    ("Corbin Bosch", PlayerRole.ALL_ROUNDER, MI, 8.0),
    ("Mitchell Santner", PlayerRole.ALL_ROUNDER, MI, 8.5),
    ("Shardul Thakur", PlayerRole.ALL_ROUNDER, MI, 8.0),
    ("Naman Dhir", PlayerRole.ALL_ROUNDER, MI, 7.5),
    ("Raj Bawa", PlayerRole.ALL_ROUNDER, MI, 7.0),
    ("Atharva Ankolekar", PlayerRole.ALL_ROUNDER, MI, 7.0),
    ("Mayank Rawat", PlayerRole.ALL_ROUNDER, MI, 6.5),
    # Bowlers
    ("Jasprit Bumrah", PlayerRole.BOWLER, MI, 10.5),
    ("Trent Boult", PlayerRole.BOWLER, MI, 9.0),
    ("Deepak Chahar", PlayerRole.BOWLER, MI, 8.5),
    ("AM Ghazanfar", PlayerRole.BOWLER, MI, 7.5),
    ("Mayank Markande", PlayerRole.BOWLER, MI, 7.0),
    ("Ashwani Kumar", PlayerRole.BOWLER, MI, 6.5),
    ("Mohd Izhar", PlayerRole.BOWLER, MI, 6.0),
    ("Raghu Sharma", PlayerRole.BOWLER, MI, 6.5),

    # Chennai Super Kings (IPL 2026 actual squad from ESPNcricinfo)
    # Batters
    ("Ruturaj Gaikwad", PlayerRole.BATSMAN, CSK, 10.0),
    ("Sanju Samson", PlayerRole.WICKET_KEEPER, CSK, 9.5),
    ("MS Dhoni", PlayerRole.WICKET_KEEPER, CSK, 9.5),
    ("Sarfaraz Khan", PlayerRole.BATSMAN, CSK, 8.5),
    ("Dewald Brevis", PlayerRole.BATSMAN, CSK, 8.0),
    ("Ayush Mhatre", PlayerRole.BATSMAN, CSK, 7.0),
    ("Urvil Patel", PlayerRole.WICKET_KEEPER, CSK, 7.0),
    ("Kartik Sharma", PlayerRole.WICKET_KEEPER, CSK, 6.0),
    # Allrounders
    ("Shivam Dube", PlayerRole.ALL_ROUNDER, CSK, 9.0),
    ("Matthew Short", PlayerRole.ALL_ROUNDER, CSK, 8.5),
    ("Jamie Overton", PlayerRole.ALL_ROUNDER, CSK, 8.5),
    ("Anshul Kamboj", PlayerRole.ALL_ROUNDER, CSK, 7.5),
    ("Zak Foulkes", PlayerRole.ALL_ROUNDER, CSK, 7.0),
    ("Ramakrishna Ghosh", PlayerRole.ALL_ROUNDER, CSK, 7.0),
    ("Aman Khan", PlayerRole.ALL_ROUNDER, CSK, 7.0),
    ("Prashant Veer", PlayerRole.ALL_ROUNDER, CSK, 6.5),
    # Bowlers
    ("Khaleel Ahmed", PlayerRole.BOWLER, CSK, 8.5),
    ("Matt Henry", PlayerRole.BOWLER, CSK, 8.0),
    ("Rahul Chahar", PlayerRole.BOWLER, CSK, 8.0),
    ("Akeal Hosein", PlayerRole.BOWLER, CSK, 7.5),
    ("Noor Ahmad", PlayerRole.BOWLER, CSK, 7.5),
    ("Shreyas Gopal", PlayerRole.BOWLER, CSK, 7.0),
    ("Gurjapneet Singh", PlayerRole.BOWLER, CSK, 6.5),
    ("Mukesh Choudhary", PlayerRole.BOWLER, CSK, 6.5),

    # Delhi Capitals (IPL 2026 actual squad from ESPNcricinfo)
    # Batters
    ("KL Rahul", PlayerRole.WICKET_KEEPER, DC, 10.0),
    ("Ben Duckett", PlayerRole.WICKET_KEEPER, DC, 9.0),
    ("Karun Nair", PlayerRole.BATSMAN, DC, 8.5),
    ("David Miller", PlayerRole.BATSMAN, DC, 8.5),
    ("Pathum Nissanka", PlayerRole.BATSMAN, DC, 8.0),
    ("Prithvi Shaw", PlayerRole.BATSMAN, DC, 7.5),
    ("Nitish Rana", PlayerRole.BATSMAN, DC, 7.5),
    ("Tristan Stubbs", PlayerRole.WICKET_KEEPER, DC, 8.0),
    ("Abishek Porel", PlayerRole.WICKET_KEEPER, DC, 7.0),
    ("Sahil Parakh", PlayerRole.BATSMAN, DC, 6.0),
    # Allrounders
    ("Axar Patel", PlayerRole.ALL_ROUNDER, DC, 9.5),
    ("Ashutosh Sharma", PlayerRole.ALL_ROUNDER, DC, 7.5),
    ("Sameer Rizvi", PlayerRole.ALL_ROUNDER, DC, 7.0),
    ("Ajay Mandal", PlayerRole.ALL_ROUNDER, DC, 6.5),
    ("Madhav Tiwari", PlayerRole.ALL_ROUNDER, DC, 6.5),
    # Bowlers
    ("Mitchell Starc", PlayerRole.BOWLER, DC, 10.0),
    ("Kuldeep Yadav", PlayerRole.BOWLER, DC, 9.0),
    ("Kyle Jamieson", PlayerRole.BOWLER, DC, 8.0),
    ("Lungi Ngidi", PlayerRole.BOWLER, DC, 8.0),
    ("T Natarajan", PlayerRole.BOWLER, DC, 7.5),
    ("Dushmantha Chameera", PlayerRole.BOWLER, DC, 7.5),
    ("Mukesh Kumar", PlayerRole.BOWLER, DC, 7.0),
    ("Auqib Nabi", PlayerRole.BOWLER, DC, 6.5),
    ("Vipraj Nigam", PlayerRole.BOWLER, DC, 6.0),
    ("Tripurana Vijay", PlayerRole.BOWLER, DC, 6.0),

    # Gujarat Titans (IPL 2026 actual squad from ESPNcricinfo)
    # Batters
    ("Shubman Gill", PlayerRole.BATSMAN, GT, 10.5),
    ("Jos Buttler", PlayerRole.WICKET_KEEPER, GT, 10.0),
    ("Sai Sudharsan", PlayerRole.BATSMAN, GT, 8.5),
    ("M Shahrukh Khan", PlayerRole.BATSMAN, GT, 8.0),
    ("Tom Banton", PlayerRole.WICKET_KEEPER, GT, 7.5),
    ("Anuj Rawat", PlayerRole.WICKET_KEEPER, GT, 7.0),
    ("Kumar Kushagra", PlayerRole.WICKET_KEEPER, GT, 6.5),
    # Allrounders
    ("Rashid Khan", PlayerRole.ALL_ROUNDER, GT, 10.0),
    ("Jason Holder", PlayerRole.ALL_ROUNDER, GT, 8.5),
    ("Glenn Phillips", PlayerRole.ALL_ROUNDER, GT, 8.5),
    ("Washington Sundar", PlayerRole.ALL_ROUNDER, GT, 8.0),
    ("Rahul Tewatia", PlayerRole.ALL_ROUNDER, GT, 7.5),
    ("Manav Suthar", PlayerRole.ALL_ROUNDER, GT, 7.0),
    ("Nishant Sindhu", PlayerRole.ALL_ROUNDER, GT, 6.5),
    # Bowlers
    ("Kagiso Rabada", PlayerRole.BOWLER, GT, 10.0),
    ("Mohammed Siraj", PlayerRole.BOWLER, GT, 9.0),
    ("Prasidh Krishna", PlayerRole.BOWLER, GT, 8.0),
    ("Ishant Sharma", PlayerRole.BOWLER, GT, 7.0),
    ("Gurnoor Brar", PlayerRole.BOWLER, GT, 7.0),
    ("Arshad Khan", PlayerRole.BOWLER, GT, 6.5),
    ("Sai Kishore", PlayerRole.BOWLER, GT, 7.0),
    ("Luke Wood", PlayerRole.BOWLER, GT, 7.0),
    ("Ashok Sharma", PlayerRole.BOWLER, GT, 6.0),
    ("Prithvi Raj", PlayerRole.BOWLER, GT, 6.0),
    ("Jayant Yadav", PlayerRole.BOWLER, GT, 6.5),

    # Kolkata Knight Riders (IPL 2026 actual squad from ESPNcricinfo)
    # Batters
    ("Ajinkya Rahane", PlayerRole.BATSMAN, KKR, 8.5),
    ("Rinku Singh", PlayerRole.BATSMAN, KKR, 9.0),
    ("Finn Allen", PlayerRole.BATSMAN, KKR, 8.5),
    ("Rovman Powell", PlayerRole.BATSMAN, KKR, 8.0),
    ("Manish Pandey", PlayerRole.BATSMAN, KKR, 7.5),
    ("Rahul Tripathi", PlayerRole.BATSMAN, KKR, 7.5),
    ("Angkrish Raghuvanshi", PlayerRole.BATSMAN, KKR, 7.0),
    ("Ramandeep Singh", PlayerRole.BATSMAN, KKR, 7.0),
    ("Sarthak Ranjan", PlayerRole.BATSMAN, KKR, 6.5),
    ("Tim Seifert", PlayerRole.WICKET_KEEPER, KKR, 7.5),
    ("Tejasvi Dahiya", PlayerRole.WICKET_KEEPER, KKR, 6.5),
    # Allrounders
    ("Sunil Narine", PlayerRole.ALL_ROUNDER, KKR, 9.5),
    ("Cameron Green", PlayerRole.ALL_ROUNDER, KKR, 9.0),
    ("Rachin Ravindra", PlayerRole.ALL_ROUNDER, KKR, 8.5),
    ("Anukul Roy", PlayerRole.ALL_ROUNDER, KKR, 7.0),
    ("Daksh Kamra", PlayerRole.ALL_ROUNDER, KKR, 6.5),
    # Bowlers
    ("Varun Chakravarthy", PlayerRole.BOWLER, KKR, 9.0),
    ("Matheesha Pathirana", PlayerRole.BOWLER, KKR, 9.0),
    ("Harshit Rana", PlayerRole.BOWLER, KKR, 8.0),
    ("Blessing Muzarabani", PlayerRole.BOWLER, KKR, 7.5),
    ("Akash Deep", PlayerRole.BOWLER, KKR, 7.5),
    ("Umran Malik", PlayerRole.BOWLER, KKR, 7.5),
    ("Vaibhav Arora", PlayerRole.BOWLER, KKR, 7.0),
    ("Kartik Tyagi", PlayerRole.BOWLER, KKR, 6.5),
    ("Prashant Solanki", PlayerRole.BOWLER, KKR, 6.5),

    # Lucknow Super Giants (IPL 2026 actual squad from ESPNcricinfo)
    ("Rishabh Pant", PlayerRole.WICKET_KEEPER, LSG, 10.5),
    ("Nicholas Pooran", PlayerRole.WICKET_KEEPER, LSG, 9.0),
    ("Aiden Markram", PlayerRole.BATSMAN, LSG, 8.5),
    ("Josh Inglis", PlayerRole.WICKET_KEEPER, LSG, 8.0),
    ("Ayush Badoni", PlayerRole.BATSMAN, LSG, 8.0),
    ("Matthew Breetzke", PlayerRole.BATSMAN, LSG, 7.0),
    ("Abdul Samad", PlayerRole.BATSMAN, LSG, 7.0),
    ("Himmat Singh", PlayerRole.BATSMAN, LSG, 6.5),
    ("Akshat Raghuwanshi", PlayerRole.BATSMAN, LSG, 6.5),
    ("Mukul Choudhary", PlayerRole.BATSMAN, LSG, 6.0),
    ("Mitchell Marsh", PlayerRole.ALL_ROUNDER, LSG, 9.0),
    ("Wanindu Hasaranga", PlayerRole.ALL_ROUNDER, LSG, 9.0),
    ("Shahbaz Ahmed", PlayerRole.ALL_ROUNDER, LSG, 7.5),
    ("Arshin Kulkarni", PlayerRole.ALL_ROUNDER, LSG, 6.5),
    ("Mohammed Shami", PlayerRole.BOWLER, LSG, 9.0),
    ("Anrich Nortje", PlayerRole.BOWLER, LSG, 8.5),
    ("Avesh Khan", PlayerRole.BOWLER, LSG, 8.0),
    ("Mayank Yadav", PlayerRole.BOWLER, LSG, 8.0),
    ("Mohsin Khan", PlayerRole.BOWLER, LSG, 7.0),
    ("Akash Singh", PlayerRole.BOWLER, LSG, 6.5),
    ("Prince Yadav", PlayerRole.BOWLER, LSG, 6.5),
    ("Manimaran Siddharth", PlayerRole.BOWLER, LSG, 6.5),
    ("Digvesh Rathi", PlayerRole.BOWLER, LSG, 6.0),
    ("Arjun Tendulkar", PlayerRole.BOWLER, LSG, 6.0),
    ("Naman Tiwari", PlayerRole.BOWLER, LSG, 6.0),

    # Punjab Kings (IPL 2026 actual squad from ESPNcricinfo)
    ("Shreyas Iyer", PlayerRole.BATSMAN, PBKS, 10.0),
    ("Nehal Wadhera", PlayerRole.BATSMAN, PBKS, 7.5),
    ("Priyansh Arya", PlayerRole.BATSMAN, PBKS, 7.0),
    ("Harnoor Singh", PlayerRole.BATSMAN, PBKS, 6.5),
    ("Pyla Avinash", PlayerRole.BATSMAN, PBKS, 6.5),
    ("Prabhsimran Singh", PlayerRole.WICKET_KEEPER, PBKS, 7.0),
    ("Vishnu Vinod", PlayerRole.WICKET_KEEPER, PBKS, 6.5),
    ("Marcus Stoinis", PlayerRole.ALL_ROUNDER, PBKS, 9.0),
    ("Marco Jansen", PlayerRole.ALL_ROUNDER, PBKS, 9.0),
    ("Azmatullah Omarzai", PlayerRole.ALL_ROUNDER, PBKS, 8.0),
    ("Shashank Singh", PlayerRole.ALL_ROUNDER, PBKS, 7.5),
    ("Cooper Connolly", PlayerRole.ALL_ROUNDER, PBKS, 7.5),
    ("Musheer Khan", PlayerRole.ALL_ROUNDER, PBKS, 7.0),
    ("Mitchell Owen", PlayerRole.ALL_ROUNDER, PBKS, 7.0),
    ("Suryansh Shedge", PlayerRole.ALL_ROUNDER, PBKS, 6.5),
    ("Arshdeep Singh", PlayerRole.BOWLER, PBKS, 9.0),
    ("Yuzvendra Chahal", PlayerRole.BOWLER, PBKS, 8.5),
    ("Lockie Ferguson", PlayerRole.BOWLER, PBKS, 8.5),
    ("Xavier Bartlett", PlayerRole.BOWLER, PBKS, 7.5),
    ("Harpreet Brar", PlayerRole.BOWLER, PBKS, 7.0),
    ("Ben Dwarshuis", PlayerRole.BOWLER, PBKS, 7.0),
    ("Vijaykumar Vyshak", PlayerRole.BOWLER, PBKS, 6.5),
    ("Yash Thakur", PlayerRole.BOWLER, PBKS, 6.5),
    ("Praveen Dubey", PlayerRole.BOWLER, PBKS, 6.5),
    ("Vishal Nishad", PlayerRole.BOWLER, PBKS, 6.0),

    # Rajasthan Royals (IPL 2026 actual squad from ESPNcricinfo)
    ("Yashasvi Jaiswal", PlayerRole.BATSMAN, RR, 10.0),
    ("Riyan Parag", PlayerRole.BATSMAN, RR, 8.5),
    ("Shimron Hetmyer", PlayerRole.BATSMAN, RR, 8.0),
    ("Dhruv Jurel", PlayerRole.WICKET_KEEPER, RR, 8.0),
    ("Lhuan-dre Pretorius", PlayerRole.WICKET_KEEPER, RR, 7.0),
    ("Vaibhav Sooryavanshi", PlayerRole.BATSMAN, RR, 7.0),
    ("Shubham Dubey", PlayerRole.BATSMAN, RR, 6.5),
    ("Aman Rao", PlayerRole.BATSMAN, RR, 6.0),
    ("Ravi Singh", PlayerRole.BATSMAN, RR, 6.0),
    ("Ravindra Jadeja", PlayerRole.ALL_ROUNDER, RR, 9.5),
    ("Donovan Ferreira", PlayerRole.ALL_ROUNDER, RR, 7.0),
    ("Jofra Archer", PlayerRole.BOWLER, RR, 9.5),
    ("Ravi Bishnoi", PlayerRole.BOWLER, RR, 8.0),
    ("Tushar Deshpande", PlayerRole.BOWLER, RR, 7.5),
    ("Kwena Maphaka", PlayerRole.BOWLER, RR, 7.5),
    ("Adam Milne", PlayerRole.BOWLER, RR, 7.0),
    ("Nandre Burger", PlayerRole.BOWLER, RR, 7.0),
    ("Sandeep Sharma", PlayerRole.BOWLER, RR, 6.5),
    ("Kuldeep Sen", PlayerRole.BOWLER, RR, 6.5),
    ("Sushant Mishra", PlayerRole.BOWLER, RR, 6.0),
    ("Vignesh Puthur", PlayerRole.BOWLER, RR, 6.0),
    ("Brijesh Sharma", PlayerRole.BOWLER, RR, 6.0),
    ("Yudhvir Singh", PlayerRole.BOWLER, RR, 6.0),
    ("Yash Raj Punja", PlayerRole.BOWLER, RR, 6.0),

    # Royal Challengers Bengaluru (IPL 2026 actual squad from ESPNcricinfo)
    ("Virat Kohli", PlayerRole.BATSMAN, RCB, 10.5),
    ("Rajat Patidar", PlayerRole.BATSMAN, RCB, 9.0),
    ("Phil Salt", PlayerRole.WICKET_KEEPER, RCB, 9.5),
    ("Tim David", PlayerRole.BATSMAN, RCB, 8.5),
    ("Devdutt Padikkal", PlayerRole.BATSMAN, RCB, 8.0),
    ("Jordan Cox", PlayerRole.WICKET_KEEPER, RCB, 7.0),
    ("Jitesh Sharma", PlayerRole.WICKET_KEEPER, RCB, 7.0),
    ("Jacob Bethell", PlayerRole.ALL_ROUNDER, RCB, 8.5),
    ("Venkatesh Iyer", PlayerRole.ALL_ROUNDER, RCB, 8.0),
    ("Krunal Pandya", PlayerRole.ALL_ROUNDER, RCB, 7.5),
    ("Romario Shepherd", PlayerRole.ALL_ROUNDER, RCB, 7.5),
    ("Kanishk Chouhan", PlayerRole.ALL_ROUNDER, RCB, 6.5),
    ("Vihaan Malhotra", PlayerRole.ALL_ROUNDER, RCB, 6.0),
    ("Mangesh Yadav", PlayerRole.ALL_ROUNDER, RCB, 6.0),
    ("Josh Hazlewood", PlayerRole.BOWLER, RCB, 9.0),
    ("Bhuvneshwar Kumar", PlayerRole.BOWLER, RCB, 8.0),
    ("Yash Dayal", PlayerRole.BOWLER, RCB, 7.5),
    ("Nuwan Thushara", PlayerRole.BOWLER, RCB, 7.0),
    ("Jacob Duffy", PlayerRole.BOWLER, RCB, 7.0),
    ("Rasikh Salam", PlayerRole.BOWLER, RCB, 6.5),
    ("Suyash Sharma", PlayerRole.BOWLER, RCB, 6.5),
    ("Abhinandan Singh", PlayerRole.BOWLER, RCB, 6.0),
    ("Satvik Deswal", PlayerRole.BOWLER, RCB, 6.0),
    ("Swapnil Singh", PlayerRole.BOWLER, RCB, 6.0),
    ("Vicky Ostwal", PlayerRole.BOWLER, RCB, 6.0),

    # Sunrisers Hyderabad (IPL 2026 actual squad from ESPNcricinfo)
    ("Ishan Kishan", PlayerRole.WICKET_KEEPER, SRH, 9.5),
    ("Travis Head", PlayerRole.BATSMAN, SRH, 10.0),
    ("Heinrich Klaasen", PlayerRole.WICKET_KEEPER, SRH, 10.0),
    ("Ravichandran Smaran", PlayerRole.BATSMAN, SRH, 6.5),
    ("Aniket Verma", PlayerRole.BATSMAN, SRH, 6.5),
    ("Salil Arora", PlayerRole.WICKET_KEEPER, SRH, 6.0),
    ("Abhishek Sharma", PlayerRole.ALL_ROUNDER, SRH, 8.5),
    ("Nitish Kumar Reddy", PlayerRole.ALL_ROUNDER, SRH, 8.5),
    ("Liam Livingstone", PlayerRole.ALL_ROUNDER, SRH, 9.0),
    ("Kamindu Mendis", PlayerRole.ALL_ROUNDER, SRH, 8.0),
    ("Harshal Patel", PlayerRole.ALL_ROUNDER, SRH, 8.0),
    ("Brydon Carse", PlayerRole.ALL_ROUNDER, SRH, 8.0),
    ("Shivam Mavi", PlayerRole.ALL_ROUNDER, SRH, 7.0),
    ("Harsh Dubey", PlayerRole.ALL_ROUNDER, SRH, 6.5),
    ("Krains Fuletra", PlayerRole.ALL_ROUNDER, SRH, 6.0),
    ("Shivang Kumar", PlayerRole.ALL_ROUNDER, SRH, 6.0),
    ("Pat Cummins", PlayerRole.BOWLER, SRH, 10.0),
    ("Jaydev Unadkat", PlayerRole.BOWLER, SRH, 7.0),
    ("David Payne", PlayerRole.BOWLER, SRH, 6.5),
    ("Eshan Malinga", PlayerRole.BOWLER, SRH, 6.5),
    ("Sakib Hussain", PlayerRole.BOWLER, SRH, 6.0),
    ("Amit Kumar", PlayerRole.BOWLER, SRH, 6.0),
    ("Praful Hinge", PlayerRole.BOWLER, SRH, 6.0),
    ("Onkar Tarmale", PlayerRole.BOWLER, SRH, 6.0),
    ("Zeeshan Ansari", PlayerRole.BOWLER, SRH, 6.0),
]

# Real IPL 2026 schedule from ESPNcricinfo
# All times stored in UTC (IST = UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def ist(year, month, day, hour, minute=0):
    """Create a UTC datetime from IST time."""
    return datetime(year, month, day, hour, minute, tzinfo=IST).astimezone(timezone.utc).replace(tzinfo=None)

MATCHES = [
    # Match 1: Sat 28 Mar, 7:30 PM IST (Night)
    (RCB, SRH, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 3, 28, 19, 30)),
    # Match 2: Sun 29 Mar, 7:30 PM IST (Night)
    (MI, KKR, "Wankhede Stadium, Mumbai", ist(2026, 3, 29, 19, 30)),
    # Match 3: Mon 30 Mar, 7:30 PM IST (Night)
    (RR, CSK, "ACA Stadium, Guwahati", ist(2026, 3, 30, 19, 30)),
    # Match 4: Tue 31 Mar, 7:30 PM IST (Night)
    (PBKS, GT, "PCA New Stadium, New Chandigarh", ist(2026, 3, 31, 19, 30)),
    # Match 5: Wed 1 Apr, 7:30 PM IST (Night)
    (LSG, DC, "BRSABV Ekana Stadium, Lucknow", ist(2026, 4, 1, 19, 30)),
    # Match 6: Thu 2 Apr, 7:30 PM IST (Night)
    (KKR, SRH, "Eden Gardens, Kolkata", ist(2026, 4, 2, 19, 30)),
    # Match 7: Fri 3 Apr, 7:30 PM IST (Night)
    (CSK, PBKS, "MA Chidambaram Stadium, Chennai", ist(2026, 4, 3, 19, 30)),
    # Match 8: Sat 4 Apr, 3:30 PM IST (Day)
    (DC, MI, "Arun Jaitley Stadium, Delhi", ist(2026, 4, 4, 15, 30)),
    # Match 9: Sat 4 Apr, 7:30 PM IST (Night)
    (GT, RR, "Narendra Modi Stadium, Ahmedabad", ist(2026, 4, 4, 19, 30)),
    # Match 10: Sun 5 Apr, 3:30 PM IST (Day)
    (SRH, LSG, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 4, 5, 15, 30)),
    # Match 11: Sun 5 Apr, 7:30 PM IST (Night)
    (RCB, CSK, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 4, 5, 19, 30)),
    # Match 12: Mon 6 Apr, 7:30 PM IST (Night)
    (KKR, PBKS, "Eden Gardens, Kolkata", ist(2026, 4, 6, 19, 30)),
    # Match 13: Tue 7 Apr, 7:30 PM IST (Night)
    (RR, MI, "ACA Stadium, Guwahati", ist(2026, 4, 7, 19, 30)),
    # Match 14: Wed 8 Apr, 7:30 PM IST (Night)
    (DC, GT, "Arun Jaitley Stadium, Delhi", ist(2026, 4, 8, 19, 30)),
    # Match 15: Thu 9 Apr, 7:30 PM IST (Night)
    (KKR, LSG, "Eden Gardens, Kolkata", ist(2026, 4, 9, 19, 30)),
    # Match 16: Fri 10 Apr, 7:30 PM IST (Night)
    (RR, RCB, "ACA Stadium, Guwahati", ist(2026, 4, 10, 19, 30)),
    # Match 17: Sat 11 Apr, 3:30 PM IST (Day)
    (PBKS, SRH, "PCA New Stadium, New Chandigarh", ist(2026, 4, 11, 15, 30)),
    # Match 18: Sat 11 Apr, 7:30 PM IST (Night)
    (CSK, DC, "MA Chidambaram Stadium, Chennai", ist(2026, 4, 11, 19, 30)),
    # Match 19: Sun 12 Apr, 3:30 PM IST (Day)
    (LSG, GT, "BRSABV Ekana Stadium, Lucknow", ist(2026, 4, 12, 15, 30)),
    # Match 20: Sun 12 Apr, 7:30 PM IST (Night)
    (MI, RCB, "Wankhede Stadium, Mumbai", ist(2026, 4, 12, 19, 30)),
    # Match 21: Mon 13 Apr, 7:30 PM IST (Night)
    (SRH, RR, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 4, 13, 19, 30)),
    # Match 22: Tue 14 Apr, 7:30 PM IST (Night)
    (CSK, KKR, "MA Chidambaram Stadium, Chennai", ist(2026, 4, 14, 19, 30)),
    # Match 23: Wed 15 Apr, 7:30 PM IST (Night)
    (RCB, LSG, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 4, 15, 19, 30)),
    # Match 24: Thu 16 Apr, 7:30 PM IST (Night)
    (MI, PBKS, "Wankhede Stadium, Mumbai", ist(2026, 4, 16, 19, 30)),
    # Match 25: Fri 17 Apr, 7:30 PM IST (Night)
    (GT, KKR, "Narendra Modi Stadium, Ahmedabad", ist(2026, 4, 17, 19, 30)),
    # Match 26: Sat 18 Apr, 3:30 PM IST (Day)
    (RCB, DC, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 4, 18, 15, 30)),
    # Match 27: Sat 18 Apr, 7:30 PM IST (Night)
    (SRH, CSK, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 4, 18, 19, 30)),
    # Match 28: Sun 19 Apr, 3:30 PM IST (Day)
    (KKR, RR, "Eden Gardens, Kolkata", ist(2026, 4, 19, 15, 30)),
    # Match 29: Sun 19 Apr, 7:30 PM IST (Night)
    (PBKS, LSG, "PCA New Stadium, New Chandigarh", ist(2026, 4, 19, 19, 30)),
    # Match 30: Mon 20 Apr, 7:30 PM IST (Night)
    (GT, MI, "Narendra Modi Stadium, Ahmedabad", ist(2026, 4, 20, 19, 30)),
    # Match 31: Tue 21 Apr, 7:30 PM IST (Night)
    (SRH, DC, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 4, 21, 19, 30)),
    # Match 32: Wed 22 Apr, 7:30 PM IST (Night)
    (LSG, RR, "BRSABV Ekana Stadium, Lucknow", ist(2026, 4, 22, 19, 30)),
    # Match 33: Thu 23 Apr, 7:30 PM IST (Night)
    (MI, CSK, "Wankhede Stadium, Mumbai", ist(2026, 4, 23, 19, 30)),
    # Match 34: Fri 24 Apr, 7:30 PM IST (Night)
    (RCB, GT, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 4, 24, 19, 30)),
    # Match 35: Sat 25 Apr, 3:30 PM IST (Day)
    (DC, PBKS, "Arun Jaitley Stadium, Delhi", ist(2026, 4, 25, 15, 30)),
    # Match 36: Sat 25 Apr, 7:30 PM IST (Night)
    (RR, SRH, "ACA Stadium, Guwahati", ist(2026, 4, 25, 19, 30)),
    # Match 37: Sun 26 Apr, 3:30 PM IST (Day)
    (GT, CSK, "Narendra Modi Stadium, Ahmedabad", ist(2026, 4, 26, 15, 30)),
    # Match 38: Sun 26 Apr, 7:30 PM IST (Night)
    (LSG, KKR, "BRSABV Ekana Stadium, Lucknow", ist(2026, 4, 26, 19, 30)),
    # Match 39: Mon 27 Apr, 7:30 PM IST (Night)
    (DC, RCB, "Arun Jaitley Stadium, Delhi", ist(2026, 4, 27, 19, 30)),
    # Match 40: Tue 28 Apr, 7:30 PM IST (Night)
    (PBKS, RR, "PCA New Stadium, New Chandigarh", ist(2026, 4, 28, 19, 30)),
    # Match 41: Wed 29 Apr, 7:30 PM IST (Night)
    (MI, SRH, "Wankhede Stadium, Mumbai", ist(2026, 4, 29, 19, 30)),
    # Match 42: Thu 30 Apr, 7:30 PM IST (Night)
    (GT, RCB, "Narendra Modi Stadium, Ahmedabad", ist(2026, 4, 30, 19, 30)),
    # Match 43: Fri 1 May, 7:30 PM IST (Night)
    (RR, DC, "ACA Stadium, Guwahati", ist(2026, 5, 1, 19, 30)),
    # Match 44: Sat 2 May, 7:30 PM IST (Night)
    (CSK, MI, "MA Chidambaram Stadium, Chennai", ist(2026, 5, 2, 19, 30)),
    # Match 45: Sun 3 May, 3:30 PM IST (Day)
    (SRH, KKR, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 5, 3, 15, 30)),
    # Match 46: Sun 3 May, 7:30 PM IST (Night)
    (GT, PBKS, "Narendra Modi Stadium, Ahmedabad", ist(2026, 5, 3, 19, 30)),
    # Match 47: Mon 4 May, 7:30 PM IST (Night)
    (MI, LSG, "Wankhede Stadium, Mumbai", ist(2026, 5, 4, 19, 30)),
    # Match 48: Tue 5 May, 7:30 PM IST (Night)
    (DC, CSK, "Arun Jaitley Stadium, Delhi", ist(2026, 5, 5, 19, 30)),
    # Match 49: Wed 6 May, 7:30 PM IST (Night)
    (SRH, PBKS, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 5, 6, 19, 30)),
    # Match 50: Thu 7 May, 7:30 PM IST (Night)
    (LSG, RCB, "BRSABV Ekana Stadium, Lucknow", ist(2026, 5, 7, 19, 30)),
    # Match 51: Fri 8 May, 7:30 PM IST (Night)
    (DC, KKR, "Arun Jaitley Stadium, Delhi", ist(2026, 5, 8, 19, 30)),
    # Match 52: Sat 9 May, 7:30 PM IST (Night)
    (RR, GT, "ACA Stadium, Guwahati", ist(2026, 5, 9, 19, 30)),
    # Match 53: Sun 10 May, 3:30 PM IST (Day)
    (CSK, LSG, "MA Chidambaram Stadium, Chennai", ist(2026, 5, 10, 15, 30)),
    # Match 54: Sun 10 May, 7:30 PM IST (Night)
    (RCB, MI, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 5, 10, 19, 30)),
    # Match 55: Mon 11 May, 7:30 PM IST (Night)
    (PBKS, DC, "PCA New Stadium, New Chandigarh", ist(2026, 5, 11, 19, 30)),
    # Match 56: Tue 12 May, 7:30 PM IST (Night)
    (GT, SRH, "Narendra Modi Stadium, Ahmedabad", ist(2026, 5, 12, 19, 30)),
    # Match 57: Wed 13 May, 7:30 PM IST (Night)
    (RCB, KKR, "M. Chinnaswamy Stadium, Bengaluru", ist(2026, 5, 13, 19, 30)),
    # Match 58: Thu 14 May, 7:30 PM IST (Night)
    (PBKS, MI, "PCA New Stadium, New Chandigarh", ist(2026, 5, 14, 19, 30)),
    # Match 59: Fri 15 May, 7:30 PM IST (Night)
    (LSG, CSK, "BRSABV Ekana Stadium, Lucknow", ist(2026, 5, 15, 19, 30)),
    # Match 60: Sat 16 May, 7:30 PM IST (Night)
    (KKR, GT, "Eden Gardens, Kolkata", ist(2026, 5, 16, 19, 30)),
    # Match 61: Sun 17 May, 3:30 PM IST (Day)
    (PBKS, RCB, "PCA New Stadium, New Chandigarh", ist(2026, 5, 17, 15, 30)),
    # Match 62: Sun 17 May, 7:30 PM IST (Night)
    (DC, RR, "Arun Jaitley Stadium, Delhi", ist(2026, 5, 17, 19, 30)),
    # Match 63: Mon 18 May, 7:30 PM IST (Night)
    (CSK, SRH, "MA Chidambaram Stadium, Chennai", ist(2026, 5, 18, 19, 30)),
    # Match 64: Tue 19 May, 7:30 PM IST (Night)
    (RR, LSG, "ACA Stadium, Guwahati", ist(2026, 5, 19, 19, 30)),
    # Match 65: Wed 20 May, 7:30 PM IST (Night)
    (KKR, MI, "Eden Gardens, Kolkata", ist(2026, 5, 20, 19, 30)),
    # Match 66: Thu 21 May, 7:30 PM IST (Night)
    (CSK, GT, "MA Chidambaram Stadium, Chennai", ist(2026, 5, 21, 19, 30)),
    # Match 67: Fri 22 May, 7:30 PM IST (Night)
    (SRH, RCB, "Rajiv Gandhi Intl Stadium, Hyderabad", ist(2026, 5, 22, 19, 30)),
    # Match 68: Sat 23 May, 7:30 PM IST (Night)
    (LSG, PBKS, "BRSABV Ekana Stadium, Lucknow", ist(2026, 5, 23, 19, 30)),
    # Match 69: Sun 24 May, 3:30 PM IST (Day)
    (MI, RR, "Wankhede Stadium, Mumbai", ist(2026, 5, 24, 15, 30)),
    # Match 70: Sun 24 May, 7:30 PM IST (Night)
    (KKR, DC, "Eden Gardens, Kolkata", ist(2026, 5, 24, 19, 30)),
]


async def seed():
    async with async_session_factory() as session:
        # Seed players
        existing = (await session.execute(select(Player))).scalars().all()
        existing_names = {p.name for p in existing}
        added_players = 0
        for name, role, franchise, cost in PLAYERS:
            if name not in existing_names:
                session.add(Player(name=name, role=role, franchise=franchise, cost=cost))
                added_players += 1
        await session.flush()
        print(f"Players: {added_players} added, {len(existing_names)} already existed")

        # Seed matches
        existing_matches = (await session.execute(select(Match))).scalars().all()
        existing_match_keys = {(m.team_a, m.team_b, m.start_time.date()) for m in existing_matches}
        added_matches = 0
        for team_a, team_b, venue, start_time in MATCHES:
            if (team_a, team_b, start_time.date()) not in existing_match_keys:
                session.add(Match(
                    team_a=team_a, team_b=team_b, venue=venue,
                    start_time=start_time, status=MatchStatus.UPCOMING,
                ))
                added_matches += 1
        await session.commit()
        print(f"Matches: {added_matches} added, {len(existing_match_keys)} already existed")
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
