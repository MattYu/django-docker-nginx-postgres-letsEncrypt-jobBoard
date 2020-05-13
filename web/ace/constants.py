MAX_LENGTH_TITLE = 100
MAX_LENGTH_DESCRIPTION = 10000
MAX_LENGTH_RESPONSABILITIES = 10000
MAX_LENGTH_REQUIREMENTS = 10000
MAX_LENGTH_STANDARDFIELDS= 100
MAX_LENGTH_STANDARDTEXTAREA = 2000
MAX_LENGTH_LONGSTANDARDFIELDS = 120
MAX_LENGTH_TERMSANDCONDITIONS = 200000

# Category Constants
ANY = "ANY"
ENGINEER_AERO_MECH = "Aerospace-&-Mechanical"
ENGINEER_ELEC = "Electrical"
ENGINEER_IND = "Industrial"
ENGINEER_QUA = "Quality-System"
ENGINEER_COEN_COMP_SOFT = "Computer,Information-Security,Software"
ENGINEER_OTHER = "Engineering(Other)"

F_A_DES = "Computational-Arts-&-Design"

JMSB_Acc_Fin = "Accounting-&-Finance"
JMSB_HR_MAR = "HR&Marketing"
JMSB_BUS = "Business-Administration"
JMSB_SUP = "Management-&-Supply-Chain"
JMSB_OTHER = "JMSB(Other)"

A_S_ACT = "Actuarial-Mathematics-&-Finance"
A_S_ECON = "Economics"
A_S_MATH_PHY = "Mathematics-&-Physics"
A_S_POL = "Political-Science"
A_S_CHEM_BIO = "Biology-&-Chemistry"
A_S_JOU = "Journalism"
A_S_TRAN = "Translation"
A_S_OTHER = "Arts-and-Science(Other)"

CATEGORY_CHOICES = [
    (ANY, "Any Category"),
    (ENGINEER_AERO_MECH, "GCS Engineering - Aerospace & Mechanical"),
    (ENGINEER_ELEC, "GCS Engineering - Electrical"),
    (ENGINEER_IND, "GCS Engineering - Industrial"),
    (ENGINEER_QUA, "GCS Engineering - Quality System"),
    (ENGINEER_COEN_COMP_SOFT, "GCS Engineering and Computer Science - Computer, Information Security & Software"),
    (ENGINEER_OTHER, "GCS Engineering - Other"),
    (F_A_DES, "Fine Arts - Computational Arts & Design"),
    (JMSB_Acc_Fin, "JMSB - Accounting & Finance"),
    (JMSB_HR_MAR, "JMSB - HR & Marketing"),
    (JMSB_BUS, "JMSB - Business Administration"),
    (JMSB_SUP, "JMSB - Management & Supply Chain Operation Management"),
    (JMSB_OTHER, "JMSB - Other"),
    (A_S_ACT, "Arts and Science - Actuarial Mathematics & Finance"),
    (A_S_ECON, "Arts and Science - Economics"),
    (A_S_MATH_PHY, "Arts and Science - Mathematics & Physics"),
    (A_S_POL, "Arts and Science - Political Science"),
    (A_S_CHEM_BIO, "Arts and Science - Biology & Chemistry"),
    (A_S_JOU, "Arts and Science - Journalism"),
    (A_S_TRAN, "Arts and Science - Translation"),
    (A_S_OTHER, "Arts and Science - Other"),
]

#Locations

LOCATION_CHOICES = [
    ("None", "Country"),
    ("CA", "Canada"),
    ("US", "USA"),
    ("Other-Europe", "Other- Europe"),
    ("Other-Asia", "Other- Asia"),
    ("Other", "Other"),
]

UPLOADTO = '/protected'

AGREE_DISAGREE = [
    ("Agree", "Agree")
]

# Login/Registration
USER_TYPE_CHOICES = (
    (1, 'candidate'),
    (2, 'employer'),
    (3, 'admin'),
    (4, 'super'),
)

USER_TYPE_EMPLOYER = 2
USER_TYPE_CANDIDATE = 1
USER_TYPE_SUPER = 4

LANGUAGE_CHOICES = (
    ("English", "English"),
    ("French", "French"),
    ("Other", "Other (Please specify below)"),
)

LANGUAGE_FLUENCY_CHOICES = (
    (0, "Elementary Proficiency"),
    (35, "Limited Working Proficiency"),
    (60, "Professional Working Proficiency"),
    (80, "Full Working Proficiency"),
    (100, "Native or Bilingual Proficiency"),
)

YES_NO = (
    ("No", "No"),
    ("Yes", "Yes"),
)

CITIZENSHIP = (
    ("Choose", "Choose"),
    ("Canadian", "Canadian"),
    ("Permanent Resident", "Permanent Resident"),
    ("International Student", "International Student"),
)

# Job applications

JOB_APPLICATION_STATUS = (
    ("Pending Review", "Pending Coop Review"),
    ("Not Approved", "Not Approved"),
    ("Submitted", "Submitted to Employer"),
    ("Interviewing", "Selected for Interview"),
    ("Not Selected", "Not Selected"),
    ("Ranked", "Ranked by Employer"),
    ("1st", "1st"),
    ("Matched", "Matched"),
    ("Not Matched", "Not Matched"),
    ("Closed", "Closed"),
)

# Company

COMPANY_STATUS = (
    ("Pending Review", "Pending Coop Review"),
    ("Not Approved", "Not approved"),
    ("Approved", "Approved")
)

# Job 
JOB_STATUS = (
    ("Pending Review", "Pending Coop Review"),
    ("Not Approved", "Not Approved"),
    ("Approved", "Approved"),
    ("Interviewing", "Interviewing"),
    ("Filled", "Filled"),
    ("Partially Filled", "Partially Filled"),
    ("Closed", "Closed")
)

EMPLOYER_STATUS = (
    ("Pending Review", "Pending Coop Review"),
    ("Not Approved", "Not approved"),
    ("Approved", "Approved")
)

# Download

FILE_TYPE_RESUME = 1
FILE_TYPE_COVER_LETTER = 2
FILE_TYPE_TRANSCRIPT = 3
FILE_TYPE_OTHER = 4


# Default video link

DEFAULT_VIDEO = "https://www.youtube.com/watch?v=NwAxNFwEEbM"

PASSWORD_MIN_LENGTH = 9

MAX_PER_PAGE = 1