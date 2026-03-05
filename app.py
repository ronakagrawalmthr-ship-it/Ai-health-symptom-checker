"""
AI Health Symptom Checker - Flask Backend

This application provides an AI-powered symptom analysis service.
It uses OpenAI API to analyze symptoms and provide possible causes,
precautions, severity levels, and emergency warnings.

If no OpenAI API key is provided, it falls back to a mock response for testing.
"""

import os
import json
import html
import re
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app)

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client if API key is available
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize OpenAI client: {e}")


# =====================================================
# COMPREHENSIVE MEDICAL CONDITION DATABASE
# =====================================================
# This database contains symptom patterns for 50+ medical conditions
# organized by symptom categories

MEDICAL_CONDITIONS = {
    # RESPIRATORY CONDITIONS
    "common_cold": {
        "keywords": ["cold", "runny nose", "sneezing", "nasal congestion", "congested nose", "stuff nose", "sardi", "nak band", "chhink", "nak se pani", "sardi khansi", "common cold", "nasal discharge", "sore throat", "gale me kharash"],
        "symptoms": ["runny nose", "sneezing", "sore throat", "mild fatigue", "congestion", "gale me kharash", "thakan", "nak congestion", "gale me sojan"],
        "severity": "Low",
        "causes": [
            "Rhinovirus infection (most common) - राइनोवायरस संक्रमण (सबसे आम)",
            "Coronaviruses (non-COVID) - कोरोनावायरस (गैर-COVID)",
            "Respiratory syncytial virus (RSV) - रेस्पिरेटरी सिंसाइटियल वायरस",
            "Adenovirus infection - एडेनोवायरस संक्रमण"
        ],
        "causes_hi": [
            "राइनोवायरस संक्रमण (सबसे आम)",
            "कोरोनावायरस (गैर-COVID)",
            "रेस्पिरेटरी सिंसाइटियल वायरस",
            "एडेनोवायरस संक्रमण"
        ],
        "precautions": [
            "Rest and get adequate sleep - आराम करें और पर्याप्त नींद लें",
            "Stay hydrated with water and fluids - पानी और तरल पदार्थों से हाइड्रेटेड रहें",
            "Use humidifier to ease congestion - भीड़ कम करने के लिए ह्यूमिडिफायर का उपयोग करें",
            "Take over-the-counter cold remedies - ओवर-द-काउंटर कोल्ड रेमेडी लें",
            "Wash hands frequently to prevent spread - फैलने से रोकने के लिए बार-बार हाथ धोएं"
        ],
        "precautions_hi": [
            "आराम करें और पर्याप्त नींद लें",
            "पानी और तरल पदार्थों से हाइड्रेटेड रहें",
            "नाक की भीड़ कम करने के लिए गर्म भाप लें",
            "ओवर-द-काउंटर दवाएं लें",
            "फैलने से रोकने के लिए बार-बार हाथ धोएं"
        ],
        "emergency_warning": ""
    },
    "flu_influenza": {
        "keywords": ["flu", "influenza", "high fever", "body aches", "muscle pain", "fatigue extreme", "flu", "bukhar", "badan dard", "tez thakan", "jawani", "viral fever", "tap", "juka", "bukhar", "taap"],
        "symptoms": ["high fever", "body aches", "muscle pain", "fatigue", "dry cough", "headache", "bukhar", "khansi", "sirdard", "badan dard", "tej thakan"],
        "severity": "Medium",
        "causes": [
            "Influenza A virus",
            "Influenza B virus",
            "Viral infection of respiratory system"
        ],
        "precautions": [
            "Rest in bed",
            "Stay hydrated",
            "Take fever reducers (acetaminophen/ibuprofen)",
            "Take antiviral medications within 48 hours if prescribed",
            "Avoid contact with others until fever-free for 24 hours"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care if experiencing difficulty breathing, chest pain, confusion, or severe vomiting."
    },
    "pneumonia": {
        "keywords": ["pneumonia", "chest infection", "lung infection", "cough with phlegm", "coughing green", "coughing yellow", "balgam", "lung infection", "feffon ka infection", "chhati me infection", "balgam wali khansi", "neguniya", "neomonia"],
        "symptoms": ["cough", "chest pain", "fever", "difficulty breathing", "phlegm", "fatigue", "khansi", "bukhar", "saans lene me pareshani", "chhati dard", "thakan", "balgam"],
        "severity": "High",
        "causes": [
            "Bacterial pneumonia (Streptococcus pneumoniae)",
            "Viral pneumonia (influenza, COVID-19)",
            "Fungal pneumonia",
            "Aspiration pneumonia"
        ],
        "precautions": [
            "Complete all prescribed antibiotics",
            "Get plenty of rest",
            "Stay hydrated",
            "Use humidifier",
            "Follow up with doctor"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Pneumonia can be life-threatening. Seek IMMEDIATE medical attention for difficulty breathing, chest pain, confusion, or blue lips/fingernails."
    },
    "asthma": {
        "keywords": ["asthma", "wheezing", "breathlessness", "tight chest", "whistling breath", "breathing difficulty", "dama", "saans ki problem", "khansi ke saath saans", "chhati mein fisal", "ehsmah", "assathma"],
        "symptoms": ["wheezing", "shortness of breath", "chest tightness", "coughing", "difficulty breathing", "saans lene mein dikkat", "chhati mein taizpan", "khansi", "wheezing sound", "khinch", "hissing"],
        "severity": "Medium",
        "causes": [
            "Airway inflammation",
            "Allergic reactions (dust, pollen, pet dander)",
            "Exercise-induced bronchoconstriction",
            "Air pollution or smoke exposure",
            "Respiratory infections"
        ],
        "precautions": [
            "Use prescribed inhaler as directed",
            "Avoid known triggers",
            "Keep rescue inhaler with you",
            "Monitor breathing with peak flow meter",
            "Get regular check-ups"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Use rescue inhaler and seek emergency care if breathing does not improve, lips/nails turn blue, or severe wheezing occurs."
    },
    "bronchitis": {
        "keywords": ["bronchitis", "chest congestion", "mucus chest", "productive cough", "long cough"],
        "symptoms": ["persistent cough", "mucus production", "chest congestion", "fatigue", "shortness of breath"],
        "severity": "Medium",
        "causes": [
            "Viral infection (most common)",
            "Bacterial infection",
            "Air pollution exposure",
            "Smoking"
        ],
        "precautions": [
            "Rest and stay hydrated",
            "Use humidifier",
            "Take cough suppressants at night",
            "Avoid smoking and pollutants",
            "Use bronchodilators if prescribed"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care if experiencing high fever, shortness of breath, or coughing up blood."
    },
    "covid19": {
        "keywords": ["covid", "coronavirus", "covid-19", "loss taste", "loss smell", "anosmia", "ageusia", "corona", "korona", "khushbu nahi aana", "swadan nash"],
        "symptoms": ["fever", "cough", "fatigue", "loss of taste", "loss of smell", "shortness of breath", "bukhar", "khansi", "thakan", "khushbu nahi aana", "swad nahi aana", "saans lene me pareshani", "sir dard", "gale me khujli", "body pain", "muh me kharas"],
        "severity": "High",
        "causes": [
            "SARS-CoV-2 virus infection",
            "COVID-19 variants (Omicron, Delta, etc.)"
        ],
        "precautions": [
            "Isolate yourself from others",
            "Monitor oxygen levels with pulse oximeter",
            "Rest and stay hydrated",
            "Take fever reducers if needed",
            "Track your symptoms"
        ],
        "emergency_warning": "⚠️ EMERGENCY: COVID-19 can be severe. Seek IMMEDIATE care for difficulty breathing, persistent chest pain, confusion, or oxygen level below 92%."
    },
    "tb_tuberculosis": {
        "keywords": ["tuberculosis", "tb", "night sweat", "weight loss", "cough blood", "coughing blood"],
        "symptoms": ["persistent cough", "coughing blood", "night sweats", "weight loss", "fever", "fatigue"],
        "severity": "High",
        "causes": [
            "Mycobacterium tuberculosis bacteria",
            "Airborne transmission from infected person"
        ],
        "precautions": [
            "Complete full course of TB medication",
            "Stay away from others until non-infectious",
            "Cover mouth when coughing",
            "Get plenty of nutrition",
            "Regular medical follow-up"
        ],
        "emergency_warning": "⚠️ EMERGENCY: TB is contagious and serious. Seek immediate medical care if coughing up blood or having difficulty breathing."
    },
    
    # DIGESTIVE CONDITIONS
    "gastroenteritis": {
        "keywords": ["stomach flu", "gastroenteritis", "stomach virus", "diarrhea", "vomiting", "stomach cramps"],
        "symptoms": ["diarrhea", "vomiting", "stomach cramps", "nausea", "fever", "fatigue"],
        "severity": "Medium",
        "causes": [
            "Norovirus",
            "Rotavirus",
            "Bacterial infection (E. coli, Salmonella)",
            "Food poisoning"
        ],
        "precautions": [
            "Stay hydrated with electrolyte solutions",
            "Eat bland foods (BRAT diet)",
            "Rest",
            "Avoid dairy and fatty foods",
            "Wash hands thoroughly"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek care if unable to keep fluids down for 24 hours, blood in stool/vomit, or signs of severe dehydration."
    },
    "food_poisoning": {
        "keywords": ["food poisoning", "food infection", "food toxin", "sick after eating", "contaminated food", "khana visam", "khana kharab", "food infection", "bed khana", "khana se beemar"],
        "symptoms": ["nausea", "vomiting", "diarrhea", "stomach cramps", "fever", "micchhami", "ultis", "dast", "pet ke cramps", "bukhar", "pet kharab", "pet dard"],
        "severity": "Medium",
        "causes": [
            "Bacterial toxins (Salmonella, E. coli)",
            "Norovirus",
            "Parasites (Giardia)",
            "Contaminated food/water"
        ],
        "precautions": [
            "Stay hydrated",
            "Let stomach settle before eating",
            "Eat bland foods gradually",
            "Rest",
            "Avoid alcohol and caffeine"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for severe vomiting, bloody diarrhea, high fever, or signs of dehydration."
    },
    "acid_reflux": {
        "keywords": ["acid reflux", "heartburn", "gerd", "indigestion", "burning chest", "reflux", "gastro", "gerd", "pet ki aag", "chhati jalna", "khana nawarna", "pet me jalan", "acidity"],
        "symptoms": ["heartburn", "chest burning", "sour taste", "difficulty swallowing", "chronic cough", "pet ki aag", "chhati jalna", "khathala swad", "khana glance nahi", "lambi khansi", "acidity"],
        "severity": "Low",
        "causes": [
            "GERD (gastroesophageal reflux disease)",
            "Weak lower esophageal sphincter",
            "Hiatal hernia",
            "Certain foods/spices"
        ],
        "precautions": [
            "Avoid trigger foods (spicy, fatty, citrus)",
            "Eat smaller meals",
            "Don't lie down after eating",
            "Elevate head while sleeping",
            "Maintain healthy weight"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Chest pain can mimic heart attack. Seek immediate care if chest pain is severe or accompanied by jaw/arm pain, sweating, or shortness of breath."
    },
    "appendicitis": {
        "keywords": ["appendicitis", "appendix", "right lower abdomen", "right side pain", "appendix pain"],
        "symptoms": ["abdominal pain", "fever", "nausea", "loss of appetite", "vomiting"],
        "severity": "High",
        "causes": [
            "Blocked appendix opening",
            "Enlarged lymphoid tissue",
            "Foreign body",
            "Tumor (rare)"
        ],
        "precautions": [
            "Do NOT eat or drink before medical evaluation",
            "Do NOT take pain medication (masks symptoms)",
            "Seek immediate medical care",
            "Rest",
            "Prepare for possible surgery"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Appendicitis is life-threatening if appendix bursts. Seek IMMEDIATE care for severe abdominal pain, especially starting around navel and moving to lower right."
    },
    "ibs_irritable_bowel": {
        "keywords": ["ibs", "irritable bowel", "bloating", "gas", "diarrhea constipation", "alternating bowel"],
        "symptoms": ["abdominal pain", "bloating", "diarrhea", "constipation", "gas", "mucus in stool"],
        "severity": "Low",
        "causes": [
            "Abnormal muscle contractions in intestines",
            "Nervous system abnormalities",
            "Inflammation",
            "Food sensitivities",
            "Stress"
        ],
        "precautions": [
            "Identify and avoid trigger foods",
            "Eat high-fiber diet",
            "Stay hydrated",
            "Exercise regularly",
            "Manage stress"
        ],
        "emergency_warning": "⚠️ IMPORTANT: Consult doctor to rule out more serious conditions like IBD or colon cancer."
    },
    "ulcer": {
        "keywords": ["ulcer", "stomach ulcer", "peptic ulcer", "duodenal ulcer", "burning stomach pain"],
        "symptoms": ["burning stomach pain", "nausea", "bloating", "heartburn", "fatigue"],
        "severity": "Medium",
        "causes": [
            "H. pylori bacterial infection",
            "NSAID use (aspirin, ibuprofen)",
            "Excessive stomach acid",
            "Smoking",
            "Stress"
        ],
        "precautions": [
            "Avoid NSAIDs and alcohol",
            "Eat small, frequent meals",
            "Avoid spicy/acidic foods",
            "Quit smoking",
            "Reduce stress"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for vomiting blood (red or black), black/tarry stools, or severe sudden pain."
    },
    "gallstones": {
        "keywords": ["gallstones", "gallbladder", "right upper abdomen", "biliary", "jaundice eyes"],
        "symptoms": ["right upper abdominal pain", "nausea", "vomiting", "jaundice", "fever"],
        "severity": "Medium",
        "causes": [
            "Excess cholesterol in bile",
            "Excess bilirubin in bile",
            "Gallbladder not emptying properly",
            "Family history"
        ],
        "precautions": [
            "Maintain healthy weight",
            "Avoid rapid weight loss",
            "Eat regular, balanced meals",
            "Limit high-fat foods",
            "Stay hydrated"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for severe abdominal pain, fever, jaundice, or inability to pass gas/have bowel movement."
    },
    "hepatitis": {
        "keywords": ["hepatitis", "liver inflammation", "jaundice", "yellow skin", "yellow eyes", "liver pain"],
        "symptoms": ["jaundice", "fatigue", "nausea", "abdominal pain", "loss of appetite", "dark urine"],
        "severity": "High",
        "causes": [
            "Hepatitis A virus (fecal-oral)",
            "Hepatitis B virus (blood/fluids)",
            "Hepatitis C virus (blood)",
            "Alcoholic hepatitis",
            "Autoimmune hepatitis"
        ],
        "precautions": [
            "Avoid alcohol completely",
            "Rest",
            "Stay hydrated",
            "Eat nutritious foods",
            "Avoid spreading to others"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for severe vomiting, confusion, bleeding, or if jaundice becomes pronounced."
    },
    
    # CARDIOVASCULAR CONDITIONS
    "heart_attack": {
        "keywords": ["heart attack", "myocardial infarction", "chest pressure", "arm pain", "sweating nausea", "crushing chest"],
        "symptoms": ["chest pain/pressure", "arm pain", "jaw pain", "sweating", "nausea", "shortness of breath"],
        "severity": "High",
        "causes": [
            "Coronary artery blockage",
            "Blood clot",
            "Spasm of coronary artery",
            "Heart disease"
        ],
        "precautions": [
            "Call emergency services immediately",
            "Chew aspirin if not allergic",
            "Stay calm and rest",
            "Loosen tight clothing",
            "Do NOT drive yourself"
        ],
        "emergency_warning": "⚠️🚨 EMERGENCY: HEART ATTACK CAN BE FATAL! Call emergency services immediately if experiencing chest pain radiating to arm/jaw, sweating, nausea, or shortness of breath. Every minute counts!"
    },
    "angina": {
        "keywords": ["angina", "chest tightness", "heart pain", "exercise chest pain", "stress chest pain"],
        "symptoms": ["chest pain", "chest tightness", "pressure in chest", "shortness of breath", "fatigue"],
        "severity": "High",
        "causes": [
            "Coronary artery disease",
            "Reduced blood flow to heart",
            "Exercise or stress",
            "Cold weather"
        ],
        "precautions": [
            "Rest when angina occurs",
            "Use prescribed nitroglycerin",
            "Avoid strenuous activity",
            "Manage stress",
            "Follow heart-healthy diet"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care if chest pain doesn't stop with rest or nitroglycerin, or if it's different from usual angina."
    },
    "arrhythmia": {
        "keywords": ["arrhythmia", "irregular heartbeat", "heart palpitation", "heart flutter", "racing heart", "slow heartbeat"],
        "symptoms": ["palpitations", "racing heartbeat", "slow heartbeat", "dizziness", "shortness of breath"],
        "severity": "Medium",
        "causes": [
            "Heart disease",
            "High blood pressure",
            "Electrolyte imbalances",
            "Thyroid problems",
            "Stimulants"
        ],
        "precautions": [
            "Avoid caffeine and alcohol",
            "Manage stress",
            "Get regular check-ups",
            "Take medications as prescribed",
            "Monitor heart rate"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for fainting, severe dizziness, chest pain, or difficulty breathing."
    },
    "heart_failure": {
        "keywords": ["heart failure", "congestive heart", "fluid retention", "leg swelling", "shortness breath lying"],
        "symptoms": ["shortness of breath", "leg swelling", "fatigue", "cough", "fluid retention", "weight gain"],
        "severity": "High",
        "causes": [
            "Coronary artery disease",
            "Previous heart attack",
            "High blood pressure",
            "Heart valve problems",
            "Cardiomyopathy"
        ],
        "precautions": [
            "Limit salt intake",
            "Monitor weight daily",
            "Take diuretics as prescribed",
            "Rest with legs elevated",
            "Follow low-sodium diet"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for sudden difficulty breathing, chest pain, fainting, or coughing up pink foam."
    },
    "hypertension": {
        "keywords": ["high blood pressure", "hypertension", "high bp", "blood pressure high", "headache high bp"],
        "symptoms": ["headache", "shortness of breath", "nosebleeds", "dizziness", "chest pain"],
        "severity": "Medium",
        "causes": [
            "Essential hypertension (unknown cause)",
            "Kidney disease",
            "Adrenal tumors",
            "Certain medications",
            "Lifestyle factors"
        ],
        "precautions": [
            "Reduce sodium intake",
            "Exercise regularly",
            "Maintain healthy weight",
            "Limit alcohol",
            "Take medications as prescribed"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for blood pressure above 180/120, chest pain, difficulty breathing, severe headache, or vision changes."
    },
    "stroke": {
        "keywords": ["stroke", "brain attack", "face droop", "arm weakness", "speech difficulty", "numbness face"],
        "symptoms": ["face drooping", "arm weakness", "speech difficulty", "numbness", "confusion", "vision loss"],
        "severity": "High",
        "causes": [
            "Ischemic stroke (blood clot)",
            "Hemorrhagic stroke (bleeding)",
            "Transient ischemic attack (TIA)"
        ],
        "precautions": [
            "Call emergency services immediately (FAST test)",
            "Note time symptoms started",
            "Do NOT give food or water",
            "Keep person calm",
            "Do NOT let them sleep"
        ],
        "emergency_warning": "⚠️🚨 EMERGENCY: STROKE IS A MEDICAL EMERGENCY! Call emergency services IMMEDIATELY if someone has face drooping, arm weakness, or speech difficulty. Time-sensitive treatment available!"
    },
    "dvt_deep_vein": {
        "keywords": ["dvt", "blood clot", "leg swelling", "leg pain", "deep vein", "calf pain"],
        "symptoms": ["leg swelling", "leg pain", "warmth in leg", "redness", "prominent veins"],
        "severity": "High",
        "causes": [
            "Immobility",
            "Surgery",
            "Injury to veins",
            "Blood clotting disorders",
            "Pregnancy"
        ],
        "precautions": [
            "Move legs regularly",
            "Wear compression socks",
            "Stay hydrated",
            "Avoid long periods of sitting",
            "Take blood thinners if prescribed"
        ],
        "emergency_warning": "⚠️ EMERGENCY: DVT can cause pulmonary embolism (lung clot). Seek IMMEDIATE care for sudden shortness of breath, chest pain, or coughing up blood."
    },
    
    # NEUROLOGICAL CONDITIONS
    "migraine": {
        "keywords": ["migraine", "severe headache", "throbbing head", "light sensitive", "sound sensitive", "aura", "migrain", "adhe sir dard", "ek taraf sir dard", "tej sir dard", "shaur sharir kehte hain"],
        "symptoms": ["severe headache", "nausea", "sensitivity to light", "sensitivity to sound", "visual disturbances", "tej sir dard", "micchhami", "roshni se takleef", "awaz se takleef", "ankhon me dikkat", "aura", "dhuan dikhai dena", "chakkar"],
        "severity": "Medium",
        "causes": [
            "Genetic predisposition",
            "Hormonal changes",
            "Stress",
            "Certain foods",
            "Sleep changes"
        ],
        "precautions": [
            "Rest in dark, quiet room",
            "Use cold compress on head",
            "Take migraine medication early",
            "Identify and avoid triggers",
            "Maintain regular sleep schedule"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for worst headache ever, fever, stiff neck, confusion, or first migraine over age 50."
    },
    "tension_headache": {
        "keywords": ["tension headache", "stress headache", "pressure head", "tight head", "band headache"],
        "symptoms": ["headache", "pressure on head", "tightness in neck", "shoulder tension", "fatigue"],
        "severity": "Low",
        "causes": [
            "Stress",
            "Poor posture",
            "Muscle tension",
            "Lack of sleep",
            "Dehydration"
        ],
        "precautions": [
            "Practice stress management",
            "Take breaks from screens",
            "Maintain good posture",
            "Get regular exercise",
            "Ensure adequate sleep"
        ],
        "emergency_warning": ""
    },
    "meningitis": {
        "keywords": ["meningitis", "neck stiffness", "neck rigid", "meninges", "neck pain fever", "headache stiff neck"],
        "symptoms": ["severe headache", "neck stiffness", "fever", "sensitivity to light", "confusion", "rash"],
        "severity": "High",
        "causes": [
            "Bacterial infection",
            "Viral infection",
            "Fungal infection",
            "Non-infectious causes"
        ],
        "precautions": [
            "Seek immediate medical care",
            "Do NOT wait for rash to appear",
            "Rest in quiet, dark room",
            "Stay hydrated",
            "Complete all prescribed treatment"
        ],
        "emergency_warning": "⚠️🚨 EMERGENCY: Meningitis can be fatal within hours! Seek IMMEDIATE care for headache + neck stiffness + fever, especially with confusion or rash."
    },
    "concussion": {
        "keywords": ["concussion", "head injury", "brain injury", "hit head", "dizzy after fall", "confusion after head"],
        "symptoms": ["headache", "dizziness", "confusion", "nausea", "sensitivity to light", "memory problems"],
        "severity": "Medium",
        "causes": [
            "Head impact",
            "Fall",
            "Sports injury",
            "Vehicle accident",
            "Assault"
        ],
        "precautions": [
            "Rest (both physical and mental)",
            "Avoid screens initially",
            "No strenuous activity",
            "Stay with someone for 24 hours",
            "Gradual return to activities"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for worsening headache, repeated vomiting, seizures, slurred speech, or loss of consciousness."
    },
    "epilepsy": {
        "keywords": ["epilepsy", "seizure", "convulsion", "fitting", "uncontrolled movement", "episode"],
        "symptoms": ["seizure", "convulsions", "loss of consciousness", "confusion", "staring spells", "stiffening"],
        "severity": "High",
        "causes": [
            "Genetic factors",
            "Brain injury",
            "Stroke",
            "Brain tumors",
            "Infections"
        ],
        "precautions": [
            "Take medications regularly",
            "Get adequate sleep",
            "Avoid triggers (flashing lights)",
            "Wear medical alert bracelet",
            "Avoid swimming alone"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Call emergency services if seizure lasts more than 5 minutes, person doesn't wake up, or it's their first seizure."
    },
    "parkinsons": {
        "keywords": ["parkinson", "tremor", "shaking hand", "slow movement", "stiffness", "balance problems"],
        "symptoms": ["tremor", "stiffness", "slowed movement", "balance problems", "mask-like face"],
        "severity": "Medium",
        "causes": [
            "Loss of dopamine-producing neurons",
            "Genetic factors",
            "Environmental factors"
        ],
        "precautions": [
            "Take medications on schedule",
            "Exercise regularly",
            "Use assistive devices",
            "Home safety modifications",
            "Physical therapy"
        ],
        "emergency_warning": ""
    },
    
    # ENDOCRINE/METABOLIC CONDITIONS
    "diabetes_type1": {
        "keywords": ["diabetes type 1", "type 1 diabetic", "insulin dependent", "thirst extreme", "urinating frequent", "diabetes type 1", "sugar", "khun me sugar", "insulin", "bhukh jyada", "pani piyana jyada", "mutra jyada"],
        "symptoms": ["excessive thirst", "frequent urination", "extreme hunger", "fatigue", "weight loss", "blurred vision", "bahut piana", "bahut mutra", "bahut bhukh", "thakan", "weight kam", "dikhai dubna"],
        "severity": "High",
        "causes": [
            "Autoimmune destruction of insulin-producing cells",
            "Genetic factors",
            "Unknown triggers"
        ],
        "precautions": [
            "Monitor blood sugar regularly",
            "Take insulin as prescribed",
            "Count carbohydrates",
            "Exercise regularly",
            "Attend regular check-ups"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Check for diabetic ketoacidosis (DKA) - confusion, fruity breath, rapid breathing. This is life-threatening! Also check for severe hypoglycemia (low sugar) - sweating, shakiness, confusion."
    },
    "diabetes_type2": {
        "keywords": ["diabetes type 2", "type 2 diabetes", "blood sugar high", "pre-diabetes", "insulin resistance", "sugar jyada", "blood sugar", "sugar ki bimari", "sugar level"],
        "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision", "slow healing", "dark patches", "pyas jyada", "mutra jyada", "thakan", "ankhon me dikkat", "ghutne dheere", "kale daag"],
        "severity": "Medium",
        "causes": [
            "Insulin resistance",
            "Genetic factors",
            "Obesity",
            "Lifestyle factors"
        ],
        "precautions": [
            "Maintain healthy weight",
            "Exercise regularly",
            "Monitor blood sugar",
            "Follow diabetic diet",
            "Take medications as prescribed"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for very high blood sugar (above 400), confusion, fruity breath, or difficulty breathing."
    },
    "hypothyroidism": {
        "keywords": ["hypothyroid", "underactive thyroid", "thyroid low", "fatigue weight gain", "cold intolerant", "hair loss thyroid", "thyroid kam", "gal gland", "thakan aur weight badhna", "thand sahi nahi", "bal girna"],
        "symptoms": ["fatigue", "weight gain", "cold intolerance", "dry skin", "hair loss", "constipation", "thakan", "weight badhna", "thand", "sookha skin", "bal girna", "kabz", "neend aana", "mansik thakan"],
        "severity": "Medium",
        "causes": [
            "Hashimoto's thyroiditis",
            "Thyroid surgery",
            "Radiation therapy",
            "Iodine deficiency"
        ],
        "precautions": [
            "Take thyroid medication daily",
            "Get regular blood tests",
            "Maintain iodine-rich diet",
            "Manage stress",
            "Regular exercise"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Myxedema coma is rare but life-threatening - seek care for severe hypothermia, confusion, or slowed breathing."
    },
    "hyperthyroidism": {
        "keywords": ["hyperthyroid", "overactive thyroid", "thyroid high", "weight loss thyroid", "heart racing thyroid", "anxious thyroid", "thyroid jyada", "gal gland jyada", "weight ghatna", "dil tez chalna", "chinta"],
        "symptoms": ["weight loss", "rapid heartbeat", "anxiety", "tremors", "heat intolerance", "sweating", "weight ghatna", "tej dharkan", "chinta", "hilti hui haath", "garamhi", "pasina"],
        "severity": "Medium",
        "causes": [
            "Graves' disease",
            "Toxic nodular goiter",
            "Thyroiditis",
            "Excess iodine"
        ],
        "precautions": [
            "Take anti-thyroid medications",
            "Avoid iodine-rich foods",
            "Manage stress",
            "Regular monitoring",
            "Adequate calorie intake"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Thyroid storm (thyrotoxic crisis) is life-threatening - seek care for fever above 104°F, rapid heart rate, confusion, or vomiting."
    },
    
    # MUSCULOSKELETAL CONDITIONS
    "arthritis": {
        "keywords": ["arthritis", "joint pain", "joint swelling", "stiff joints", "knee pain", "hip pain"],
        "symptoms": ["joint pain", "joint swelling", "stiffness", "reduced range of motion", "warmth in joints"],
        "severity": "Medium",
        "causes": [
            "Osteoarthritis (wear and tear)",
            "Rheumatoid arthritis (autoimmune)",
            "Psoriatic arthritis",
            "Gout"
        ],
        "precautions": [
            "Exercise regularly (low impact)",
            "Maintain healthy weight",
            "Use joint protection",
            "Apply heat/cold therapy",
            "Take anti-inflammatory medications"
        ],
        "emergency_warning": ""
    },
    "gout": {
        "keywords": ["gout", "big toe pain", "joint inflammation", "uric acid", "swollen joint", "foot pain"],
        "symptoms": ["severe joint pain", "swelling", "redness", "heat in joint", "commonly in big toe"],
        "severity": "Medium",
        "causes": [
            "High uric acid levels",
            "Purine-rich foods",
            "Alcohol consumption",
            "Kidney problems",
            "Genetics"
        ],
        "precautions": [
            "Limit purine-rich foods (red meat, seafood)",
            "Avoid alcohol",
            "Stay hydrated",
            "Maintain healthy weight",
            "Take medications as prescribed"
        ],
        "emergency_warning": ""
    },
    "fracture": {
        "keywords": ["fracture", "broken bone", "bone break", "xray", "snap", "trauma"],
        "symptoms": ["severe pain", "swelling", "deformity", "inability to move", "bruising"],
        "severity": "High",
        "causes": [
            "Trauma/fall",
            "Sports injury",
            "Accident",
            "Osteoporosis",
            "Repetitive stress"
        ],
        "precautions": [
            "Do NOT move injured area",
            "Call emergency services",
            "Apply ice wrapped in cloth",
            "Keep person still",
            "Treat for shock if needed"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for obvious deformity, bone protruding, heavy bleeding, or inability to move."
    },
    "back_pain": {
        "keywords": ["back pain", "lower back pain", "backache", "spine pain", "back stiffness"],
        "symptoms": ["back pain", "stiffness", "muscle ache", "limited movement", "sciatica"],
        "severity": "Low",
        "causes": [
            "Muscle strain",
            "Poor posture",
            "Herniated disc",
            "Arthritis",
            "Osteoporosis"
        ],
        "precautions": [
            "Rest briefly (not prolonged)",
            "Apply heat/cold",
            "Maintain good posture",
            "Exercise strengthen back",
            "Use proper lifting technique"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for back pain with fever, bowel/bladder problems, numbness in legs, or after severe injury."
    },
    "fibromyalgia": {
        "keywords": ["fibromyalgia", "widespread pain", "tender points", "all over pain", "chronic pain"],
        "symptoms": ["widespread pain", "fatigue", "sleep problems", "cognitive issues", "headaches"],
        "severity": "Medium",
        "causes": [
            "Unknown (possibly abnormal pain processing)",
            "Genetics",
            "Trauma",
            "Infections"
        ],
        "precautions": [
            "Regular exercise",
            "Stress management",
            "Adequate sleep",
            "Pace activities",
            "Follow treatment plan"
        ],
        "emergency_warning": ""
    },
    
    # SKIN CONDITIONS
    "eczema": {
        "keywords": ["eczema", "dermatitis", "skin inflammation", "itchy rash", "dry skin rash", "atopic"],
        "symptoms": ["itchy skin", "dry skin", "redness", "rash", "thickened skin", "flaking"],
        "severity": "Low",
        "causes": [
            "Genetic factors",
            "Immune system dysfunction",
            "Environmental triggers",
            "Stress",
            "Allergens"
        ],
        "precautions": [
            "Moisturize regularly",
            "Avoid triggers",
            "Use mild soaps",
            "Wear cotton clothing",
            "Manage stress"
        ],
        "emergency_warning": ""
    },
    "psoriasis": {
        "keywords": ["psoriasis", "scaly skin", "skin plaques", "red patches", "silver scales"],
        "symptoms": ["red patches", "silver scales", "dry skin", "itching", "thickened nails", "joint pain"],
        "severity": "Medium",
        "causes": [
            "Autoimmune condition",
            "Genetic factors",
            "Triggers (stress, infection)",
            "Certain medications"
        ],
        "precautions": [
            "Moisturize skin",
            "Avoid triggers",
            "Take medications as prescribed",
            "Phototherapy if recommended",
            "Manage stress"
        ],
        "emergency_warning": ""
    },
    "cellulitis": {
        "keywords": ["cellulitis", "skin infection", "spreading redness", "infected skin", "warm skin"],
        "symptoms": ["redness", "swelling", "warmth", "pain", "fever", "tenderness"],
        "severity": "High",
        "causes": [
            "Bacterial infection (Strep, Staph)",
            "Break in skin",
            "Skin conditions",
            "Weakened immune system"
        ],
        "precautions": [
            "Complete all antibiotics",
            "Keep wound clean",
            "Elevate affected area",
            "Monitor for spreading",
            "Rest"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for rapidly spreading redness, fever, confusion, or red streaks from the area."
    },
    "shingles": {
        "keywords": ["shingles", "herpes zoster", "rash painful", "blisters rash", "nerve pain rash"],
        "symptoms": ["painful rash", "blisters", "burning sensation", "tingling", "fever", "headache"],
        "severity": "Medium",
        "causes": [
            "Varicella-zoster virus (chickenpox reactivation)",
            "Age (risk increases over 50)",
            "Weakened immune system",
            "Stress"
        ],
        "precautions": [
            "Start antiviral medication ASAP",
            "Keep rash clean and dry",
            "Don't scratch blisters",
            "Avoid pregnant people/immunocompromised",
            "Pain management"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care if rash is near eyes (can cause vision damage) or if symptoms are severe."
    },
    
    # MENTAL HEALTH CONDITIONS
    "depression": {
        "keywords": ["depression", "depressed", "sadness", "no interest", "hopeless", "worthlessness"],
        "symptoms": ["persistent sadness", "loss of interest", "fatigue", "sleep changes", "appetite changes", "feelings of guilt"],
        "severity": "Medium",
        "causes": [
            "Chemical imbalances in brain",
            "Genetic factors",
            "Life events",
            "Medical conditions",
            "Substance abuse"
        ],
        "precautions": [
            "Seek professional help",
            "Regular exercise",
            "Maintain routine",
            "Social support",
            "Consider therapy/medication"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate help for thoughts of suicide, self-harm, or inability to care for basic needs."
    },
    "anxiety": {
        "keywords": ["anxiety", "anxious", "worry", "panic", "nervousness", "stress", "panic attack"],
        "symptoms": ["excessive worry", "restlessness", "rapid heartbeat", "shortness of breath", "sweating", "difficulty concentrating"],
        "severity": "Medium",
        "causes": [
            "Genetic factors",
            "Brain chemistry",
            "Life stressors",
            "Medical conditions",
            "Substance use"
        ],
        "precautions": [
            "Practice deep breathing",
            "Regular exercise",
            "Limit caffeine",
            "Adequate sleep",
            "Consider therapy"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for chest pain, difficulty breathing, or feeling out of control during panic attack."
    },
    "panic_disorder": {
        "keywords": ["panic attack", "panic disorder", "overwhelming fear", "heart racing", "shaking", "suffocating"],
        "symptoms": ["intense fear", "racing heart", "shaking", "shortness of breath", "chest pain", "feeling of dying"],
        "severity": "Medium",
        "causes": [
            "Genetic factors",
            "Brain chemistry",
            "Stress",
            "Trauma"
        ],
        "precautions": [
            "Learn breathing techniques",
            "Challenge anxious thoughts",
            "Regular exercise",
            "Avoid alcohol/drugs",
            "Consider therapy/medication"
        ],
        "emergency_warning": "⚠️ EMERGENCY: While panic attacks aren't dangerous, symptoms can mimic heart attack. Seek care to rule out cardiac issues."
    },
    
    # INFECTIOUS DISEASES
    "malaria": {
        "keywords": ["malaria", "mosquito", "travel malaria", "shaking chills", "high fever cycles", "malaria", "machar ke daag", "kala bukhar", "fever with chills"],
        "symptoms": ["fever", "chills", "sweating", "headache", "nausea", "muscle pain", "bukhar", "thandak", "pasina", "sir dard", "micchhami", "sharir me dard", "ukhunna", "lazar", "teeth chattering"],
        "severity": "High",
        "causes": [
            "Plasmodium parasite (mosquito bite)",
            "P. falciparum (most dangerous)",
            "P. vivax, P. ovale, P. malariae"
        ],
        "precautions": [
            "Use mosquito nets",
            "Apply insect repellent",
            "Take prophylactic medication when traveling",
            "Eliminate mosquito breeding sites",
            "Seek prompt treatment"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Malaria can be fatal within 24 hours. Seek IMMEDIATE care if you have fever within weeks of traveling to malaria area."
    },
    "dengue": {
        "keywords": ["dengue", "dengue fever", "breakbone fever", "mosquito dengue", "rash dengue", "dengu", "dangoo", "mosquito bite fever", "machar ka daag"],
        "symptoms": ["high fever", "severe headache", "rash", "muscle pain", "joint pain", "bleeding", "bukhar", "sir dard", "chhatiya", "muscle dard", "joint pain", "khun nikalna", "aaton me dard", "gardan me dard", "ankhon me dard"],
        "severity": "High",
        "causes": [
            "Dengue virus (mosquito-borne)",
            "Aedes mosquito bite",
            "Multiple serotypes"
        ],
        "precautions": [
            "Use mosquito repellent",
            "Wear protective clothing",
            "Eliminate standing water",
            "Rest",
            "Stay hydrated"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Dengue hemorrhagic fever is life-threatening. Seek immediate care for severe abdominal pain, persistent vomiting, bleeding gums, or difficulty breathing."
    },
    "typhoid": {
        "keywords": ["typhoid", "typhoid fever", "continuous fever", "abdominal pain fever", "rose spots", "taifoid", "tapadi", "pet ka bukhar"],
        "symptoms": ["high fever", "headache", "abdominal pain", "constipation", "rash", "weakness", "bukhar", "sir dard", "pet dard", "kabz", "chhatiya", "kamzori", "thakan", "dengee", "tap"],
        "severity": "High",
        "causes": [
            "Salmonella Typhi bacteria",
            "Contaminated food/water",
            "Fecal-oral transmission"
        ],
        "precautions": [
            "Get vaccinated",
            "Drink safe water",
            "Eat cooked foods",
            "Wash hands frequently",
            "Complete antibiotic treatment"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for severe abdominal pain, intestinal bleeding, or confusion."
    },
    "chikungunya": {
        "keywords": ["chikungunya", "chikungunya fever", "joint pain fever", "mosquito joint", "chikangunya", "chikun gunya", "joint pain mosquito", "machar se hone wala dard"],
        "symptoms": ["fever", "severe joint pain", "rash", "headache", "muscle pain", "fatigue", "bukhar", "bohot joint dard", "chhatiya", "sir dard", "muscle dard", "thakan", "guchhi hona", "swelling"],
        "severity": "Medium",
        "causes": [
            "Chikungunya virus (mosquito-borne)",
            "Aedes mosquito bite"
        ],
        "precautions": [
            "Use mosquito repellent",
            "Rest",
            "Stay hydrated",
            "Take pain relievers",
            "Protect others from mosquitoes"
        ],
        "emergency_warning": ""
    },
    
    # ALLERGIC REACTIONS
    "allergic_reaction": {
        "keywords": ["allergy", "allergic reaction", "hives", "itching", "swelling", "rash", "allerghi", "ek derma", "khujli", "sujan", "chhatiya", "dust allergy", "khaana allergy", "doodh allergy", "phoolon se allergy"],
        "symptoms": ["hives", "itching", "swelling", "rash", "sneezing", "watery eyes", "khujli", "sujan", "chhatiya", "chhina", "chini aana", "ankhon me aansu", "dant me sujan", "deh me khujli"],
        "severity": "Medium",
        "causes": [
            "Food allergens",
            "Medication allergens",
            "Environmental allergens",
            "Insect stings",
            "Latex"
        ],
        "precautions": [
            "Avoid known allergens",
            "Carry epinephrine if prescribed",
            "Take antihistamines",
            "Wear medical alert bracelet",
            "Identify and avoid triggers"
        ],
        "emergency_warning": "⚠️ EMERGENCY: ANAPHYLAXIS is life-threatening! Seek immediate care for difficulty breathing, throat swelling, dizziness, or rapid heartbeat."
    },
    "anaphylaxis": {
        "keywords": ["anaphylaxis", "allergic emergency", "severe allergy", "throat swelling", "cant breathe", "anaphylactic shock", "khuna", "tej allergy", "gale me sujan", "saans nahi aa rahi", "allergy se mareep"],
        "symptoms": ["difficulty breathing", "throat swelling", "dizziness", "rapid heartbeat", "hives", "vomiting", "saans lene me dikkat", "gale me sujan", "chakkar aana", "tej dharkan", "chhatiya", "ultis", "muh sujana", "ankhon me andhera"],
        "severity": "High",
        "causes": [
            "Food allergens (nuts, shellfish)",
            "Medication allergens",
            "Insect stings",
            "Latex"
        ],
        "precautions": [
            "Carry epinephrine auto-injector",
            "Wear medical alert ID",
            "Avoid all allergens",
            "Educate family/friends",
            "Regular check-ups"
        ],
        "emergency_warning": "⚠️🚨 EMERGENCY: ANAPHYLAXIS IS LIFE-THREATENING! Use epinephrine auto-injector and call emergency services IMMEDIATELY. Do NOT wait!"
    },
    
    # KIDNEY/URINARY CONDITIONS
    "uti": {
        "keywords": ["uti", "urinary infection", "bladder infection", "pain urination", "burning urine", "frequent urination", "moo trachy", "petisha", "pathri", "water ki problem", "urine me jalan", "urine me khuun"],
        "symptoms": ["painful urination", "frequent urination", "urgency", "cloudy urine", "pelvic pain", "blood in urine", "mutra prait", "bathne me dard", "jaldi jaldi mutra aana", "dull mutra", "pelvic dard", "mutra me khuun", "bathne me jalan"],
        "severity": "Medium",
        "causes": [
            "E. coli bacteria",
            "Sexual activity",
            "Poor hygiene",
            "Kidney stones",
            "Diabetes"
        ],
        "precautions": [
            "Complete all antibiotics",
            "Drink plenty of water",
            "Urinate after intercourse",
            "Wipe front to back",
            "Avoid irritants"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for fever, back pain (kidney infection), or confusion - infection may have spread to blood."
    },
    "kidney_stones": {
        "keywords": ["kidney stones", "kidney pain", "renal colic", "back pain severe", "flank pain", "stone"],
        "symptoms": ["severe back pain", "flank pain", "blood in urine", "nausea", "vomiting", "painful urination"],
        "severity": "High",
        "causes": [
            "Calcium oxalate stones",
            "Uric acid stones",
            "Dehydration",
            "Diet high in oxalates",
            "Family history"
        ],
        "precautions": [
            "Stay hydrated (3L water/day)",
            "Limit sodium",
            "Reduce oxalate foods",
            "Moderate animal protein",
            "Take prescribed medications"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for fever (infection), inability to urinate, or severe pain not controlled by medication."
    },
    "kidney_infection": {
        "keywords": ["kidney infection", "pyelonephritis", "kidney pain fever", "back pain fever", "chills kidney"],
        "symptoms": ["fever", "back/flank pain", "nausea", "vomiting", "frequent urination", "burning urination"],
        "severity": "High",
        "causes": [
            "Bacteria from bladder infection",
            "E. coli",
            "Urinary tract obstruction",
            "Weakened immune system"
        ],
        "precautions": [
            "Complete all antibiotics",
            "Rest",
            "Stay hydrated",
            "Complete follow-up testing",
            "Treat underlying UTIs promptly"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Kidney infection can cause sepsis (blood infection). Seek IMMEDIATE care for high fever, shaking chills, confusion, or rapid heartbeat."
    },
    
    # EYE CONDITIONS
    "conjunctivitis": {
        "keywords": ["conjunctivitis", "pink eye", "red eye", "eye infection", "eye discharge", "watery eye"],
        "symptoms": ["redness", "itching", "discharge", "gritty feeling", "crusty eyes", "tearing"],
        "severity": "Low",
        "causes": [
            "Viral infection",
            "Bacterial infection",
            "Allergies",
            "Irritants"
        ],
        "precautions": [
            "Don't touch eyes",
            "Wash hands frequently",
            "Use warm compresses",
            "Don't share towels",
            "Complete antibiotic course if prescribed"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for pain, vision changes, or light sensitivity."
    },
    "stye": {
        "keywords": ["stye", "hordeolum", "eye bump", "eyelid bump", "painful eyelid"],
        "symptoms": ["painful bump on eyelid", "redness", "swelling", "tenderness", "tearing"],
        "severity": "Low",
        "causes": [
            "Bacterial infection (Staph)",
            "Blocked oil gland",
            "Poor eyelid hygiene"
        ],
        "precautions": [
            "Apply warm compress",
            "Don't squeeze the stye",
            "Keep area clean",
            "Don't wear makeup/lenses",
            "Wash hands before touching eyes"
        ],
        "emergency_warning": ""
    },
    
    # OTHER CONDITIONS
    "anemia": {
        "keywords": ["anemia", "low blood", "tiredness", "pale skin", "shortness breath", "dizzy", "khun ki kami", "rupiya", "nakli", "lal patla", "saans lene me dikkat"],
        "symptoms": ["fatigue", "pallor", "shortness of breath", "dizziness", "headache", "cold hands/feet", "thakan", "rupiya", "saans lene me pareshani", "chakkar aana", "sir dard", "thand hath panw"],
        "severity": "Medium",
        "causes": [
            "Iron deficiency",
            "Vitamin B12 deficiency",
            "Chronic blood loss",
            "Bone marrow problems",
            "Hemolysis"
        ],
        "precautions": [
            "Eat iron-rich foods",
            "Take supplements if prescribed",
            "Treat underlying cause",
            "Avoid blood loss",
            "Regular monitoring"
        ],
        "emergency_warning": "⚠️ EMERGENCY: Seek immediate care for chest pain, shortness of breath at rest, or fainting."
    },
    "cancer": {
        "keywords": ["cancer", "tumor", "lump", "mass", "unexplained weight loss", "bleeding abnormal"],
        "symptoms": ["unexplained weight loss", "lump/mass", "unusual bleeding", "fatigue", "persistent pain", "persistent cough"],
        "severity": "High",
        "causes": [
            "Genetic mutations",
            "Carcinogens",
            "Viruses",
            "Lifestyle factors",
            "Family history"
        ],
        "precautions": [
            "Get regular screenings",
            "Know your family history",
            "Healthy lifestyle",
            "Know warning signs",
            "Early detection improves outcomes"
        ],
        "emergency_warning": "⚠️ IMPORTANT: Many cancers are treatable when caught early. Consult doctor for persistent unusual symptoms."
    },
    "default": {
        "keywords": [],
        "symptoms": [],
        "severity": "Medium",
        "causes": [
            "Various potential causes - further evaluation needed",
            "Could be related to stress or lifestyle factors",
            "May require laboratory tests for accurate diagnosis",
            "Could be early signs of a condition that needs medical attention"
        ],
        "precautions": [
            "Maintain a symptom diary",
            "Get adequate rest",
            "Stay hydrated",
            "Monitor symptoms for changes",
            "Consult a healthcare provider if symptoms persist"
        ],
        "emergency_warning": "⚠️ If symptoms are severe, persistent, or worsening, please consult a qualified healthcare professional immediately."
    }
}


def sanitize_input(text):
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text: User input string
        
    Returns:
        Sanitized string with HTML entities escaped
    """
    return html.escape(text.strip())


def analyze_symptoms_ml(symptoms, language='en'):
    """
    Advanced symptom analysis using keyword matching and scoring.
    
    Args:
        symptoms: User-provided symptoms string
        language: Language for response ('en', 'hi', or 'hinglish')
        
    Returns:
        Dictionary containing structured analysis results
    """
    symptoms_lower = symptoms.lower()
    
    # Remove punctuation and normalize
    symptoms_clean = re.sub(r'[^\w\s]', ' ', symptoms_lower)
    symptoms_list = symptoms_clean.split()
    
    # Score each condition based on keyword matches
    condition_scores = {}
    
    for condition_name, condition_data in MEDICAL_CONDITIONS.items():
        if condition_name == "default":
            continue
            
        score = 0
        matched_keywords = []
        
        # Check keywords
        for keyword in condition_data["keywords"]:
            if keyword in symptoms_lower:
                score += 3
                matched_keywords.append(keyword)
        
        # Check symptoms
        for symptom in condition_data["symptoms"]:
            if symptom in symptoms_lower:
                score += 2
            # Also check individual words
            for word in symptoms_list:
                if len(word) > 3 and word in symptom:
                    score += 1
        
        if score > 0:
            condition_scores[condition_name] = {
                "score": score,
                "matched": matched_keywords
            }
    
    # Sort by score
    sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1]["score"], reverse=True)
    
    # Get the best match if score is significant
    if sorted_conditions and sorted_conditions[0][1]["score"] >= 3:
        best_condition = sorted_conditions[0][0]
        condition = MEDICAL_CONDITIONS[best_condition]
        
        # Prepare causes and precautions based on language
        if language == 'hi':
            # Hindi only
            causes = condition.get('causes_hi', condition.get('causes', []))
            precautions = condition.get('precautions_hi', condition.get('precautions', []))
        elif language == 'hinglish':
            # Bilingual: English + Hindi
            causes = condition.get('causes', []) + condition.get('causes_hi', [])
            precautions = condition.get('precautions', []) + condition.get('precautions_hi', [])
        else:
            # English (default)
            causes = condition.get('causes', [])
            precautions = condition.get('precautions', [])
        
        return {
            "possible_causes": causes,
            "precautions": precautions,
            "severity": condition["severity"],
            "emergency_warning": condition["emergency_warning"],
            "matched_condition": best_condition,
            "confidence": min(sorted_conditions[0][1]["score"] * 10, 100),
            "disclaimer": "This is not medical advice. Consult a qualified doctor.",
            "language": language
        }
    
    # Return default response for unrecognized symptoms
    default = MEDICAL_CONDITIONS["default"]
    
    # Prepare default causes and precautions based on language
    if language == 'hi':
        causes = default.get('causes_hi', default.get('causes', []))
        precautions = default.get('precautions_hi', default.get('precautions', []))
    elif language == 'hinglish':
        causes = default.get('causes', []) + default.get('causes_hi', [])
        precautions = default.get('precautions', []) + default.get('precautions_hi', [])
    else:
        causes = default.get('causes', [])
        precautions = default.get('precautions', [])
    
    return {
        "possible_causes": causes,
        "precautions": precautions,
        "severity": default["severity"],
        "emergency_warning": default["emergency_warning"],
        "matched_condition": None,
        "confidence": 0,
        "disclaimer": "This is not medical advice. Consult a qualified doctor.",
        "language": language
    }


def get_mock_response(symptoms, language='en'):
    """
    Generate a mock AI response using the enhanced symptom analysis.
    
    Args:
        symptoms: User-provided symptoms string
        language: Language for response ('en', 'hi', or 'hinglish')
        
    Returns:
        Dictionary containing structured analysis results
    """
    return analyze_symptoms_ml(symptoms, language)


def get_ai_response(symptoms):
    """
    Get AI-powered analysis of symptoms using OpenAI API.
    
    Args:
        symptoms: User-provided symptoms string
        
    Returns:
        Dictionary containing structured analysis results
    """
    prompt = f"""Act as a general physician. Based on the provided symptoms: {symptoms}

Please provide a structured response with the following sections:
1. Possible Causes (not diagnosis) - List 3-5 possible causes
2. Basic Precautions - List 3-5 precautionary measures
3. Severity Level - Assign as Low, Medium, or High
4. Emergency Warning - Add if condition seems serious

Keep output structured, concise, and user-friendly. Format your response as JSON with these keys:
- possible_causes (array)
- precautions (array)
- severity (string: "Low", "Medium", or "High")
- emergency_warning (string or empty string if not needed)

Do not provide any diagnosis - only possible causes based on symptoms presented."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical information assistant. Provide general health information only, not medical diagnoses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        # Parse the AI response
        ai_content = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            json_start = ai_content.find('{')
            json_end = ai_content.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = ai_content[json_start:json_end]
                result = json.loads(json_str)
                
                # Add disclaimer to the result
                result["disclaimer"] = "This is not medical advice. Consult a qualified doctor."
                
                return result
            else:
                # If no JSON found, return error
                return {
                    "error": "Could not parse AI response",
                    "possible_causes": ["Unable to analyze symptoms"],
                    "precautions": ["Please try again or consult a doctor"],
                    "severity": "Unknown",
                    "emergency_warning": "",
                    "disclaimer": "This is not medical advice. Consult a qualified doctor."
                }
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse AI response",
                "possible_causes": ["Unable to analyze symptoms"],
                "precautions": ["Please try again or consult a doctor"],
                "severity": "Unknown",
                "emergency_warning": "",
                "disclaimer": "This is not medical advice. Consult a qualified doctor."
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "possible_causes": ["An error occurred during analysis"],
            "precautions": ["Please try again later"],
            "severity": "Unknown",
            "emergency_warning": "",
            "disclaimer": "This is not medical advice. Consult a qualified doctor."
        }


@app.route('/')
def index():
    """Render the intro/landing page."""
    return render_template('intro.html')

@app.route('/language')
def language():
    """Render the language selection page."""
    return render_template('language.html')

@app.route('/home')
def home():
    """Render the main symptom checker page."""
    language = request.args.get('lang', 'en')
    return render_template('index.html', language=language)


@app.route('/voice-assistant')
def voice_assistant():
    """Render the voice assistant page."""
    return render_template('voice_assistant.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_symptoms():
    """
    API endpoint to analyze symptoms.
    
    Expects JSON payload with 'symptoms' field and optional 'language' field.
    Returns JSON with analysis results.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "possible_causes": [],
                "precautions": [],
                "severity": "",
                "emergency_warning": ""
            }), 400
        
        # Get symptoms and language from request
        symptoms = data.get('symptoms', '')
        language = data.get('language', 'en')  # Default to English
        
        # Sanitize input
        symptoms = sanitize_input(symptoms)
        
        # Validate symptoms
        if not symptoms or len(symptoms) < 2:
            return jsonify({
                "error": "Please enter your symptoms",
                "possible_causes": [],
                "precautions": [],
                "severity": "",
                "emergency_warning": ""
            }), 400
        
        if len(symptoms) > 1000:
            return jsonify({
                "error": "Symptom description is too long",
                "possible_causes": [],
                "precautions": [],
                "severity": "",
                "emergency_warning": ""
            }), 400
        
        # Use mock response if no OpenAI API key
        if not client:
            print(f"Using enhanced symptom analysis for: {symptoms} (lang: {language})")
            result = get_mock_response(symptoms, language)
            return jsonify(result)
        
        # Get AI response
        result = get_ai_response(symptoms, language)
        
        # Check for errors in result
        if "error" in result and result["error"]:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "possible_causes": [],
            "precautions": [],
            "severity": "",
            "emergency_warning": ""
        }), 500


@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    """Get list of all supported conditions."""
    conditions = []
    for name, data in MEDICAL_CONDITIONS.items():
        if name != "default":
            conditions.append({
                "name": name,
                "keywords": data["keywords"][:5],  # First 5 keywords
                "severity": data["severity"]
            })
    return jsonify(conditions)


@app.route('/api/voice-chat', methods=['POST'])
def voice_chat():
    """
    Voice chat endpoint for the AI assistant.
    Accepts Hindi, English, or Hinglish input.
    Returns AI response in the same language.
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "No message provided",
                "response": ""
            }), 400
        
        user_message = data.get('message', '')
        language = data.get('language', 'hi-IN')
        history = data.get('history', [])
        
        # Sanitize input
        user_message = sanitize_input(user_message)
        
        if not user_message or len(user_message) < 2:
            return jsonify({
                "error": "Please provide a valid message",
                "response": ""
            }), 400
        
        # Determine language for response
        if 'hi' in language or language == 'hinglish':
            system_prompt = """You are a friendly AI Health Assistant. Respond in Hindi (with some English if needed).
You should:
- Ask about symptoms and health concerns
- Provide general health advice
- Suggest precautions
- Mention when to see a doctor
- Keep responses conversational and helpful
- Never provide specific diagnoses
- Always suggest consulting a doctor for proper medical advice

Use simple language that anyone can understand."""
            response_lang = "Hindi"
        else:
            system_prompt = """You are a friendly AI Health Assistant. Respond in English.
You should:
- Ask about symptoms and health concerns
- Provide general health advice
- Suggest precautions
- Mention when to see a doctor
- Keep responses conversational and helpful
- Never provide specific diagnoses
- Always suggest consulting a doctor for proper medical advice

Use simple language that anyone can understand."""
            response_lang = "English"
        
        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history (last 6 messages)
        for msg in history[-6:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Use OpenAI if available, otherwise use local database
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                ai_response = response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI error: {e}")
                ai_response = get_local_health_response(user_message, language)
        else:
            ai_response = get_local_health_response(user_message, language)
        
        return jsonify({
            "response": ai_response,
            "language": response_lang
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "response": "Sorry, I encountered an error. Please try again."
        }), 500


def get_local_health_response(message, language):
    """
    Get a local response based on keywords when OpenAI is not available.
    Supports Hindi, English, and Hinglish.
    """
    message_lower = message.lower()
    
    # Define responses in both languages
    responses = {
        "symptom_check": {
            "hi": "मैं आपके लक्षणों के बारे में जानना चाहूंगा। कृपया बताएं कि आपको क्या समस्या है? जैसे सिरदर्द, बुखार, खांसी, या कोई दर्द।",
            "en": "I'd like to know about your symptoms. Please tell me what you're experiencing - like headache, fever, cough, or any pain."
        },
        "fever": {
            "hi": "बुखार के कई कारण हो सकते हैं जैसे इन्फ्लुएंज़ा, इन्फेक्शन, या गर्मी की वजह से। अगर बुखार 102°F से ऊपर है या 3 दिन से ज्यादा है, तो डॉक्टर से मिलें। पर्याप्त पानी पिएं और आराम करें।",
            "en": "Fever can be caused by many things like flu, infection, or heat exposure. If fever is above 102°F or lasts more than 3 days, please see a doctor. Drink plenty of fluids and rest."
        },
        "cold_cough": {
            "hi": "सर्दी और खांसी आमतौर पर वायरल इन्फेक्शन से होती है। गरम पानी पिएं, आराम करें, और अगर लक्षण बढ़ें तो डॉक्टर से मिलें।",
            "en": "Cold and cough are usually caused by viral infections. Drink warm water, rest, and see a doctor if symptoms worsen."
        },
        "headache": {
            "hi": "सिरदर्द के कई कारण हो सकते हैं जैसे तनाव, माइग्रेन, या आंखों का तनाव। अगर सिरदर्द गंभीर है या बार-बार होता है, तो डॉक्टर से मिलें।",
            "en": "Headache can be caused by many things like stress, migraine, or eye strain. If headache is severe or frequent, please see a doctor."
        },
        "stomach": {
            "hi": "पेट दर्द के कई कारण हो सकते हैं। अगर दर्द गंभीर है या उल्टी/दस्त के साथ है, तो तुरंत डॉक्टर से मिलें।",
            "en": "Stomach pain can have many causes. If pain is severe or accompanied by vomiting/diarrhea, please see a doctor immediately."
        },
        "general_advice": {
            "hi": "स्वस्थ रहने के लिए: संतुलित आहार लें, पर्याप्त नींद लें, व्यायाम करें, और तनाव से बचें। अगर कोई गंभीर लक्षण हो तो डॉक्टर से मिलें।",
            "en": "For staying healthy: eat a balanced diet, get enough sleep, exercise, and avoid stress. If you have any serious symptoms, please see a doctor."
        },
        "doctor_visit": {
            "hi": "अगर आपको गंभीर लक्षण हैं जैसे सीने में दर्द, सांस लेने में कठिनाई, या तेज बुखार, तो तुरंत डॉक्टर से मिलें।",
            "en": "If you have serious symptoms like chest pain, difficulty breathing, or high fever, please see a doctor immediately."
        },
        "default": {
            "hi": "मैं समझ नहीं पाया। क्या आप अपने लक्षणों के बारे में बता सकते हैं? जैसे - सिरदर्द, बुखार, खांसी, पेट दर्द, थकान, आदि।",
            "en": "I didn't understand. Can you tell me about your symptoms? Like - headache, fever, cough, stomach pain, fatigue, etc."
        }
    }
    
    # Check for keywords in the message
    if any(word in message_lower for word in ['symptom', 'problem', 'issue', 'lakhshan', 'takleef', 'दर्द', 'परेशानी', 'समस्या']):
        return responses['symptom_check']['hi'] if 'hi' in language else responses['symptom_check']['en']
    
    if any(word in message_lower for word in ['fever', 'bukhar', 'bujha', 'taap', 'बुखार', 'तेज़ बुखार']):
        return responses['fever']['hi'] if 'hi' in language else responses['fever']['en']
    
    if any(word in message_lower for word in ['cold', 'cough', 'khansi', 'sardi', 'सर्दी', 'खांसी']):
        return responses['cold_cough']['hi'] if 'hi' in language else responses['cold_cough']['en']
    
    if any(word in message_lower for word in ['head', 'sir', 'sirdard', 'headache', 'सिर', 'सिरदर्द']):
        return responses['headache']['hi'] if 'hi' in language else responses['headache']['en']
    
    if any(word in message_lower for word in ['stomach', 'pet', 'pain', 'dard', 'पेट', 'पेट दर्द', 'pet dard']):
        return responses['stomach']['hi'] if 'hi' in language else responses['stomach']['en']
    
    if any(word in message_lower for word in ['advice', 'suggest', 'help', 'salah', 'madad', 'सलाह', 'सहायता', 'advice']):
        return responses['general_advice']['hi'] if 'hi' in language else responses['general_advice']['en']
    
    if any(word in message_lower for word in ['doctor', 'hospital', 'clinic', 'daktar', 'डॉक्टर', 'अस्पताल']):
        return responses['doctor_visit']['hi'] if 'hi' in language else responses['doctor_visit']['en']
    
    # Default response
    return responses['default']['hi'] if 'hi' in language else responses['default']['en']


# =====================================================
# COMPREHENSIVE EMERGENCY CONTACTS DATABASE
# =====================================================

EMERGENCY_CONTACTS = {
    "india": {
        "emergency": {
            "number": "112",
            "name": "Emergency Services",
            "icon": "🆘",
            "description": "All emergency services"
        },
        "ambulance": {
            "number": "102",
            "name": "Ambulance",
            "icon": "🚑",
            "description": "Medical emergency ambulance"
        },
        "police": {
            "number": "100",
            "name": "Police",
            "icon": "🚔",
            "description": "Police emergency"
        },
        "fire": {
            "number": "101",
            "name": "Fire Department",
            "icon": "🚒",
            "description": "Fire emergency"
        },
        "disaster": {
            "number": "108",
            "name": "Disaster Management",
            "icon": "🌪️",
            "description": "Disaster relief services"
        },
        "poison_control": {
            "number": "1066",
            "name": "Poison Control",
            "icon": "☠️",
            "description": "Poison emergency helpline"
        },
        "medical_emergency": {
            "number": "102",
            "name": "Medical Emergency",
            "icon": "🏥",
            "description": "National medical emergency"
        },
        "women_helpline": {
            "number": "1091",
            "name": "Women Helpline",
            "icon": "👩",
            "description": "Women emergency assistance"
        },
        "child_helpline": {
            "number": "1098",
            "name": "Child Helpline",
            "icon": "👶",
            "description": "Child emergency assistance"
        },
        "mental_health": {
            "number": "1800-599-0019",
            "name": "Mental Health Helpline",
            "icon": "🧠",
            "description": "Mental health support"
        },
        "covid": {
            "number": "1075",
            "name": "COVID Helpline",
            "icon": "🦠",
            "description": "COVID-19 assistance"
        },
        "air_ambulance": {
            "number": "104",
            "name": "Air Ambulance",
            "icon": "🚁",
            "description": "Air emergency services"
        },
        "railway": {
            "number": "139",
            "name": "Railway Helpline",
            "icon": "🚂",
            "description": "Railway emergency"
        },
        "road_accident": {
            "number": "1073",
            "name": "Road Accident Emergency",
            "icon": "🚗",
            "description": "Road accident emergency"
        }
    },
    "usa": {
        "emergency": {
            "number": "911",
            "name": "Emergency Services",
            "icon": "🆘",
            "description": "All emergency services"
        },
        "poison_control": {
            "number": "1-800-222-1222",
            "name": "Poison Control",
            "icon": "☠️",
            "description": "Poison emergency helpline"
        },
        "suicide_prevention": {
            "number": "988",
            "name": "Suicide Prevention",
            "icon": "🧠",
            "description": "Mental health crisis line"
        },
        "police": {
            "number": "911",
            "name": "Police",
            "icon": "🚔",
            "description": "Police emergency"
        },
        "fire": {
            "number": "911",
            "name": "Fire Department",
            "icon": "🚒",
            "description": "Fire emergency"
        }
    },
    "uk": {
        "emergency": {
            "number": "999",
            "name": "Emergency Services",
            "icon": "🆘",
            "description": "All emergency services"
        },
        "ambulance": {
            "number": "999",
            "name": "Ambulance",
            "icon": "🚑",
            "description": "Medical emergency"
        },
        "police": {
            "number": "999",
            "name": "Police",
            "icon": "🚔",
            "description": "Police emergency"
        },
        "poison": {
            "number": "111",
            "name": "NHS Helpline",
            "icon": "☠️",
            "description": "NHS non-emergency"
        }
    }
}

# Specialist type mapping based on symptoms
SPECIALIST_MAPPING = {
    "cardiologist": {
        "keywords": ["chest pain", "heart", "cardiac", "palpitation", "heartbeat", "cardiovascular", "bp", "blood pressure", "chest tightness"],
        "name": "Cardiologist",
        "icon": "❤️",
        "query": "cardiologist"
    },
    "pulmonologist": {
        "keywords": ["breathing", "lung", "cough", "asthma", "respiratory", "shortness of breath", "wheezing", "tb", "tuberculosis"],
        "name": "Pulmonologist",
        "icon": "🫁",
        "query": "pulmonologist"
    },
    "dermatologist": {
        "keywords": ["skin", "rash", "allergy", "itching", "eczema", "psoriasis", "acne", "dermatitis", "skin infection"],
        "name": "Dermatologist",
        "icon": "🧴",
        "query": "dermatologist"
    },
    "neurologist": {
        "keywords": ["headache", "migraine", "brain", "nerve", "seizure", "epilepsy", "stroke", "dizziness", "vertigo", "tremor"],
        "name": "Neurologist",
        "icon": "🧠",
        "query": "neurologist"
    },
    "orthopedist": {
        "keywords": ["bone", "joint", "fracture", "sprain", "back pain", "neck pain", "knee pain", "arthritis", "muscle tear"],
        "name": "Orthopedist",
        "icon": "🦴",
        "query": "orthopedist"
    },
    "psychiatrist": {
        "keywords": ["mental", "depression", "anxiety", "stress", "suicide", "panic", "mental health", "psychological"],
        "name": "Psychiatrist",
        "icon": "🧘",
        "query": "psychiatrist"
    },
    "pediatrician": {
        "keywords": ["child", "kid", "infant", "baby", "pediatric", "children health"],
        "name": "Pediatrician",
        "icon": "👶",
        "query": "pediatrician"
    },
    "gastroenterologist": {
        "keywords": ["stomach", "digestion", "liver", "vomiting", "diarrhea", "constipation", "gastric", "intestine", "food poisoning"],
        "name": "Gastroenterologist",
        "icon": "🫃",
        "query": "gastroenterologist"
    },
    "gynecologist": {
        "keywords": ["pregnancy", "pregnant", "period", "menstrual", "women health", "fertility", "pcod", "pcos"],
        "name": "Gynecologist",
        "icon": "🏥",
        "query": "gynecologist"
    },
    "ophthalmologist": {
        "keywords": ["eye", "vision", "sight", "blind", "cataract", "glaucoma", "eye pain", "eye problem"],
        "name": "Ophthalmologist",
        "icon": "👁️",
        "query": "ophthalmologist"
    },
    "ent": {
        "keywords": ["ear", "nose", "throat", "hearing", "sinus", "nasal", "tonsil", "ear pain", "hearing loss"],
        "name": "ENT Specialist",
        "icon": "👂",
        "query": "ent specialist"
    },
    "general_physician": {
        "keywords": ["fever", "cold", "flu", "general", "unknown", "tired", "fatigue", "weakness", "symptom"],
        "name": "General Physician",
        "icon": "🩺",
        "query": "general physician"
    }
}


@app.route('/api/emergency-contacts')
def get_emergency_contacts():
    """
    Get emergency contacts for a specific country.
    Query params: country (default: 'india')
    Returns: JSON with all emergency contact numbers
    """
    country = request.args.get('country', 'india').lower()
    contacts = EMERGENCY_CONTACTS.get(country, EMERGENCY_CONTACTS['india'])
    
    return jsonify({
        "country": country,
        "contacts": contacts,
        "total": len(contacts)
    })


@app.route('/api/analyze-symptoms', methods=['POST'])
def analyze_symptoms_for_specialist():
    """
    Analyze symptoms to determine the appropriate specialist type.
    Accepts JSON: { "symptoms": "description of symptoms" }
    Returns: JSON with recommended specialist type
    """
    try:
        data = request.get_json()
        if not data or 'symptoms' not in data:
            return jsonify({"error": "No symptoms provided"}), 400
        
        symptoms = data['symptoms'].lower()
        language = data.get('language', 'en')
        
        # Find matching specialist
        best_match = None
        best_score = 0
        
        for specialist_type, specialist_info in SPECIALIST_MAPPING.items():
            score = 0
            for keyword in specialist_info['keywords']:
                if keyword in symptoms:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = {
                    "type": specialist_type,
                    "name": specialist_info['name'],
                    "icon": specialist_info['icon'],
                    "query": specialist_info['query']
                }
        
        # Default to general physician if no match
        if not best_match:
            best_match = {
                "type": "general_physician",
                "name": SPECIALIST_MAPPING["general_physician"]["name"],
                "icon": SPECIALIST_MAPPING["general_physician"]["icon"],
                "query": SPECIALIST_MAPPING["general_physician"]["query"]
            }
        
        # Get emergency warning if symptoms indicate emergency
        emergency_keywords = ["chest pain", "heart attack", "stroke", "difficulty breathing", "bleeding", "unconscious", "seizure", "severe pain"]
        is_emergency = any(kw in symptoms for kw in emergency_keywords)
        
        return jsonify({
            "symptoms": symptoms,
            "specialist": best_match,
            "is_emergency": is_emergency,
            "language": language,
            "all_specialists": [{"type": specialist_type, "name": s["name"], "icon": s["icon"]} for specialist_type, s in SPECIALIST_MAPPING.items()]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/find-doctors', methods=['POST'])
def find_doctors():
    """
    Find nearby doctors based on symptoms and location.
    Accepts JSON: { 
        "symptoms": "description of symptoms",
        "latitude": 123.456,
        "longitude": 78.901,
        "radius": 5000 (optional, in meters)
    }
    Returns: JSON with list of nearby specialists
    
    Note: This uses Google Places API. If API key is not configured,
    returns mock data for demonstration.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        symptoms = data.get('symptoms', '')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 10000)  # Default 10km radius
        
        if not latitude or not longitude:
            return jsonify({"error": "Location not provided"}), 400
        
        # Analyze symptoms to get specialist type
        symptoms_lower = symptoms.lower()
        best_match = None
        best_score = 0
        
        for specialist_type, specialist_info in SPECIALIST_MAPPING.items():
            score = 0
            for keyword in specialist_info['keywords']:
                if keyword in symptoms_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = {
                    "type": specialist_type,
                    "name": specialist_info['name'],
                    "icon": specialist_info['icon'],
                    "query": specialist_info['query']
                }
        
        if not best_match:
            best_match = {
                "type": "general_physician",
                "name": SPECIALIST_MAPPING["general_physician"]["name"],
                "icon": SPECIALIST_MAPPING["general_physician"]["icon"],
                "query": SPECIALIST_MAPPING["general_physician"]["query"]
            }
        
        # Check for Google Maps API key
        google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        
        if google_api_key:
            # Use Google Places API to fetch real doctors
            doctors = fetch_doctors_from_google_places(latitude, longitude, best_match['query'], radius, google_api_key)
        else:
            # Return mock data for demonstration
            doctors = generate_mock_doctors(latitude, longitude, best_match)
        
        return jsonify({
            "user_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "search_query": best_match['query'],
            "specialist": best_match,
            "doctors": doctors,
            "count": len(doctors),
            "radius_meters": radius
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def fetch_doctors_from_google_places(lat, lng, query, radius, api_key):
    """
    Fetch doctors from Google Places API.
    Requires: Google Places API enabled in Google Cloud Console
    """
    import requests
    
    # Use Places API - Nearby Search
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "hospital",
        "keyword": query,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        doctors = []
        for place in data.get('results', [])[:10]:  # Limit to 10 results
            doctors.append({
                "name": place.get('name'),
                "address": place.get('vicinity'),
                "location": {
                    "lat": place.get('geometry', {}).get('location', {}).get('lat'),
                    "lng": place.get('geometry', {}).get('location', {}).get('lng')
                },
                "rating": place.get('rating', 0),
                "user_ratings_total": place.get('user_ratings_total', 0),
                "place_id": place.get('place_id'),
                "open_now": place.get('opening_hours', {}).get('open_now'),
                "types": place.get('types', [])
            })
        
        return doctors
        
    except Exception as e:
        print(f"Error fetching from Google Places: {e}")
        return generate_mock_doctors(lat, lng, {"type": query, "name": query.title(), "icon": "🩺"})


def generate_mock_doctors(lat, lng, specialist):
    """
    Generate mock doctor data for demonstration when Google API is not configured.
    """
    import random
    
    # Sample doctor names
    doctor_names = [
        f"Dr. {random.choice(['Rajesh', 'Priya', 'Amit', 'Sunita', 'Vijay', 'Anita', 'Rahul', 'Meera'])} "
        f"{random.choice(['Kumar', 'Sharma', 'Patel', 'Gupta', 'Singh', 'Verma', 'Joshi', 'Reddy'])}",
        f"{specialist['name']} Clinic",
        f"City {specialist['name']} Center",
        f"Health Plus {specialist['name']}",
        f"Medicare Hospital - {specialist['name']}"
    ]
    
    addresses = [
        f"{random.randint(1, 500)}, Main Road, {random.choice(['Sector 15', 'Civil Lines', 'Model Town', 'Raj Nagar', 'Kamla Nagar'])}",
        f"{random.randint(1, 200)}, {random.choice(['Park Street', 'MG Road', 'Nehru Road', 'Gandhi Chowk'])}",
        f"{random.randint(1, 100)}, {random.choice(['Hospital Road', 'Medical Campus', 'Health Avenue', 'Care Center'])}"
    ]
    
    doctors = []
    for i in range(8):
        # Generate random offset within ~5km
        offset_lat = (random.random() - 0.5) * 0.02
        offset_lng = (random.random() - 0.5) * 0.02
        
        doctors.append({
            "name": doctor_names[i % len(doctor_names)],
            "address": addresses[i % len(addresses)],
            "location": {
                "lat": lat + offset_lat,
                "lng": lng + offset_lng
            },
            "rating": round(random.uniform(3.5, 5.0), 1),
            "user_ratings_total": random.randint(10, 500),
            "distance_km": round(random.uniform(0.5, 5.0), 1),
            "phone": f"+91-{random.randint(7000000000, 9999999999)}",
            "open_now": random.choice([True, False, None]),
            "specialization": specialist['name'],
            "icon": specialist['icon']
        })
    
    # Sort by rating
    doctors.sort(key=lambda x: x['rating'], reverse=True)
    
    return doctors


@app.route('/api/get-directions', methods=['GET'])
def get_directions():
    """
    Get directions to a specific doctor.
    Query params: origin_lat, origin_lng, dest_lat, dest_lng
    Returns: URL for Google Maps directions
    """
    origin_lat = request.args.get('origin_lat')
    origin_lng = request.args.get('origin_lng')
    dest_lat = request.args.get('dest_lat')
    dest_lng = request.args.get('dest_lng')
    
    if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
        return jsonify({"error": "Missing coordinates"}), 400
    
    # Generate Google Maps directions URL
    directions_url = f"https://www.google.com/maps/dir/{origin_lat},{origin_lng}/{dest_lat},{dest_lng}"
    
    return jsonify({
        "directions_url": directions_url
    })


@app.route('/api/countries')
def get_countries():
    """
    Get list of supported countries for emergency contacts.
    """
    return jsonify({
        "countries": [
            {"code": "india", "name": "India", "flag": "🇮🇳"},
            {"code": "usa", "name": "United States", "flag": "🇺🇸"},
            {"code": "uk", "name": "United Kingdom", "flag": "🇬🇧"}
        ]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "api_available": bool(client),
        "conditions_count": len([c for c in MEDICAL_CONDITIONS if c != "default"])
    })


@app.route('/api/speak', methods=['POST'])
def speak_text():
    """
    Text-to-Speech endpoint using edge-tts for melodious Indian voices.
    Accepts JSON: { "text": "text to speak", "lang": "en", "hi", or "hinglish" }
    Returns: Audio file (MP3)
    
    Voice Options (Melodious Female Voices):
    - English: en-IN-NeerjaExpressiveNeural (expressive Indian female voice)
    - Hindi: hi-IN-SwaraNeural (very melodious Hindi female voice)
    - Hinglish: en-IN-NeerjaExpressiveNeural (handles code-switching well)
    """
    try:
        import edge_tts
        import asyncio
        import io
        import tempfile
        import os
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        lang = data.get('lang', 'en').lower()  # 'en', 'hi', or 'hinglish'
        
        # Select the most melodious female voice based on language
        # Using ExpressiveNeural for more natural-sounding voice
        voice_map = {
            'en': 'en-IN-NeerjaExpressiveNeural',       # English - Indian female (expressive)
            'hi': 'hi-IN-SwaraNeural',                  # Hindi - very melodious female
            'hinglish': 'en-IN-NeerjaExpressiveNeural',  # Hinglish - English female (handles mixing)
        }
        
        voice = voice_map.get(lang, 'en-IN-NeerjaExpressiveNeural')
        
        # Create communicate object
        communicate = edge_tts.Communicate(text, voice)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            temp_path = tmp.name
        
        # Run async to save audio
        asyncio.run(communicate.save(temp_path))
        
        # Read the file
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Return as audio file
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
        
    except ImportError:
        return jsonify({"error": "Text-to-speech not available. Please install edge-tts: pip install edge-tts"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting AI Health Symptom Checker...")
    print(f"OpenAI API: {'Available' if client else 'Not configured (using enhanced symptom database)'}")
    print(f"Medical conditions in database: {len([c for c in MEDICAL_CONDITIONS if c != 'default'])}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
